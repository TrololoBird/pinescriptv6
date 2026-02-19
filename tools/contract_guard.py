#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

PINE_FILE = Path("prizrak_trade_setup_detector_v12_0_0.pine")
LOCK_FILE = Path("contract.lock.json")
INPUT_RE = re.compile(r"^\s*[A-Za-z_]\w*\s*=\s*input\.\w+\s*\(")
INDICATOR_RE = re.compile(r"^\s*indicator\s*\(")
ALERT_RE = re.compile(r"^\s*alertcondition\s*\(")


def sha256_lines(lines: List[str]) -> str:
    payload = "\n".join(lines).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_block(lines: List[str]) -> Dict[str, object]:
    return {
        "count": len(lines),
        "sha256": sha256_lines(lines),
        "lines": lines,
    }


def extract_contract(path: Path) -> Dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing canonical Pine file: {path}")

    text_lines = path.read_text(encoding="utf-8").splitlines()

    indicator_lines = [ln for ln in text_lines if INDICATOR_RE.match(ln)]
    if len(indicator_lines) != 1:
        raise ValueError(
            f"Expected exactly 1 indicator(...) line in {path}, found {len(indicator_lines)}"
        )

    input_lines = [ln for ln in text_lines if INPUT_RE.match(ln)]
    alert_lines = [ln for ln in text_lines if ALERT_RE.match(ln)]

    return {
        "source_file": str(path),
        "indicator": build_block(indicator_lines),
        "inputs": build_block(input_lines),
        "alerts": build_block(alert_lines),
    }


def print_block_diff(name: str, actual: Dict[str, object], expected: Dict[str, object], max_lines: int) -> None:
    print(f"\n[{name}] mismatch")
    print(f"  expected count={expected.get('count')} sha256={expected.get('sha256')}")
    print(f"  actual   count={actual.get('count')} sha256={actual.get('sha256')}")
    exp_lines = expected.get("lines", [])
    act_lines = actual.get("lines", [])
    diff = list(
        difflib.unified_diff(
            exp_lines,
            act_lines,
            fromfile=f"lock/{name}",
            tofile=f"current/{name}",
            lineterm="",
        )
    )
    if not diff:
        return
    print("  first diff lines:")
    for ln in diff[:max_lines]:
        print(f"    {ln}")
    if len(diff) > max_lines:
        print(f"    ... ({len(diff) - max_lines} more lines omitted)")


def run_check(max_lines: int) -> int:
    if not LOCK_FILE.exists():
        print(f"ERROR: lock file not found: {LOCK_FILE}")
        print("Run: python tools/contract_guard.py --init")
        return 2

    current = extract_contract(PINE_FILE)
    expected = json.loads(LOCK_FILE.read_text(encoding="utf-8"))

    bad = False
    for block in ("indicator", "inputs", "alerts"):
        if current.get(block) != expected.get(block):
            bad = True
            print_block_diff(block, current.get(block, {}), expected.get(block, {}), max_lines)

    if bad:
        print("\nContract check FAILED.")
        print("If the interface change is intentional, run: python tools/contract_guard.py --init and commit contract.lock.json")
        return 1

    print("Contract check OK.")
    return 0


def _git_changed_files() -> List[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", "--", "."],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return []
    return [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]


def run_dev_check(max_lines: int) -> int:
    current = extract_contract(PINE_FILE)
    if LOCK_FILE.exists():
        expected = json.loads(LOCK_FILE.read_text(encoding="utf-8"))
    else:
        expected = {}

    print("DEV contract report:")
    changed_blocks: List[str] = []
    for block in ("indicator", "inputs", "alerts"):
        actual_block = current.get(block, {})
        expected_block = expected.get(block, {})
        if actual_block != expected_block:
            changed_blocks.append(block)
            print(f"- {block}: changed")
            print(f"  lock   count={expected_block.get('count')} sha256={expected_block.get('sha256')}")
            print(f"  actual count={actual_block.get('count')} sha256={actual_block.get('sha256')}")
            print_block_diff(block, actual_block, expected_block, max_lines)
        else:
            print(
                f"- {block}: unchanged (count={actual_block.get('count')} sha256={actual_block.get('sha256')})"
            )

    if not changed_blocks:
        print("DEV contract report: no contract drift.")
        return 0

    changed_files = set(_git_changed_files())
    docs_touched = (
        "docs/COURSE_LOGIC_SPEC.md" in changed_files
        or "docs/CHANGELOG_DEV.md" in changed_files
    )

    if docs_touched:
        print("DEV guard OK: contract changed and docs updated (COURSE_LOGIC_SPEC.md or CHANGELOG_DEV.md).")
        return 0

    print("\nDEV guard FAILED: contract/interface changed, but no docs update found in git diff.")
    print("Touch one of:")
    print("- docs/COURSE_LOGIC_SPEC.md")
    print("- docs/CHANGELOG_DEV.md")
    return 1


def run_init() -> int:
    contract = extract_contract(PINE_FILE)
    LOCK_FILE.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {LOCK_FILE}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Guard Pine public contract (indicator/inputs/alerts).")
    parser.add_argument("--init", action="store_true", help="Rebuild contract lock from current Pine file")
    parser.add_argument("--check", action="store_true", help="Run check in selected mode (default action)")
    parser.add_argument(
        "--mode",
        choices=("dev", "release"),
        default=os.environ.get("CONTRACT_MODE", "dev"),
        help="Contract guard mode: dev (report+docs guard) or release (strict lock)",
    )
    parser.add_argument("--max-diff-lines", type=int, default=20, help="Max diff lines per block")
    args = parser.parse_args()

    if args.init:
        return run_init()

    if args.mode == "release":
        return run_check(max_lines=args.max_diff_lines)
    return run_dev_check(max_lines=args.max_diff_lines)


if __name__ == "__main__":
    sys.exit(main())

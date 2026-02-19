#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PINE_FILE = Path("prizrak_trade_setup_detector_v12_0_0.pine")

NA_COMPARE_RE = re.compile(r"(==\s*na\b|!=\s*na\b)")
NAMED_ASSIGN_IN_CALL_RE = re.compile(r"\([^\n)]*\b[A-Za-z_]\w*\s*:=")


def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    sys.exit(1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Pine lint guard (v12)")
    parser.add_argument("--dev", action="store_true", help="Print extra info")
    _ = parser.parse_args()

    if not PINE_FILE.exists():
        fail(f"Missing file: {PINE_FILE}")

    lines = PINE_FILE.read_text(encoding="utf-8").splitlines()
    text = "\n".join(lines)

    na_hits = [(i, ln.strip()) for i, ln in enumerate(lines, 1) if NA_COMPARE_RE.search(ln)]
    if na_hits:
        details = "; ".join([f"line {i}: {txt}" for i, txt in na_hits[:10]])
        fail(f"Forbidden comparison with na: {details}")

    named_assign_hits = [(i, ln.strip()) for i, ln in enumerate(lines, 1) if NAMED_ASSIGN_IN_CALL_RE.search(ln)]
    if named_assign_hits:
        details = "; ".join([f"line {i}: {txt}" for i, txt in named_assign_hits[:10]])
        fail(f"Forbidden ':=' usage inside call args: {details}")

    if "indicator(" not in text:
        fail("Missing indicator(...) declaration")

    security_lines = [(i, ln.replace(" ", "")) for i, ln in enumerate(lines, 1) if "request.security" in ln]
    for i, ln in security_lines:
        if "lookahead=barmerge.lookahead_off" not in ln or "gaps=barmerge.gaps_off" not in ln:
            fail(f"request.security at line {i} must set gaps_off + lookahead_off")

    print("Lint guard OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

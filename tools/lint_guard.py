#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PINE_FILE = Path("prizrak_trade_setup_detector_v12_0_0.pine")
NA_COMPARE_RE = re.compile(r"(==\s*na\b|!=\s*na\b)")
SECURITY_RE = re.compile(r"request\.security\(")


def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    sys.exit(1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Pine lint guard")
    parser.add_argument("--dev", action="store_true", help="Enable DEV-only output")
    args = parser.parse_args()

    if not PINE_FILE.exists():
        fail(f"Missing file: {PINE_FILE}")

    lines = PINE_FILE.read_text(encoding="utf-8").splitlines()

    na_hits = [(i, ln.strip()) for i, ln in enumerate(lines, 1) if NA_COMPARE_RE.search(ln)]
    if na_hits:
        details = "; ".join([f"line {i}: {txt}" for i, txt in na_hits[:10]])
        fail(f"Forbidden comparison with na: {details}")

    for i, ln in enumerate(lines, 1):
        if SECURITY_RE.search(ln):
            compact = ln.replace(" ", "")
            if "lookahead=barmerge.lookahead_off" not in compact or "gaps=barmerge.gaps_off" not in compact:
                fail(f"request.security at line {i} must include gaps_off + lookahead_off")

    if args.dev:
        print("DEV lint: lightweight checks enabled")

    print("Lint guard OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

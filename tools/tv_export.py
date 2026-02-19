#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PINE_FILE = Path("prizrak_trade_setup_detector_v12_0_0.pine")


def strip_comments(text: str) -> str:
    out_lines = []
    for line in text.splitlines():
        if re.match(r"^\s*//", line):
            continue
        out_lines.append(line)
    return "\n".join(out_lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Export canonical Pine script for TradingView copy/paste")
    parser.add_argument("--strip-comments", action="store_true", help="Drop full-line comments for a shorter export")
    parser.add_argument("--out", type=Path, help="Optional output file path (e.g., dist/tv_export.pine)")
    args = parser.parse_args()

    if not PINE_FILE.exists():
        print(f"ERROR: Missing canonical Pine file: {PINE_FILE}", file=sys.stderr)
        return 1

    text = PINE_FILE.read_text(encoding="utf-8")
    payload = strip_comments(text) if args.strip_comments else text

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
        print(f"Wrote {args.out}", file=sys.stderr)
        return 0

    sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

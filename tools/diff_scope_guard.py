#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PINE_FILE = "prizrak_trade_setup_detector_v12_0_0.pine"

ALLOWED_TOKEN_RE = re.compile(
    r"(skin_|rr_c|f_opaque|f_with_alpha|f_contrast_text|"
    r"color\.new|color\.rgb|chart\.fg_color|chart\.bg_color|"
    r"line\.style_|label\.style_|\bsize\.|"
    r"border_width|border_color|bgcolor|color=|textcolor=|width=|style=|size=)"
)

BLOCKED_TOKEN_RE = re.compile(
    r"\b(if|else|for|while|switch)\b|"
    r"\b(ta\.|request\.|array\.|math\.)|"
    r"\b(bar_index|time|high|low|close|open|hlc3)\b|"
    r"(==|!=|<=|>=|\+|-|\*|/|%|\?|:)"
)


def get_diff(base: str) -> list[str]:
    cmd = ["git", "diff", base, "--", PINE_FILE]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        print(proc.stderr.strip())
        raise SystemExit(proc.returncode)
    return proc.stdout.splitlines()


def main() -> int:
    parser = argparse.ArgumentParser(description="Guard style-only Pine diffs")
    parser.add_argument("--mode", default="style-only", choices=["style-only"], help="Guard mode")
    parser.add_argument("--base", default="HEAD", help="git diff base")
    args = parser.parse_args()

    diff_lines = get_diff(args.base)
    if not diff_lines:
        print("Style diff guard OK: no diff.")
        return 0

    changed = []
    line_no_new = 0
    for ln in diff_lines:
        if ln.startswith("@@"):
            m = re.search(r"\+(\d+)", ln)
            line_no_new = int(m.group(1)) - 1 if m else 0
            continue
        if ln.startswith("+++") or ln.startswith("---") or ln.startswith("diff --git") or ln.startswith("index "):
            continue
        if ln.startswith("+"):
            line_no_new += 1
            content = ln[1:]
            if not content.strip() or content.strip().startswith("//"):
                continue
            changed.append((line_no_new, content))
        elif ln.startswith(" "):
            line_no_new += 1

    violations = []
    for lineno, content in changed:
        if BLOCKED_TOKEN_RE.search(content):
            violations.append((lineno, "blocked token", content.strip()))
            continue
        if not ALLOWED_TOKEN_RE.search(content):
            violations.append((lineno, "outside allowlist", content.strip()))

    if violations:
        print("Style-only diff guard FAILED.")
        for lineno, reason, content in violations[:30]:
            print(f"  line {lineno}: {reason}: {content}")
        if len(violations) > 30:
            print(f"  ... {len(violations)-30} more violations")
        return 1

    print("Style-only diff guard OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

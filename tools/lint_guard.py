#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

PINE_FILE = Path("prizrak_trade_setup_detector_v11_7_0.pine")

NA_COMPARE_RE = re.compile(r"(==\s*na\b|!=\s*na\b)")
VAR_SELF_ASSIGN_RE = re.compile(r"\bvar\s+\w+\s+([A-Za-z_]\w*)\s*=\s*\1\b")
SECTION_HEADER_RE = re.compile(r"^//\s*(={3,}|STATE\b|CORE\b|MODULES\b)")
RAW_COLOR_RE = re.compile(
    r"\bcolor\.(red|green|blue|black|white|yellow|gray|grey|orange|purple|teal|fuchsia|aqua|lime|maroon|navy|olive|silver)\b"
)


def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    sys.exit(1)


def main() -> int:
    if not PINE_FILE.exists():
        fail(f"Missing file: {PINE_FILE}")

    lines = PINE_FILE.read_text(encoding="utf-8").splitlines()

    # 1) na comparisons
    na_hits = [(i, ln.strip()) for i, ln in enumerate(lines, 1) if NA_COMPARE_RE.search(ln)]
    if na_hits:
        details = "; ".join([f"line {i}: {txt}" for i, txt in na_hits[:10]])
        fail(f"Forbidden comparison with na detected by regex {NA_COMPARE_RE.pattern}: {details}")

    # 2) var self assignment
    var_hits = [(i, ln.strip()) for i, ln in enumerate(lines, 1) if VAR_SELF_ASSIGN_RE.search(ln)]
    if var_hits:
        details = "; ".join([f"line {i}: {txt}" for i, txt in var_hits[:10]])
        fail(f"Forbidden var self-assignment detected by regex {VAR_SELF_ASSIGN_RE.pattern}: {details}")

    # 3) centralized constructors/deletes
    text = "\n".join(lines)
    exact_counts = {
        "box.new": 1,
        "line.new": 2,
        "label.new": 1,
        "box.delete": 1,
        "line.delete": 1,
        "label.delete": 1,
    }
    for token, expected in exact_counts.items():
        actual = text.count(token)
        if actual != expected:
            fail(f"Token count mismatch for '{token}': expected {expected}, got {actual}")

    # 4) request.security lookahead guard
    security_lines = [(i, ln) for i, ln in enumerate(lines, 1) if "request.security" in ln]
    if security_lines:
        bad = [
            (i, ln.strip())
            for i, ln in security_lines
            if "lookahead=barmerge.lookahead_off" not in ln.replace(" ", "")
        ]
        if bad:
            details = "; ".join([f"line {i}: {txt}" for i, txt in bad[:10]])
            fail("request.security must include lookahead=barmerge.lookahead_off. " + details)

    # 5) raw colors only inside skin area
    skin_start = None
    for i, ln in enumerate(lines, 1):
        if "f_opaque(" in ln or "zone_opacity_eff" in ln:
            skin_start = i
            break
    if skin_start is None:
        fail("Could not detect skin-start (expected 'f_opaque(' or 'zone_opacity_eff').")

    skin_end = len(lines) + 1
    for i in range(skin_start + 1, len(lines) + 1):
        if SECTION_HEADER_RE.search(lines[i - 1]):
            skin_end = i
            break

    bad_colors = []
    for i, ln in enumerate(lines, 1):
        if RAW_COLOR_RE.search(ln):
            in_skin = skin_start <= i < skin_end
            if not in_skin:
                bad_colors.append((i, ln.strip()))

    if bad_colors:
        details = "; ".join([f"line {i}: {txt}" for i, txt in bad_colors[:20]])
        fail(
            f"Raw color constants found outside skin area ({skin_start}-{skin_end - 1}): {details}"
        )

    print("Lint guard OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
FORBIDDEN_TUPLE_COLON_ASSIGN_RE = re.compile(r"\[[^\]]+\]\s*:=")
FORBIDDEN_LABEL_STYLE_TYPE_RE = re.compile(r"\blabel\.style\s+[A-Za-z_]\w*")
FORBIDDEN_ENUM_TYPE_RE = re.compile(r"\b(?:label\.style|line\.style|size)\s+[A-Za-z_]\w*")
FORBIDDEN_STYLE_STRING_SIG_RE = re.compile(r"\bstring\s+(_style|_st|_sz)\b")
FORBIDDEN_DRAW_STYLE_STRING_RE = re.compile(r"^\s*(?:var\s+)?string\s+[A-Za-z_]\w*(?:_style|_size|_st|_sz)\b\s*=")
HELPER_STYLE_STRING_SIG_RE = re.compile(r"^\s*f_(?:line_styled|label)\([^)]*\bstring\s+(_style|_st|_sz)\b")
NAMED_ASSIGN_IN_CALL_RE = re.compile(r"\([^\n)]*\b[A-Za-z_]\w*\s*:=")


def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    sys.exit(1)


def _extract_input_int(lines: list[str], name: str) -> int | None:
    pat = re.compile(rf"^\s*{re.escape(name)}\s*=\s*input\.int\(\s*([0-9]+)")
    for ln in lines:
        m = pat.match(ln)
        if m:
            return int(m.group(1))
    return None


def _line_index(lines: list[str], regex: re.Pattern[str]) -> int | None:
    for i, ln in enumerate(lines, 1):
        if regex.search(ln):
            return i
    return None


def _dev_object_budget_report(lines: list[str]) -> None:
    max_lines = 500
    max_labels = 500
    max_boxes = 300

    max_poc_keep = _extract_input_int(lines, "max_poc_keep") or 10
    rr_hist_keep = _extract_input_int(lines, "rr_hist_keep") or 80

    rr_safety_margin = 40
    rr_other_box_budget = 16
    rr_other_line_budget = 32
    rr_other_label_budget = 20
    rr_keep_dev_cap = max(5, int(rr_hist_keep * 0.8))
    rr_keep_by_boxes = max(5, (max(0, max_boxes - rr_safety_margin - rr_other_box_budget)) // 3)
    rr_keep_by_lines = max(5, (max(0, max_lines - rr_safety_margin - rr_other_line_budget)) // 1)
    rr_keep_by_labels = max(5, (max(0, max_labels - rr_safety_margin - rr_other_label_budget)) // 1)
    rr_keep_effective = max(5, min(rr_hist_keep, rr_keep_dev_cap, rr_keep_by_boxes, rr_keep_by_lines, rr_keep_by_labels))

    # Estimated concurrent objects in worst active state (heuristic, DEV-warning only):
    # lines: poc_lines + wl + sl + rr_open_entry + rr_hist_entry
    est_lines = max_poc_keep + 1 + 1 + 1 + rr_keep_effective
    # boxes: flat + rr_open(3) + rr_hist(3 per log entry)
    est_boxes = 1 + 3 + (3 * rr_keep_effective)
    # labels: working level + trap up/down + pp + rr_open_stat + rr_hist_stat
    est_labels = 1 + 1 + 1 + 1 + 1 + rr_keep_effective

    safe_ratio = 0.7
    warn = False
    for kind, est, cap in (("lines", est_lines, max_lines), ("boxes", est_boxes, max_boxes), ("labels", est_labels, max_labels)):
        ratio = est / cap
        if ratio > safe_ratio:
            warn = True
            print(
                f"WARN: DEV object budget high for {kind}: estimated={est}, cap={cap}, usage={ratio:.1%} (> {safe_ratio:.0%})"
            )
        else:
            print(
                f"INFO: DEV object budget {kind}: estimated={est}, cap={cap}, usage={ratio:.1%}"
            )
    if warn:
        print("WARN: Consider reducing max_poc_keep/rr_hist_keep or visual object density for safer long-history runtime.")
    print(f"INFO: DEV RR keep effective={rr_keep_effective}, requested={rr_hist_keep}, caps(box/line/label)={rr_keep_by_boxes}/{rr_keep_by_lines}/{rr_keep_by_labels}")



def _check_persistent_object_shadowing(lines: list[str]) -> None:
    persistent_decl_re = re.compile(r"^\s*var\s+(box|line|label)\s+([A-Za-z_]\w*)\b")
    local_object_decl_re = re.compile(r"^\s*(?!var\b)(box|line|label)\s+([A-Za-z_]\w*)\b")

    persistent: dict[str, tuple[str, int]] = {}
    for i, ln in enumerate(lines, 1):
        m = persistent_decl_re.match(ln)
        if m:
            persistent[m.group(2)] = (m.group(1), i)

    shadow_hits: list[tuple[int, str, str, int]] = []
    for i, ln in enumerate(lines, 1):
        m = local_object_decl_re.match(ln)
        if not m:
            continue
        obj_type, name = m.group(1), m.group(2)
        if name in persistent:
            ptype, pline = persistent[name]
            shadow_hits.append((i, obj_type, name, pline))

    if shadow_hits:
        details = "; ".join([f"line {i}: {obj_type} {name} shadows persistent {name} declared at line {pline}" for i, obj_type, name, pline in shadow_hits[:10]])
        fail(
            "Forbidden shadowing of persistent drawing object vars (box/line/label). "
            "Rename local variables to avoid lifetime/handle confusion. "
            + details
        )

def main() -> int:
    if not PINE_FILE.exists():
        fail(f"Missing file: {PINE_FILE}")

    parser = argparse.ArgumentParser(description="Pine lint guard")
    parser.add_argument("--dev", action="store_true", help="Enable DEV-only warnings")
    args = parser.parse_args()

    lines = PINE_FILE.read_text(encoding="utf-8").splitlines()

    # 1) na comparisons
    na_hits = [(i, ln.strip()) for i, ln in enumerate(lines, 1) if NA_COMPARE_RE.search(ln)]
    if na_hits:
        details = "; ".join([f"line {i}: {txt}" for i, txt in na_hits[:10]])
        fail(f"Forbidden comparison with na detected by regex {NA_COMPARE_RE.pattern}: {details}")

    # 1b) tuple destructuring must use '=' in Pine (':=' is invalid syntax)
    tuple_colon_hits = [(i, ln.strip()) for i, ln in enumerate(lines, 1) if FORBIDDEN_TUPLE_COLON_ASSIGN_RE.search(ln)]
    if tuple_colon_hits:
        details = "; ".join([f"line {i}: {txt}" for i, txt in tuple_colon_hits[:10]])
        fail(
            "Forbidden tuple destructuring with ':='. Use '=' for tuple unpacking, then assign to persistent vars with ':=' if needed. "
            + details
        )

    # 1c) Pine does not support enum namespaces as type annotations (label.style/line.style/size)
    bad_enum_type_hits = [(i, ln.strip()) for i, ln in enumerate(lines, 1) if FORBIDDEN_ENUM_TYPE_RE.search(ln)]
    if bad_enum_type_hits:
        details = "; ".join([f"line {i}: {txt}" for i, txt in bad_enum_type_hits[:10]])
        fail("Forbidden enum type annotation. Use int or inferred type with *_style/size constants. " + details)

    # 1d) forbid string-typed style/size helper params used for drawing enums
    bad_style_sig_hits = [(i, ln.strip()) for i, ln in enumerate(lines, 1) if FORBIDDEN_STYLE_STRING_SIG_RE.search(ln)]
    if bad_style_sig_hits:
        details = "; ".join([f"line {i}: {txt}" for i, txt in bad_style_sig_hits[:10]])
        fail("Forbidden string style/size parameter name (_style/_st/_sz). Use int for drawing enums. " + details)

    helper_style_string_hits = [(i, ln.strip()) for i, ln in enumerate(lines, 1) if HELPER_STYLE_STRING_SIG_RE.search(ln)]
    if helper_style_string_hits:
        details = "; ".join([f"line {i}: {txt}" for i, txt in helper_style_string_hits[:10]])
        fail("Drawing helpers f_line_styled/f_label must not declare style or size params as string. " + details)

    draw_style_string_hits = [(i, ln.strip()) for i, ln in enumerate(lines, 1) if FORBIDDEN_DRAW_STYLE_STRING_RE.search(ln)]
    if draw_style_string_hits:
        details = "; ".join([f"line {i}: {txt}" for i, txt in draw_style_string_hits[:10]])
        fail("Forbidden string-typed draw style/size variable. Use int enums for draw styles/sizes. " + details)

    # 1e) label.new(style=_style) must not be paired with string _style helper signature
    label_new_style_idx = _line_index(lines, re.compile(r"label\.new\([^)]*style\s*=\s*_style"))
    if label_new_style_idx is not None:
        label_sig_idx = _line_index(lines, re.compile(r"^\s*f_label\([^)]*\bstring\s+_style\b"))
        if label_sig_idx is not None:
            fail("label.new(style=_style) detected with string _style parameter in f_label signature; use int.")

    # 1f) named-argument style assignment ':=' inside function calls is invalid in Pine
    named_assign_hits = [(i, ln.strip()) for i, ln in enumerate(lines, 1) if NAMED_ASSIGN_IN_CALL_RE.search(ln)]
    if named_assign_hits:
        details = "; ".join([f"line {i}: {txt}" for i, txt in named_assign_hits[:10]])
        fail(
            "Forbidden ':=' assignment-like token inside function call arguments; "
            "use '=' for named args or perform assignment before call. "
            + details
        )

    # 1g) cap declarations must appear before first use in helpers
    poc_bins_decl = _line_index(lines, re.compile(r"^\s*int\s+poc_bins_cap\s*=\s*"))
    poc_bins_use = _line_index(lines, re.compile(r"\bpoc_bins_cap\b"))
    if poc_bins_decl is None:
        fail("Missing declaration: int poc_bins_cap = ...")
    if poc_bins_use is not None and poc_bins_use < poc_bins_decl:
        fail("poc_bins_cap used before declaration. Move declarations above calculatePOC/f_bin_size.")

    poc_window_decl = _line_index(lines, re.compile(r"^\s*int\s+poc_window_cap\s*=\s*"))
    poc_window_use = _line_index(lines, re.compile(r"\bpoc_window_cap\b"))
    if poc_window_decl is None:
        fail("Missing declaration: int poc_window_cap = ...")
    if poc_window_use is not None and poc_window_use < poc_window_decl:
        fail("poc_window_cap used before declaration. Move declarations above calculatePOC/f_bin_size.")

    # 2) var self assignment
    var_hits = [(i, ln.strip()) for i, ln in enumerate(lines, 1) if VAR_SELF_ASSIGN_RE.search(ln)]
    if var_hits:
        details = "; ".join([f"line {i}: {txt}" for i, txt in var_hits[:10]])
        fail(f"Forbidden var self-assignment detected by regex {VAR_SELF_ASSIGN_RE.pattern}: {details}")

    # 2b) prevent local shadowing of persistent box/line/label handles
    _check_persistent_object_shadowing(lines)

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

    # 3b) constructors/deletes must stay in helpers only
    helper_boundaries = {
        "f_box": "box.new",
        "f_line": "line.new",
        "f_line_styled": "line.new",
        "f_label": "label.new",
        "f_del_box": "box.delete",
        "f_del_line": "line.delete",
        "f_del_label": "label.delete",
    }
    for fn_name, token in helper_boundaries.items():
        fn_idx = next((i for i, ln in enumerate(lines, 1) if ln.strip().startswith(f"{fn_name}(")), None)
        tok_idx = [i for i, ln in enumerate(lines, 1) if token in ln]
        if fn_idx is None or not tok_idx:
            fail(f"Could not locate helper '{fn_name}' or token '{token}' for helper-scope check")
        for i in tok_idx:
            if abs(i - fn_idx) > 25:
                fail(f"Token '{token}' at line {i} appears outside expected helper scope near '{fn_name}'")

    # 4) request.security lookahead guard
    security_lines = [(i, ln) for i, ln in enumerate(lines, 1) if "request.security" in ln]
    if security_lines:
        bad = [
            (i, ln.strip())
            for i, ln in security_lines
            if "lookahead=barmerge.lookahead_off" not in ln.replace(" ", "")
            or "gaps=barmerge.gaps_off" not in ln.replace(" ", "")
        ]
        if bad:
            details = "; ".join([f"line {i}: {txt}" for i, txt in bad[:10]])
            fail("request.security must include lookahead=barmerge.lookahead_off and gaps=barmerge.gaps_off. " + details)

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

    if args.dev:
        _dev_object_budget_report(lines)

    print("Lint guard OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

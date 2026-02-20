# STATUS CHECKPOINT (append-only)

## 2026-02-20T22:21:38Z — Baseline before Pine edits
- Target file audited: `prizrak_trade_setup_detector_v12_0_0.pine` (indicator title shows v12.2.0).
- Baseline checks:
  - `python tools/contract_guard.py --mode release --check` → PASS.
  - `python tools/lint_guard.py` → PASS.
  - `make check-release` → PASS.
  - `make tv-export` → PASS.
- Current counts/limits:
  - Pine lines: `825`.
  - `request.security` occurrences: `4` (within lint budget <= 6).
  - Indicator object caps: `max_boxes_count=300`, `max_labels_count=300`.
- Known problems/hypotheses to address next:
  1. Stable-cross gap: `buy_level_changed/sell_level_changed` are computed but not used in `entry_trigger_ok_*`, so ENTRY may trigger on level jump.
  2. Trap volume gate is currently `HTF1 OR HTF2`, not tied to active zone TF (`z_tf[buy_idx]/z_tf[sell_idx]`).
  3. RR TP selection currently overwrites with the last matching opposite POC on same TF, not nearest valid TP.
  4. Docs drift expected: `docs/INDICATOR_SPEC.md` and root `AGENTS.md` likely inconsistent with factual v12 canonical and touch/close behavior.
- Deep-research source note:
  - Expected `deep-research-report` markdown file was not found by `rg --files | rg -i "deep|research|report"`; use this checkpoint as baseline anchor until file path is provided/found.

## 2026-02-20T22:30:00Z — Post P0/P1 pass
- Updated file: `prizrak_trade_setup_detector_v12_0_0.pine`.
- New counts:
  - Pine lines: `852`.
  - `request.security`: `4` (still <= 6 limit).
  - Object caps unchanged: `max_boxes_count=300`, `max_labels_count=300`.
- Implemented fixes:
  1. Stable-cross guard now blocks ENTRY on trigger-level jump (`*_level_changed` integrated into entry trigger).
  2. Trap volume gate now reads volume/MA strictly from active zone TF.
  3. RR TP selection now picks nearest valid opposite POC on same TF (fallback ATR kept).
  4. STOPVOL origin tagging added with explicit visual distinction.
  5. Docs/canonical alignment updated (`docs/INDICATOR_SPEC.md`, root `AGENTS.md`, `docs/CHANGELOG_DEV.md`).
- Validation snapshot:
  - `python tools/contract_guard.py --init` executed intentionally due to interface change (new Stop Volume inputs).
  - Release contract/lint/check-release pass after lock refresh.

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

## 2026-02-20T22:57:19Z — Baseline audit refresh (no Pine edits)
- Audited canonical file: `prizrak_trade_setup_detector_v12_0_0.pine` (header version: `v12.2.0`).
- Baseline command results:
  - `python tools/contract_guard.py --mode release --check` → **FAIL** (`inputs` mismatch: lock expects 54, actual 56).
  - `python tools/lint_guard.py` → PASS.
  - `make check-release` → **FAIL** (fails on same contract mismatch).
  - `make tv-export` → PASS.
  - `wc -l prizrak_trade_setup_detector_v12_0_0.pine` → `938` lines.
  - `rg -c "request.security" prizrak_trade_setup_detector_v12_0_0.pine` → `4` (within limit <= 6).
- Current technical limits (from indicator declaration):
  - `max_boxes_count=300`, `max_labels_count=300`.
- Known open issues to prioritize in next iteration (from provided deep-research summary):
  1. `buy_level_changed/sell_level_changed` are computed but not applied in `entry_trigger_ok_*` protection logic.
  2. Trap volume gate uses OR across HTF1/HTF2 instead of evaluating volume on active zone TF.
  3. RR TP selection should use nearest valid opposite POC (correct direction), not last matching one.
  4. Docs drift: `docs/INDICATOR_SPEC.md` touch semantics vs code behavior (wick overlap), plus canonical-file confusion risk in agent docs.
  5. Methodology gap: stop-volume origin handling needs parity with v11 module.
- Deep research report reference note:
  - No in-repo file matched `deep-research-report` by filename (`rg --files | rg -i "deep|research|report"` returned no matches); using user-provided summary as checkpoint source for now.

## 2026-02-21T00:47:12Z — Phase 0 baseline before P0 fixes
- Audited canonical file: `prizrak_trade_setup_detector_v12_0_0.pine` (indicator title: `v12.2.0`).
- Baseline command results:
  - `python tools/contract_guard.py --mode release --check` → PASS.
  - `python tools/lint_guard.py` → PASS.
  - `make check-release` → PASS.
  - `make tv-export` → PASS.
- Metrics snapshot:
  - `wc -l prizrak_trade_setup_detector_v12_0_0.pine` → `962` lines.
  - `rg -c "request.security" prizrak_trade_setup_detector_v12_0_0.pine` → `4` (within limit <= 6).
  - Indicator caps unchanged: `max_boxes_count=300`, `max_labels_count=300`.
- Open P0 issues queued:
  1. IN_ZONE semantics rely on wick overlap; stages/blocked/wait/alerts should use close-in-zone semantics.
  2. RR gate uses `abs(...)`, hiding invalid directional risk/reward geometry.
  3. STOPVOL origin currently tagged by heuristic, while zones are created from base edges instead of stop edges.
  4. Zone age/flip windows are based on time-delta (`tf_ms`) and can drift across session/weekend gaps.
  5. Trap type2 mixes chart-TF range with LTF ATR while input text says zone-TF behavior.

## 2026-02-21T01:48:13Z — Phase 0 quick confirmation before P1
- Audited canonical file: `prizrak_trade_setup_detector_v12_0_0.pine` (indicator title: `v12.2.0`).
- Baseline command results:
  - `python tools/contract_guard.py --mode release --check` → PASS.
  - `python tools/lint_guard.py` → PASS.
  - `make check-release` → PASS.
  - `make tv-export` → PASS.
- Quick grep confirmations (P0 invariants):
  - `wick_touch` and close-in-zone predicates are present (`close >= ... <= ...`).
  - RR line uses directional ratio `buy_reward / buy_risk` (without `abs` in RR computation).
  - STOPVOL edges/fields (`htf1_stop_up`, STOPVOL-origin zones) are present.
  - TF counters (`z_tf_seq`, `z_break_seq`) are present.
  - Trap range uses zone-TF values (`htf1_trap_range`/`htf2_trap_range`).
- Metrics snapshot:
  - `wc -l prizrak_trade_setup_detector_v12_0_0.pine` → `962` lines.
  - `rg -c "request.security" prizrak_trade_setup_detector_v12_0_0.pine` → `4` (within limit <= 6).
  - Indicator caps currently `max_boxes_count=300`, `max_labels_count=300`.
- Planned P1 implementation scope:
  1. P1.1 strict trigger decoupling (`trigger_mode`) + explicit HUD TRIG status.
  2. P1.2 label budget safety for event icons (`icon_keep_eff`, HUD eff/req).
  3. P1.3 render mode (`HISTORY`/`LAST_BAR_ONLY`) and remove duplicate `label.set_text` writes.
  4. P1.4 audit trail events table (bounded recent events).
  5. P1.5 `ui_mode` mapping (CLEAN/STANDARD/FULL/DEBUG) without touching lifecycle logic.

## 2026-02-21T01:51:09Z — Post P1.1–P1.5 implementation
- Updated canonical file: `prizrak_trade_setup_detector_v12_0_0.pine`.
- Final metrics:
  - `wc -l prizrak_trade_setup_detector_v12_0_0.pine` → `1068` lines.
  - `rg -c "request.security" prizrak_trade_setup_detector_v12_0_0.pine` → `4` (within limit <= 6).
  - Indicator object caps unchanged: `max_boxes_count=300`, `max_labels_count=300`.
- Implemented in this pass:
  1. STRICT trigger mode (separated trigger-level semantics from entry plan).
  2. Label budget safety (`icon_keep_eff`) + HUD icons budget visibility.
  3. Render mode for last-bar-only visual refresh + duplicate label text update removed.
  4. Audit trail table (bounded recent events) for explainability.
  5. UI mode profiles (CLEAN/STANDARD/FULL/DEBUG) as top-level visual presets.
- Contract/status:
  - RELEASE contract intentionally updated (`trigger_mode`, `ui_mode`, `render_mode`) and lock refreshed via `python tools/contract_guard.py --init`.
- Validation snapshot:
  - `python tools/contract_guard.py --mode release --check` → PASS.
  - `python tools/lint_guard.py` → PASS.
  - `make check-release` → PASS.
  - `make tv-export` → PASS.

## 2026-02-21T07:07:15Z — Phase 0 baseline before P1.6/P1.7 cycle
- Baseline commands (no edits):
  - `python tools/contract_guard.py --mode release --check` → PASS.
  - `python tools/lint_guard.py` → PASS.
  - `make check-release` → PASS.
  - `make tv-export` → PASS.
- Snapshot before edits:
  - commit: `2887900`
  - `wc -l prizrak_trade_setup_detector_v12_0_0.pine` → `1088`
  - counts: `inputs=61`, `alerts=18`, `request.security=4`
- Scope for this PR:
  - fix TRAP return-volume gate semantics to match return event intent;
  - add STRICT_SWING trigger-level stability guard and explicit HUD “TRIG SHIFT” state;
  - harden icon budget enforcement and CLEAN-mode icon cleanup;
  - make `render_mode=LAST_BAR_ONLY` affect only visual updates (`box.set_right`) without touching lifecycle.

## 2026-02-21T07:07:15Z — Post P1.6/P1.7 implementation checkpoint
- Validation commands:
  - `python tools/lint_guard.py` → PASS.
  - `make check-release` → PASS.
  - `make tv-export` → PASS.
- Contract status:
  - RELEASE contract intentionally updated (Trap input captions clarified);
  - lock refreshed via `python tools/contract_guard.py --init`.
- Snapshot after edits:
  - `wc -l prizrak_trade_setup_detector_v12_0_0.pine` → `1086`
  - counts: `inputs=61`, `alerts=18`, `request.security=4` (still <= 6).

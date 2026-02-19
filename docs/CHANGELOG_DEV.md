# DEV Changelog

## 2026-02-18 (docs follow-up)

- Reworked `docs/PRIZRAK_TRADE_SETUP_DETECTOR_V2_ARCHITECTURE.md` to match the requested Russian full-architecture format verbatim (design-only, no Pine code).

## 2026-02-18

- Added design-only architecture document `docs/PRIZRAK_TRADE_SETUP_DETECTOR_V2_ARCHITECTURE.md`:
  - Captures the full v2.0 module map (STF/MTF/Entry TF responsibilities, state containers, setup engine, RR overlay, alerts, debug flow).
  - Defines strict per-bar execution order and formula-level contracts without introducing Pine code changes.


## 2026-02-18

- Added STF+HTF trend separation for setup direction and trap context:
  - New `stf` timeframe input for higher-level direction alignment.
  - Setup gating now requires HTF+STF directional agreement unless counter-trend is explicitly allowed.
- Hardened PP TRUE confirmation in DEV mode:
  - Added configurable `PP confirm bars` and `PP volume >= MA *` checks before promoting pending PP to active TRUE.
- Improved trap detector quality in DEV mode:
  - Added optional `Trap: нужен TF mismatch` gate so trap events require trend mismatch context (HTF/STF vs local break).
- Adjusted RR/SL placement to be level-anchored and volatility-aware:
  - Entries now anchor to `working_level` when available (instead of raw close-only anchoring).
  - Added `Min SL ATR mult` floor so stop distance respects minimum ATR risk width.
- Added `docs/TV_FEEDBACK.md` as the single TradingView feedback artifact (compiler/runtime/screenshots/notes).
- Switched contract guard flow to DEV-by-default vs RELEASE opt-in:
  - `make check` now aliases `make check-dev`.
  - Added `make check-release` and `make contract-release` for strict lock enforcement.
  - Updated `tools/contract_guard.py` with `--mode {dev,release}` and `CONTRACT_MODE` defaulting to `dev`.
- Fixed Pine label-style typing in `prizrak_trade_setup_detector_v11_7_0.pine` by using Pine-valid style value typing in helper/usage paths.
- Updated lint guard to block `label.style` type annotations (compile-error class) while allowing `int`/inferred style vars.



- Fixed RR draw tuple updates in `prizrak_trade_setup_detector_v11_7_0.pine` to use `:=` reassignment for existing objects (`rr_open_*`, `sb/tb/t2/el/slb`) instead of declaration-style `=`.
- Removed Pine warnings about variable shadowing / duplicate definitions around RR open + RR history rendering blocks.
- Verification sweep for this fix: `make check-dev`, `make check`, `make contract-check`, `make lint`.

## 2026-02-17

- Guardrails split into DEV/RELEASE behavior:
  - `make check` remains strict contract lock validation.
  - `make check-dev` now runs contract drift report (`--dev-check`) + DEV lint warnings.
- Added `make tv-export` and `tools/tv_export.py` for TradingView copy/paste export (with optional comment stripping).
- Added DEV object-budget warning heuristic in `tools/lint_guard.py`.
- Updated PP/legacy-CHOCH UI naming in canonical Pine inputs/alerts and added alias layer (`pp_*` -> `choch_*`) for readability without runtime behavior redesign.
- Reduced debug series to compact compile-first markers (6 plots) while keeping `barstate.islast` table updates.

## 2026-02-18 (strict-compat stabilization pass)

- Synced `prizrak_trade_setup_detector_v11_7_0.pine` public interface back to `contract.lock.json` by removing DEV-only extra inputs and replacing them with internal constants (`TRAP_NEED_TF_MISMATCH`, `STF_TF`, `PP_CONFIRM_BARS`, `PP_CONFIRM_VOL_MULT`, `SL_MIN_ATR_MULT`).
- Fixed helper typing safety for TradingView enum styles/sizes:
  - `f_line_styled` and `f_label` no longer use string-typed style/size params.
- Updated working level selection to nearest active POC to current `close` (excluding dead POC by `poc_dead_tests`) instead of “last active POC”.
- Reworked trap break registration to use crossover/crossunder on working level + volume gate + HTF alignment (`up` only when `htf_trend_dir <= 0`, `down` only when `htf_trend_dir >= 0`).
- Aligned PP strict-compat behavior:
  - TRUE (kinds 2/4) requires retest when `choch_need_retest=true`.
  - EARLY (kinds 1/3) can proceed without retest.
  - Active/pending/confirm-alive PP now blocks both BUY and SELL setups.
- Hardened RR gate quality computation to be explicitly based on TP main/ext distances from entry (not TP1-only shortcut).
- Added mandatory level zone layer around working level as update-in-place single box (clean mode uses higher transparency).
- Kept mandatory visuals available in clean mode for baseline parity (working level, POC lines, RR history, level zone).

### Intentional deviations / notes
- STF branch remains runtime-enabled but uses fixed internal timeframe constant (`STF_TF = "D"`) to preserve strict public contract compatibility.

## 2026-02-18 (strict-compat verification pass)

- Re-ran strict gates against canonical Pine script without modifying public interface:
  - `make check-release`
  - `make contract-check`
  - `make lint`
  - `make check-dev`
- Confirmed `prizrak_trade_setup_detector_v11_7_0.pine` remains release-clean with contract lock parity for `indicator(...)`, all `input.*`, and all `alertcondition(...)` declarations.
- Confirmed `contract.lock.json` was not refreshed/edited during this pass (stable strict-compat preserved).

## 2026-02-18 (strict-compat release-ideal pass)

- Enforced strict-compat trap mismatch semantics to HTF-only (`tf_mismatch_*` no longer depends on STF trend direction).
- Applied RR gate to setup generation (BUY/SELL now require `rr_quality >= rr_min` when `rr_gate_enabled=true`, with zero-risk guard).
- Switched setup flow to base-setup + RR-gated final setup states to keep diagnostics explicit.
- Preserved release contract parity and lock stability (`contract.lock.json` untouched).
- Revalidated full required gate set: `make check-release`, `make contract-check`, `make lint`, `make check-dev`, `make tv-export`.

## 2026-02-19 — strict-compat hardening pass (stable interface preserved)

### Core logic hardening
- Break/trap logic anchored to `last_break_level`: break registration now snapshots the exact `working_level` that was broken and trap-return is evaluated against this frozen level, not the potentially shifted nearest-POC on later bars.
- Dynamic `working_level` cross hardening: replaced `ta.crossover/ta.crossunder` usage for working-level events with explicit close-to-level transition checks (`close > level and close[1] <= level`, mirrored for down).
- Break registration gates remain at the break moment (volume gate + HTF alignment):
  - up-break only when `htf_trend_dir <= 0`
  - down-break only when `htf_trend_dir >= 0`
- TF mismatch gate is applied at break registration only; no second mismatch gate at trap-return (intentional alignment with COURSE_LOGIC_SPEC strict-compat semantics).

### Safety / runtime robustness
- RR gate na/zero safety tightened: when computed risk is non-positive, `rr_quality_*` remains `na` and `rr_ok_*` is forced false; with `rr_gate_enabled=true`, such setups are blocked without division-by-zero risk.

### Visual/UI improvements (no signal-condition drift)
- Event icons switched from single mutable marker to bounded history arrays (`ICON_KEEP=20`) for trap-up/trap-down/PP labels with automatic pruning.
- `clean_mode` explicitly purges icon arrays to prevent object accumulation.
- Palette tweaks toward architecture visual hierarchy:
  - buy fill -> green-based
  - sell fill -> red-based
  - PP/CHOCH marker -> purple

## 2026-02-19 — v12.0.0 interface + product rewrite

- Added new canonical script `prizrak_trade_setup_detector_v12_0_0.pine` as a product-oriented rewrite (zones → prepare → entry flow).
- Introduced AUTO/Manual MTF hierarchy inputs, HTF zone engine, LTF entry-zone modes (POC/ACCUM), stage machine (FAR/NEAR/IN_ZONE/CONFIRM/ENTRY/BLOCKED), HUD, and new alert set.
- Updated toolchain to target v12 as canonical (`tools/contract_guard.py`, `tools/lint_guard.py`, `tools/tv_export.py`).
- Refreshed `contract.lock.json` to match v12 interface.

## 2026-02-19 — v12.0.0 stability & UX hardening pass

- ENTRY event icons are now emitted on every `stage_changed && stage == ENTRY` edge using `entry_buy_sig/entry_sell_sig`, without dependency on previous stage being `CONFIRM`.
- Zone lifecycle cleanup hardened:
  - INVALID and EXPIRED zones are now physically removed (`f_remove_zone`) in reverse-index batch pass.
  - Prevents stale object accumulation and mitigates `max_boxes_count` exhaustion.
- Touch counting converted to edge-trigger logic via `z_inside_prev`:
  - touch increments only on first bar entering zone (`inside_now && !was_inside`).
  - TOUCHED state is set only on first entry.
- Zone age semantics switched from chart `bar_index` age to zone-timeframe age:
  - `age_bars_zone = floor((time - z_pivot_time) / dt_ms(tf))`.
  - expiration now uses zone-relative age (`age_bars_zone > max_age_bars`).
- Live zones now extend right edge continuously while ACTIVE/TOUCHED:
  - per-bar `right = time + dt_ms(tf) * zone_extend_bars` update applied.
- LTF entry-zone computation moved to true LTF context with one `request.security` call on `ltf`:
  - returns `atr_ltf`, `poc_candidate` (max-volume bar proxy), `accum_hi`, `accum_lo`.
  - POC/ACCUM construction now uses these LTF-derived series with `lookahead_off` + `gaps_off`.
- Added moving active-zone UX label (`active_label`) anchored near current bar/time:
  - text format: `ACTIVE DEMAND/SUPPLY <TF> | stage=<...> | next=<...>`.
- Confirm-stage reason semantics split:
  - introduced `ready_reason_*` for `CONFIRM` waiting state.
  - `block_reason_*` kept for `BLOCKED` stage; HUD shows block reasons only when stage is BLOCKED.
- Added optional lifecycle alerts:
  - `zone_created_demand/supply`
  - `zone_invalidated_demand/supply`
- Refreshed `contract.lock.json` to capture intentional alert/interface updates.

## 2026-02-19 (v12 migration: v11 core ports)

- v12 promoted as canonical runtime path; v11 kept as legacy/reference only (no deletion).
- Ported v11 core modules into `prizrak_trade_setup_detector_v12_0_0.pine` while keeping v12 UX flow (zones → stages → entry, HUD/icons/lifecycle alerts):
  - Real LTF POC profile (`binning + volume aggregation`) with `poc_bins`, `poc_price_mode`, and capped sampling step.
  - LTF FLAT mode with touch-based range validation and stable flat zone rendering.
  - Anchored trap state (`last_break_*`, window reset, optional volume gates) for sweep+return confirmation.
  - PP strict pending→confirm→active state machine on HTF1; PP can drive bias (`bias_mode=PP`).
  - RR model switched to zone-boundary stop with TP multipliers (`rr_main_mult`, `rr_ext_mult`) + bounded RR history overlay (`rr_hist_keep`).
- Public contract intentionally changed (new inputs/options), `contract.lock.json` refreshed via `python tools/contract_guard.py --init`.
- Performance/object-budget safeguards preserved: `lookahead_off` requests only, bounded RR history pruning, capped POC bins/sampling step.

## 2026-02-19 — v12.0.0 stage/zone consistency + near/in-zone edge reliability

- Zone ATR is now persisted per-zone (`z_atr`) and consumed consistently for:
  - invalidation padding during zone lifecycle checks,
  - active-zone NEAR threshold (`near_thr`),
  - RR stop padding (`buy_stop`/`sell_stop`).
- NEAR and IN_ZONE edge events were decoupled from stage-transition-only logic:
  - added geometric edge memory (`prev_near_now`, `prev_inside_now`) with reset on active-zone switch,
  - `near_edge` now triggers on first geometric NEAR approach,
  - `in_zone_edge` now triggers on first geometric zone entry even if stage escalates to CONFIRM/ENTRY on the same bar.
- Event icons aligned with geometric edges:
  - `⏳` emitted on `near_edge`,
  - `⚡` emitted on `in_zone_edge`.
- Updated near/in-zone alert descriptions to reflect geometric semantics while preserving existing alert IDs.
- PP bias hardening:
  - `bias_mode="PP"` now uses `pp_trend_dir` only when `pp_state >= 3`; otherwise bias is neutral (`0`).
- POC profile allocation optimization in `f_poc_profile_last_n`:
  - replaced per-call array allocation with reusable `var float[]` buffer,
  - dynamic resize only on bin-count changes,
  - explicit zeroing loop for reuse (`bins<=120`).
- FLAT LTF detection upgraded to a minimal state machine via new `f_flat_state_ltf_stateful`:
  - persistent `in_flat`, `flat_hi/flat_lo`, and `exit_cnt`,
  - candidate-entry capture on valid/touches condition,
  - confirmed exit requires `_exit_confirm` consecutive closes outside the flat range.
- Contract lock refreshed (`python tools/contract_guard.py --init`) to record intentional alert text updates.

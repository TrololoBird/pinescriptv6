# DEV Changelog

## 2026-02-19 — v12 active-zone hysteresis + HUD bias source polish

- Added active-zone anti-flicker hysteresis in `prizrak_trade_setup_detector_v12_0_0.pine`:
  - New stage inputs: `active_hold_bars` and `active_switch_margin`.
  - Active zone now remains sticky for a minimum hold window and switches only when a challenger is materially closer by margin.
- Improved zone visual hierarchy:
  - HTF1 zones use a thicker base border than HTF2.
  - ACTIVE zone border width increased for clearer focus.
- HUD bias line now shows source annotation (`BUY/SELL/NEUTRAL (PP|EMA)`) for UX clarity.
- Refreshed `contract.lock.json` to capture intentional v12 input interface expansion.

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

## 2026-02-19 — v12 top-down workflow hardening (AUTO LTF + LTF gate)

- Added `auto_ltf_mode` in TF Hierarchy with three modes:
  - `AUTO_BY_CHART` (chart-relative lower TF mapping),
  - `AUTO_BY_HTF2` (LTF equals resolved HTF2),
  - `CHART` (LTF equals chart TF).
- Integrated LTF entry-zone gating into stage/entry logic:
  - new stage inputs `use_ltf_entry_gate`, `ltf_gate_mode`, `ltf_near_atr`;
  - `CONFIRM` now reports `WAIT_LTF` when all filters pass but LTF gate is not satisfied;
  - `ENTRY` transition is now allowed only when LTF gate passes.
- Added LTF entry edge event and alerts:
  - icon/event: `🎯 LTF ZONE` on first entry into LTF zone;
  - alerts: `price_in_ltf_buy_zone`, `price_in_ltf_sell_zone`.
- HUD and active label now expose resolved TF stack (`HTF1/HTF2/LTF`) to make top-down context explicit on any chart TF.
- HTF rendering rank tuned to 3 levels:
  - HTF1 strongest, HTF2 medium, others weakest (`fill_alpha`/width differentiation).
- Refreshed `contract.lock.json` for intentional interface/alert additions.

## 2026-02-19 — v12.1.0 baseline audit + full MTF pipeline rewrite

### Baseline audit (before edits)
- Canonical file at start: `prizrak_trade_setup_detector_v12_0_0.pine`.
- Baseline size: `wc -l` = **821** lines.
- Baseline public contract: **49** `input.*` declarations and **15** `alertcondition(...)` declarations.
- Baseline TF controls: `manual_htf1=240`, `manual_htf2=60`, `manual_ltf(blank=chart)`, `auto_ltf_mode` with `AUTO_BY_CHART/AUTO_BY_HTF2/CHART`.
- Baseline checks before rewrite:
  - `make check-release` ✅
  - `make lint` ✅
  - `make check-dev` ✅
  - `make tv-export` ✅

### Rewrite summary (methodology sync)
- Reworked HTF engine from pivot-centric behavior to **base/flat → breakout edge → POC zone** flow for HTF1/HTF2.
- Added stateful HTF base pack (inside `request.security`, `lookahead_off`, `gaps_off`) with required controls:
  - `base_len`, `touch_tolerance`, `min_touches`, `max_range_atr`, `exit_confirm_bars`.
- Zone creation now occurs once per breakout edge and is centered around base POC with ATR pad (`htf_poc_pad_mult`).
- Added explicit zone lifecycle statuses and transitions: `ACTIVE`, `TOUCHED`, `CONSUMED`, `INVALID`, `EXPIRED`.
  - Touches increment only on first-entry edge.
  - `CONSUMED` after first touch + reaction threshold (`consume_reaction_atr_mult`).
  - `INVALID` confirmation with `invalidate_confirm_bars` + optional `body_confirm`.
  - Optional role reversal via `flip_on_break`.
- Enforced two active contexts for UX readability:
  - nearest BUY zone and nearest SELL zone are tracked independently and shown simultaneously in HUD.
- Made LTF stage mandatory-capable:
  - Added `use_ltf_entry_gate`, `ltf_gate_mode(NEAR/IN_ZONE)`, `ltf_near_atr`.
  - LTF bundle is computed in one `request.security(ltf, ...)` pack and used in stage pipeline.
- Reworked confirm module to modular mode:
  - Added `confirm_mode (ALL/ANY/SCORE)` + `confirm_min_passed`.
  - Trap moved to event-style signal + optional confirm member (`use_trap_confirm` default false).
  - RR gate hardened with safe risk guard (`risk > mintick` + `not na`).
- UX refresh:
  - stage icons (`⏳`, `⚡`, `✅`, `▲/▼`, `⛔`) and dual BUY/SELL HUD rows with module status flags.
  - zone labels include side + POC + TF text (`BUY POC (4H)`, etc).
- Contract intentionally changed (inputs/alerts renamed/expanded for the new pipeline); lock file refreshed via repo tool.

## 2026-02-19 — v12.1.0 core alignment to PDF base/POC methodology

- Fixed HTF base breakout confirmation by replacing `prev_in_base` single-edge logic with explicit state machine in `f_htf_pack`: `BASE_OFF -> BASE_ON -> POST_BASE`, with one-shot edge only after confirmed exit bars and rollback from `POST_BASE` to `BASE_ON` when price returns inside base.
- Replaced HTF `ta.vwap` pseudo-POC with per-base volume bins (`htf_poc_bins`) and base price mode (`htf_poc_price_mode`), with base window cap (`base_max_bars`) and breakout-time POC extraction from max-volume bin.
- Reworked invalidation confirmation to HTF-discrete counting (`z_inv_cnt`, `z_last_tf_time`) so `invalidate_confirm_bars` is counted per new HTF candle, not LTF bar accumulation.
- Fixed dual-side stage/edge pipeline:
  - separate BUY and SELL near/in-zone edges,
  - separate `stage_buy`/`stage_sell` transitions,
  - side-bound alerts (`near_buy`, `near_sell`, `in_zone_buy`, `in_zone_sell`, etc.) now use side-specific edges.
- PP naming cleanup: module renamed to `EMA_BIAS` (`use_ema_bias_confirm`) across inputs/HUD logic to avoid claiming PDF-PP implementation.
- LTF POC entry zone changed from VWAP to bounded volume-profile bins (`ltf_poc_len`, `ltf_poc_bins`, `ltf_poc_pad_mult`) and gate now reflects that computed zone.
- RR logic aligned to base structure:
  - per-zone base extremes persisted (`z_base_hi`, `z_base_lo`),
  - default stop uses base boundary ± ATR pad,
  - reward targets nearest opposite active zone on same TF, fallback to ATR-based target.
- Added bounded icon history with `icon_keep` and label pruning to avoid object-limit pressure.
- Contract intentionally updated for new/renamed inputs; lock refreshed.

## 2026-02-20 — v12.2.0 product hardening (PDF flow, no strict-compat)

- BUY/SELL execution path fully split end-to-end:
  - independent side contexts (`buy_inside/buy_near` vs `sell_inside/sell_near`),
  - independent stage machines (`stage_buy`, `stage_sell`),
  - side-specific edge resets on zone switch (`prev_buy_zone_id`, `prev_sell_zone_id`),
  - side-specific module gates in HUD/alerts (`ltf_gate_ok_buy/sell`, `entry_trigger_ok_buy/sell`, etc).
- HTF engine rewritten as state machine with persistent counters:
  - states `BASE_OFF/BASE_ON/POST_BASE`,
  - persistent `out_cnt_up/out_cnt_dn` confirmation counters,
  - breakout edge emission only after `_exit_confirm` bars outside base,
  - rollback to `BASE_ON` when price returns into base.
- HTF POC upgraded to true volume-profile binning on breakout edge only:
  - `array.new_float(_bins)` accumulation over capped base history,
  - bin max selection (`max_idx`) for POC extraction,
  - added `htf_poc_price_mode` = `HLC3|VWAP|CLOSE` and `base_max_bars` cap.
- LTF POC upgraded to volume-profile bins (removed pseudo-VWAP fallback):
  - `ltf_poc_bins` histogram, max-volume bin selection, and POC±ATR pad entry zone.
- Invalidation confirmation pinned to zone timeframe bars:
  - `z_inv_cnt` increments only on new zone-TF candle (`z_last_tf_time` delta),
  - confirmation checks use zone bounds plus `invalidate_pad_atr`.
- Trap logic reworked to anchored model:
  - break level/time/zone state captured at confirmed invalidation,
  - trap-return requires crossing back over anchored level within `trap_max_bars` (zone TF bars),
  - optional volume gate on return (`trap_use_volume_gate`, `trap_return_volume_mult`).
- RR model aligned to base structure:
  - `buy_stop = base_lo - pad`, `sell_stop = base_hi + pad` (ATR/% pad),
  - reward target = nearest opposite active zone on same TF, fallback ATR*2,
  - RR valid only for positive/non-NA risk & reward.
- Visual/runtime:
  - zone extension made configurable via `zone_extend_bars` (replacing fixed 400),
  - stage icons preserved with `icon_keep` pruning budget.

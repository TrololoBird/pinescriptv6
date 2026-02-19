# Course Logic Spec (formal, implementation-facing)

## Purpose
This specification formalizes the course terminology into deterministic Pine v6 rules for the repository indicator. The document is technical and validation-oriented: it defines states, boolean conditions, object lifecycle, and edge handling. It does not provide usage recommendations.

## Source basis
- `Курс по трейдингу от PrizrakTrade.pdf` terminology sections (glossary and module chapters: accumulation, POC, stop-volume, traps, PP/structure change, RR terms).
- Pine v6 docs in this repo for execution model, request/security behavior, visuals/objects, and limitations.

## 1) Definitions (canonical terms)

### 1.1 Flat (Accumulation)
A Flat is a bounded range state with:
- upper boundary `flat_high`
- lower boundary `flat_low`
- touch counts (`touches_top`, `touches_bottom`)
- validity status based on touch and range constraints

Flat candidate constraints:
- `cand_rng_pct <= flat_max_range_pct`
- combined touches `cand_touch_top + cand_touch_bot >= max(min_touches, 4)`
- side-specific minimums `cand_touch_top >= min_touches_side` and `cand_touch_bot >= min_touches_side`

Flat termination (`finalize`) occurs when at least one of:
- early boundary violation,
- true boundary violation,
- close-based exit confirmation counter reached,
- max flat duration exceeded.

Flat validity at termination:
- `flat_valid = (touches_top + touches_bottom) >= min_touch_req and touches_top >= min_touches_side and touches_bottom >= min_touches_side`.

### 1.2 POC level
POC (Point of Control) is the price bin with maximum aggregated volume computed from finalized valid Flat window.
- Computed only when POC module is enabled and flat is valid.
- Stored in arrays with metadata:
  - `poc_prices[i]`
  - `poc_bars[i]`
  - `poc_tests[i]`
- Retained with hard cap `max_poc_keep` and dead-level pruning via `poc_dead_tests`.

### 1.3 Stop-Volume event
Stop-volume state (`in_stop`) is a low-range + elevated-volume consolidation event. Technical criteria include:
- bounded range (`stop_max_range_pct` and ATR-normalized bound `stop_range_atr_mult`),
- range density bound (`stop_density_mult`) to avoid wide/noisy windows,
- volume condition relative to moving average (`stop_vol_mult`),
- controlled exit logic with confirmation bars (`stop_exit_confirm`),
- explicit policy for flat overlap: allowed only when `stop_detect_inside=true`.

The event transitions through:
1. detection/start,
2. in-window tracking,
3. finalize/reset.

### 1.4 Trap event
Trap event is a failed continuation after a recent working-level break.
- Break is tracked by direction (`last_break_dir`) and bar index (`last_break_bar`).
- Trap window: `(bar_index - last_break_bar) <= trap_max_bars`.
- Directional trap booleans:
  - `trap_up`: prior up-break, then close back below level in window,
  - `trap_down`: prior down-break, then close back above level in window.
- Optional volume filter: `volume < vol_ma * trap_vol_drop` when enabled.
- Structural mismatch filter: trap break registration requires mismatch against current HTF priority
  (`htf_trend_dir<=0` for up-break registration, `htf_trend_dir>=0` for down-break registration).

### 1.5 PP state (early/true)
PP (trend-priority/state-shift logic; runtime currently uses legacy `choch_*` variable names with `pp_*` aliases for readability) has 4 state codes:
- `1` = early down,
- `2` = true down,
- `3` = early up,
- `4` = true up.

True break:
- down: close crosses below latest HTF low with `choch_break_true` margin,
- up: close crosses above latest HTF high with `choch_break_true` margin.

Early break:
- evaluated against early reference levels (`pp_early_*`) with `choch_break_early` margin,
- guarded by reference constraints (`early_*_guard`).

Optional retest mode (`choch_need_retest`) introduces pending state (`choch_pending_*`) with validity window `choch_retest_bars`.

After break or retest resolution, PP activation requires a fixed 2-bar close confirmation beyond the break threshold (`pp_confirm_bars = 2`, internal constant in DEV, no public input change).

### 1.6 RR overlay terms
RR terms are presentation and accounting values for risk/reward visualization:
- entry (`open_entry`), stop (`open_stopOrig`), main target (`open_takeMain`), extension target (`open_takeExt`)
- multipliers: `rr_main_mult`, `rr_ext_mult`
- gate pass/fail (`rr_gate_enabled`, `rr_min`, risk>0 checks). DEV default baseline: `rr_min=3.0`.
- rendered objects: stop/take boxes, entry line, optional status labels, historical logs.

## 2) MTF rules

### 2.1 HTF source
HTF pivots are requested via:
`request.security(syminfo.tickerid, htf, [...], gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off, calc_bars_count=...)`

Contract requirements:
- `lookahead_off` is mandatory to avoid future leak.
- Gaps are disabled for stable series behavior.

### 2.2 Trend priority computation
Trend priority uses latest two HTF highs and lows:
- `htf_trend_up := htf_last_ll > htf_prev_ll`
- `htf_trend_down := htf_last_hh < htf_prev_hh`

This is equivalent to structure progression checks for higher lows / lower highs and remains deterministic under `lookahead_off`.

`htf_ready` requires at least two highs and two lows in arrays.
If not ready, both priorities are false.

## 3) Formal module conditions

### 3.1 Flat candidate boolean
`cand_ok = enable_accum and not in_flat and bar_index >= max_flat_bars and cand_rng_pct <= flat_max_range_pct and cand_touch_top + cand_touch_bot >= min_touch_req and cand_touch_top >= min_touches_side and cand_touch_bot >= min_touches_side`

### 3.2 Flat finalize boolean
`finalize = outside_early or outside_true or exit_confirm_cnt >= exit_confirm_bars or (bar_index - flat_start) > max_flat_bars`

Boundary exit confirmation is close-based (`outside_any` via close beyond boundary), while hard invalidations use high/low against early/true margins.

### 3.3 Working level selection
`working_level` is nearest active POC by absolute distance to `close`, excluding dead levels.

### 3.4 Break + trap detection
Break:
- up: `close > working_level and close[1] <= working_level and vol_break_ok and htf_align_up`
- down: `close < working_level and close[1] >= working_level and vol_break_ok and htf_align_dn`

Trap:
- `in_window = (bar_index - last_break_bar) <= trap_max_bars`
- `trap_up = last_break_dir == "up" and in_window and close < working_level and vol_trap_ok`
- `trap_down = last_break_dir == "down" and in_window and close > working_level and vol_trap_ok`

Where:
- `htf_align_up = htf_trend_dir <= 0`
- `htf_align_dn = htf_trend_dir >= 0`

### 3.5 PP state decision (legacy CHOCH runtime vars)
- Compute `true_dir_now` from true break booleans.
- Compute `early_evt` and `early_kind` from early break booleans and guards.
- If retest enabled:
  - set pending on true break,
  - while pending alive, confirm on directional retest; else allow early event.
- If retest disabled:
  - true event immediate;
  - early event as fallback.

### 3.6 RR quality gate (DEV)
When setup candidate exists, RR quality is evaluated with:
- strictly positive risk (`risk_buy > 0` or `risk_sell > 0`),
- multiplier policy `max(rr_main_mult, rr_ext_mult) >= rr_min`.

In current DEV mode this result is emitted as telemetry (`rr_quality`, `rr_ok_*`) and does **not** suppress setup/open creation.
Default DEV floor: `rr_min = 3.0`.

## 4) Edge cases and runtime safety

### 4.1 `na` handling
- All key price/level series guard against `na` before arithmetic or comparisons.
- Plot/debug outputs use ternaries with `na` fallback to avoid invalid object updates.

### 4.2 Insufficient history
- Flat candidate is disabled before `bar_index >= max_flat_bars`.
- HTF trend logic is disabled before `htf_ready`.
- POC arrays can be empty; working level remains `na` until available.

### 4.3 Realtime bar behavior
- Last-bar-only heavy table updates use `barstate.islast`.
- History object redraw for RR history is controlled by `barstate.islast` and cleanup branches to prevent runaway allocations.

## 5) Object model and lifecycle

### 5.1 Object types
- Boxes: accumulation zones, RR stop/take regions.
- Lines: working level, POC lines, RR entry, stop line.
- Labels: trap/PP markers, RR status labels.
- Table: debug state snapshot.

### 5.2 Lifecycle contract
- Update-in-place helpers (`f_box`, `f_line`, `f_label`) reuse handles when present.
- Explicit deletion helpers (`f_del_box`, `f_del_line`, `f_del_label`) are required for cleanup paths.
- RR history object arrays resize to log size and delete excess handles on shrink.

### 5.3 Caps and pruning strategy
- Pine indicator caps are declared in `indicator(...)` (`max_lines_count`, `max_labels_count`, `max_boxes_count`).
- POC arrays are bounded by `max_poc_keep`; dead POCs tracked via test counters.
- RR history is bounded by `rr_hist_keep`; old entries and corresponding visuals are pruned.

DEV hardening safety margin:
- runtime pruning uses internal 80% caps for long-history stability:
  - `internal_poc_keep = floor(max_poc_keep * 0.8)`
  - `internal_rr_keep = floor(rr_hist_keep * 0.8)`
- POC workload caps:
  - max bins per POC pass (`poc_bins_cap`)
  - max sampled bars per pass via adaptive stepping (`poc_window_cap`)

These caps are deterministic and only tighten runtime workload; they do not change interface semantics.

## 7) Ambiguities / assumptions (from PDF phrasing)
- PDF examples are partly discretionary and trading-oriented; this spec keeps only technical, reproducible conditions.
- For trap logic, “ложный пробой/возврат” is encoded as level break + return within fixed bar window (`trap_max_bars`) with optional volume filter.
- For PP, “подтверждение тестом” is implemented as retest-window + fixed 2-bar close confirmation to avoid realtime ambiguity.
- For stop-volume “плотность/сжатие” wording, an explicit ATR-density bound (`stop_density_mult`) is assumed for deterministic implementation.

## 6) Validation harness (debug-only)

### 6.1 Toggle policy
Debug harness is active only when `debug_mode=true`.
When `debug_mode=false`, no debug plots/table are rendered.

### 6.2 Debug outputs (module coverage)
- Flat:
  - `DBG Flat Mid`
  - `DBG Flat Valid` (0/1)
- PP:
  - `DBG PP State` (coded integer)
  - `DBG PP State` event/state marker
- POC:
  - `DBG POC Level`
  - `DBG Working Level`
- Trap:
  - `DBG Trap Flags` (`1` up, `-1` down, `0` none)
- RR:
  - `DBG RR Gate Passed`
  - `DBG RR Main Mult`
  - `DBG RR Ext Mult`

### 6.3 Debug table
Optional with `show_debug_table=true`:
- rows for latest scalar states (`flat_valid`, `pp_state`, `poc_level`, `trap_flags`, RR multipliers, etc.)
- updated only on `barstate.islast`.


## 8) DEV milestone behavior (logic-validation mode)

The current DEV implementation intentionally prioritizes signal observability/correctness validation over strict gating.

### 8.1 HTF influence mode (bias, not hard gate)
- HTF direction (`htf_trend_dir`) biases setup side preference.
- Neutral HTF (`htf_trend_dir=0`) does not hard-block setup detection.
- Flat lifecycle (candidate/finalize) does **not** require HTF readiness in DEV.

### 8.2 PP phase handling for setup blocking
- PP runtime phases are represented by `choch_kind` codes:
  - `1` early down, `2` true down, `3` early up, `4` true up.
- Active PP blocks only counter-direction setups:
  - block BUY when kind is down (`1/2`),
  - block SELL when kind is up (`3/4`).
- Pending/retest/confirm phases are diagnostic states and do not hard-block aligned entries in DEV.

### 8.3 Flat validation relaxation
- Flat candidate/final validity keeps range + touch constraints.
- Side-touch requirement is relaxed by a high-touch override:
  - pass if side minimums are met **or** total touches exceed elevated threshold (`min_touch_req + min_touches_side`).

### 8.4 Trap semantics in DEV
- Trap module produces `trap_flag` (`1` up-trap, `-1` down-trap, `0` none) for diagnostics.
- Trap conditions flag context and visuals; they do not suppress setup creation.
- Trap debug decomposition includes break detection, trap window status, and trap volume gate pass.

### 8.5 RR gate semantics in DEV
- RR checks are computed as quality telemetry (`rr_quality`, multiplier/risk validity).
- Setup/open signal creation is not suppressed by RR in DEV validation mode.
- RR quality remains exposed in debug table/plots for post-run analysis.

### 8.6 Observability contract (debug harness)
When `debug_mode=true` and `show_debug_table=true`, debug table reports module-level states suitable for TV feedback triage:
- Flat: state code, last finalize bar, hi/lo, touches, exit confirm.
- POC: working level, working tests, active POC count.
- Stop-volume: event flag + tracked level.
- Trap: flag + break/window/volume gate components.
- PP: state text/code + pending dir + confirm count.
- HTF: trend dir + previous/latest pivot pairs.
- RR: gate/quality + requested/effective history keep and budget caps.

## 2026-02-19 — v12 product UX (zones → stages → entry)

### Flow overview
- v12 is built around a top-down MTF flow: HTF zones define context, LTF zone refines execution, stage machine drives operator actions.
- Active zone is selected as closest valid zone with bias-aware preference (BUY bias prefers demand, SELL bias prefers supply).
- Stage progression:
  1. **FAR**: price is away from active zone.
  2. **NEAR**: price within ATR-based threshold (`near_thr_atr`) → prepare direction.
  3. **IN_ZONE**: close enters active zone bounds.
  4. **CONFIRM**: enabled confirms pass (PP/CHOCH, trap-return, RSI/MACD, RR gate).
  5. **ENTRY**: confirmation + trigger breakout of local micro-structure.
  6. **BLOCKED**: inside zone but confirm stack fails; HUD exposes reason.

### MTF auto hierarchy
- `chart <= 15m`: `HTF1=4H`, `HTF2=1H`, `LTF=chart`.
- `chart = 30m/1H`: `HTF1=1D`, `HTF2=4H`, `LTF=chart`.
- `chart >= 4H`: `HTF1=1W`, `HTF2=1D`, `LTF=chart`.
- Manual mode allows explicit TF override.

### Zone model
- HTF supply/demand is built from pivots with ATR padding.
- Zones are boxed, extended to the right, lifecycle-managed (touch/age/invalidation), and capped per TF+type for object safety.
- LTF entry zone supports `POC` (VWMA-centric ATR zone) or `ACCUM` (validated local flat range).


## v12 canonical status (2026-02-19)

- Canonical tooling target is `prizrak_trade_setup_detector_v12_0_0.pine`; v11 remains legacy/reference only.
- v11 core trading modules migrated into v12 runtime:
  - POC profile engine (volume-by-bin),
  - Flat/accum touch-state zone logic,
  - Anchored trap confirm module,
  - PP strict state machine for confirm+bias,
  - RR stop/TP model with bounded visual history.
- UX contract of v12 preserved: stage pipeline, right-extended boxes, HUD, icons, lifecycle alerts.

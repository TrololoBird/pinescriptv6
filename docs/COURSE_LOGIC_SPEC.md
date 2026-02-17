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

### 3.6 RR gate boolean
When setup candidate exists (`open_buy` or `open_sell`), gate requires:
- strictly positive risk (`risk_buy > 0` or `risk_sell > 0`)
- multiplier policy `max(rr_main_mult, rr_ext_mult) >= rr_min`

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

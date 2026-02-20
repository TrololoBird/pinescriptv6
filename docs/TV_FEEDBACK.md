# TradingView Feedback Log

## Compiler errors (paste verbatim)
- No compiler errors have been pasted in this thread yet. Paste the latest TradingView compiler output here verbatim.

## Runtime warnings
- (paste verbatim)

## Screenshots (15m BTCUSDT.P, 1h BTCUSDT.P, 1D AAPL)
- 15m BTCUSDT.P:
- 1h BTCUSDT.P:
- 1D AAPL:

## Notes on what looks wrong
- (describe mismatches vs COURSE_LOGIC_SPEC.md)

## 2026-02-18 17:34:04Z — Codex intake from user report (awaiting fresh TV rerun)
- Symbol: (user to provide)
- Timeframe: (user to provide)

### Compiler errors (raw lines reported by user)
- Undeclared identifier: `poc_bins_cap`
- Undeclared identifier: `poc_window_cap`
- Duplicate definitions / "already defined" errors in RR draw tuple locals
- Shadowing variable exists in parent scope (caused by accidental local re-declaration)
- Label/line style typing errors (enum misuse)
- Label style/type mismatch and size/type mismatch in helper signatures
- `Cannot assign const string to const int` for style selector variables
- `Syntax error at input ':='`

### Runtime warnings
- (none provided in this intake batch)

### Codex triage/actions applied in repo
- Normalized style/size helper signatures to int-based enums for `f_line_styled` and `f_label`.
- Normalized trap/choch style variables to `int`.
- Removed collision-prone temporary tuple variables and renamed RR history locals to unique names.
- Kept `poc_bins_cap` and `poc_window_cap` declared before first usage.
- Extended `tools/lint_guard.py` to block string-typed style/size helper params and related regressions.

### Next TV run requested from user
- Re-run TradingView compile on the updated export and paste **raw** compiler output here.
- Confirm whether these prior classes are resolved: undeclared identifiers, duplicate definitions, shadowing, style/type mismatches, `':='` syntax errors.
- If compile passes, add runtime warnings (if any) and screenshots (debug on/off) plus short visual mismatch notes.

## 2026-02-18 17:56:42Z — DEV diagnostics added; awaiting user TV run
- Status: DEV-only gating telemetry and heartbeat debug visuals were added in-repo.
- TradingView run ownership: user executes TV compile/runtime loop; Codex consumes appended feedback from this file.

### User TV rerun checklist
- Symbol/timeframe matrix:
  - 15m BTCUSDT.P
  - 1h BTCUSDT.P
  - 1D AAPL
- For each chart, run with `debug_mode=true` and `show_debug_table=true`:
  - Paste **raw** compiler errors/warnings verbatim (if any).
  - Paste **raw** runtime warnings verbatim (if any).
  - Attach screenshots with debug table + debug label visible.
  - Note latest "diag last" lines from debug table (last gating reasons).
- Then rerun with `debug_mode=false` and append screenshots/notes if visuals still look sparse.
- Keep all new entries append-only in this file with UTC timestamps.

## 2026-02-18 20:00:00Z — Template for next user TV run (append-only)
- Symbol:
- Timeframe:
- Debug mode: (`true` / `false`)

### Compiler output (raw, verbatim)
- 

### Runtime warnings (raw, verbatim)
- 

### Debug table snapshot (key rows)
- flat state/final:
- flat hi/lo:
- flat touch/exit:
- poc tests/active:
- sv event/level:
- trap flag:
- trap break/window:
- trap vol_gate:
- pp state:
- pp pending/dir:
- pp confirm cnt:
- htf dir:
- htf pivots prev:
- htf pivots last:
- rr gate/qual:
- rr keep req/eff:
- rr keep box/ln/lb:
- setup raw/final:
- diag last:

### Visual notes (vs COURSE_LOGIC_SPEC)
- flat visibility:
- working level visibility:
- PP markers:
- trap markers:
- RR overlays:

### Screenshots/links
- debug on:
- debug off:

## 2026-02-18 23:31:23Z — Codex strict-compat pass (awaiting user TV validation)
- TradingView actions remain user-owned per `docs/TV_COMPILE_LOOP.md`.
- Export used for this pass: `make tv-export`.

### User TV rerun checklist (append raw outputs below)
- Symbols/timeframes to validate (minimum):
  - BTCUSDT 15m
  - BTCUSDT 1h
  - AAPL 1D
- For each chart provide:
  - Raw Pine compiler output (verbatim, including line/column text).
  - Raw runtime warnings (verbatim).
  - Screenshots with `debug_mode=true` + `show_debug_table=true`.
  - Screenshots with `debug_mode=false` (clean visual pass).
- Extra focus checks for this pass:
  - Working level picks nearest active POC to price.
  - Trap break registration respects HTF alignment.
  - PP pending/confirm/active blocks both BUY and SELL setups.
  - Level zone is visible around working level (thinner in clean mode).
  - RR history and open RR overlays remain present without object-limit warnings.

## 2026-02-18 23:41:45Z — Strict-compat recheck (Codex)
- Repository gates passed locally in strict mode.
- Export command executed: `make tv-export`.
- No lock refresh performed (`contract.lock.json` unchanged).

### User checklist for TradingView validation (append raw outputs below)
- Symbols/TF:
  - BTCUSDT 15m
  - BTCUSDT 1h
  - AAPL 1D
- For each run, please append:
  - Raw compiler output (verbatim).
  - Raw runtime warnings (verbatim).
  - Screenshot with `debug_mode=true` and `show_debug_table=true`.
  - Screenshot with `debug_mode=false`.
- Focus points:
  - Working level aligns to nearest active POC.
  - Trap break alignment follows HTF direction gates.
  - PP pending/confirm/active blocks BUY+SELL while alive.
  - Level zone stays visible around working level (clean mode = higher transparency).
  - RR overlays/history remain present without object-limit warnings.

## 2026-02-18 23:55:00Z — Strict-compat TV validation checklist (Codex append-only)
- Local release checks passed before TV handoff:
  - `make check-release`
  - `make contract-check`
  - `make lint`
  - `make check-dev`
  - `make tv-export`
- Contract integrity:
  - `git diff -- contract.lock.json` is empty.
- Focus checklist for TV rerun:
  - Verify trap mismatch gating is HTF-only (no STF dependency in break/trap gating).
  - Verify RR gate blocks setup creation when `rr_quality < rr_min`.
  - Verify level zone remains visible around `working_level` and is more transparent in `clean_mode`.
  - Verify POC lines and RR history remain available in `clean_mode`.

## 2026-02-19 00:00:00Z — Codex post-change TV validation checklist (append-only)
- Scope of this pass: strict-compat logic hardening with public contract preserved.
- Export command for this pass: `make tv-export`.

### What to verify in TradingView
- Symbols/TF matrix:
  - BTCUSDT 15m
  - BTCUSDT 1h
  - AAPL 1D
- Trap validation focus:
  - Confirm trap is evaluated relative to break-time level snapshot (no false trap due to nearest-POC level jump after break).
  - Confirm break registration still respects HTF-only mismatch gate at break moment.
- Setup cross focus:
  - Confirm no false setup appears solely because `working_level` jumped between bars while price did not truly cross that level.
- Visual focus:
  - Trap and PP icons retain a short history (not just one latest icon).
  - In `clean_mode=true`, trap/PP icons are not drawn and previously drawn icon history is cleared.

### Artifacts to attach
- Per chart (BTCUSDT 15m/1h, AAPL 1D):
  - Raw compiler output (verbatim).
  - Raw runtime warnings (verbatim).
  - Screenshot with `debug_mode=true` + `show_debug_table=true`.
  - Screenshot with `debug_mode=false`.
- Include notes whether trap happened vs expected break-level anchor behavior.

## 2026-02-19 00:20:00Z — Codex BTCUSDT 5m/15m/30m verification checklist (append-only)
- Local strict gates for this patch are expected to pass both before and after edits:
  - `make check-release`
  - `make contract-check`
  - `make lint`
  - `make check-dev`
  - `make tv-export`
- Contract guardrails:
  - Keep public contract unchanged (`indicator/input/alertcondition`).
  - Confirm `git diff -- contract.lock.json` is empty.

### TradingView replay checklist
- Symbols/TF:
  - BTCUSDT 5m
  - BTCUSDT 15m
  - BTCUSDT 30m
- For each TF, validate in both modes:
  - `debug_mode=true` (+ optional debug table on)
  - `debug_mode=false`

### Focus checks for this patch
- Debug overlay scale:
  - Candles do not collapse/squash when `debug_mode=true`.
  - Only price-unit debug plots stay on overlay scale (`DBG Flat Mid`, `DBG POC Level`, `DBG Stop Price`).
- Future-time extension:
  - `rr_open_extend` visibly extends OPEN-RR objects to the right of current bar.
  - Right-side RR labels/boxes are placed in future time, not pinned to current bar.
- POC tests edge-trigger:
  - `poc_tests` increments only on touch-entry transitions (not every touched bar).
  - Active POC levels decay slower; `POC:block no_active_poc` appears less frequently on 30m.
- Working-level cross hardening:
  - Cross/break/setup signals are not produced from nearest-POC jumping between bars.
- Trap lifecycle:
  - `last_break_*` state clears after `trap_max_bars` expiry (no sticky stale break diagnostics).
- Anti-spam setup gate:
  - RR history no longer forms dense barcode-like vertical stripes around one level on 5m/15m.

## 2026-02-19 01:10:00Z — v12 TV validation checklist (demo/first-trades readiness)
- Scope: `prizrak_trade_setup_detector_v12_0_0.pine` MTF zone anchoring/stage-machine hardening.
- Pre-TV local gates expected PASS:
  - `make check-release`
  - `make check-dev`
  - `make lint`
  - `make tv-export`

### TradingView matrix
- BTCUSDT 15m / 1h / 4h:
  - HTF supply/demand boxes start from pivot bar timestamp.
  - Active zone is deterministic and visually highlighted.
  - FAR/NEAR/IN_ZONE/CONFIRM/ENTRY/BLOCKED stage transitions are readable in HUD.
  - Alerts are edge-triggered on stage changes (no repeated spam per bar).
- TIAUSDT 15m:
  - Zone padding never collapses to zero (`pad >= syminfo.mintick`).
  - Low-price symbols still render visible HTF/LTF zones.

### MTF safety checks
- All `request.security` use `gaps_off` + `lookahead_off`.
- Security-call budget remains `<= 6` per bar.
- Zone/object pruning keeps `max_zones_per_tf` and object budgets stable.

## 2026-02-19 02:00:00Z — v12 top-down workflow manual checklist (AUTO LTF + LTF gate)

- Pre-flight local gates expected PASS:
  - `python tools/contract_guard.py --mode release --check`
  - `python tools/lint_guard.py`
  - `make check-release`
  - `make tv-export`

### Manual TradingView checks
- TF stack visibility:
  - Verify HUD shows `TF: HTF1/HTF2/LTF` and active label includes same stack.
- AUTO LTF behavior (`mode_tf=AUTO`):
  - On 15m chart, resolved LTF should be 5m.
  - On 4h chart, resolved LTF should be 1h (or configured chart-map bucket).
  - Switch `auto_ltf_mode=AUTO_BY_HTF2` and confirm LTF equals HTF2.
- LTF gate behavior:
  - With `use_ltf_entry_gate=true`, confirm `CONFIRM` can show `WAIT_LTF` until price reaches LTF entry zone.
  - Confirm `ENTRY` appears only after LTF gate is satisfied and breakout trigger occurs.
- LTF edge observability:
  - Verify `🎯 LTF ZONE` event on edge enter into LTF entry zone.
  - Verify new alerts fire once on edge:
    - `price_in_ltf_buy_zone`
    - `price_in_ltf_sell_zone`
- Visual rank clarity:
  - Verify HTF1 zones are visually stronger than HTF2 and both are distinct from fallback/other TF zones.

## 2026-02-20 — P0/P1 verification checklist (HTF breakout + BLOCKED semantics)

- [ ] BTCUSDT 15m/1h/4h: in Data Window `DBG htf1_edge_up/dn` and `DBG htf2_edge_up/dn` are not permanently zero; values reach `1` on valid HTF breakouts.
- [ ] New HTF zones appear after real breakout confirmations (no long freeze with only historical zones).
- [ ] Stage flow is sequential and human-readable: `FAR/NEAR -> IN_ZONE -> ✅ CONFIRM_READY -> ENTRY` when trigger crosses.
- [ ] `⛔ BLOCKED` appears only when price is in zone and LTF gate is already valid, but confirm filters fail.
- [ ] `WAIT TRIG` appears when filters are all OK in-zone but entry trigger has not crossed yet.
- [ ] `blocked_*` icons/alerts do not fire while price is FAR/NEAR or before in-zone gating.
- [ ] Trap volume gate behavior is stable across chart TF changes (uses HTF volume MA from HTF context).

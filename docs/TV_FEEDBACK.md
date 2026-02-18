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

# Error Prevention Checklist (Pine v6)

Use this checklist before and after edits in `prizrak_trade_setup_detector_v11_7_0.pine`.

## 1) Before coding
- Confirm scope: no interface-contract changes unless explicitly requested.
- Keep `indicator(...)`, `input.*`, and `alertcondition(...)` untouched by default.
- If editing existing stateful variables (`var`), prefer reassignment `:=` over redeclaration `=`.

## 2) During coding
- For tuple updates of already-declared variables, use `:=`:
  - Correct: `[a, b, c] := f_update(a, b, c)`
  - Risky for existing vars: `[a, b, c] = f_update(a, b, c)`
- Avoid duplicate local declarations in loops/branches for the same identifier.

## 3) Validation commands
Run all checks:

```bash
make check-dev
make check
make contract-check
make lint
```

## 4) Release notes discipline
- Record each bug/fix pair in `docs/CHANGELOG_DEV.md` with date and impacted area.
- Include exact warning text when possible, so regressions are searchable.

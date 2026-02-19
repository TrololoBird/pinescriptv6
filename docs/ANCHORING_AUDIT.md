# Anchored break/trap audit

Date: 2026-02-19

## Goal
Verify that anchored break/trap changes are present in `prizrak_trade_setup_detector_v11_7_0.pine` without changing the public contract (`indicator(...)`, `input.*`, `alertcondition(...)`) and without changing `contract.lock.json`.

## Verification commands
```bash
git rev-parse --abbrev-ref HEAD
git log -1 --oneline
git status --short
git diff --stat
grep -n "last_break_level" prizrak_trade_setup_detector_v11_7_0.pine
grep -n "ta.crossover(close, working_level)\|ta.crossunder(close, working_level)" prizrak_trade_setup_detector_v11_7_0.pine
```

## Findings
- `last_break_level` is declared in persistent state.
- `work_cross_up/work_cross_dn` are explicit close-vs-level cross checks (no `ta.crossover/ta.crossunder` for `working_level`).
- On break registration (`brk_up/brk_dn`), `last_break_level := working_level` is persisted.
- Trap return uses `last_break_level` (not `working_level`).
- Trap debug state gate checks `na(last_break_level)`.

## Guard/check status
- `make check-release`: PASS
- `make contract-check`: PASS
- `make lint`: PASS
- `make check-dev`: PASS
- `make tv-export`: PASS
- `make style-check`: PASS (no diff in Pine file)
- `git diff -- contract.lock.json`: empty


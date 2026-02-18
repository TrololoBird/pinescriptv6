# DEV Changelog

## 2026-02-18

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

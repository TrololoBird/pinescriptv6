# Repository guardrails for Codex

## Canonical file
- Canonical indicator file: `prizrak_trade_setup_detector_v11_7_0.pine`.
- Do not change it unless the task explicitly requires Pine edits.

## Interface contract rules
- Public interface is locked: `indicator(...)`, all `input.*` declarations (`name = input...`), and all `alertcondition(...)` lines.
- Before commit, run `make check`.
- Contract checks:
  - `make contract-check` validates the Pine interface against `contract.lock.json`.
  - `make contract-init` refreshes lock file **only for intentional contract updates**.
- Do not add new inputs or modify alertconditions without explicit request.

## Style-only change policy
- For style-only tasks, only visual tokens are allowed (e.g. color/opacity/width/style/size/textcolor/border fields).
- Do not change geometry, conditions, timing, state lifecycle, module logic, or signal generation.
- Enforce with `make style-check` when the task is style-only.

## Prompt template for future tasks (GitHub issue style)
Include these sections:
1. Goal
2. Hard constraints (what must not change)
3. Scope (files allowed to edit)
4. Acceptance checks
5. Verification commands (`make check`, plus task-specific checks)

# TradingView compile loop (user-driven, Codex-assisted)

## Ownership and hard boundary
- **User-only TradingView actions:** paste script, save, add to chart, switch symbols/timeframes, collect compiler/runtime output, and take screenshots.
- **Codex-only repo actions:** consume artifacts committed in-repo, apply code/doc fixes, run repository checks (`make check-dev`, lint/contract guards), and request the next TV validation run.
- Codex must **never** be instructed to perform TradingView UI actions directly.

## Required loop
1. User exports latest script from repo (for example `make tv-export`) and pastes it into TradingView Pine Editor.
2. User clicks **Save** and **Add to chart**.
3. User captures:
   - compiler output (errors/warnings, with line/column text),
   - runtime warnings (object limits, na/runtime issues),
   - screenshots for requested symbols/timeframes/debug modes.
4. User appends raw results to `docs/TV_FEEDBACK.md` (append-only, timestamped entries).
5. Codex reads `docs/TV_FEEDBACK.md`, updates code/docs in repo, runs `make check-dev`, and records what changed.
6. Codex appends "awaiting user TV compile results" + a concrete rerun checklist in `docs/TV_FEEDBACK.md`.

## Reporting format for user entries in `docs/TV_FEEDBACK.md`
- Timestamp (UTC), symbol, timeframe.
- Raw compiler lines verbatim.
- Raw runtime warning lines verbatim.
- Screenshot paths/links.
- Short note on what appears visually incorrect versus `docs/COURSE_LOGIC_SPEC.md`.

## Minimum rerun checklist after each Codex fix
- Recompile in TradingView (same symbol/timeframe as previous failing run).
- Confirm whether previous error classes are gone.
- If compile succeeds, toggle debug mode on/off and capture screenshots.
- Append results to `docs/TV_FEEDBACK.md` with raw text.

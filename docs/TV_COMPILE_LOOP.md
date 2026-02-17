# TradingView compile loop (DEV validation harness)

## Goal
Run a reproducible compile/runtime loop for the Pine script and collect technical evidence for:
- compile success,
- object/runtime stability,
- debug harness visibility across multiple timeframes.

## Exact compile steps in TradingView
1. Open TradingView in browser.
2. Open **Pine Editor**.
3. Open local file `prizrak_trade_setup_detector_v11_7_0.pine` in this repo and copy all content.
4. Paste script into a new Pine Editor tab.
5. Ensure Pine version is `//@version=6`.
6. Click **Save**.
7. Click **Add to chart**.
8. Record compile result:
   - if error: copy exact error text + line number,
   - if success: capture screenshot with no compile error banner.
9. Open settings and toggle:
   - `Debug mode = true`,
   - `Show debug table = true`.
10. Confirm debug plots/table appear.
11. Repeat visual check on exactly three chart timeframes:
   - 15m,
   - 1h,
   - 4h.

## What to capture
- Compile stage:
  - exact compile errors (if any), including line numbers.
- Runtime stage:
  - any `max_lines_count`, `max_labels_count`, `max_boxes_count`, or other runtime warnings.
- Screenshots:
  - 1 screenshot per timeframe (15m/1h/4h) with debug enabled,
  - 1 screenshot with debug disabled (`Debug mode=false`) to verify debug visuals are suppressed.

## 10-minute smoke checklist (technical only)
- [ ] Script compiles in Pine v6 without errors.
- [ ] No runtime object-limit warnings while scrolling history (~5k bars loaded).
- [ ] No `na`-driven runtime failures when switching 15m -> 1h -> 4h.
- [ ] Debug plots render when `Debug mode=true`.
- [ ] Debug table renders only when `Debug mode=true` and `Show debug table=true`.
- [ ] Debug table disappears when `Show debug table=false` or `Debug mode=false`.
- [ ] With `Debug mode=false`, no extra debug plots/objects remain visible.
- [ ] Existing alert conditions still compile.

## Reporting template
Use this structure when reporting results:
1. Compile result: pass/fail + full error text if fail.
2. Runtime result: pass/fail + full warning text if present.
3. Timeframe evidence:
   - 15m screenshot path
   - 1h screenshot path
   - 4h screenshot path
4. Debug off screenshot path.
5. Notes on any reproducible instability and exact reproduction steps.


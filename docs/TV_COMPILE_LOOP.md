# TradingView compile loop (DEV)

## Goal
Validate that the Pine v6 script compiles and runs without runtime object-limit issues on a long history window.

## Steps
1. Open TradingView Pine Editor.
2. Open `prizrak_trade_setup_detector_v11_7_0.pine` from this repo and copy all contents.
3. Paste into a new Pine Editor tab.
4. Save and click **Add to chart**.
5. In the Pine Editor, confirm there are no compile errors.
6. Scroll chart history to load approximately 5k bars.
7. Confirm there are no runtime limit errors related to visual objects.
8. Keep default settings and then toggle the PP module input on/off once to verify script stability.

## What to return
- One screenshot showing the script attached to chart with no compile error banner.
- One screenshot showing no runtime error banner after history load.
- If any error appears, return exact error text and line number.

## Known-good checklist
- Script compiles in Pine v6.
- No runtime `max_*` object-limit errors on approximately 5k bars.
- PP events can appear without compile/runtime failure.

# Полная Архитектура Индикатора "Prizrak Trade Setup Detector v2.0"

(строго на Pine Script 6, с учётом всех возможностей TradingView 2026 года, без единой строки кода)

## 1. Общая Концепция и Цели

Индикатор полностью воспроизводит логику мини-курса Prizrak Trade (69 страниц) на одном графике.

Главная идея:
- **СТФ** (D1 или W1) — определяет **приоритет направления** (шорт/лонг/флэт).
- **МТФ** (H4 или H1) — определяет **структуру** и ключевые уровни.
- **Младший ТФ** (15m / 5m) — только **вход + подтверждение** (2+ бара, объём, дивергенция).

Никогда не смешивать уровни разных ТФ.

Цель: минимум ложных сигналов, чёткие сетапы с RR, чистый визуал, поддержка clean mode.

## 2. Структура Индикатора (Модульная Архитектура)

### 2.1. Inputs (7 групп)

- **Основные модули** — включение/выключение каждого блока (накопления, POC, стоповый объём, ловушки, PP, фильтры, RR gate).
- **Накопления** — min touches (4), min touches на сторону (2), max range % (5%), early/true break %, auto/manual длина флэта по ТФ.
- **POC / рабочий уровень** — bins, max keep, dead tests, price mode (HLC3/VWAP), bin min %.
- **Стоповый объём** — окно, max range %, vol mult, early break %, density ATR filter.
- **Ловушки** — max bars window, vol drop factor, cooldown.
- **PP (переприор)** — HTF, pivot length, early/true break %, need retest, retest bars.
- **Фильтры** — RSI len, MACD params, div lookback.
- **Сетапы** — ATR proximity, allow countertrend, RR min, main/ext mult.
- **Визуализация** — clean mode, show boxes, show POC lines, show stop line, squeeze params, target preset.
- **RR Overlay** — show history, show stat labels, draw open trade, history keep.
- **Debug** — debug mode, show debug table.

### 2.2. State Management

- Все переменные с `var` или `varip`.
- Отдельные структуры для:
  - Текущего флэта (`high`, `low`, `touches_top`, `touches_bottom`, `start_bar`).
  - POC массива (`prices`, `bars`, `tests`).
  - Стопового объёма (`high`, `low`, `start_bar`, `volume_event`).
  - PP (`pending` / `confirm`, `level`, `bar`, `count`).
  - Открытой позиции (`dir`, `entry`, `stop`, `tp_main`, `tp_ext`, `breakeven`).
  - RR истории (arrays для `dir`, `entry`, `exit`, `rr`, `result`, `bars`).

### 2.3. Core Modules (выполняются в строгом порядке каждый бар)

1. **МТФ Trend Direction** (`request.security` D1/W1)
   - Возвращает: `+1` (up), `-1` (down), `0` (flat).

2. **Накопление (Flat Detection)** — на МТФ (H4)
   - Формула: `cand_high = highest(high, max_flat_bars)`, `cand_low = lowest(low, max_flat_bars)`.
   - Касания: `touch_top`, если `high >= flat_high - tolerance`; `touch_bottom`, если `low <= flat_low + tolerance`.
   - Условие активного флэта: `total_touches >= min_touches` И касания на каждую сторону `>= min_touches_side` И `range % <= flat_max_range_pct`.
   - Early break: цена вышла за границу на `flat_break_early %`.
   - True break: цена вышла на `flat_break_true %` + 2+ бара подтверждения.

3. **Рабочий уровень (POC)** — на МТФ (H4)
   - Профиль объёма по `HLC3` или `VWAP` за период флэта.
   - `POC` = цена бина с максимальным объёмом.
   - Снимается после `poc_dead_tests` тестов (тест = цена коснулась уровня и закрылась за ним).

4. **Стоповый объём** — на МТФ (H4)
   - Окно `stop_len` баров.
   - Условие: диапазон `<= ATR × stop_range_atr_mult` И плотность `(max-min)/ATR <= stop_density_mult` И объём хотя бы одного бара `>= vol_ma × stop_vol_mult`.

5. **Ловушки (Traps)** — на младшем (15m)
   - False BOS/CHoCH на младшем против тренда МТФ.
   - Условие: break структуры + low vol (`volume < vol_ma × trap_vol_drop`) + no conf bars.

6. **Переприор (PP true/false)** — на МТФ (H4)
   - `PP true` = break структуры + retest уровня + 2+ бара подтверждения + volume spike или дивергенция.
   - `PP early` = break без retest.
   - `PP pending` — ждёт retest (`pp_retest_bars`).

7. **Фильтры** — RSI/MACD/BBW на младшем (15m)
   - Bull/Bear div (`div_lookback`).
   - Squeeze = `BBW < BBW_ma × squeeze_factor`.

### 2.4. Setup Engine (главный блок)

- BUY setup = hold Discount + conf на 15m + bull фильтры (и optionally `allow_counter`).
- SELL setup = rejection Premium/EQ + conf на 15m + bear фильтры.
- RR Gate: рассчитывается от предполагаемого входа к стопу и TP (`main = ×1.618`, `ext = ×2.618`).
- Только если `RR >= rr_min` — сетап активен.
- При активации: рисуем открытую сделку (RR overlay).

### 2.5. Визуальная Система

- **Clean Mode**: только ключевые линии (`EQ`, `Premium`, `Discount`, `PDL`, `Weak Low`, рабочий `POC`).
- **Boxes**: флэт-боксы (зелёный если up тренд, красный если down тренд).
- **Линии**: `POC` (жёлтая), stop line (красная), RR zones (полупрозрачные).
- **Labels**: BUY/SELL (зелёный/красный), TRAP (оранжевый ромб), PP TRUE (фиолетовый).
- **RR Overlay**: для открытой сделки — 3 бокса (`stop`, `TP1`, `TP2`) + `entry line` + stat label (`RR` и результат).
- **История RR**: последние `N` сделок (настраиваемо) с цветом результата (зелёный/красный).

### 2.6. Alerts

- `Prizrak BUY` / `Prizrak SELL` — при активации сетапа.
- `Prizrak TRAP` — при обнаружении ловушки.
- `Prizrak PP TRUE` — при истинном переприоре.
- `Prizrak BREAKEVEN` — когда позиция переведена в BE.

### 2.7. Debug & Diagnostics

- Debug table (`top_right`) с состоянием всех модулей (`flat valid`, `PP state`, `RR quality`, `trap flag` и т.д.).
- Debug labels на графике (при `debug_mode = true`).
- Лог последних событий (array строк).

## 3. Таймфреймы в Архитектуре

- **СТФ** — D1 (или W1 по выбору пользователя) — только направление тренда.
- **МТФ** — H4 (основной) или H1 (альтернатива) — накопления, структура, PP, POC, стоповый объём.
- **Entry TF** — текущий график (15m или 5m) — вход, подтверждение 2+ баров, дивергенция, trap detection.

Все `request.security` делаются с `lookahead = barmerge.lookahead_off`.

## 4. Формулы (псевдо-математика)

- Flat range % = `(high - low) / low × 100`.
- Touch tolerance = `ATR × touch_tolerance`.
- RR = `(TP - entry) / (entry - stop)`.
- POC bin size = `(high - low) / bins`, с min bin = `syminfo.mintick × factor`.
- Squeeze = `BBW < BBW_ma × squeeze_factor`.
- PP true = `break + retest + 2+ bars + volume > vol_ma × 1.5`.

## 5. Визуал (цвета и стиль)

- Premium — тёмно-красный полупрозрачный.
- Discount — тёмно-зелёный полупрозрачный.
- EQ — серая линия.
- POC — жёлтая линия.
- Stop line — красная пунктирная.
- RR zones — зелёный/красный с прозрачностью 80%.
- Labels — размер `normal/small`, стиль `arrow` или `label_left`.

## 6. Flow расчёта (порядок выполнения каждый бар)

1. Получить СТФ тренд.
2. Рассчитать накопление на МТФ.
3. Рассчитать POC / рабочий уровень.
4. Рассчитать стоповый объём.
5. Проверить ловушки.
6. Проверить PP (`pending / confirm`).
7. Применить фильтры (`RSI/MACD/BBW`).
8. Сформировать BUY/SELL setup.
9. Если сетап активен — нарисовать RR overlay.
10. Обновить историю RR.
11. Нарисовать визуал (`clean mode` или полный).
12. Выдать алерты.
13. Обновить debug table.

Эта архитектура полностью соответствует курсу Prizrak Trade, учитывает скриншоты и замечания, и остаётся в границах design-only спецификации (без Pine-кода).

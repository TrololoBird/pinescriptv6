# Полная архитектура индикатора «Prizrak Trade Setup Detector v2.0»

Документ фиксирует целевую модульную архитектуру индикатора в терминах Pine Script v6 и текущих возможностей TradingView (2026). Это спецификация уровня дизайна (без кода): последовательность расчётов, состояния, контракты данных между модулями, визуал и алерты.

## 1. Общая концепция и цели

Индикатор должен воспроизводить логику мини-курса Prizrak Trade в одном рабочем пространстве графика.

Базовая иерархия:
- **СТФ (D1/W1)**: определяет **приоритет направления** (`long` / `short` / `flat`).
- **МТФ (H4/H1)**: определяет **структуру рынка** и ключевые рабочие уровни.
- **Entry TF (15m/5m)**: отвечает только за **вход и подтверждение** (2+ баров, объём, дивергенции).

Принцип: **не смешивать уровни между ТФ**. Цель — снижать ложные сигналы, сохранять чистый визуал и поддерживать `clean mode`.

## 2. Модульная структура

### 2.1 Группы входных параметров (inputs)

Архитектура предусматривает 11 логических групп:
1. **Основные модули** (enable/disable блоков: accumulation, POC, stop volume, traps, PP, filters, RR gate).
2. **Накопления** (`min_touches`, `min_touches_side`, `flat_max_range_pct`, early/true break %, auto/manual flat length по ТФ).
3. **POC / рабочий уровень** (`bins`, `max_keep`, `dead_tests`, `price_mode` HLC3/VWAP, `bin_min_pct`).
4. **Стоповый объём** (`stop_len`, `stop_range_atr_mult`, `stop_vol_mult`, early break %, `stop_density_mult`).
5. **Ловушки** (`trap_max_bars`, `trap_vol_drop`, `trap_cooldown`).
6. **PP (переприор)** (`pp_htf`, `pivot_len`, early/true break %, `need_retest`, `pp_retest_bars`).
7. **Фильтры** (`rsi_len`, MACD-параметры, `div_lookback`).
8. **Сетапы** (`atr_proximity`, `allow_countertrend`, `rr_min`, `rr_main_mult`, `rr_ext_mult`).
9. **Визуализация** (`clean_mode`, `show_boxes`, `show_poc_lines`, `show_stop_line`, squeeze params, target preset).
10. **RR Overlay** (`show_history`, `show_stat_labels`, `draw_open_trade`, `history_keep`).
11. **Debug** (`debug_mode`, `show_debug_table`).

### 2.2 Управление состоянием (state)

Все долгоживущие сущности держатся в `var`/`varip`-состояниях и массивах:
- Текущий флэт: `high`, `low`, `touches_top`, `touches_bottom`, `start_bar`.
- POC-контейнер: массивы `prices`, `bars`, `tests`.
- Стоповый объём: `high`, `low`, `start_bar`, `volume_event`.
- PP-машина: `pending/confirm`, `level`, `bar`, `count`.
- Открытая сделка: `dir`, `entry`, `stop`, `tp_main`, `tp_ext`, `breakeven`.
- RR-история: массивы `dir`, `entry`, `exit`, `rr`, `result`, `bars`.

### 2.3 Core-модули и строгий порядок исполнения на каждом баре

1. **MTF Trend Direction** (через `request.security` D1/W1): выход `+1`, `-1`, `0`.
2. **Accumulation / Flat Detection** (МТФ H4/H1): диапазон, касания, valid-state, early/true-break.
3. **POC / рабочий уровень**: профиль объёма по флэту, удаление уровня по `dead_tests`.
4. **Стоповый объём**: low-range + volume spike + ATR density.
5. **Traps** (Entry TF): ложный структурный пробой против МТФ-приоритета, low volume, нет подтверждения.
6. **PP (early/true + pending)**: break, retest, подтверждение 2+ барами, trigger от объёма/дивергенции.
7. **Фильтры** (RSI/MACD/BBW, дивергенции, squeeze).

### 2.4 Setup Engine (главный блок принятия решения)

- **BUY**: удержание Discount + подтверждение на Entry TF + bullish-фильтры (+ optional countertrend).
- **SELL**: rejection в Premium/EQ + подтверждение + bearish-фильтры.
- **RR Gate**:
  - `main target = risk × 1.618`
  - `ext target = risk × 2.618`
  - активация сетапа только при `RR >= rr_min`.

При активации создаётся открытая сделка и объектная RR-визуализация.

### 2.5 Визуальная система

- **Clean Mode**: только EQ, Premium, Discount, PDL, Weak Low, активный POC.
- **Boxes**: зоны флэта (зелёный для up-приоритета, красный для down).
- **Линии**: POC (жёлтая), stop-line (красная пунктирная), RR-зоны (полупрозрачные).
- **Labels**: BUY/SELL, TRAP (оранжевый), PP TRUE (фиолетовый).
- **RR Overlay**: stop-box, TP1-box, TP2-box, entry-line, статус RR/result.
- **История RR**: последние N закрытых сделок с цветом исхода.

### 2.6 Alerts

- `Prizrak BUY`
- `Prizrak SELL`
- `Prizrak TRAP`
- `Prizrak PP TRUE`
- `Prizrak BREAKEVEN`

### 2.7 Debug и диагностика

- Таблица (`top_right`) по состоянию модулей: flat-valid, PP-state, trap-flag, RR-quality и др.
- Локальные debug-labels на графике при `debug_mode = true`.
- Кольцевой лог последних событий (array строк).

## 3. Таймфрейм-контракт архитектуры

- **СТФ**: D1 (или W1) — только приоритет направления.
- **МТФ**: H4 (или H1) — структура, PP, POC, accumulation, stop-volume.
- **Entry TF**: текущий график 15m/5m — вход и подтверждение.

Требование к MTF-запросам: `request.security(..., lookahead = barmerge.lookahead_off)`.

## 4. Расчётные формулы (псевдо-математика)

- `flat_range_pct = (high - low) / low * 100`
- `touch_tolerance = ATR * touch_tolerance_factor`
- `RR = (TP - entry) / (entry - stop)`
- `poc_bin_size = (high - low) / bins`, минимум `syminfo.mintick * factor`
- `squeeze = BBW < BBW_MA * squeeze_factor`
- `PP_true = break + retest + 2+ bars + (volume > vol_ma * 1.5 | divergence)`

## 5. Визуальные токены и стиль

- Premium: тёмно-красный, полупрозрачный.
- Discount: тёмно-зелёный, полупрозрачный.
- EQ: серая линия.
- POC: жёлтая линия.
- Stop-line: красная пунктирная.
- RR-зоны: зелёный/красный, прозрачность ~80%.
- Labels: `normal/small`, стиль `arrow` или `label_left`.

## 6. Операционный flow (bar-by-bar)

1. Получить СТФ-приоритет.
2. Рассчитать accumulation на МТФ.
3. Рассчитать POC/рабочий уровень.
4. Рассчитать stop-volume.
5. Проверить traps на Entry TF.
6. Проверить PP (`pending/confirm/true`).
7. Применить фильтры RSI/MACD/BBW/div/squeeze.
8. Сформировать BUY/SELL setup.
9. При валидном сетапе построить RR overlay.
10. Обновить RR-историю.
11. Отрисовать визуал (`clean/full`).
12. Сгенерировать alert-сигналы.
13. Обновить debug-table и event-log.

## 7. Границы ответственности и неизменяемые принципы

- Entry-модуль не пересчитывает структуру МТФ.
- СТФ не принимает решение о входе; только задаёт приоритет.
- Любой setup считается валидным только после прохождения RR gate.
- `clean_mode` обязан скрывать второстепенный визуальный шум без потери ключевых уровней.

## 8. Связь с текущей спецификацией репозитория

Этот документ дополняет `docs/COURSE_LOGIC_SPEC.md` как целевую архитектуру версии `v2.0` (design-level) и может использоваться как источник требований для поэтапной реализации модулей и DEV-валидации.

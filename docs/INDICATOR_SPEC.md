# INDICATOR SPEC — Prizrak v12.2.0 (zone → prep → confirm → entry)

## 1) База/накопление и формирование уровня

### 1.1 Что считаем базой
База (накопление) считается на HTF как узкий диапазон, где:
- есть минимум `min_base_bars` баров;
- есть минимум `min_touches` касаний верхней и нижней границы (по wick overlap, edge-trigger логика);
- диапазон базы `base_hi-base_lo` не превышает `ATR(14)*max_range_atr`.

Технически используется машина состояний:
`SEEK_BASE → BUILD_BASE → BASE_VALID → BREAKOUT_UP/BREAKOUT_DN`.

### 1.2 Когда появляется уровень
Уровень (зона POC) создаётся **только после подтверждённого выхода из валидной базы** на том же HTF:
- вверх: `close > base_hi` на `exit_confirm_bars` HTF-барах подряд;
- вниз: `close < base_lo` на `exit_confirm_bars` HTF-барах подряд.

После breakout создаётся зона `POC ± pad`, где `pad = ATR_zone * htf_poc_pad_mult`.
Сохраняются `base_hi/base_lo` как структурная опора для стопа/инвалидации.

### 1.3 Что такое POC
POC — price bin с максимальным объёмом внутри окна базы (`base_bars`, ограничено `base_max_bars`).
Вычисление по `htf_poc_bins`; массивы бинов реиспользуются без постоянной новой аллокации.

## 2) Жизненный цикл зоны

### 2.1 Статусы зоны
- `ACTIVE`
- `TOUCHED`
- `CONSUMED`
- `INVALID`
- `EXPIRED`

### 2.2 «Уровень отработан и удаляем»
После первого качественного отклика зона помечается `CONSUMED`:
- BUY: реакция вверх от зоны `>= ATR_zone*consume_reaction_atr_mult`;
- SELL: реакция вниз от зоны `>= ATR_zone*consume_reaction_atr_mult`.

По умолчанию consumed-уровни удаляются; история может быть оставлена через `show_consumed_history`.

### 2.3 Touch и invalidation
- Touch считается только edge-trigger по **входу wick overlap в зону** (`high >= bot && low <= top`).
- Invalidation считается строго по TF зоны, с подтверждением `invalidate_confirm_bars`.
- Flip (если включён) делается только после invalidation + ретеста в окне `flip_retest_bars`.

## 3) Подтверждение, ловушки, вход и RR

### 3.1 ПП (переприор)
Реализован модуль PP (на отдельном TF):
- **True PP**: swing break (pivot high/low), ретест уровня, 2–3 подтверждающих закрытия телами;
- **Early PP**: ранний break локальной структуры + ретест.

Параметры:
`pp_enabled`, `pp_type (TRUE/EARLY/BOTH)`, `pp_confirm_closes`, `pp_retest_window`, `pp_tf`.
В HUD: `PP = OK/WAI/BAD`.

### 3.2 Trap: 3 сценария
- Тип 1: sweep за уровень + возврат обратно.
- Тип 2: пробой и мини-база по другую сторону уровня (упрощённо).
- Тип 3: усиление возврата объёмом на TF зоны (если включён volume gate).

### 3.3 Stage machine
Единый каскад приоритетов:
`FAR → NEAR → IN_ZONE → LTF_READY → CONFIRM_READY → ENTRY`.

`BLOCKED` не перезаписывает stage, а ведётся отдельным флагом + причинами:
`RR/PP/TRAP/OSC/LTF/TRIG`.

### 3.4 Entry trigger
Для MTF используется stable-cross без `ta.crossover/ta.crossunder`:
- BUY: `close > lvl_now && close[1] <= lvl_prev` + защита от смены уровня;
- SELL: зеркально.

`entry_plan` считается отдельно (POC или край зоны), trigger — только разрешение на вход.

### 3.5 RR
RR считается **от entry_plan**:
- `entry_plan_mode`: `POC` или `ZONE_EDGE`;
- стоп: за `base_hi/base_lo` + `max(% pad, ATR pad)`;
- цель: ближайшая противоположная зона того же TF, иначе fallback `ATR*X`.

## 4) Таблица модулей

| Модуль | TF расчёта | Выходные флаги/сигналы | Что рисуем |
|---|---|---|---|
| HTF Base Detector | HTF1/HTF2 | `zone_created`, direction edge, `base_hi/base_lo`, `poc` | BUY/SELL box зоны, подпись POC |
| Zone Lifecycle | TF зоны | `zone_consumed`, `zone_invalidated`, `zone_flipped` | Обновление статусов и продления боксов |
| Stage Engine | Chart + HTF/LTF модули | `stage_buy/sell`, `blocked_*`, причины | HUD стадии, активные BUY/SELL labels |
| PP Confirm | `pp_tf` (или LTF) | `pp_ok_buy/sell`, `PP state` | PP статус в HUD |
| Trap | TF зоны + chart | `trap_event_buy/sell`, `trap_ok_*` | Иконки/алерты trap |
| RR | Chart + зона/HTF | `rr_ok_*`, `rr` | Линии entry/stop/tp, RR в HUD |
| Alerts | Chart | stage edges + blocked edges + zone lifecycle | `alertcondition(...)` |


## 5) Step-1 (P0) implementation constraints

- `ENTRY` must be blocked on trigger-level jumps: `entry_trigger_ok_*` requires `not *_level_changed`.
- Trap volume gate must use active zone TF only (`z_tf[buy_idx]/z_tf[sell_idx]`), not `HTF1 OR HTF2`.
- RR target uses nearest valid opposite-zone POC on same TF and correct side; otherwise `rr_fallback_atr * ATR`.
- P0 scope excludes unrelated origin/features; keep zone origin behavior unchanged unless separate task explicitly requests it.

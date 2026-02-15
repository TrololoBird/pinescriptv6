# Prizrak Trade Setup Detector v11.7.0 — error check & fixes

Ниже перечислены критические ошибки компиляции/логики в присланном Pine Script v6 коде и точечные исправления.

## 1) Необъявленные функции `f_box`, `f_line`, `f_label`

В коде они используются многократно, но нигде не определены.

### Добавить в секцию HELPERS
```pine
f_box(box _bx, int _x1, float _y1, int _x2, float _y2, color _bg, color _bd, int _bw) =>
    box _out = _bx
    if na(_out)
        _out := box.new(_x1, _y1, _x2, _y2, bgcolor=_bg, border_color=_bd, border_width=_bw)
    else
        box.set_left(_out, _x1)
        box.set_top(_out, _y1)
        box.set_right(_out, _x2)
        box.set_bottom(_out, _y2)
        box.set_bgcolor(_out, _bg)
        box.set_border_color(_out, _bd)
        box.set_border_width(_out, _bw)
    _out

f_line(line _ln, int _x1, float _y1, int _x2, float _y2, color _c, int _w) =>
    line _out = _ln
    if na(_out)
        _out := line.new(_x1, _y1, _x2, _y2, color=_c, width=_w)
    else
        line.set_xy1(_out, _x1, _y1)
        line.set_xy2(_out, _x2, _y2)
        line.set_color(_out, _c)
        line.set_width(_out, _w)
    _out

f_label(label _lb, int _x, float _y, string _txt, label_style _style, color _bg, color _tc, size _size) =>
    label _out = _lb
    if na(_out)
        _out := label.new(_x, _y, _txt, style=_style, color=_bg, textcolor=_tc, size=_size)
    else
        label.set_xy(_out, _x, _y)
        label.set_text(_out, _txt)
        label.set_style(_out, _style)
        label.set_color(_out, _bg)
        label.set_textcolor(_out, _tc)
        label.set_size(_out, _size)
    _out
```

---

## 2) Необъявленные переменные RR-палитры

В `f_rr_draw_one()` используются `rr_cStop`, `rr_cTake`, `rr_cTake2`, `rr_cEdge`, `rr_cEntry`, `rr_cTagRisk`, `rr_cTagPnl`, но они не заданы.

### Добавить перед `f_rr_draw_one()`
```pine
rr_cStop    = color.new(color.red, 82)
rr_cTake    = color.new(color.green, 82)
rr_cTake2   = color.new(color.teal, 84)
rr_cEdge    = color.new(color.black, 0)
rr_cEntry   = color.new(color.yellow, 0)
rr_cTagRisk = color.new(color.orange, 0)
rr_cTagPnl  = color.new(color.green, 0)
```

---

## 3) Некорректные проверки `!= na`

В Pine корректный способ — `not na(x)` или `na(x)`. Проверки вида `x != na` приводят к ошибочной/неопределенной логике.

### Заменить
```pine
bool rr_ok_buy  = lvl != na ? (...) : true
bool rr_ok_sell = lvl != na ? (...) : true
```
на:
```pine
bool rr_ok_buy  = not na(lvl) ? (...) : true
bool rr_ok_sell = not na(lvl) ? (...) : true
```

и в `f_rr_draw_one()`:
```pine
if _entry != na and _stopOrig != na and _takeMain != na
```
на:
```pine
if not na(_entry) and not na(_stopOrig) and not na(_takeMain)
```

---

## 4) Логическая ошибка RR gate (использование `tp_main` до расчета)

В блоке RR gate сравнение идет с `tp_main`, который вычисляется позже при открытии позиции, из-за чего gate работает некорректно.

### Исправление (пересчитывать кандидаты TP внутри gate)
```pine
if rr_gate_enabled and (open_buy or open_sell)
    float lvl = working_level
    float st_buy  = not na(last_flat_low)  ? last_flat_low  : close - atr
    float st_sell = not na(last_flat_high) ? last_flat_high : close + atr

    float risk_buy  = math.abs(close - st_buy)
    float risk_sell = math.abs(close - st_sell)
    float tp_buy_main  = close + risk_buy  * rr_main_mult
    float tp_sell_main = close - risk_sell * rr_main_mult

    bool rr_ok_buy  = not na(lvl) and risk_buy  > 0 ? (math.abs(tp_buy_main  - close) / risk_buy  >= rr_min) : true
    bool rr_ok_sell = not na(lvl) and risk_sell > 0 ? (math.abs(close - tp_sell_main) / risk_sell >= rr_min) : true

    open_buy  := open_buy  and rr_ok_buy
    open_sell := open_sell and rr_ok_sell
```

---

## 5) `flat_valid` используется вне области видимости

Переменная объявлена локально в финализации флэта, но используется в VISUALS как будто глобальная (`if flat_valid`). Это ошибка компиляции.

### Исправление
Создать отдельный runtime-флаг перед VISUALS:
```pine
bool flat_valid_now = in_flat and ((touches_top + touches_bottom) >= min_touches)
```

И заменить в VISUALS:
- `if flat_valid` → `if flat_valid_now`
- `if flat_valid and not na(flatBox)` → `if flat_valid_now and not na(flatBox)`

(Либо завести `var bool flat_valid = false` в STATE и поддерживать его обновление.)

---

## 6) Защита цикла зон при пустом массиве

Чтобы избежать пограничных ошибок на ранних барах, безопаснее:
```pine
if array.size(poc_zone_box) > 0
    for i = 0 to array.size(poc_zone_box) - 1
        ...
```

---

## 7) Косметика/устойчивость

- `icon_cooldown` объявлен, но не используется (можно оставить как backward-compatible input).
- `choch_pivot_cap` объявлен, но не используется (аналогично).
- `target_preset`, `show_only_working`, `max_zone_keep`, `zone_reaction_*` сейчас не задействованы — не ошибка компиляции, но стоит либо реализовать, либо пометить как reserved.

---

## Минимальный «компиляционный» патч (обязательный)

1. Добавить `f_box/f_line/f_label`.
2. Добавить RR color constants.
3. Исправить `!= na` на `not na(...)`.
4. Исправить `flat_valid` → `flat_valid_now` (или глобальную `flat_valid`).
5. Исправить RR gate, чтобы не использовать `tp_main` до инициализации.

После этих правок скрипт перестает содержать явные блокирующие ошибки из присланного фрагмента.

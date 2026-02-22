# API_INPUTS_V12

Справочник входных параметров индикатора `prizrak_trade_setup_detector_v12_0_0.pine`.

Всего inputs: **72**.

## TF Hierarchy
| Переменная | Тип input | Название в UI |
|---|---|---|
| `mode_tf` | `string` | TF mode |
| `manual_htf1` | `timeframe` | Manual HTF1 |
| `manual_htf2` | `timeframe` | Manual HTF2 |
| `manual_htf3` | `timeframe` | Manual HTF3 |
| `use_htf3` | `bool` | Enable HTF3 |
| `manual_ltf` | `timeframe` | Manual LTF (blank = chart) |
| `auto_ltf_mode` | `string` | AUTO LTF mode |

## Zone Engine • HTF
| Переменная | Тип input | Название в UI |
|---|---|---|
| `base_len` | `int` | HTF base seek length |
| `min_base_bars` | `int` | HTF min base bars |
| `touch_tolerance` | `float` | HTF base touch tolerance |
| `min_touches` | `int` | HTF base min touches |
| `max_range_atr` | `float` | HTF base max range ATR |
| `exit_confirm_bars` | `int` | HTF breakout confirm bars |
| `htf_poc_pad_mult` | `float` | HTF POC pad ATR mult |
| `htf_poc_bins` | `int` | HTF POC bins |
| `base_max_bars` | `int` | HTF max bars in base |
| `max_zones_per_tf` | `int` | Max zones per TF per side |
| `max_age_bars` | `int` | Max age bars |
| `consume_reaction_atr_mult` | `float` | Consume reaction ATR mult |
| `invalidate_confirm_bars` | `int` | Invalidate confirm bars |
| `invalidate_pad_atr` | `float` | Invalidate pad ATR mult |
| `flip_on_break` | `bool` | Flip on break + retest |
| `flip_retest_bars` | `int` | Flip retest window (zone TF bars) |
| `show_consumed_history` | `bool` | Show consumed history |

## Zone Engine • LTF
| Переменная | Тип input | Название в UI |
|---|---|---|
| `use_ltf_entry_gate` | `bool` | Use LTF entry gate |
| `ltf_gate_mode` | `string` | LTF gate mode |
| `touch_mode` | `string` | Zone touch mode |
| `ltf_near_atr` | `float` | LTF near ATR mult |
| `ltf_poc_len` | `int` | LTF POC length |
| `ltf_poc_bins` | `int` | LTF POC bins |
| `entry_break_len` | `int` | LTF trigger break lookback |

## Stages
| Переменная | Тип input | Название в UI |
|---|---|---|
| `near_thr_atr` | `float` | Near threshold ATR multiple |
| `use_rr_gate` | `bool` | Use RR gate |
| `rr_min` | `float` | Min RR |
| `entry_plan_mode` | `string` | Entry plan mode |
| `poc_proxy_mode` | `string` | POC proxy mode |
| `trigger_mode` | `string` | Trigger mode |
| `countertrend_enabled` | `bool` | Countertrend filter |
| `countertrend_mode` | `string` | Countertrend action |
| `countertrend_penalty` | `float` | Countertrend score penalty |
| `stop_pad_atr_mult` | `float` | Stop pad ATR mult |
| `stop_pad_pct` | `float` | Stop pad % |
| `stop_mode` | `string` | Stop mode |
| `stopvol_near_pct` | `float` | StopVol near threshold % |
| `rr_fallback_atr` | `float` | RR fallback target ATR |
| `use_ema_bias_confirm` | `bool` | Use EMA_BIAS |
| `use_trap_confirm` | `bool` | Use TRAP |
| `osc_mode` | `string` | Oscillator confirm mode |
| `div_left_bars` | `int` | Divergence pivot left bars |
| `div_right_bars` | `int` | Divergence pivot right bars |
| `div_lookback_bars` | `int` | Divergence lookback bars |

## Confirm • PP
| Переменная | Тип input | Название в UI |
|---|---|---|
| `pp_enabled` | `bool` | Enable PP confirm |
| `pp_type` | `string` | PP type |
| `pp_tf` | `timeframe` | PP timeframe (blank = LTF) |
| `pp_confirm_closes` | `int` | PP confirm closes |
| `pp_retest_window` | `int` | PP retest window |

## Trap
| Переменная | Тип input | Название в UI |
|---|---|---|
| `trap_max_bars` | `int` | Trap max bars |
| `trap_use_volume_gate` | `bool` | Trap return volume gate (zone TF volume) |
| `trap_return_volume_mult` | `float` | Trap return vol <= MA * |

## Stop Volume
| Переменная | Тип input | Название в UI |
|---|---|---|
| `stopvol_enabled` | `bool` | Enable stop-volume origin |
| `stopvol_len` | `int` | Stop-volume compression length |
| `stopvol_exit_confirm` | `int` | Stop-volume breakout confirm bars |
| `stopvol_range_atr_mult` | `float` | Stop-volume range <= ATR * |
| `stopvol_vol_mult` | `float` | Stop-volume vol >= MA * |

## Visual
| Переменная | Тип input | Название в UI |
|---|---|---|
| `show_hud` | `bool` | Show HUD |
| `ui_mode` | `string` | UI mode |
| `render_mode` | `string` | Render mode |
| `show_active_zones_only` | `bool` | Show active zones only |
| `show_labels` | `bool` | Show stage icons |
| `show_rr_lines` | `bool` | Show entry/stop/tp lines |
| `icon_keep` | `int` | Icons keep |
| `zone_extend_bars` | `int` | Zone extend bars |

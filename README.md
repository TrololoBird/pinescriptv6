# Prizrak Trade Setup Detector — v12

Репозиторий переведён на **ветку v12** и очищен от legacy-артефактов v11.

## Основной файл
- `prizrak_trade_setup_detector_v12_0_0.pine` — каноничный Pine-скрипт индикатора.

## Контракт интерфейса
- `contract.lock.json` фиксирует публичный интерфейс (строка `indicator(...)`, `input.*`, `alertcondition(...)`).
- Для локальной проверки в DEV-цикле: `make check-dev`.
- Для релизного контроля: `make check-release`.
- Для обновления lock-файла при намеренном изменении интерфейса: `make contract-init`.

## Документация v12
- `ARCHITECTURE_V12.md` — архитектура и ключевые подсистемы.
- `API_INPUTS_V12.md` — каталог входных параметров.
- `TROUBLESHOOTING_V12.md` — FAQ по диагностике и исправлениям.
- `CHANGELOG.md` — структурированный журнал изменений.
- `release_notes.md` — заметки по релизам.

## Быстрый старт
1. Откройте `prizrak_trade_setup_detector_v12_0_0.pine` в TradingView Pine Editor.
2. Скомпилируйте скрипт и примените к графику.
3. Настройте параметры через группы `TF Hierarchy`, `Zone Engine`, `Stages`, `Visual`.
4. Проверьте алерты по условиям `entry_*`, `near_*`, `zone_*`, `trap_*`.

## Проверки
- `make check-dev`
- `make check-release`
- `make contract-dev`
- `make contract-check`

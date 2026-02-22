# Release notes

## v12.0.0 — Cleanup & Optimization

### Что сделано
- Выполнена очистка репозитория от legacy-файлов v11.
- Документация сфокусирована на v12 (README, архитектура, inputs API, troubleshooting, changelog).
- Контракт интерфейса синхронизирован с каноничным Pine-файлом v12.

### Что важно для пользователей
- Основной файл для работы: `prizrak_trade_setup_detector_v12_0_0.pine`.
- Для DEV-итераций используйте `make check-dev`.
- Перед релизом используйте `make check-release`.

---

## Archive: TradingView Pine Script platform updates

### December 2025
(Историческая секция сохранена как архив внешних платформенных апдейтов.)

#### Updated line wrapping
Scripts now have improved line wrapping behavior. Previously, all multiline text representing a _single line_ of code required indenting each line after the first by any number of spaces that was _not_ a multiple of four, because Pine reserved four-space indentation for local code blocks.

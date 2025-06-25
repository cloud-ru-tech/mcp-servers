# Тесты MCP сервера погоды

Эта папка содержит все тесты для MCP сервера погоды с интеграцией Open-Meteo API.

## Структура тестов

```
test/
├── test_weather_api.py     # Unit тесты с mock (быстрые)
├── test_integration.py     # Интеграционные тесты (с реальным API)
├── test_tools.py          # Демонстрационные тесты
├── run_tests.py           # Скрипт для запуска тестов
├── TESTING.md             # Подробная документация
└── README.md              # Этот файл
```

## Быстрый старт

### Через Makefile (рекомендуется)
```bash
# Установить зависимости
make install

# Запустить основные тесты
make test

# Запустить все тесты с покрытием
make test-cov

# Показать все команды
make help
```

### Через uv напрямую
```bash
# Unit тесты (быстрые)
uv run pytest test/test_weather_api.py -v

# Интеграционные тесты (медленные, требуют интернет)
uv run pytest test/test_integration.py -v -m integration

# Все тесты
uv run pytest test/ -v
```

## Типы тестов

- **Unit тесты** (`test_weather_api.py`) - быстрые с mock, для разработки
- **Интеграционные** (`test_integration.py`) - с реальным API, для проверки
- **Демонстрационные** (`test_tools.py`) - интерактивные, для показа

Подробная документация в файле `TESTING.md`. 
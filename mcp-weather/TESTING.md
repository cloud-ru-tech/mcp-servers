# Тестирование MCP сервера погоды

Этот проект включает комплексные тесты для MCP сервера с интеграцией Open-Meteo API.

## Типы тестов

### 1. Unit тесты (`test_weather_api.py`)
- **Быстрые тесты с mock** - не делают реальных HTTP запросов
- Тестируют функции получения координат и данных о погоде
- Проверяют обработку ошибок и граничные случаи
- **Рекомендуется для CI/CD**

```bash
# Запуск unit тестов
python run_tests.py --type unit
# или
pytest test_weather_api.py -v
```

### 2. Интеграционные тесты (`test_integration.py`)
- **Медленные тесты с реальным API** - делают HTTP запросы к Open-Meteo
- Проверяют работу с реальными данными
- Тестируют производительность
- **Требуют интернет-соединения**

```bash
# Запуск интеграционных тестов
python run_tests.py --type integration
# или
pytest test_integration.py -v -m integration
```

### 3. Демонстрационные тесты (`test_tools.py`)
- **Интерактивные тесты** - показывают результаты в консоли
- Удобно для ручного тестирования
- Работают с реальным API

```bash
# Запуск демо тестов
python run_tests.py --type demo
# или
python test_tools.py
```

## Установка зависимостей

```bash
# Установка зависимостей для тестирования
uv sync --dev
```

## Запуск тестов

### Быстрые тесты (рекомендуется)
```bash
python run_tests.py --type unit
```

### Все тесты с покрытием кода
```bash
python run_tests.py --type all
```

### Только интеграционные тесты
```bash
python run_tests.py --type integration
```

### Исключить медленные тесты
```bash
pytest -m "not slow"
```

## Структура тестов

```
test_weather_api.py         # Unit тесты с mock
├── TestCityCoordinates     # Тесты геокодирования
├── TestWeatherData         # Тесты получения погоды
├── TestWeatherCodeConversion # Тесты конвертации кодов
├── TestRealWeatherData     # Тесты обработки данных
├── TestMCPTools           # Тесты MCP инструментов
├── TestIntegration        # Интеграционные тесты
└── TestEdgeCases          # Тесты граничных случаев

test_integration.py         # Интеграционные тесты
├── TestRealAPIIntegration  # Тесты с реальным API
└── TestPerformance        # Тесты производительности

test_tools.py              # Демонстрационные тесты
```

## Покрытие кода

```bash
# Генерация отчета о покрытии
pytest --cov=server --cov-report=html

# Открыть отчет в браузере
open htmlcov/index.html
```

## Конфигурация pytest

Настройки находятся в `pytest.ini`:
- Маркеры для разных типов тестов
- Автоматический режим для async тестов
- Пути к тестовым файлам

## Примеры тестируемых функций

### Получение координат города
```python
result = await get_city_coordinates("Moscow")
assert result == (55.7558, 37.6176)
```

### Получение данных о погоде
```python
result = await get_weather_data(55.7558, 37.6176, 1)
assert "current" in result
assert "daily" in result
```

### MCP инструменты
```python
result = await get_today_weather("London")
assert "London" in result
assert "°C" in result
assert "Open-Meteo API" in result
```

## Отладка

### Подробный вывод ошибок
```bash
pytest -v --tb=long
```

### Запуск одного теста
```bash
pytest test_weather_api.py::TestCityCoordinates::test_get_city_coordinates_success -v
```

### Запуск тестов в определенном файле
```bash
pytest test_weather_api.py -v
```

## CI/CD рекомендации

Для автоматического тестирования рекомендуется:
1. Запускать только unit тесты в CI
2. Интеграционные тесты - в отдельном job или по расписанию
3. Исключать медленные тесты: `pytest -m "not slow"`

```yaml
# Пример для GitHub Actions
- name: Run tests
  run: |
    pytest test_weather_api.py -v
    # Не запускаем integration тесты в CI
```

## Troubleshooting

### Ошибки сети
- Интеграционные тесты требуют стабильного интернета
- Open-Meteo API может быть временно недоступен
- Используйте unit тесты для проверки логики

### Медленные тесты
- Используйте маркер `@pytest.mark.slow` для медленных тестов
- Исключайте их при быстрой проверке: `pytest -m "not slow"`

### Асинхронные тесты
- Убедитесь что используете `@pytest.mark.asyncio`
- Проверьте что `pytest-asyncio` установлен 
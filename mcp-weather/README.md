# 🌤️ MCP Weather Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0-green.svg)](https://github.com/jlowin/fastmcp)
[![Free API](https://img.shields.io/badge/API-Free-brightgreen.svg)](https://open-meteo.com/)

MCP сервер для получения данных о погоде с использованием Open-Meteo API. **Полностью бесплатно без API ключей!** 🎉

## 🚀 Возможности

- **🌍 Погода сегодня** - актуальная погода для любого города мира
- **📅 Прогноз на неделю** - детальный недельный прогноз
- **🔄 Реальные данные** - Open-Meteo API без необходимости API ключей
- **🌐 Мультиязычность** - поддержка городов с любыми названиями
- **⚡ Быстро и надежно** - FastMCP 2.0 фреймворк

## 📦 Установка

```bash
# Клонируйте репозиторий
cd mcp-weather

# Установите зависимости
uv sync

# Запустите сервер
uv run python server.py
```

## 🛠️ Доступные инструменты

### `get_today_weather(city: str)`
Получает актуальную погоду на сегодня для указанного города.

```python
# Примеры использования
await get_today_weather("Москва")
await get_today_weather("Paris") 
await get_today_weather("New York")
await get_today_weather("東京")
```

### `get_weekly_forecast(city: str)`
Получает прогноз погоды на неделю для указанного города.

```python
# Примеры использования
await get_weekly_forecast("Лондон")
await get_weekly_forecast("Berlin")
await get_weekly_forecast("São Paulo")
```

## 🧪 Тестирование

Проект включает полный набор тестов:

```bash
# Все тесты
make test-all

# Unit тесты (быстрые, с моками)
make test-unit

# Интеграционные тесты (с реальным API)
make test-integration

# Демонстрационные тесты
make test-demo

# Тесты с покрытием кода
make test-cov
```

## 🐳 Docker

```bash
# Сборка и запуск
docker-compose up --build

# Только сборка
docker build -t mcp-weather .

# Запуск контейнера
docker run -p 8001:8001 mcp-weather
```

## 🌐 Endpoints

- **SSE**: `http://localhost:8001/sse`
- **Messages**: `http://localhost:8001/messages/`

## 📊 Покрытие тестами

- **Unit тесты**: 17 тестов
- **Интеграционные тесты**: 7 тестов  
- **Демо тесты**: 6 функций
- **Общее покрытие**: 87%

## 🏗️ Архитектура

- **FastMCP 2.0** - MCP фреймворк
- **httpx** - HTTP клиент
- **Open-Meteo API** - данные о погоде
- **pytest** - тестирование
- **uv** - управление зависимостями

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 🤝 Вклад в проект

Мы приветствуем любые улучшения! 

1. **Fork** проект
2. Создайте **feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit** изменения (`git commit -m 'Add some AmazingFeature'`)
4. **Push** в branch (`git push origin feature/AmazingFeature`)
5. Откройте **Pull Request**

## 🆘 Поддержка

- 📫 **Issues**: [GitHub Issues](https://github.com/your-username/simple_mcp_server/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-username/simple_mcp_server/discussions)

## 🎉 Благодарности

- [FastMCP](https://github.com/jlowin/fastmcp) - отличный MCP фреймворк
- [Open-Meteo](https://open-meteo.com/) - бесплатное API погоды

---

⭐ **Понравился проект? Поставьте звездочку!** ⭐ 
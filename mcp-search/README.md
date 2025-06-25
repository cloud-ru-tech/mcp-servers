# 🔍 MCP Search Server

MCP сервер для поиска в интернете с использованием улучшенного DuckDuckGo поиска.

## 🚀 Новые возможности v2.0

- **🌐 Веб-поиск** - до 50 результатов на запрос с полной информацией
- **📰 Поиск новостей** - до 30 новостей с датами и источниками  
- **🖼️ Поиск изображений** - до 20 изображений с размерами и превью
- **🎥 Поиск видео** - до 20 видео с длительностью и описанием
- **🔧 Новый движок** - пакет `duckduckgo-search` v8.0+
- **🎯 Больше результатов** - в 5 раз больше данных чем раньше
- **⚡ Быстрее и надежнее** - прямые API вызовы без промежуточных API
- **🌍 Региональный поиск** - настройка региона поиска
- **⏰ Фильтры времени** - поиск по дню/неделе/месяцу/году

## 🆕 Что изменилось

### Старая версия (v1.x):
- ❌ Использовала простой DuckDuckGo API
- ❌ Максимум 5-10 результатов
- ❌ Ограниченная информация о результатах
- ❌ Нет настроек региона и времени

### Новая версия (v2.0):
- ✅ Использует продвинутый пакет `duckduckgo-search`
- ✅ До 50 результатов для веб-поиска
- ✅ Полная информация: заголовки, описания, даты, источники
- ✅ Региональные настройки (us-en, ru-ru, wt-wt и др.)
- ✅ Фильтры по времени (день, неделя, месяц, год)
- ✅ Поиск видео с длительностью
- ✅ Изображения с размерами

## 📦 Установка

```bash
# Клонируйте репозиторий
cd mcp-search

# Установите зависимости (включая новый пакет)
uv sync

# Запустите сервер
uv run python server.py
```

## 🛠️ Доступные инструменты

### `search_web(query, max_results=15, region="wt-wt", time_limit=None)`
**Улучшенный веб-поиск** - до 50 результатов с полной информацией.

```python
# Основные примеры
await search_web("Python programming", 20)
await search_web("новости ИИ", 15, "ru-ru")
await search_web("latest AI news", 25, "us-en", "w")  # последняя неделя

# Региональный поиск
await search_web("погода", 10, "ru-ru")  # Россия
await search_web("weather", 10, "us-en")  # США
await search_web("météo", 10, "fr-fr")   # Франция

# По времени
await search_web("Bitcoin news", 15, "wt-wt", "d")  # день
await search_web("SpaceX launch", 10, "us-en", "w") # неделя
await search_web("AI breakthrough", 20, "wt-wt", "m") # месяц
```

### `search_news(query, max_results=15, region="wt-wt", time_limit="w")`
**Улучшенный поиск новостей** - до 30 новостей с датами и источниками.

```python
# Новости с датами и источниками
await search_news("технологии", 20, "ru-ru", "d")
await search_news("AI breakthrough", 15, "us-en", "w")
await search_news("climate change", 25, "wt-wt", "m")
```

### `search_images(query, max_results=10, region="wt-wt")`
**Улучшенный поиск изображений** - до 20 изображений с размерами.

```python
# Изображения с размерами и превью
await search_images("beautiful landscapes", 15)
await search_images("Python logo", 10, "us-en")
await search_images("архитектура Москвы", 20, "ru-ru")
```

### `search_videos(query, max_results=10, region="wt-wt", time_limit=None)`
**🆕 НОВЫЙ! Поиск видео** - до 20 видео с длительностью и описанием.

```python
# Видео с длительностью и каналами
await search_videos("Python tutorial", 15)
await search_videos("cooking recipes", 10, "us-en", "w")
await search_videos("музыка", 20, "ru-ru", "m")
```

## 🌍 Поддерживаемые регионы

```python
# Популярные регионы
"wt-wt"  # Мир (по умолчанию)
"us-en"  # США
"ru-ru"  # Россия  
"uk-en"  # Великобритания
"de-de"  # Германия
"fr-fr"  # Франция
"jp-jp"  # Япония
"cn-zh"  # Китай
"in-en"  # Индия
```

## ⏰ Фильтры времени

```python
# Временные фильтры
"d"  # День
"w"  # Неделя  
"m"  # Месяц
"y"  # Год
None # Все время
```

## 📦 Новые зависимости

```toml
[project]
dependencies = [
    "duckduckgo-search>=8.0.0",  # 🆕 Новый мощный пакет
    "fastmcp>=0.2.0",
    "httpx>=0.27.0",
    # ... остальные
]
```

## 🧪 Тестирование

```bash
# Тест новых возможностей
make test-all

# Демо с новыми функциями
make test-demo
```

## 📊 Новые ограничения и возможности

| Функция | Старая версия | Новая версия |
|---------|---------------|--------------|
| Веб-поиск | 1-10 результатов | 1-50 результатов |
| Новости | 1-10 результатов | 1-30 результатов |
| Изображения | Только ссылки | 1-20 с размерами |
| Видео | ❌ Не поддерживалось | ✅ 1-20 с длительностью |
| Регионы | ❌ Без настройки | ✅ 40+ регионов |
| Время | ❌ Все время | ✅ День/неделя/месяц/год |
| Информация | Минимум | Максимум |

## 🔧 Сравнение результатов

### Пример запроса: `search_web("Python tutorial", 5)`

**Старая версия:**
```
🌐 Веб-поиск по запросу "Python tutorial"
📊 Найдено результатов: 2
📑 1. Python Tutorial
🔗 https://example.com
📝 Basic Python info
```

**Новая версия:**
```
🌐 Веб-поиск по запросу "Python tutorial"
📊 Найдено результатов: 5
🕒 Время поиска: 2024-12-26 14:30:15
🔧 Используется: duckduckgo-search v8.0+

📑 1. Python Tutorial - Complete Guide for Beginners
🔗 https://docs.python.org/3/tutorial/
📝 The Python Tutorial — Python 3.12.0 documentation. Python is an easy to learn, powerful programming language...
──────────────────────────────────────────────────────

📑 2. Learn Python Programming - Comprehensive Tutorial
🔗 https://www.programiz.com/python-programming
📝 Learn Python programming with our comprehensive tutorial. From basics to advanced concepts...
──────────────────────────────────────────────────────

[... еще 3 подробных результата]
```

## 🌍 Поддерживаемые языки

- 🇷🇺 Русский: "поиск информации о Python"
- 🇺🇸 English: "Python programming tutorial"
- 🇫🇷 Français: "programmation Python"
- 🇩🇪 Deutsch: "Python Programmierung"
- 🇯🇵 日本語: "Python プログラミング"
- 🇨🇳 中文: "Python 编程"
- И многие другие!

## 🐳 Docker

```bash
# Собрать образ
make docker-build

# Запустить в контейнере
make docker-run

# Или с docker-compose
docker-compose up -d
```

## 📊 Ограничения

- **Веб-поиск**: 1-50 результатов
- **Поиск новостей**: 1-30 результатов  
- **Поиск изображений**: 1-20 результатов
- **Поиск видео**: 1-20 результатов
- **Запросы**: любые символы и языки
- **API лимиты**: без ограничений (DuckDuckGo)

## 🔧 Конфигурация

Сервер запускается на порту **8002**:
- SSE endpoint: `http://localhost:8002/sse`
- Messages endpoint: `http://localhost:8002/messages/`

## 🛡️ Безопасность

- ✅ Без сохранения истории поиска
- ✅ Без передачи персональных данных
- ✅ Использует публичный DuckDuckGo API
- ✅ Валидация входных параметров
- ✅ Обработка ошибок и таймаутов

## 📈 Производительность

- **Таймаут запросов**: 30 секунд
- **Параллельные запросы**: поддерживаются
- **Кеширование**: нет (всегда актуальные данные)
- **Ограничение скорости**: естественное через DuckDuckGo

## 🔗 API Источники

- **DuckDuckGo Instant Answer API**: `https://api.duckduckgo.com/`
- **Без регистрации и ключей**
- **Бесплатное использование**
- **Поддержка международных запросов**

## 🛠️ Технологии

- **FastMCP 2.0** - MCP фреймворк
- **Python 3.13** - язык программирования
- **httpx** - HTTP клиент
- **uvicorn** - ASGI сервер
- **pytest** - тестирование
- **Docker** - контейнеризация
- **uv** - управление зависимостями

## 📚 Примеры использования

### Простой поиск
```python
result = await search_web("FastMCP tutorial", 5)
print(result)
```

### Многоязычный поиск
```python
# Русский
result = await search_web("как создать MCP сервер", 3)

# Английский  
result = await search_web("how to create MCP server", 3)

# Французский
result = await search_web("comment créer serveur MCP", 3)
```

### Поиск новостей
```python
news = await search_news("artificial intelligence breakthrough", 5)
print(news)
```

### Обработка ошибок
```python
try:
    result = await search_web("", 5)  # Пустой запрос
except McpError as e:
    print(f"Ошибка: {e.message}")
```

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📝 Лицензия

MIT License - смотрите файл LICENSE для деталей.

## 🆘 Поддержка

- 📧 Email: support@example.com
- 🐛 Issues: GitHub Issues
- 📖 Docs: README.md
- 💬 Discussions: GitHub Discussions

---

🔍 **MCP Search Server** - мощный инструмент для поиска в интернете без ограничений! 
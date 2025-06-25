# 📚 MCP Wikipedia Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0-green.svg)](https://github.com/jlowin/fastmcp)
[![Free API](https://img.shields.io/badge/API-Free-brightgreen.svg)](https://wikipedia.org/)

🔍 MCP сервер для поиска и получения информации из Wikipedia. **Полностью бесплатно!** 🎉

## Особенности

- 🌐 **Многоязычный поиск**: поддержка русского, английского, немецкого, французского и испанского языков
- 📖 **Пять типов запросов**:
  - Поиск статей по ключевым словам
  - Получение краткого содержания статьи
  - Получение полного текста статьи
  - Получение структуры разделов статьи
  - Получение ссылок из статьи
- ⚡ **Быстрый и эффективный**: использует официальный Wikipedia API
- 🐳 **Docker support**: готовые образы для легкого развертывания
- 🧪 **Полное тестирование**: unit и интеграционные тесты

## Установка

### С помощью uv (рекомендуется)

```bash
# Клонировать репозиторий
git clone <repository-url>
cd mcp-wikipedia

# Установить зависимости
make install

# Запустить сервер
make run-server
```

### С помощью Docker

```bash
# Собрать и запустить
make docker-build
make docker-run

# Или использовать docker-compose
docker-compose up -d
```

## Использование

### Доступные инструменты

#### 1. `search_wikipedia`
Поиск статей в Wikipedia по ключевым словам.

**Параметры:**
- `query` (str): поисковый запрос
- `limit` (int, optional): количество результатов (по умолчанию 10, максимум 50)
- `language` (str, optional): язык поиска (ru, en, de, fr, es)

**Пример:**
```python
# Поиск на русском языке
await search_wikipedia("искусственный интеллект", limit=5, language="ru")

# Поиск на английском языке
await search_wikipedia("artificial intelligence", limit=10, language="en")
```

#### 2. `get_wikipedia_summary`
Получение краткого содержания статьи.

**Параметры:**
- `title` (str): точное название статьи
- `language` (str, optional): язык статьи (ru, en, de, fr, es)

**Пример:**
```python
await get_wikipedia_summary("Искусственный интеллект", language="ru")
```

#### 3. `get_wikipedia_content`
Получение полного содержания статьи без ограничений по размеру.

**Параметры:**
- `title` (str): точное название статьи
- `language` (str, optional): язык статьи (ru, en, de, fr, es)

**Примечание:** Возвращает полный текст статьи, который может быть очень большим для некоторых статей.

**Пример:**
```python
await get_wikipedia_content("Искусственный интеллект", language="ru")
```

#### 4. `get_wikipedia_sections`
Получение структуры разделов статьи Wikipedia.

**Параметры:**
- `title` (str): точное название статьи
- `language` (str, optional): язык статьи (ru, en, de, fr, es)

**Пример:**
```python
await get_wikipedia_sections("Искусственный интеллект", language="ru")
```

#### 5. `get_wikipedia_links`
Получение всех ссылок из статьи Wikipedia на другие статьи.

**Параметры:**
- `title` (str): точное название статьи
- `language` (str, optional): язык статьи (ru, en, de, fr, es)

**Примечание:** Возвращает первые 20 ссылок из статьи для удобства чтения.

**Пример:**
```python
await get_wikipedia_links("Искусственный интеллект", language="ru")
```

### Поддерживаемые языки

- 🇷🇺 `ru` - русский
- 🇺🇸 `en` - английский
- 🇩🇪 `de` - немецкий
- 🇫🇷 `fr` - французский
- 🇪🇸 `es` - испанский

## Разработка

### Команды Makefile

```bash
make help           # Показать все доступные команды
make install        # Установить зависимости
make test          # Запустить быстрые тесты
make test-all      # Запустить все тесты
make test-cov      # Тесты с покрытием кода
make lint          # Проверить код линтером
make format        # Отформатировать код
make run-server    # Запустить сервер локально
make docker-build  # Собрать Docker образ
make clean         # Очистить временные файлы
```

### Структура проекта

```
mcp-wikipedia/
├── server.py              # Основной файл сервера
├── pyproject.toml         # Конфигурация зависимостей
├── Makefile              # Команды для разработки
├── Dockerfile            # Docker образ
├── docker-compose.yml    # Docker Compose конфигурация
├── pytest.ini           # Конфигурация тестов
├── README.md            # Документация
└── test/               # Тесты
    ├── __init__.py
    ├── test_wikipedia_api.py
    ├── test_integration.py
    └── test_tools.py
```

## Конфигурация

### Переменные окружения

- `WIKIPEDIA_TIMEOUT` - таймаут запросов к API (по умолчанию 10 секунд)
- `WIKIPEDIA_USER_AGENT` - User-Agent для запросов

### Настройки сервера

Сервер по умолчанию запускается на порту `8003`. Для изменения порта:

```bash
# Через аргументы командной строки
python server.py --port 8080

# Или через переменную окружения
PORT=8080 python server.py
```

## API Endpoints

- `GET/POST /sse` - Server-Sent Events endpoint для MCP клиентов
- Health check доступен на том же порту

## Тестирование

### Unit тесты
```bash
make test-unit
```

### Интеграционные тесты
```bash
make test-integration
```

### Все тесты с покрытием
```bash
make test-cov
```

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
- [Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page) - бесплатное API для доступа к Wikipedia

---

⭐ **Понравился проект? Поставьте звездочку!** ⭐ 
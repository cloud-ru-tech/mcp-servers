# MCP Yandex Search Server

MCP сервер для поиска в интернете через Yandex Search API на базе FastMCP с SSE протоколом.

## Возможности

- 🔍 Поиск в интернете через официальный Yandex Search API
- 📊 Структурированные результаты с заголовками, URL и описанием
- 💾 Поддержка сохраненных копий страниц
- 🌐 SSE (Server-Sent Events) протокол для реального времени
- 🐳 Docker поддержка

## Требования

- Python 3.13+
- Yandex Cloud API ключ
- Yandex Cloud Folder ID

## Установка

### Локальная установка

```bash
# Клонирование репозитория
git clone <repository-url>
cd mcp-yandex-search

# Установка зависимостей
make install

# Или для разработки
make dev
```

### Docker установка

```bash
# Сборка образа
make docker-build

# Запуск контейнера
make docker-run
```

## Настройка

Создайте файл `.env` или установите переменные окружения:

```bash
export YANDEX_API_KEY="your-yandex-api-key"
export YANDEX_FOLDER_ID="your-folder-id"
```

### Получение API ключа Yandex Cloud

1. Перейдите в [Yandex Cloud Console](https://console.cloud.yandex.ru/)
2. Создайте сервисный аккаунт
3. Назначьте роль `search-api.executor`
4. Создайте API ключ
5. Скопируйте ID папки из консоли

## Запуск

### Локальный запуск

```bash
make run
```

### Разработка с автоперезагрузкой

```bash
make dev-run
```

### Docker запуск

```bash
make docker-run
```

Сервер будет доступен по адресу:
- HTTP: `http://localhost:8003`
- SSE: `http://localhost:8003/sse`
- Messages: `http://localhost:8003/messages/`

## Использование

### Доступные инструменты

#### `search_web`

Поиск в интернете через Yandex Search API.

**Параметры:**
- `query` (string, обязательный): Поисковый запрос
- `page_size` (int, опциональный): Количество результатов на странице (по умолчанию 10, макс 50)
- `page_number` (int, опциональный): Номер страницы, начиная с 0 (по умолчанию 0)

**Пример:**
```json
{
  "name": "search_web",
  "arguments": {
    "query": "FastMCP tutorial",
    "page_size": 5,
    "page_number": 0
  }
}
```

### Интеграция с MCP клиентом

```python
import asyncio
from mcp.client import MCPClient

async def main():
    client = MCPClient("http://localhost:8003")
    
    # Поиск в интернете
    result = await client.call_tool("search_web", {
        "query": "Python MCP server",
        "page_size": 10
    })
    
    print(result)

asyncio.run(main())
```

## Разработка

### Структура проекта

```
mcp-yandex-search/
├── server.py              # Основной сервер
├── pyproject.toml         # Конфигурация проекта
├── Dockerfile            # Docker образ
├── docker-compose.yml    # Docker Compose
├── Makefile             # Задачи разработки
├── README.md            # Документация
└── test/                # Тесты
    ├── __init__.py
    ├── test_yandex_api.py
    ├── test_tools.py
    └── test_integration.py
```

### Команды разработки

```bash
# Установка зависимостей для разработки
make dev

# Запуск тестов
make test

# Проверка кода
make lint

# Форматирование кода
make format

# Очистка проекта
make clean
```

## Тестирование

```bash
# Запуск всех тестов
make test

# Запуск конкретного теста
pytest test/test_yandex_api.py -v

# Запуск с покрытием
pytest test/ --cov=. --cov-report=html
```

## Архитектура

### Основные компоненты

1. **YandexSearchAPI** - Клиент для работы с Yandex Search API
2. **YandexSearchParser** - Парсер XML ответов от API
3. **FastMCP Server** - MCP сервер с SSE транспортом
4. **Starlette App** - Web приложение для обработки HTTP запросов

### Поток обработки запроса

```
Client Request → SSE Transport → MCP Server → YandexSearchAPI → Yandex Cloud API
                                                     ↓
Client Response ← SSE Transport ← MCP Server ← YandexSearchParser ← XML Response
```

## Мониторинг

### Логирование

Сервер записывает логи в:
- Стандартный вывод (stdout)
- Файл `logs/server.log` (при использовании Docker)

### Проверка здоровья

```bash
# Проверка статуса сервера
curl -f http://localhost:8003/sse

# Проверка через Docker
docker-compose ps
```

## Устранение неполадок

### Распространенные проблемы

1. **"Missing YANDEX_API_KEY"**
   - Убедитесь, что установлена переменная окружения
   - Проверьте правильность API ключа

2. **"Yandex Search API error: 403"**
   - Проверьте права доступа сервисного аккаунта
   - Убедитесь, что назначена роль `search-api.executor`

3. **"Failed to parse XML response"**
   - API может вернуть некорректный XML
   - Проверьте логи для диагностики

### Отладка

```bash
# Включение подробного логирования
DEBUG=1 python server.py

# Проверка сетевых запросов
HTTPX_LOG_LEVEL=DEBUG python server.py
```

## Лицензия

MIT License

## Поддержка

Для вопросов и предложений создайте issue в репозитории проекта. 
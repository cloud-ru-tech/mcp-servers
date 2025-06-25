# 📥 MCP Fetch Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0-green.svg)](https://github.com/jlowin/fastmcp)
[![Free](https://img.shields.io/badge/Free-100%25-brightgreen.svg)]()

**Сервер для получения текстового содержимого веб-страниц через Model Context Protocol (MCP). Полностью бесплатно!** 🎉

## 🎯 Описание

MCP Fetch сервер предоставляет инструмент для получения текстового содержимого веб-страниц без HTML/CSS/JS элементов. Сервер извлекает только основное содержание страницы, очищая его от разметки и стилей.

## 🚀 Особенности

- **Один инструмент** `fetch_page` для получения контента страниц
- **Умное извлечение текста** с помощью BeautifulSoup4
- **Автоматическая очистка** от HTML/CSS/JS элементов
- **Поддержка редиректов** и различных кодировок
- **Настраиваемый таймаут** для запросов
- **Имитация браузера** для обхода простых блокировок
- **Валидация URL** и обработка ошибок

## 📋 Инструменты

### `fetch_page`
Получает содержимое веб-страницы и возвращает только текст без HTML/CSS/JS.

**Параметры:**
- `url` (string): URL страницы для получения (с протоколом http:// или https://)
- `timeout` (int, optional): Таймаут запроса в секундах (по умолчанию 30, максимум 120)

**Возвращает:**
- Текстовое содержимое страницы с информацией о URL, статусе, размере и кодировке

## 🛠 Установка и запуск

### Локальный запуск

1. **Установка зависимостей:**
```bash
make install
```

2. **Запуск сервера:**
```bash
make run-server
```

Сервер будет доступен по адресу: `http://localhost:8002/sse`

### Docker

1. **Сборка образа:**
```bash
make docker-build
```

2. **Запуск контейнера:**
```bash
make docker-run
```

### Docker Compose

```bash
docker-compose up -d
```

## 🧪 Тестирование

- **Быстрые тесты:** `make test`
- **Все тесты:** `make test-all`
- **Тесты с покрытием:** `make test-cov`
- **Интеграционные тесты:** `make test-integration`

## 📖 Примеры использования

```python
# Получение содержимого страницы
result = await fetch_page("https://example.com")

# С настройкой таймаута
result = await fetch_page("https://example.com", timeout=60)
```

## 🔧 Конфигурация

- **Порт:** 8002
- **Таймаут по умолчанию:** 30 секунд
- **Максимальный таймаут:** 120 секунд
- **Максимальное количество редиректов:** 10

## 📝 Архитектура

Сервер построен на:
- **FastMCP** - фреймворк для MCP серверов
- **httpx** - HTTP клиент для получения страниц
- **BeautifulSoup4** - парсинг HTML и извлечение текста
- **Starlette** - ASGI веб-фреймворк
- **uvicorn** - ASGI сервер

## 🔍 Обработка ошибок

Сервер обрабатывает следующие типы ошибок:
- Некорректные URL
- Таймауты запросов
- HTTP ошибки (404, 500, etc.)
- Ошибки парсинга HTML
- Проблемы с кодировкой

## 🌟 Возможности

- Автоматическое определение основного контента страницы
- Поиск в элементах `<main>`, `<article>`, или областях с классами `content`/`main`
- Удаление нежелательных элементов (`<script>`, `<style>`, `<nav>`, etc.)
- Извлечение заголовка страницы
- Очистка от лишних пробелов и переносов строк

## 🤝 Совместимость

- **Python:** 3.13+
- **MCP:** Model Context Protocol
- **Клиенты:** Claude Desktop, OpenAI API, и другие MCP-совместимые клиенты

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
- [Model Context Protocol](https://github.com/modelcontextprotocol/protocol) - спецификация MCP
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML парсинг

---

⭐ **Понравился проект? Поставьте звездочку!** ⭐ 
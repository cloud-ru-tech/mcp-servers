# 🔧 Simple MCP Server Collection

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0-green.svg)](https://github.com/jlowin/fastmcp)

Коллекция простых и мощных MCP (Model Context Protocol) серверов для различных задач. **Большинство серверов работают полностью бесплатно без API ключей!** 🎉

## 🎯 Доступные серверы

| Сервер | Порт | Описание | API | Статус |
|--------|------|----------|-----|--------|
| 🌤️ [**Weather**](./mcp-weather/) | 8001 | Погода и прогнозы | Open-Meteo | 🆓 Бесплатно |
| 🔍 [**Search**](./mcp-search/) | 8002 | Веб-поиск, новости, изображения | DuckDuckGo | 🆓 Бесплатно |
| 🌐 [**IP Info**](./mcp-ip/) | 8003 | Информация об IP-адресах | Бесплатные API | 🆓 Бесплатно |
| 🏛️ [**Artifact Registry**](./mcp-artifact-registry/) | 8004 | Cloud.ru реестр артефактов | Cloud.ru | 🔑 Требует ключи |
| 🥊 [**UFC**](./mcp-ufc/) | 8005 | UFC и MMA информация | UFC API | 🆓 Бесплатно |
| 📚 [**Wikipedia**](./mcp-wikipedia/) | 8006 | Поиск в Wikipedia | Wikipedia API | 🆓 Бесплатно |
| 🔍 [**Yandex Search**](./mcp-yandex-search/) | 8007 | Поиск Yandex | Yandex API | 🔑 Требует ключи |
| 📥 [**Fetch**](./mcp-fetch/) | 8008 | HTTP запросы и загрузка | - | 🆓 Бесплатно |

## ⚡ Быстрый старт

### Установка и запуск всех бесплатных серверов:

```bash
# Клонируйте репозиторий
git clone https://github.com/your-username/simple_mcp_server.git
cd simple_mcp_server

# Запустите все бесплатные серверы одной командой
make start-all

# Проверьте статус
make ports
```

### Отдельный запуск сервера:

```bash
# Например, Weather сервер
cd mcp-weather
uv sync
uv run python server.py
```

### Docker запуск:

```bash
# Запуск конкретного сервера
make weather-run-build

# Или используйте docker-compose в папке сервера
cd mcp-weather
docker-compose up -d
```

## 🌤️ Weather Server - Погода

**Возможности:**
- 🌍 Актуальная погода для любого города мира
- 📅 Прогноз погоды на неделю
- 🔄 Реальные данные без API ключей (Open-Meteo)
- 🌐 Поддержка международных названий городов

```bash
cd mcp-weather && uv run python server.py
# Доступен на http://localhost:8001
```

## 🔍 Search Server - Веб-поиск

**Возможности:**
- 🌐 Веб-поиск (до 50 результатов)
- 📰 Поиск новостей с датами
- 🖼️ Поиск изображений с размерами
- 🎥 Поиск видео с длительностью
- 🌍 Региональные настройки
- ⏰ Фильтры по времени

```bash
cd mcp-search && uv run python server.py
# Доступен на http://localhost:8002
```

## 🌐 IP Server - IP информация

**Возможности:**
- 🌍 Геолокация IP-адресов
- 🎯 Детальная информация (провайдер, часовой пояс)
- 🤖 Автоопределение IP пользователя
- 🔄 Поддержка IPv4 и IPv6
- 🛡️ Автоматический fallback между API

```bash
cd mcp-ip && uv run python server.py
# Доступен на http://localhost:8003
```

## 📚 Wikipedia Server - Поиск в Wikipedia

**Возможности:**
- 🔍 Поиск статей по ключевым словам
- 📖 Краткое и полное содержание статей
- 🏗️ Структура разделов статьи
- 🔗 Извлечение ссылок из статей
- 🌐 Поддержка 5 языков (ru, en, de, fr, es)

```bash
cd mcp-wikipedia && uv run python server.py
# Доступен на http://localhost:8006
```

## 🥊 UFC Server - UFC & MMA

**Возможности:**
- 🥊 Информация о бойцах и статистика
- 📅 Расписание турниров
- 🏆 Официальные рейтинги
- 📊 Результаты боев
- 👑 История чемпионских боев

```bash
cd mcp-ufc && uv run python server.py
# Доступен на http://localhost:8005
```

## 🏛️ Artifact Registry Server - Cloud.ru

**Возможности:**
- 📦 Управление реестрами Docker/Debian/RPM
- ⚙️ Мониторинг операций
- 🛡️ Управление безопасностью
- 🔍 Детальная информация о реестрах

**Требует настройки:**
```bash
export CLOUD_RU_KEY_ID="your_key_id_here"
export CLOUD_RU_SECRET="your_secret_here"
cd mcp-artifact-registry && uv run python server.py
```

## 🔍 Yandex Search Server

**Возможности:**
- 🌐 Поиск через Yandex Search API
- 📊 Структурированные результаты
- 🔧 Гибкие настройки поиска

**Требует API ключ Yandex**

## 📥 Fetch Server - HTTP клиент

**Возможности:**
- 🌐 HTTP GET/POST запросы
- 📥 Загрузка файлов и контента
- 🔧 Настраиваемые заголовки
- ⚡ Асинхронные запросы

```bash
cd mcp-fetch && uv run python server.py
# Доступен на http://localhost:8008
```

## 🛠️ Технологии

- **FastMCP 2.0** - MCP фреймворк для Python
- **Python 3.11+** - современная версия Python
- **uv** - быстрое управление зависимостями
- **pytest** - комплексное тестирование
- **Docker** - контейнеризация
- **httpx** - асинхронный HTTP клиент

## 📊 Статистика проекта

- **8 серверов** в коллекции
- **6 бесплатных** серверов (не требуют API ключей)
- **35+ инструментов** доступно
- **120+ тестов** с полным покрытием
- **Docker support** для всех серверов
- **Makefile** команды для удобства

## 🐳 Docker команды

```bash
# Управление всеми сервисами
make start-all      # Запустить все бесплатные серверы
make stop-all       # Остановить все серверы
make ports          # Показать используемые порты
make list-services  # Список всех сервисов

# Команды для отдельных серверов
make weather-run-build    # Weather сервер
make search-run-build     # Search сервер
make ip-run-build         # IP сервер
make ufc-run-build        # UFC сервер
make wikipedia-run-build  # Wikipedia сервер
# ... и т.д.
```

## 🧪 Тестирование

Каждый сервер включает полный набор тестов:

```bash
# Тестирование конкретного сервера
cd mcp-weather
make test-all       # Все тесты
make test-unit      # Unit тесты
make test-integration # Интеграционные тесты
make test-cov       # Тесты с покрытием

# Демонстрационные тесты
make test-demo      # Показать работу всех функций
```

## 📁 Структура проекта

```
simple_mcp_server/
├── LICENSE                    # MIT лицензия
├── README.md                  # Этот файл
├── Makefile                   # Команды управления
├── mcp-weather/              # 🌤️ Weather сервер
├── mcp-search/               # 🔍 Search сервер
├── mcp-ip/                   # 🌐 IP информация
├── mcp-artifact-registry/    # 🏛️ Cloud.ru Artifact Registry
├── mcp-ufc/                  # 🥊 UFC информация
├── mcp-wikipedia/            # 📚 Wikipedia поиск
├── mcp-yandex-search/        # 🔍 Yandex поиск
└── mcp-fetch/                # 📥 HTTP клиент
```

Каждая папка содержит:
- `server.py` - основной сервер
- `README.md` - детальная документация
- `pyproject.toml` - зависимости
- `Dockerfile` - Docker конфигурация
- `test/` - тесты
- `Makefile` - команды разработки



## 🤝 Вклад в проект

Мы приветствуем любые улучшения! 

1. **Fork** проект
2. Создайте **feature branch** (`git checkout -b feature/AmazingFeature`)  
3. **Commit** изменения (`git commit -m 'Add some AmazingFeature'`)
4. **Push** в branch (`git push origin feature/AmazingFeature`)
5. Откройте **Pull Request**

### Идеи для вклада:
- 🆕 Новые MCP серверы
- 🐛 Исправление багов
- 📚 Улучшение документации
- 🧪 Добавление тестов
- 🌐 Локализация
- ⚡ Оптимизация производительности

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.



## 🎉 Благодарности

- [FastMCP](https://github.com/jlowin/fastmcp) - отличный MCP фреймворк
- [Open-Meteo](https://open-meteo.com/) - бесплатное API погоды
- [DuckDuckGo](https://duckduckgo.com/) - приватный поиск
- Все контрибьюторы проекта!

---

⭐ **Понравился проект? Поставьте звездочку!** ⭐ 
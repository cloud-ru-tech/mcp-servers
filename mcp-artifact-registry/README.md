# 🏛️ MCP Artifact Registry Server

**MCP сервер для работы с Cloud.ru Artifact Registry** - полнофункциональный инструмент для управления реестрами артефактов через Model Context Protocol.

## 🚀 Возможности

### 📦 Управление реестрами
- **Просмотр реестров** - получение списка всех реестров в проекте с подробной информацией
- **Создание реестров** - создание новых реестров Docker, Debian, RPM
- **Получение информации** - детальная информация о конкретном реестре
- **Удаление реестров** - безопасное удаление реестров

### ⚙️ Мониторинг операций
- **Отслеживание операций** - просмотр всех операций с возможностью фильтрации
- **Статус операций** - получение подробного статуса любой операции
- **Операции реестров** - история операций для конкретных реестров

### 🛡️ Управление безопасностью
- **Режимы карантина** - настройка уровней безопасности (DISABLED, LOW, MEDIUM, HIGH, CRITICAL)
- **Управление доступом** - настройка публичности реестров
- **Автоматическая авторизация** - встроенная работа с Cloud.ru IAM API

## 🔧 Установка и настройка

### Предварительные требования

1. **Python 3.13+**
2. **Ключи доступа Cloud.ru** - получите их в [личном кабинете Cloud.ru](https://cloud.ru)
3. **ID проекта** - UUID вашего проекта в Cloud.ru
4. **Docker** (опционально) - для контейнеризации

### 🚀 Быстрый старт

#### Локальная установка

```bash
# Клонируйте репозиторий
git clone <repository_url>
cd simple_mcp_server/mcp-artifact-registry

# Установите зависимости
make install

# Настройте переменные окружения
export CLOUD_RU_KEY_ID="your_key_id_here"
export CLOUD_RU_SECRET="your_secret_here"
export CLOUD_RU_PROJECT_ID="your_project_id_here"

# Запустите сервер
make run-server
```

#### Docker (рекомендуется)

```bash
# Установите переменные окружения
export CLOUD_RU_KEY_ID="your_key_id_here"
export CLOUD_RU_SECRET="your_secret_here"
export CLOUD_RU_PROJECT_ID="your_project_id_here"

# Запуск через Docker Compose
make compose-up

# Или обычный Docker
make docker-run-build
```

📖 **Подробное руководство по Docker**: См. [DOCKER.md](./DOCKER.md)

## 🔑 Аутентификация и конфигурация

### Получение ключей доступа Cloud.ru

Выберите один из способов:

1. **Персональный ключ доступа**:
   - Войдите в [личный кабинет Cloud.ru](https://cloud.ru)
   - Перейдите в раздел "API ключи"
   - Создайте новый персональный ключ

2. **Сервисный аккаунт**:
   - Создайте сервисный аккаунт в проекте
   - Сгенерируйте ключи доступа для аккаунта

### Настройка переменных окружения

```bash
# Обязательные переменные
export CLOUD_RU_KEY_ID="your_key_id"
export CLOUD_RU_SECRET="your_secret" 
export CLOUD_RU_PROJECT_ID="your_project_uuid"
```

#### Файл .env (альтернативный способ)

Создайте файл `.env` в корне проекта:

```bash
CLOUD_RU_KEY_ID=your_key_id_here
CLOUD_RU_SECRET=your_secret_here
CLOUD_RU_PROJECT_ID=your_project_id_here
```

### Проверка конфигурации

```bash
# Проверить переменные окружения
make env-check

# Показать пример конфигурации
make env-example
```

## 🛠️ Доступные MCP инструменты

Сервер предоставляет 8 инструментов для работы с Artifact Registry:

### 1. `list_registries`
Получение списка реестров в проекте

**Параметры:**
- `page_size` (опциональный) - размер страницы
- `page_token` (опциональный) - токен для пагинации

**Пример использования:**
```python
result = await list_registries(page_size=20)
```

### 2. `get_registry`
Получение детальной информации о реестре

**Параметры:**
- `registry_id` (обязательный) - UUID реестра

### 3. `create_registry`
Создание нового реестра

**Параметры:**
- `name` (обязательный) - название реестра
- `registry_type` (опциональный) - тип: DOCKER, DEBIAN, RPM (по умолчанию DOCKER)
- `is_public` (опциональный) - публичный доступ (по умолчанию false)

### 4. `delete_registry`
Удаление реестра

**Параметры:**
- `registry_id` (обязательный) - UUID реестра

⚠️ **ВНИМАНИЕ:** Удаление необратимо!

### 5. `list_operations`
Получение списка операций

**Параметры:**
- `resource_id` (опциональный) - фильтр по ID ресурса
- `resource_name` (опциональный) - фильтр по имени ресурса
- `page_size` (опциональный) - размер страницы
- `page_token` (опциональный) - токен пагинации

### 6. `get_operation`
Получение информации об операции

**Параметры:**
- `operation_id` (обязательный) - UUID операции

### 7. `update_quarantine_mode`
Изменение уровня карантина реестра

**Параметры:**
- `registry_id` (обязательный) - UUID реестра
- `quarantine_mode` (обязательный) - режим: DISABLED, LOW, MEDIUM, HIGH, CRITICAL

### 8. `get_registry_operations`
Получение операций для конкретного реестра

**Параметры:**
- `registry_id` (обязательный) - UUID реестра
- `page_size` (опциональный) - размер страницы
- `page_token` (опциональный) - токен пагинации

## 🌐 API Endpoints

После запуска сервер доступен на следующих endpoints:

- **SSE (Server-Sent Events)**: `http://localhost:8004/sse`
- **Health Check**: Встроенная проверка работоспособности

## 🧪 Тестирование и разработка

### Unit тесты
```bash
make test-unit
```

### Интеграционные тесты
```bash
# Требуют реальные ключи доступа
export CLOUD_RU_KEY_ID="your_key_id"
export CLOUD_RU_SECRET="your_secret"
export CLOUD_RU_PROJECT_ID="your_project_id"

make test-integration
```

### Демонстрация API
```bash
# Запуск примера использования
python example.py
```

### Все тесты
```bash
make test
```

### Покрытие кода
```bash
make test-cov
```

## 🔍 Мониторинг и отладка

### Проверка работоспособности
```bash
# Проверка статуса сервера
make health

# Статус Docker контейнеров
make status

# Логи приложения
make compose-logs  # для Docker Compose
make docker-logs   # для Docker
```

### Форматирование и линтинг
```bash
make format  # Автоформатирование кода
make lint    # Проверка стиля кода
make check   # Полная проверка (lint + tests)
```

## 🛡️ Безопасность

### Авторизация
- Автоматическое получение и обновление токенов
- Безопасное хранение ключей в переменных окружения
- Обработка ошибок авторизации

### Docker Security
- Non-root пользователь в контейнере
- Изолированная сеть
- Minimal base image (Python slim)

## 📈 Производительность

### Оптимизации
- Переиспользование HTTP соединений
- Автоматическое обновление токенов
- Эффективная обработка пагинации
- Graceful shutdown

### Масштабирование
```bash
# Horizontal scaling с Docker Compose
docker-compose up -d --scale mcp-artifact-registry=3
```

## 🐳 Docker деплоймент

### Быстрый старт
```bash
# Проверка переменных
make env-check

# Запуск
make compose-up

# Мониторинг
make compose-ps
make compose-logs
```

### Команды управления
```bash
make compose-down       # Остановка
make compose-restart    # Перезапуск  
make compose-build      # Пересборка
make docker-clean       # Очистка ресурсов
```

См. [DOCKER.md](./DOCKER.md) для подробных инструкций.

## 📚 Примеры использования

### Базовый пример

Запустите `python example.py` для демонстрации всех возможностей API.

### Интеграция с MCP клиентами

Сервер полностью совместим со стандартом Model Context Protocol и может использоваться с любыми MCP клиентами.

## ❓ Troubleshooting

### Частые проблемы

1. **Ошибка авторизации**
   ```bash
   make env-check  # Проверьте переменные окружения
   ```

2. **Сервер не запускается**
   ```bash
   make health     # Проверьте статус
   make docker-logs # Проверьте логи
   ```

3. **Проблемы с Docker**
   ```bash
   make docker-clean  # Очистите ресурсы
   make docker-build  # Пересоберите образ
   ```

### Получение помощи

```bash
make help  # Список всех доступных команд
```

## 🤝 Разработка

### Структура проекта
```
mcp-artifact-registry/
├── server.py           # Основной сервер
├── example.py          # Пример использования
├── test/              # Тесты
├── Dockerfile         # Docker образ
├── docker-compose.yml # Compose конфигурация
├── Makefile          # Команды управления
└── README.md         # Документация
```

### Добавление новых функций

1. Обновите `server.py` с новыми MCP инструментами
2. Добавьте тесты в `test/`
3. Обновите документацию
4. Запустите `make check` для проверки

## 📋 Требования к системе

- **Python**: 3.13+
- **Память**: 256MB минимум
- **Диск**: 100MB для образа Docker
- **Сеть**: HTTPS доступ к cloud.ru

## 📞 Поддержка

- [Документация Cloud.ru Artifact Registry](https://cloud.ru/docs/artifact-registry-evolution/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

## 📄 Лицензия

Этот проект предоставляется как есть для демонстрационных целей.

**Версия**: 1.0.0  
**Совместимость**: Cloud.ru Artifact Registry API v1 
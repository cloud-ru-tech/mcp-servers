# 🐳 Docker Guide для MCP Artifact Registry Server

Это руководство поможет вам запустить MCP Artifact Registry Server с помощью Docker.

## 📋 Требования

- Docker 20.10+
- Docker Compose 2.0+
- Ключи доступа Cloud.ru

## 🚀 Быстрый запуск

### 1. Установка переменных окружения

```bash
export CLOUD_RU_KEY_ID="your_key_id_here"
export CLOUD_RU_SECRET="your_secret_here"  
export CLOUD_RU_PROJECT_ID="your_project_id_here"
```

### 2. Запуск через Docker Compose (рекомендуется)

```bash
# Сборка и запуск
make compose-up

# Или напрямую
docker-compose up -d
```

### 3. Запуск через Docker

```bash
# Сборка образа
make docker-build

# Запуск контейнера
make docker-run
```

## 🛠️ Доступные команды Make

### Docker команды
```bash
make docker-build        # Собрать Docker образ
make docker-run          # Запустить в Docker
make docker-run-build    # Собрать и запустить
make docker-stop         # Остановить контейнер
make docker-clean        # Очистить ресурсы
make docker-logs         # Показать логи
```

### Docker Compose команды
```bash
make compose-up          # Запустить через docker-compose
make compose-down        # Остановить docker-compose
make compose-build       # Пересобрать образы
make compose-logs        # Показать логи
make compose-restart     # Перезапустить сервисы
make compose-ps          # Статус контейнеров
```

### Утилиты
```bash
make health              # Проверка здоровья сервера
make status              # Статус сервера и контейнеров
make env-check           # Проверка переменных окружения
make env-example         # Показать пример .env файла
```

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | Обязательная |
|------------|----------|--------------|
| `CLOUD_RU_KEY_ID` | Идентификатор ключа доступа | ✅ |
| `CLOUD_RU_SECRET` | Секретный ключ доступа | ✅ |
| `CLOUD_RU_PROJECT_ID` | UUID проекта в Cloud.ru | ✅ |

### Файл .env (опционально)

Создайте файл `.env` в корне проекта:

```bash
# Cloud.ru API ключи
CLOUD_RU_KEY_ID=your_key_id_here
CLOUD_RU_SECRET=your_secret_here
CLOUD_RU_PROJECT_ID=your_project_id_here
```

## 📊 Мониторинг

### Проверка здоровья сервера

```bash
# Через Make
make health

# Напрямую
curl -I http://localhost:8004/sse
```

### Логи

```bash
# Docker Compose
make compose-logs

# Docker контейнер
make docker-logs

# Реальное время
docker-compose logs -f mcp-artifact-registry
```

### Статус контейнеров

```bash
make compose-ps
# или
docker-compose ps
```

## 🏗️ Архитектура Docker

### Сервисы

1. **mcp-artifact-registry** - основной MCP сервер
   - Порт: 8004
   - Healthcheck: `/sse` endpoint
   - Volume: `./logs:/app/logs`

2. **healthcheck-monitor** - мониторинг здоровья (опционально)
   - Проверяет статус каждые 60 секунд
   - Выводит логи состояния

### Сеть

- **mcp-network** - изолированная сеть для сервисов
- Тип: bridge
- Имя: `mcp-artifact-registry-network`

### Volumes

- **logs** - логи приложения (`./logs:/app/logs`)

## 🔍 Troubleshooting

### Проблема: Контейнер не запускается

```bash
# Проверьте переменные окружения
make env-check

# Проверьте логи
make docker-logs
```

### Проблема: Сервер недоступен

```bash
# Проверьте статус
make status

# Проверьте здоровье
make health

# Проверьте порты
docker-compose ps
```

### Проблема: Ошибки авторизации

1. Убедитесь, что переменные окружения установлены правильно
2. Проверьте валидность ключей в Cloud.ru
3. Убедитесь, что project_id существует

## 📈 Масштабирование

### Horizontal scaling

```bash
# Запуск нескольких экземпляров
docker-compose up -d --scale mcp-artifact-registry=3
```

### Load Balancer

Для продакшн развертывания добавьте nginx или traefik:

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - mcp-artifact-registry
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

## 🚨 Безопасность

### Переменные окружения

- Никогда не коммитьте реальные ключи в git
- Используйте Docker secrets в продакшене
- Регулярно ротируйте ключи доступа

### Сеть

- Сервисы изолированы в отдельной сети
- Порт 8004 доступен только на localhost
- Для публичного доступа используйте reverse proxy

## 📚 Полезные ссылки

- [Документация Cloud.ru](https://cloud.ru/docs/artifact-registry-evolution/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [MCP Protocol](https://modelcontextprotocol.io/)

---

💡 **Совет**: Используйте `make help` для просмотра всех доступных команд! 
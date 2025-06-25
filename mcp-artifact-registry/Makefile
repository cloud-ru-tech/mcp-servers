# Makefile для MCP Artifact Registry Server

.PHONY: help install run-server test test-unit test-integration test-demo \
        docker-build docker-run docker-stop docker-clean \
        lint format clean check health

# Переменные
PROJECT_NAME := mcp-artifact-registry
DOCKER_IMAGE := $(PROJECT_NAME)
DOCKER_CONTAINER := $(PROJECT_NAME)
PORT := 8004

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	uv sync

install-dev: ## Установить зависимости для разработки
	uv sync --dev

run-server: ## Запустить сервер локально
	@echo "🚀 Запуск MCP Artifact Registry Server..."
	@if [ -z "$$CLOUD_RU_KEY_ID" ] || [ -z "$$CLOUD_RU_SECRET" ] || [ -z "$$CLOUD_RU_PROJECT_ID" ]; then \
		echo "⚠️  ВНИМАНИЕ: Установите переменные окружения:"; \
		echo "   export CLOUD_RU_KEY_ID='your_key_id'"; \
		echo "   export CLOUD_RU_SECRET='your_secret'"; \
		echo "   export CLOUD_RU_PROJECT_ID='your_project_id'"; \
		echo ""; \
	fi
	uv run python server.py

test: ## Запустить все тесты
	uv run pytest test/ -v

test-unit: ## Запустить unit тесты
	uv run pytest test/test_ar_api.py -v

test-integration: ## Запустить интеграционные тесты
	@echo "⚠️  Требуют настроенные CLOUD_RU_KEY_ID и CLOUD_RU_SECRET"
	uv run pytest test/test_integration.py -v -m integration

test-demo: ## Запустить демонстрацию
	cd test && uv run python test_tools.py

test-cov: ## Тесты с покрытием кода
	uv run pytest test/ --cov=server --cov-report=html --cov-report=term

lint: ## Проверить код линтером
	uv run flake8 server.py test/
	uv run black --check server.py test/
	uv run isort --check-only server.py test/

format: ## Отформатировать код
	uv run black server.py test/
	uv run isort server.py test/

check: ## Полная проверка кода (линтер + тесты)
	make lint
	make test-unit

# Docker команды
docker-build: ## Собрать Docker образ
	docker build -t $(DOCKER_IMAGE) .

docker-run: ## Запустить в Docker
	@echo "🐳 Запуск $(PROJECT_NAME) в Docker..."
	@if [ -z "$$CLOUD_RU_KEY_ID" ] || [ -z "$$CLOUD_RU_SECRET" ] || [ -z "$$CLOUD_RU_PROJECT_ID" ]; then \
		echo "⚠️  ВНИМАНИЕ: Установите переменные окружения:"; \
		echo "   export CLOUD_RU_KEY_ID='your_key_id'"; \
		echo "   export CLOUD_RU_SECRET='your_secret'"; \
		echo "   export CLOUD_RU_PROJECT_ID='your_project_id'"; \
		echo ""; \
	fi
	docker run -d \
		--name $(DOCKER_CONTAINER) \
		-p $(PORT):$(PORT) \
		-e CLOUD_RU_KEY_ID="$$CLOUD_RU_KEY_ID" \
		-e CLOUD_RU_SECRET="$$CLOUD_RU_SECRET" \
		-e CLOUD_RU_PROJECT_ID="$$CLOUD_RU_PROJECT_ID" \
		-v ./logs:/app/logs \
		$(DOCKER_IMAGE)

docker-run-build: ## Собрать и запустить в Docker
	make docker-build
	make docker-run

docker-stop: ## Остановить Docker контейнер
	docker stop $(DOCKER_CONTAINER) || true
	docker rm $(DOCKER_CONTAINER) || true

docker-clean: ## Очистить Docker ресурсы
	make docker-stop
	docker rmi $(DOCKER_IMAGE) || true

docker-logs: ## Показать логи Docker контейнера
	docker logs -f $(DOCKER_CONTAINER)

# Docker Compose команды
compose-up: ## Запустить через docker-compose
	@echo "🐳 Запуск через docker-compose..."
	@if [ -z "$$CLOUD_RU_KEY_ID" ] || [ -z "$$CLOUD_RU_SECRET" ] || [ -z "$$CLOUD_RU_PROJECT_ID" ]; then \
		echo "⚠️  ВНИМАНИЕ: Установите переменные окружения:"; \
		echo "   export CLOUD_RU_KEY_ID='your_key_id'"; \
		echo "   export CLOUD_RU_SECRET='your_secret'"; \
		echo "   export CLOUD_RU_PROJECT_ID='your_project_id'"; \
		echo ""; \
	fi
	docker-compose up -d

compose-down: ## Остановить docker-compose
	docker-compose down

compose-build: ## Пересобрать через docker-compose
	docker-compose build

compose-logs: ## Логи docker-compose
	docker-compose logs -f

compose-restart: ## Перезапустить docker-compose
	docker-compose restart

compose-ps: ## Показать статус контейнеров
	docker-compose ps

# Утилиты
health: ## Проверить здоровье сервера
	@echo "🔍 Проверка здоровья сервера..."
	@curl -s -I http://localhost:$(PORT)/sse || echo "❌ Сервер недоступен"

status: ## Показать статус сервера
	@echo "📊 Статус MCP Artifact Registry Server:"
	@echo "├─ Порт: $(PORT)"
	@echo "├─ Docker образ: $(DOCKER_IMAGE)"
	@echo "├─ Docker контейнер: $(DOCKER_CONTAINER)"
	@if docker ps | grep -q $(DOCKER_CONTAINER); then \
		echo "└─ Статус: ✅ Запущен"; \
	else \
		echo "└─ Статус: ❌ Остановлен"; \
	fi

clean: ## Очистить временные файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

# Команды окружения
env-example: ## Показать пример переменных окружения
	@echo "# Пример файла .env для MCP Artifact Registry"
	@echo "CLOUD_RU_KEY_ID=your_key_id_here"
	@echo "CLOUD_RU_SECRET=your_secret_here"
	@echo "CLOUD_RU_PROJECT_ID=your_project_id_here"

env-check: ## Проверить переменные окружения
	@echo "🔍 Проверка переменных окружения:"
	@if [ -n "$$CLOUD_RU_KEY_ID" ]; then \
		echo "✅ CLOUD_RU_KEY_ID: $$CLOUD_RU_KEY_ID"; \
	else \
		echo "❌ CLOUD_RU_KEY_ID: не установлено"; \
	fi
	@if [ -n "$$CLOUD_RU_SECRET" ]; then \
		echo "✅ CLOUD_RU_SECRET: [скрыто]"; \
	else \
		echo "❌ CLOUD_RU_SECRET: не установлено"; \
	fi
	@if [ -n "$$CLOUD_RU_PROJECT_ID" ]; then \
		echo "✅ CLOUD_RU_PROJECT_ID: $$CLOUD_RU_PROJECT_ID"; \
	else \
		echo "❌ CLOUD_RU_PROJECT_ID: не установлено"; \
	fi 
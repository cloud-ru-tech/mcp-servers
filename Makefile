# =============================================================================
# Simple MCP Server Projects - Main Makefile
# =============================================================================

.PHONY: help weather-build weather-run weather-stop weather-logs weather-test weather-shell weather-clean \
        search-build search-run search-stop search-logs search-test search-shell search-clean \
        ip-build ip-run ip-stop ip-logs ip-test ip-shell ip-clean \
        yandex-build yandex-run yandex-stop yandex-logs yandex-test yandex-shell yandex-clean

# Default target
help: ## Показать справку по командам
	@echo "🔧 Simple MCP Server Projects"
	@echo "=============================="
	@echo ""
	@echo "🌤️  MCP Weather Server Commands:"
	@echo "🔍 MCP Search Server Commands:"
	@echo "🌐 MCP IP Server Commands:"
	@echo "🔍 MCP Yandex Search Server Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# =============================================================================
# MCP Weather Server Commands
# =============================================================================

weather-build: ## Собрать Docker образ для MCP Weather сервера
	@echo "🔨 Сборка Docker образа для MCP Weather..."
	cd mcp-weather && docker build -t mcp-weather:latest .
	@echo "✅ Docker образ mcp-weather:latest готов!"

weather-run: ## Запустить MCP Weather сервер в Docker контейнере
	@echo "🚀 Запуск MCP Weather сервера..."
	cd mcp-weather && docker-compose up -d
	@echo "✅ MCP Weather сервер запущен!"
	@echo "🌐 Доступен по адресу: http://localhost:8001"
	@echo "📡 SSE endpoint: http://localhost:8001/sse"
	@echo "📧 Messages endpoint: http://localhost:8001/messages/"

weather-run-build: ## Собрать и запустить MCP Weather сервер
	@echo "🔨 Сборка и запуск MCP Weather сервера..."
	cd mcp-weather && docker-compose up -d --build
	@echo "✅ MCP Weather сервер собран и запущен!"
	@echo "🌐 Доступен по адресу: http://localhost:8001"

weather-stop: ## Остановить MCP Weather сервер
	@echo "⏹️  Остановка MCP Weather сервера..."
	cd mcp-weather && docker-compose down
	@echo "✅ MCP Weather сервер остановлен!"

weather-restart: ## Перезапустить MCP Weather сервер
	@echo "🔄 Перезапуск MCP Weather сервера..."
	cd mcp-weather && docker-compose restart
	@echo "✅ MCP Weather сервер перезапущен!"

weather-logs: ## Показать логи MCP Weather сервера
	@echo "📄 Логи MCP Weather сервера:"
	cd mcp-weather && docker-compose logs -f

weather-status: ## Показать статус MCP Weather контейнера
	@echo "📊 Статус MCP Weather сервера:"
	cd mcp-weather && docker-compose ps

weather-test: ## Запустить тесты MCP Weather в Docker контейнере
	@echo "🧪 Запуск тестов MCP Weather..."
	cd mcp-weather && docker-compose exec mcp-weather uv run pytest test/test_weather_api.py -v || \
	docker run --rm -v $(PWD)/mcp-weather:/app -w /app mcp-weather:latest uv run pytest test/test_weather_api.py -v
	@echo "✅ Тесты завершены!"

weather-shell: ## Открыть shell в MCP Weather контейнере
	@echo "🐚 Подключение к MCP Weather контейнеру..."
	cd mcp-weather && docker-compose exec mcp-weather /bin/bash || \
	docker run --rm -it -v $(PWD)/mcp-weather:/app -w /app mcp-weather:latest /bin/bash

weather-clean: ## Очистить Docker ресурсы MCP Weather
	@echo "🧹 Очистка Docker ресурсов..."
	cd mcp-weather && docker-compose down -v --remove-orphans
	docker rmi mcp-weather:latest 2>/dev/null || true
	@echo "✅ Очистка завершена!"

weather-dev: ## Запустить MCP Weather в режиме разработки (с автоперезагрузкой)
	@echo "🔧 Запуск MCP Weather в режиме разработки..."
	cd mcp-weather && docker-compose -f docker-compose.yml up --build

# =============================================================================
# Полезные команды
# =============================================================================

weather-health: ## Проверить здоровье MCP Weather сервера
	@echo "🩺 Проверка здоровья MCP Weather сервера..."
	@curl -s -I http://localhost:8001/sse | head -1 || echo "❌ Сервер недоступен"
	@echo "✅ Проверка завершена!"

weather-demo: ## Запустить демонстрацию MCP Weather
	@echo "🎭 Демонстрация MCP Weather..."
	cd mcp-weather && docker-compose exec mcp-weather make test-demo || \
	docker run --rm -v $(PWD)/mcp-weather:/app -w /app mcp-weather:latest uv run python test/test_tools.py

# =============================================================================
# MCP Search Server Commands
# =============================================================================

search-build: ## Собрать Docker образ для MCP Search сервера
	@echo "🔨 Сборка Docker образа для MCP Search..."
	cd mcp-search && docker build -t mcp-search:latest .
	@echo "✅ Docker образ mcp-search:latest готов!"

search-run: ## Запустить MCP Search сервер в Docker контейнере
	@echo "🚀 Запуск MCP Search сервера..."
	cd mcp-search && docker-compose up -d
	@echo "✅ MCP Search сервер запущен!"
	@echo "🌐 Доступен по адресу: http://localhost:8002"
	@echo "📡 SSE endpoint: http://localhost:8002/sse"
	@echo "📧 Messages endpoint: http://localhost:8002/messages/"

search-run-build: ## Собрать и запустить MCP Search сервер
	@echo "🔨 Сборка и запуск MCP Search сервера..."
	cd mcp-search && docker-compose up -d --build
	@echo "✅ MCP Search сервер собран и запущен!"
	@echo "🌐 Доступен по адресу: http://localhost:8002"

search-stop: ## Остановить MCP Search сервер
	@echo "⏹️  Остановка MCP Search сервера..."
	cd mcp-search && docker-compose down
	@echo "✅ MCP Search сервер остановлен!"

search-restart: ## Перезапустить MCP Search сервер
	@echo "🔄 Перезапуск MCP Search сервера..."
	cd mcp-search && docker-compose restart
	@echo "✅ MCP Search сервер перезапущен!"

search-logs: ## Показать логи MCP Search сервера
	@echo "📄 Логи MCP Search сервера:"
	cd mcp-search && docker-compose logs -f

search-status: ## Показать статус MCP Search контейнера
	@echo "📊 Статус MCP Search сервера:"
	cd mcp-search && docker-compose ps

search-test: ## Запустить тесты MCP Search в Docker контейнере
	@echo "🧪 Запуск тестов MCP Search..."
	cd mcp-search && docker-compose exec mcp-search uv run pytest test/test_search_api.py -v || \
	docker run --rm -v $(PWD)/mcp-search:/app -w /app mcp-search:latest uv run pytest test/test_search_api.py -v
	@echo "✅ Тесты завершены!"

search-shell: ## Открыть shell в MCP Search контейнере
	@echo "🐚 Подключение к MCP Search контейнеру..."
	cd mcp-search && docker-compose exec mcp-search /bin/bash || \
	docker run --rm -it -v $(PWD)/mcp-search:/app -w /app mcp-search:latest /bin/bash

search-clean: ## Очистить Docker ресурсы MCP Search
	@echo "🧹 Очистка Docker ресурсов..."
	cd mcp-search && docker-compose down -v --remove-orphans
	docker rmi mcp-search:latest 2>/dev/null || true
	@echo "✅ Очистка завершена!"

search-dev: ## Запустить MCP Search в режиме разработки
	@echo "🔧 Запуск MCP Search в режиме разработки..."
	cd mcp-search && docker-compose -f docker-compose.yml up --build

search-health: ## Проверить здоровье MCP Search сервера
	@echo "🩺 Проверка здоровья MCP Search сервера..."
	@curl -s -I http://localhost:8002/sse | head -1 || echo "❌ Сервер недоступен"
	@echo "✅ Проверка завершена!"

search-demo: ## Запустить демонстрацию MCP Search
	@echo "🎭 Демонстрация MCP Search..."
	cd mcp-search && docker-compose exec mcp-search make test-demo || \
	docker run --rm -v $(PWD)/mcp-search:/app -w /app mcp-search:latest uv run python test/test_tools.py

# =============================================================================
# MCP IP Server Commands
# =============================================================================

ip-build: ## Собрать Docker образ для MCP IP сервера
	@echo "🔨 Сборка Docker образа для MCP IP..."
	cd mcp-ip && docker build -t mcp-ip:latest .
	@echo "✅ Docker образ mcp-ip:latest готов!"

ip-run: ## Запустить MCP IP сервер в Docker контейнере
	@echo "🚀 Запуск MCP IP сервера..."
	cd mcp-ip && docker-compose up -d
	@echo "✅ MCP IP сервер запущен!"
	@echo "🌐 Доступен по адресу: http://localhost:8003"
	@echo "📡 SSE endpoint: http://localhost:8003/sse"
	@echo "📧 Messages endpoint: http://localhost:8003/messages/"

ip-run-build: ## Собрать и запустить MCP IP сервер
	@echo "🔨 Сборка и запуск MCP IP сервера..."
	cd mcp-ip && docker-compose up -d --build
	@echo "✅ MCP IP сервер собран и запущен!"
	@echo "🌐 Доступен по адресу: http://localhost:8003"

ip-stop: ## Остановить MCP IP сервер
	@echo "⏹️  Остановка MCP IP сервера..."
	cd mcp-ip && docker-compose down
	@echo "✅ MCP IP сервер остановлен!"

ip-restart: ## Перезапустить MCP IP сервер
	@echo "🔄 Перезапуск MCP IP сервера..."
	cd mcp-ip && docker-compose restart
	@echo "✅ MCP IP сервер перезапущен!"

ip-logs: ## Показать логи MCP IP сервера
	@echo "📄 Логи MCP IP сервера:"
	cd mcp-ip && docker-compose logs -f

ip-status: ## Показать статус MCP IP контейнера
	@echo "📊 Статус MCP IP сервера:"
	cd mcp-ip && docker-compose ps

ip-test: ## Запустить тесты MCP IP в Docker контейнере
	@echo "🧪 Запуск тестов MCP IP..."
	cd mcp-ip && docker-compose exec mcp-ip uv run pytest test/test_ip_api.py -v || \
	docker run --rm -v $(PWD)/mcp-ip:/app -w /app mcp-ip:latest uv run pytest test/test_ip_api.py -v
	@echo "✅ Тесты завершены!"

ip-shell: ## Открыть shell в MCP IP контейнере
	@echo "🐚 Подключение к MCP IP контейнеру..."
	cd mcp-ip && docker-compose exec mcp-ip /bin/bash || \
	docker run --rm -it -v $(PWD)/mcp-ip:/app -w /app mcp-ip:latest /bin/bash

ip-clean: ## Очистить Docker ресурсы MCP IP
	@echo "🧹 Очистка Docker ресурсов..."
	cd mcp-ip && docker-compose down -v --remove-orphans
	docker rmi mcp-ip:latest 2>/dev/null || true
	@echo "✅ Очистка завершена!"

ip-dev: ## Запустить MCP IP в режиме разработки
	@echo "🔧 Запуск MCP IP в режиме разработки..."
	cd mcp-ip && docker-compose -f docker-compose.yml up --build

ip-health: ## Проверить здоровье MCP IP сервера
	@echo "🩺 Проверка здоровья MCP IP сервера..."
	@curl -s -I http://localhost:8003/sse | head -1 || echo "❌ Сервер недоступен"
	@echo "✅ Проверка завершена!"

ip-demo: ## Запустить демонстрацию MCP IP
	@echo "🎭 Демонстрация MCP IP..."
	cd mcp-ip && docker-compose exec mcp-ip make test-demo || \
	docker run --rm -v $(PWD)/mcp-ip:/app -w /app mcp-ip:latest uv run python test/test_tools.py

# =============================================================================
# MCP Yandex Search Server Commands
# =============================================================================

yandex-build: ## Собрать Docker образ для MCP Yandex Search сервера
	@echo "🔨 Сборка Docker образа для MCP Yandex Search..."
	cd mcp-yandex-search && docker build -t mcp-yandex-search:latest .
	@echo "✅ Docker образ mcp-yandex-search:latest готов!"

yandex-run: ## Запустить MCP Yandex Search сервер в Docker контейнере
	@echo "🚀 Запуск MCP Yandex Search сервера..."
	@if [ -z "$$YANDEX_API_KEY" ] || [ -z "$$YANDEX_FOLDER_ID" ]; then \
		echo "⚠️  ВНИМАНИЕ: Установите переменные окружения:"; \
		echo "   export YANDEX_API_KEY='your_api_key'"; \
		echo "   export YANDEX_FOLDER_ID='your_folder_id'"; \
		echo ""; \
	fi
	cd mcp-yandex-search && docker-compose up -d
	@echo "✅ MCP Yandex Search сервер запущен!"
	@echo "🌐 Доступен по адресу: http://localhost:8006"
	@echo "📡 SSE endpoint: http://localhost:8006/sse"
	@echo "📧 Messages endpoint: http://localhost:8006/messages/"

yandex-run-build: ## Собрать и запустить MCP Yandex Search сервер
	@echo "🔨 Сборка и запуск MCP Yandex Search сервера..."
	@if [ -z "$$YANDEX_API_KEY" ] || [ -z "$$YANDEX_FOLDER_ID" ]; then \
		echo "⚠️  ВНИМАНИЕ: Установите переменные окружения:"; \
		echo "   export YANDEX_API_KEY='your_api_key'"; \
		echo "   export YANDEX_FOLDER_ID='your_folder_id'"; \
		echo ""; \
	fi
	cd mcp-yandex-search && docker-compose up -d --build
	@echo "✅ MCP Yandex Search сервер собран и запущен!"
	@echo "🌐 Доступен по адресу: http://localhost:8006"

yandex-stop: ## Остановить MCP Yandex Search сервер
	@echo "⏹️  Остановка MCP Yandex Search сервера..."
	cd mcp-yandex-search && docker-compose down
	@echo "✅ MCP Yandex Search сервер остановлен!"

yandex-restart: ## Перезапустить MCP Yandex Search сервер
	@echo "🔄 Перезапуск MCP Yandex Search сервера..."
	cd mcp-yandex-search && docker-compose restart
	@echo "✅ MCP Yandex Search сервер перезапущен!"

yandex-logs: ## Показать логи MCP Yandex Search сервера
	@echo "📄 Логи MCP Yandex Search сервера:"
	cd mcp-yandex-search && docker-compose logs -f

yandex-status: ## Показать статус MCP Yandex Search контейнера
	@echo "📊 Статус MCP Yandex Search сервера:"
	cd mcp-yandex-search && docker-compose ps

yandex-test: ## Запустить тесты MCP Yandex Search в Docker контейнере
	@echo "🧪 Запуск тестов MCP Yandex Search..."
	cd mcp-yandex-search && docker-compose exec mcp-yandex-search uv run pytest test/test_yandex_api.py -v || \
	docker run --rm -v $(PWD)/mcp-yandex-search:/app -w /app mcp-yandex-search:latest uv run pytest test/test_yandex_api.py -v
	@echo "✅ Тесты завершены!"

yandex-shell: ## Открыть shell в MCP Yandex Search контейнере
	@echo "🐚 Подключение к MCP Yandex Search контейнеру..."
	cd mcp-yandex-search && docker-compose exec mcp-yandex-search /bin/bash || \
	docker run --rm -it -v $(PWD)/mcp-yandex-search:/app -w /app mcp-yandex-search:latest /bin/bash

yandex-clean: ## Очистить Docker ресурсы MCP Yandex Search
	@echo "🧹 Очистка Docker ресурсов..."
	cd mcp-yandex-search && docker-compose down -v --remove-orphans
	docker rmi mcp-yandex-search:latest 2>/dev/null || true
	@echo "✅ Очистка завершена!"

yandex-dev: ## Запустить MCP Yandex Search в режиме разработки
	@echo "🔧 Запуск MCP Yandex Search в режиме разработки..."
	cd mcp-yandex-search && docker-compose -f docker-compose.yml up --build

yandex-health: ## Проверить здоровье MCP Yandex Search сервера
	@echo "🩺 Проверка здоровья MCP Yandex Search сервера..."
	@curl -s -I http://localhost:8006/sse | head -1 || echo "❌ Сервер недоступен"
	@echo "✅ Проверка завершена!"

yandex-demo: ## Запустить демонстрацию MCP Yandex Search
	@echo "🎭 Демонстрация MCP Yandex Search..."
	@if [ -z "$$YANDEX_API_KEY" ] || [ -z "$$YANDEX_FOLDER_ID" ]; then \
		echo "⚠️  Для демонстрации установите переменные окружения:"; \
		echo "   export YANDEX_API_KEY='your_api_key'"; \
		echo "   export YANDEX_FOLDER_ID='your_folder_id'"; \
	fi
	cd mcp-yandex-search && docker-compose exec mcp-yandex-search make test-demo || \
	docker run --rm -v $(PWD)/mcp-yandex-search:/app -w /app -e YANDEX_API_KEY -e YANDEX_FOLDER_ID mcp-yandex-search:latest uv run python test/test_tools.py

# =============================================================================
# MCP Artifact Registry Server Commands
# =============================================================================

ar-build: ## Собрать Docker образ для MCP Artifact Registry сервера
	@echo "🔨 Сборка Docker образа для MCP Artifact Registry..."
	cd mcp-artifact-registry && docker build -t mcp-artifact-registry:latest .
	@echo "✅ Docker образ mcp-artifact-registry:latest готов!"

ar-run: ## Запустить MCP Artifact Registry сервер в Docker контейнере
	@echo "🚀 Запуск MCP Artifact Registry сервера..."
	@if [ -z "$$CLOUD_RU_KEY_ID" ] || [ -z "$$CLOUD_RU_SECRET" ]; then \
		echo "⚠️  ВНИМАНИЕ: Установите переменные окружения:"; \
		echo "   export CLOUD_RU_KEY_ID='your_key_id'"; \
		echo "   export CLOUD_RU_SECRET='your_secret'"; \
		echo ""; \
	fi
	cd mcp-artifact-registry && docker-compose up -d
	@echo "✅ MCP Artifact Registry сервер запущен!"
	@echo "🌐 Доступен по адресу: http://localhost:8004"
	@echo "📡 SSE endpoint: http://localhost:8004/sse"
	@echo "📧 Messages endpoint: http://localhost:8004/messages/"

ar-run-build: ## Собрать и запустить MCP Artifact Registry сервер
	@echo "🔨 Сборка и запуск MCP Artifact Registry сервера..."
	@if [ -z "$$CLOUD_RU_KEY_ID" ] || [ -z "$$CLOUD_RU_SECRET" ]; then \
		echo "⚠️  ВНИМАНИЕ: Установите переменные окружения:"; \
		echo "   export CLOUD_RU_KEY_ID='your_key_id'"; \
		echo "   export CLOUD_RU_SECRET='your_secret'"; \
		echo ""; \
	fi
	cd mcp-artifact-registry && docker-compose up -d --build
	@echo "✅ MCP Artifact Registry сервер собран и запущен!"
	@echo "🌐 Доступен по адресу: http://localhost:8004"

ar-stop: ## Остановить MCP Artifact Registry сервер
	@echo "⏹️  Остановка MCP Artifact Registry сервера..."
	cd mcp-artifact-registry && docker-compose down
	@echo "✅ MCP Artifact Registry сервер остановлен!"

ar-restart: ## Перезапустить MCP Artifact Registry сервер
	@echo "🔄 Перезапуск MCP Artifact Registry сервера..."
	cd mcp-artifact-registry && docker-compose restart
	@echo "✅ MCP Artifact Registry сервер перезапущен!"

ar-logs: ## Показать логи MCP Artifact Registry сервера
	@echo "📄 Логи MCP Artifact Registry сервера:"
	cd mcp-artifact-registry && docker-compose logs -f

ar-status: ## Показать статус MCP Artifact Registry контейнера
	@echo "📊 Статус MCP Artifact Registry сервера:"
	cd mcp-artifact-registry && docker-compose ps

ar-test: ## Запустить тесты MCP Artifact Registry в Docker контейнере
	@echo "🧪 Запуск тестов MCP Artifact Registry..."
	cd mcp-artifact-registry && docker-compose exec mcp-artifact-registry uv run pytest test/test_ar_api.py -v || \
	docker run --rm -v $(PWD)/mcp-artifact-registry:/app -w /app mcp-artifact-registry:latest uv run pytest test/test_ar_api.py -v
	@echo "✅ Тесты завершены!"

ar-test-integration: ## Запустить интеграционные тесты
	@echo "🧪 Запуск интеграционных тестов MCP Artifact Registry..."
	@if [ -z "$$CLOUD_RU_KEY_ID" ] || [ -z "$$CLOUD_RU_SECRET" ] || [ -z "$$TEST_PROJECT_ID" ]; then \
		echo "⚠️  Для интеграционных тестов установите переменные:"; \
		echo "   export CLOUD_RU_KEY_ID='your_key_id'"; \
		echo "   export CLOUD_RU_SECRET='your_secret'"; \
		echo "   export TEST_PROJECT_ID='your_project_uuid'"; \
		echo ""; \
	fi
	cd mcp-artifact-registry && docker-compose exec mcp-artifact-registry uv run pytest test/test_integration.py -v -m integration || \
	docker run --rm -v $(PWD)/mcp-artifact-registry:/app -w /app -e CLOUD_RU_KEY_ID -e CLOUD_RU_SECRET -e TEST_PROJECT_ID mcp-artifact-registry:latest uv run pytest test/test_integration.py -v -m integration

ar-shell: ## Открыть shell в MCP Artifact Registry контейнере
	@echo "🐚 Подключение к MCP Artifact Registry контейнеру..."
	cd mcp-artifact-registry && docker-compose exec mcp-artifact-registry /bin/bash || \
	docker run --rm -it -v $(PWD)/mcp-artifact-registry:/app -w /app mcp-artifact-registry:latest /bin/bash

ar-clean: ## Очистить Docker ресурсы MCP Artifact Registry
	@echo "🧹 Очистка Docker ресурсов..."
	cd mcp-artifact-registry && docker-compose down -v --remove-orphans
	docker rmi mcp-artifact-registry:latest 2>/dev/null || true
	@echo "✅ Очистка завершена!"

ar-dev: ## Запустить MCP Artifact Registry в режиме разработки
	@echo "🔧 Запуск MCP Artifact Registry в режиме разработки..."
	cd mcp-artifact-registry && docker-compose -f docker-compose.yml up --build

ar-health: ## Проверить здоровье MCP Artifact Registry сервера
	@echo "🩺 Проверка здоровья MCP Artifact Registry сервера..."
	@curl -s -I http://localhost:8004/sse | head -1 || echo "❌ Сервер недоступен"
	@echo "✅ Проверка завершена!"

ar-demo: ## Запустить демонстрацию MCP Artifact Registry
	@echo "🎭 Демонстрация MCP Artifact Registry..."
	@if [ -z "$$CLOUD_RU_KEY_ID" ] || [ -z "$$CLOUD_RU_SECRET" ]; then \
		echo "⚠️  Для демонстрации установите переменные окружения:"; \
		echo "   export CLOUD_RU_KEY_ID='your_key_id'"; \
		echo "   export CLOUD_RU_SECRET='your_secret'"; \
		echo "   export TEST_PROJECT_ID='your_project_uuid' (опционально)"; \
	fi
	cd mcp-artifact-registry && docker-compose exec mcp-artifact-registry make test-demo || \
	docker run --rm -v $(PWD)/mcp-artifact-registry:/app -w /app -e CLOUD_RU_KEY_ID -e CLOUD_RU_SECRET -e TEST_PROJECT_ID mcp-artifact-registry:latest uv run python test/test_tools.py

ar-env-check: ## Проверить переменные окружения для Artifact Registry
	@echo "🔍 Проверка переменных окружения для MCP Artifact Registry:"
	cd mcp-artifact-registry && make env-check

# =============================================================================
# MCP UFC Server Commands
# =============================================================================

ufc-build: ## Собрать Docker образ для MCP UFC сервера
	@echo "🔨 Сборка Docker образа для MCP UFC..."
	cd mcp-ufc && docker build -t mcp-ufc:latest .
	@echo "✅ Docker образ mcp-ufc:latest готов!"

ufc-run: ## Запустить MCP UFC сервер в Docker контейнере
	@echo "🚀 Запуск MCP UFC сервера..."
	cd mcp-ufc && docker-compose up -d
	@echo "✅ MCP UFC сервер запущен!"
	@echo "🌐 Доступен по адресу: http://localhost:8005"
	@echo "📡 SSE endpoint: http://localhost:8005/sse"
	@echo "📧 Messages endpoint: http://localhost:8005/messages/"

ufc-run-build: ## Собрать и запустить MCP UFC сервер
	@echo "🔨 Сборка и запуск MCP UFC сервера..."
	cd mcp-ufc && docker-compose up -d --build
	@echo "✅ MCP UFC сервер собран и запущен!"
	@echo "🌐 Доступен по адресу: http://localhost:8005"

ufc-stop: ## Остановить MCP UFC сервер
	@echo "⏹️  Остановка MCP UFC сервера..."
	cd mcp-ufc && docker-compose down
	@echo "✅ MCP UFC сервер остановлен!"

ufc-restart: ## Перезапустить MCP UFC сервер
	@echo "🔄 Перезапуск MCP UFC сервера..."
	cd mcp-ufc && docker-compose restart
	@echo "✅ MCP UFC сервер перезапущен!"

ufc-logs: ## Показать логи MCP UFC сервера
	@echo "📄 Логи MCP UFC сервера:"
	cd mcp-ufc && docker-compose logs -f

ufc-status: ## Показать статус MCP UFC контейнера
	@echo "📊 Статус MCP UFC сервера:"
	cd mcp-ufc && docker-compose ps

ufc-test: ## Запустить тесты MCP UFC в Docker контейнере
	@echo "🧪 Запуск тестов MCP UFC..."
	cd mcp-ufc && docker-compose exec mcp-ufc uv run pytest test/ -v || \
	docker run --rm -v $(PWD)/mcp-ufc:/app -w /app mcp-ufc:latest uv run pytest test/ -v
	@echo "✅ Тесты завершены!"

ufc-shell: ## Открыть shell в MCP UFC контейнере
	@echo "🐚 Подключение к MCP UFC контейнеру..."
	cd mcp-ufc && docker-compose exec mcp-ufc /bin/bash || \
	docker run --rm -it -v $(PWD)/mcp-ufc:/app -w /app mcp-ufc:latest /bin/bash

ufc-clean: ## Очистить Docker ресурсы MCP UFC
	@echo "🧹 Очистка Docker ресурсов..."
	cd mcp-ufc && docker-compose down -v --remove-orphans
	docker rmi mcp-ufc:latest 2>/dev/null || true
	@echo "✅ Очистка завершена!"

ufc-dev: ## Запустить MCP UFC в режиме разработки
	@echo "🔧 Запуск MCP UFC в режиме разработки..."
	cd mcp-ufc && docker-compose -f docker-compose.yml up --build

ufc-health: ## Проверить здоровье MCP UFC сервера
	@echo "🩺 Проверка здоровья MCP UFC сервера..."
	@curl -s -I http://localhost:8005/sse | head -1 || echo "❌ Сервер недоступен"
	@echo "✅ Проверка завершена!"

ufc-demo: ## Запустить демонстрацию MCP UFC
	@echo "🎭 Демонстрация MCP UFC..."
	cd mcp-ufc && docker-compose exec mcp-ufc make demo || \
	docker run --rm -v $(PWD)/mcp-ufc:/app -w /app mcp-ufc:latest uv run python test/test_tools.py

# =============================================================================
# Управление всеми сервисами
# =============================================================================

start-all: weather-run search-run ip-run yandex-run ar-run ufc-run ## Запустить все MCP серверы
	@echo "🚀 Все MCP серверы запущены!"

stop-all: weather-stop search-stop ip-stop yandex-stop ar-stop ufc-stop ## Остановить все MCP серверы
	@echo "⏹️  Все MCP серверы остановлены!"

clean-all: weather-clean search-clean ip-clean yandex-clean ar-clean ufc-clean ## Очистить все Docker ресурсы
	@echo "🧹 Все ресурсы очищены!"

# =============================================================================
# Информационные команды
# =============================================================================

list-services: ## Показать список всех MCP сервисов
	@echo "📋 Доступные MCP сервисы:"
	@echo "  🌤️  mcp-weather - Сервер погоды (порт 8001)"
	@echo "  🔍 mcp-search - Сервер поиска (порт 8002)"
	@echo "  🌐 mcp-ip - Сервер IP-информации (порт 8003)"
	@echo "  🔍 mcp-yandex-search - Yandex поиск (порт 8006)"
	@echo "  🏛️  mcp-artifact-registry - Cloud.ru Artifact Registry (порт 8004)"
	@echo "  🥊 mcp-ufc - UFC и MMA сервер (порт 8005)"
	@echo ""
	@echo "💡 Планируемые сервисы:"
	@echo "  📊 mcp-analytics - Аналитика данных"  
	@echo "  🗄️  mcp-database - Работа с БД"
	@echo "  🔗 mcp-api - REST API интеграции"

ports: ## Показать используемые порты
	@echo "🔌 Используемые порты:"
	@echo "  8001 - MCP Weather Server"
	@echo "  8002 - MCP Search Server"
	@echo "  8003 - MCP IP Server"
	@echo "  8004 - MCP Artifact Registry Server"
	@echo "  8005 - MCP UFC Server"
	@docker ps --format "table {{.Names}}\t{{.Ports}}" | grep -E "(mcp-|PORTS)" || true 
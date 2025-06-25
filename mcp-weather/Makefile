# Makefile для MCP сервера погоды
# Используется uv для управления зависимостями и запуска тестов

.PHONY: help install test test-unit test-integration test-demo test-all test-cov \
        clean lint format server run-server docker-build docker-run

# Цвета для вывода
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Показать справку
	@echo "$(GREEN)MCP Weather Server - Makefile команды:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

install: ## Установить зависимости через uv
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	uv sync --dev

test: test-unit ## Запустить основные тесты (alias для test-unit)

test-unit: ## Запустить быстрые unit тесты с mock
	@echo "$(GREEN)Запуск unit тестов...$(NC)"
	uv run pytest test/test_weather_api.py -v --tb=short

test-integration: ## Запустить интеграционные тесты с реальным API
	@echo "$(YELLOW)Запуск интеграционных тестов (требует интернет)...$(NC)"
	uv run pytest test/test_integration.py -v --tb=short -m integration

test-demo: ## Запустить демонстрационные тесты
	@echo "$(GREEN)Запуск демонстрационных тестов...$(NC)"
	cd test && uv run python test_tools.py

test-all: ## Запустить все тесты
	@echo "$(GREEN)Запуск всех тестов...$(NC)"
	uv run pytest test/ -v --tb=short

test-cov: ## Запустить тесты с покрытием кода
	@echo "$(GREEN)Запуск тестов с покрытием кода...$(NC)"
	uv run pytest test/ -v --cov=server --cov-report=term-missing --cov-report=html

test-fast: ## Запустить только быстрые тесты (исключить медленные)
	@echo "$(GREEN)Запуск быстрых тестов...$(NC)"
	uv run pytest test/ -v -m "not slow"

test-ci: ## Запустить тесты для CI/CD (только unit тесты)
	@echo "$(GREEN)Запуск тестов для CI...$(NC)"
	uv run pytest test/test_weather_api.py -v --tb=short --junitxml=test-results.xml

lint: ## Проверить код линтером
	@echo "$(GREEN)Проверка кода линтером...$(NC)"
	uv run ruff check server.py test/

format: ## Форматировать код
	@echo "$(GREEN)Форматирование кода...$(NC)"
	uv run ruff format server.py test/

server: run-server ## Запустить сервер (alias)

run-server: ## Запустить MCP сервер локально
	@echo "$(GREEN)Запуск MCP сервера погоды...$(NC)"
	uv run python server.py

dev-server: ## Запустить сервер в режиме разработки
	@echo "$(GREEN)Запуск сервера в dev режиме...$(NC)"
	uv run python server.py --reload

docker-build: ## Собрать Docker образ
	@echo "$(GREEN)Сборка Docker образа...$(NC)"
	docker build -t weather-mcp-server .

docker-run: ## Запустить сервер в Docker
	@echo "$(GREEN)Запуск сервера в Docker...$(NC)"
	docker run -p 8001:8001 weather-mcp-server

clean: ## Очистить временные файлы
	@echo "$(GREEN)Очистка временных файлов...$(NC)"
	rm -rf __pycache__ test/__pycache__ .pytest_cache htmlcov .coverage
	rm -f test-results.xml
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

deps-update: ## Обновить зависимости
	@echo "$(GREEN)Обновление зависимостей...$(NC)"
	uv sync --upgrade

deps-add: ## Добавить новую зависимость (использование: make deps-add PACKAGE=название_пакета)
	@if [ -z "$(PACKAGE)" ]; then \
		echo "$(RED)Ошибка: укажите PACKAGE=название_пакета$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Добавление зависимости $(PACKAGE)...$(NC)"
	uv add $(PACKAGE)

deps-add-dev: ## Добавить dev зависимость (использование: make deps-add-dev PACKAGE=название_пакета)
	@if [ -z "$(PACKAGE)" ]; then \
		echo "$(RED)Ошибка: укажите PACKAGE=название_пакета$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Добавление dev зависимости $(PACKAGE)...$(NC)"
	uv add --dev $(PACKAGE)

check: lint test-unit ## Полная проверка кода (линтер + unit тесты)

all: clean install lint test-cov ## Полный цикл: очистка, установка, линтер, тесты с покрытием

# Примеры использования в комментариях:
# make install          # Установить зависимости
# make test            # Быстрые тесты
# make test-all        # Все тесты
# make test-cov        # Тесты + покрытие
# make run-server      # Запустить сервер
# make docker-build    # Собрать Docker образ
# make clean           # Очистить временные файлы 
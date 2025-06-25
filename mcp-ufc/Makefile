# Makefile для MCP UFC Server

SHELL := /bin/bash
.PHONY: help install dev-install run test clean build docker-build docker-run docker-stop logs demo lint format check-deps health

# Цвета для вывода
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Показать это сообщение помощи
	@echo "$(GREEN)MCP UFC Server - Makefile команды:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	uv sync

dev-install: ## Установить зависимости для разработки
	@echo "$(GREEN)Установка dev зависимостей...$(NC)"
	uv sync --dev

run: ## Запустить сервер локально
	@echo "$(GREEN)Запуск UFC Server на порту 8005...$(NC)"
	uv run python server.py

test: ## Запустить тесты
	@echo "$(GREEN)Запуск тестов...$(NC)"
	uv run pytest test/ -v

test-integration: ## Запустить интеграционные тесты
	@echo "$(GREEN)Запуск интеграционных тестов...$(NC)"
	uv run pytest test/ -v -m integration

test-coverage: ## Запустить тесты с покрытием
	@echo "$(GREEN)Запуск тестов с покрытием...$(NC)"
	uv run pytest test/ --cov=. --cov-report=html --cov-report=term

lint: ## Проверить код линтером
	@echo "$(GREEN)Проверка кода...$(NC)"
	uv run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	uv run flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format: ## Форматировать код
	@echo "$(GREEN)Форматирование кода...$(NC)"
	uv run black .
	uv run isort .

clean: ## Очистить временные файлы
	@echo "$(GREEN)Очистка временных файлов...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/

build: ## Собрать проект
	@echo "$(GREEN)Сборка проекта...$(NC)"
	uv build

docker-build: ## Собрать Docker образ
	@echo "$(GREEN)Сборка Docker образа...$(NC)"
	docker build -t mcp-ufc:latest .

docker-run: ## Запустить в Docker
	@echo "$(GREEN)Запуск в Docker...$(NC)"
	docker-compose up -d

docker-stop: ## Остановить Docker контейнер
	@echo "$(GREEN)Остановка Docker контейнеров...$(NC)"
	docker-compose down

docker-logs: ## Посмотреть логи Docker
	@echo "$(GREEN)Логи Docker контейнера:$(NC)"
	docker-compose logs -f

docker-rebuild: ## Пересобрать и запустить Docker
	@echo "$(GREEN)Пересборка и запуск Docker...$(NC)"
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

logs: ## Посмотреть логи приложения
	@echo "$(GREEN)Логи приложения:$(NC)"
	tail -f logs/*.log 2>/dev/null || echo "Логи не найдены"

demo: ## Запустить демонстрацию функций
	@echo "$(GREEN)Демонстрация UFC API...$(NC)"
	uv run python test/test_tools.py

health: ## Проверить состояние сервера
	@echo "$(GREEN)Проверка состояния сервера...$(NC)"
	curl -f http://localhost:8005/sse || echo "$(RED)Сервер не отвечает$(NC)"

check-deps: ## Проверить зависимости
	@echo "$(GREEN)Проверка зависимостей...$(NC)"
	uv tree

dev: dev-install run ## Установить dev зависимости и запустить

all: clean install test build ## Выполнить полный цикл: очистка, установка, тесты, сборка

# Алиасы для совместимости
up: docker-run
down: docker-stop
ps: 
	@docker-compose ps

restart: docker-stop docker-run ## Перезапустить Docker контейнеры

shell: ## Войти в контейнер
	@docker-compose exec mcp-ufc /bin/bash 
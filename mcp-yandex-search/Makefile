.PHONY: install dev test run docker-build docker-run clean lint format

# Установка зависимостей
install:
	pip install -e .

# Установка зависимостей для разработки
dev:
	pip install -e ".[dev]"

# Запуск тестов
test:
	pytest test/ -v --cov=. --cov-report=html

# Запуск сервера
run:
	python server.py

# Сборка Docker образа
docker-build:
	docker build -t mcp-yandex-search .

# Запуск через Docker
docker-run:
	docker-compose up -d

# Остановка Docker контейнеров
docker-stop:
	docker-compose down

# Очистка
clean:
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# Проверка кода
lint:
	ruff check .
	mypy .

# Форматирование кода
format:
	ruff format .

# Запуск в режиме разработки
dev-run:
	uvicorn server:app --host 0.0.0.0 --port 8006 --reload 
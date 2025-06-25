# Базовый образ с Python 3.13
FROM python:3.13-slim

# Метаданные образа
LABEL maintainer="MCP Team"
LABEL description="MCP сервер для работы с Cloud.ru Artifact Registry"
LABEL version="1.0.0"

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Установка uv для управления зависимостями
RUN pip install --no-cache-dir uv

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash --uid 1000 app

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей и README
COPY pyproject.toml pytest.ini README.md ./

# Создание виртуального окружения и установка зависимостей
RUN uv venv && \
    uv pip install --no-cache-dir \
        fastmcp>=0.1.0 \
        httpx>=0.24.0 \
        uvicorn>=0.23.0 \
        starlette>=0.27.0

# Копирование кода приложения
COPY server.py example.py ./
COPY test/ ./test/

# Смена владельца файлов
RUN chown -R app:app /app

# Переключение на пользователя app
USER app

# Открытие порта
EXPOSE 8004

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"

# Проверка работоспособности
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8004/sse || exit 1

# Команда запуска
CMD ["python", "server.py"] 
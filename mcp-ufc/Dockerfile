# Базовый образ с Python 3.13
FROM python:3.13-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка uv для управления зависимостями
RUN pip install uv

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml ./

# Установка зависимостей
RUN uv sync --no-dev

# Копирование кода приложения
COPY . .

# Смена владельца файлов
RUN chown -R app:app /app

# Переключение на пользователя app
USER app

# Открытие порта
EXPOSE 8005

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV UV_SYSTEM_PYTHON=1

# Команда запуска
CMD ["uv", "run", "python", "server.py"] 
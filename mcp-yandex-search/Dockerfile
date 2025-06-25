FROM python:3.13-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Создание рабочей директории
WORKDIR /app

# Копирование файлов проекта
COPY pyproject.toml .
COPY server.py .

# Установка Python зависимостей
RUN pip install -e .

# Создание пользователя для запуска приложения
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Открытие порта
EXPOSE 8006

# Команда запуска
CMD ["python", "server.py", "--host", "0.0.0.0"] 
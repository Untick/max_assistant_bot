FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование requirements.txt и установка Python-зависимостей
COPY services/mcp_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода сервиса и shared
COPY services/mcp_server/ ./services/mcp_server/
COPY shared/ ./shared/

# Экспортирование порта
EXPOSE 8003

# Точка входа - запуск mcp_server
CMD ["python", "-m", "services.mcp_server.server"]

"""
Dockerfile для MCP Server
"""

FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY services/mcp_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY services/mcp_server/ ./services/mcp_server/
COPY shared/ ./shared/

# Установка PYTHONPATH
ENV PYTHONPATH=/app

# Запуск
CMD ["python", "-m", "services.mcp_server.server"]

"""
Dockerfile для tg_gateway
"""

FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY services/tg_gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY services/tg_gateway/ ./services/tg_gateway/
COPY shared/ ./shared/

# Установка PYTHONPATH
ENV PYTHONPATH=/app

# Запуск
CMD ["python", "-m", "services.tg_gateway.main"]

FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование requirements.txt и установка Python-зависимостей
COPY services/tg_gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода сервиса и shared
COPY services/tg_gateway/ ./services/tg_gateway/
COPY shared/ ./shared/

# Экспортирование порта
EXPOSE 8080

# Точка входа - запуск tg_gateway
CMD ["python", "-m", "services.tg_gateway.main"]

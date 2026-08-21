FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование requirements.txt и установка Python-зависимостей
COPY services/scheduler/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода сервиса и shared
COPY services/scheduler/ ./services/scheduler/
COPY shared/ ./shared/

# Точка входа - запуск scheduler jobs
CMD ["python", "-m", "services.scheduler.jobs"]

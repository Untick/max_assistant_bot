"""
Dockerfile для Scheduler Service
"""

FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY services/scheduler/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY services/scheduler/ ./services/scheduler/
COPY shared/ ./shared/

# Установка PYTHONPATH
ENV PYTHONPATH=/app

# Запуск
CMD ["python", "-m", "services.scheduler.jobs"]

"""
Dockerfile для ASR Service
"""

FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    cmake \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY services/asr/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY services/asr/ ./services/asr/
COPY shared/ ./shared/

# Установка PYTHONPATH
ENV PYTHONPATH=/app

# Запуск (ASR работает как HTTP-сервис)
CMD ["python", "-m", "uvicorn", "services.asr.server:app", "--host", "0.0.0.0", "--port", "8001"]

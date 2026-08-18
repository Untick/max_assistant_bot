FROM python:3.11-slim

# Установка системных зависимостей, включая ffmpeg для конвертации аудио
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование requirements.txt и установка Python-зависимостей
COPY services/asr/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода сервиса
COPY services/asr/ ./services/asr/
COPY shared/ ./shared/

# Экспортирование порта
EXPOSE 8000

# Точка входа - запуск ASR сервиса через uvicorn
CMD ["uvicorn", "services.asr.server:app", "--host", "0.0.0.0", "--port", "8000"]

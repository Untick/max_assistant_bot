FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование requirements.txt и установка Python-зависимостей (включая FAISS и sentence-transformers)
COPY services/rag/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода сервиса и shared
COPY services/rag/ ./services/rag/
COPY shared/ ./shared/

# Экспортирование порта
EXPOSE 8002

# Точка входа - запуск rag ingest
CMD ["python", "-m", "services.rag.ingest"]

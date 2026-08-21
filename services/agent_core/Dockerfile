FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование requirements.txt и установка Python-зависимостей
COPY services/agent_core/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода сервиса и shared
COPY services/agent_core/ ./services/agent_core/
COPY shared/ ./shared/

# Экспортирование порта
EXPOSE 8001

# Точка входа - запуск agent_core
CMD ["python", "-m", "services.agent_core.agent"]

"""
Dockerfile для Agent Core
"""

FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY services/agent_core/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY services/agent_core/ ./services/agent_core/
COPY shared/ ./shared/

# Установка PYTHONPATH
ENV PYTHONPATH=/app

# Запуск
CMD ["python", "-m", "services.agent_core.agent"]

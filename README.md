# Personal Planner - LLM-Агент Персонального Планирования

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-compose-latest-blue.svg)](https://docs.docker.com/compose/)

Микросервисная система персонального планирования с голосовым и текстовым интерфейсом через Telegram.

## 📋 Возможности

- 🎤 **Голосовые сообщения** — транскрибация через Whisper с сохранением пунктуации
- 📅 **Календарь** — интеграция с Google Calendar, проверка пересечений, буфер 120 минут
- ✅ **Задачи** — управление задачами с автоматическим контролем дедлайнов
- ⏰ **Напоминания** — многоуровневые уведомления (48ч, 24ч, 10:00, 30мин)
- 🔍 **RAG-поиск** — контекстный поиск по истории встреч и диалогов
- 🛡️ **Безопасность** — шифрование токенов, PII-фильтрация, защита от инъекций
- 🕐 **МСК** — жесткая фиксация московского времени для всех операций

## 🏗️ Архитектура

```
personal-planner/
├── services/
│   ├── tg_gateway/       # Telegram Bot (Aiogram 3.x)
│   ├── asr/              # Транскрибация (Whisper)
│   ├── agent_core/       # LLM Agent (LangChain/LangGraph)
│   ├── mcp_server/       # Инструменты (FastMCP)
│   ├── rag/              # RAG-поиск (FAISS + SQLite FTS5)
│   └── scheduler/        # Напоминания (APScheduler)
├── shared/               # Общие модули
├── storage/              # Миграции БД
├── tests/                # Тесты
└── docs/                 # Документация
```

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)
- Токен Telegram бота
- OAuth credentials Google (опционально)
- LLM API endpoint (open-source модель)

### Шаг 1: Клонирование репозитория

```bash
git clone <repository-url>
cd personal-planner
```

### Шаг 2: Настройка переменных окружения

Скопируйте файл `.env.example` в `.env` и заполните необходимые значения:

```bash
cp .env.example .env
```

**⚠️ ПЕРЕД ПЕРВЫМ ЗАПУСКОМ НЕОБХОДИМО ЗАПОЛНИТЬ:**

Откройте `.env` и установите следующие обязательные параметры:

```ini
# Обязательно: Токен Telegram бота
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Обязательно: LLM API (open-source модель)
LLM_API_BASE_URL=https://your-llm-provider.com/v1
LLM_API_KEY=your_llm_api_key_here

# Обязательно: Ключ шифрования (32 байта hex)
ENCRYPTION_KEY=your_32_byte_random_key_hex_here

# Опционально: Google OAuth (для интеграции с календарем)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
```

**🔒 ВАЖНО: Файл `.env` содержит секретные ключи и добавлен в `.gitignore`. НИКОГДА не коммитьте его в репозиторий!**

#### Как получить токен Telegram бота:

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен

#### Как получить LLM API ключ:

Рекомендуемые провайдеры open-source моделей:
- [OpenRouter](https://openrouter.ai/) — доступ к различным моделям
- [Together AI](https://together.ai/) — открытые модели
- Локальная установка: [Ollama](https://ollama.ai/), [vLLM](https://github.com/vllm-project/vllm)

#### Генерация ключа шифрования:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Шаг 3: Запуск сервисов

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### Шаг 4: Проверка работы

1. Найдите своего бота в Telegram по username
2. Отправьте команду `/start`
3. Бот ответит приветственным сообщением

## 📝 Использование

### Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Начать работу |
| `/help` | Показать справку |
| `/schedule` | Расписание на сегодня |
| `/tasks` | Список задач |

### Примеры запросов

**Текст:**
```
Запиши встречу с командой завтра в 15:00
```

**Голосовое сообщение:**
```
[голосовое] "Нужно подготовить отчет к пятнице"
```

**Проверка расписания:**
```
Покажи встречи на завтра
Свободен ли я в пятницу в 14:00?
```

## 🔧 Разработка

### Установка зависимостей (локально)

```bash
pip install -r services/tg_gateway/requirements.txt
pip install -r services/asr/requirements.txt
pip install -r services/agent_core/requirements.txt
```

### Запуск отдельных сервисов

```bash
# Telegram Gateway
python -m services.tg_gateway.main

# ASR Service
python -m uvicorn services.asr.server:app --host 0.0.0.0 --port 8001
```

### Тестирование

```bash
# Unit тесты
make test

# E2E тесты
make test-e2e
```

### Makefile команды

```bash
make up          # Запуск всех сервисов
make down        # Остановка сервисов
make build       # Пересборка контейнеров
make logs        # Просмотр логов
make shell-tg    # Shell в tg_gateway
make shell-agent # Shell в agent_core
make test        # Запуск тестов
make clean       # Очистка томов и кэшей
```

## 📚 Документация

- [Техническое задание](docs/tz.md)
- [Архитектура](docs/architecture.md)
- [Системные промпты](docs/prompts/)

## 🔒 Безопасность

- Шифрование токенов доступа (Fernet)
- PII-фильтрация перед отправкой в LLM
- Защита от prompt injection
- Валидация дат на уровне кода
- Строгий парсинг JSON ответов

## 📊 Мониторинг

- Сквозное логирование всех запросов
- Трассировка latency
- Аудит действий пользователя
- Версионирование промптов

## 💰 Стоимость эксплуатации

| Компонент | Стоимость (мес) |
|-----------|-----------------|
| VPS сервер | 500-1000 руб |
| LLM API | ~1000 руб |
| Итого | 1000-2500 руб |

## ⚠️ Риски и митигация

| Риск | Стратегия |
|------|-----------|
| Ошибка распознавания имен | Контекстные словари, постобработка |
| Недоступность LLM API | Retry + fallback на локальную модель |
| Превышение лимитов токенов | Динамическое сжатие контекста |
| Некорректные даты | Валидация кодом, get_date инструмент |

## 📄 Лицензия

MIT License

## 👥 Контакты

Для вопросов и предложений создайте Issue в репозитории.

"""
Telegram Gateway - точка входа Aiogram 3.x
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.redis import RedisStorage
from shared.config import settings
from shared.logging.tracing import get_logger

logger = get_logger("tg_gateway", settings.LOG_LEVEL)


async def main():
    """Основная функция запуска бота"""
    
    # Проверка наличия токена
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.log_error(0, "startup", "TELEGRAM_BOT_TOKEN не установлен")
        raise ValueError("Необходимо установить TELEGRAM_BOT_TOKEN в .env файле")
    
    # Инициализация бота и диспетчера
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    storage = RedisStorage.from_url(settings.REDIS_URL)
    dp = Dispatcher(storage=storage)
    
    # Регистрация хендлеров
    @dp.message(CommandStart())
    async def cmd_start(message: types.Message):
        """Обработчик команды /start"""
        user_id = message.from_user.id
        logger.log_request(user_id, "command_start", {"text": "/start"})
        
        await message.answer(
            "👋 Привет! Я ваш персональный планировщик.\n\n"
            "Я могу помочь вам:\n"
            "• 📅 Запланировать встречу\n"
            "• ✅ Создать задачу\n"
            "• 🔍 Проверить расписание\n"
            "• ⏰ Установить напоминание\n\n"
            "Просто напишите мне или отправьте голосовое сообщение!"
        )
        
        logger.log_response(user_id, "command_start", {"status": "ok"}, 0)
    
    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        """Обработчик команды /help"""
        user_id = message.from_user.id
        
        await message.answer(
            "📚 Помощь:\n\n"
            "Команды:\n"
            "/start - Начать работу\n"
            "/help - Показать эту справку\n"
            "/schedule - Показать расписание на сегодня\n"
            "/tasks - Показать задачи\n"
            "\n"
            "Вы также можете:\n"
            "• Отправить текстовое сообщение с описанием встречи/задачи\n"
            "• Отправить голосовое сообщение для быстрого добавления"
        )
    
    @dp.message(Command("schedule"))
    async def cmd_schedule(message: types.Message):
        """Обработчик команды /schedule"""
        user_id = message.from_user.id
        logger.log_request(user_id, "command_schedule", {"text": "/schedule"})
        
        # TODO: Интеграция с agent_core для получения расписания
        await message.answer("📅 Расписание на сегодня:\n\nЗагрузка...")
        
        logger.log_response(user_id, "command_schedule", {"status": "ok"}, 0)
    
    @dp.message(Command("tasks"))
    async def cmd_tasks(message: types.Message):
        """Обработчик команды /tasks"""
        user_id = message.from_user.id
        logger.log_request(user_id, "command_tasks", {"text": "/tasks"})
        
        # TODO: Интеграция с agent_core для получения задач
        await message.answer("✅ Ваши задачи:\n\nЗагрузка...")
        
        logger.log_response(user_id, "command_tasks", {"status": "ok"}, 0)
    
    @dp.message()
    async def handle_message(message: types.Message):
        """Обработчик обычных сообщений"""
        user_id = message.from_user.id
        
        if message.text:
            logger.log_request(user_id, "text_message", {"text": message.text})
            # TODO: Отправка в agent_core для обработки
            await message.answer("Сообщение получено. Обрабатываю...")
            logger.log_response(user_id, "text_message", {"status": "received"}, 0)
        
        elif message.voice:
            logger.log_request(user_id, "voice_message", {"file_id": message.voice.file_id})
            # TODO: Отправка в asr_service для транскрибации
            await message.answer("Голосовое сообщение получено. Расшифровываю...")
            logger.log_response(user_id, "voice_message", {"status": "received"}, 0)
    
    # Запуск polling
    logger.log_request(0, "bot_startup", {"status": "starting"})
    print(f"Бот запущен (@{(await bot.get_me()).username})")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

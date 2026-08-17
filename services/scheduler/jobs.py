"""
Scheduler Service - Напоминания и задачи (APScheduler)
Напоминания: за 48 ч, за 24 ч, в 10:00 дня встречи, за 30 мин (п. 3.7)
"""

from datetime import datetime, timedelta
from typing import List, Optional
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from shared.config import settings
from shared.logging.tracing import get_logger

logger = get_logger("scheduler_service", settings.LOG_LEVEL)


class ReminderScheduler:
    """Планировщик напоминаний"""
    
    REMINDER_TYPES = {
        '48h': {'hours': 48},
        '24h': {'hours': 24},
        '10am': {'hour': 10, 'minute': 0},  # 10:00 дня встречи
        '30min': {'minutes': 30},
    }
    
    def __init__(self, timezone: str = None):
        self.timezone = ZoneInfo(timezone or settings.SCHEDULER_TIMEZONE)
        self.scheduler = AsyncIOScheduler(timezone=self.timezone)
    
    def start(self):
        """Запуск планировщика"""
        self.scheduler.start()
        logger.log_request(0, "scheduler_start", {"timezone": str(self.timezone)})
    
    def stop(self):
        """Остановка планировщика"""
        self.scheduler.shutdown()
        logger.log_request(0, "scheduler_stop", {})
    
    def schedule_meeting_reminders(self, user_id: int, event_id: str, 
                                   event_datetime: datetime, title: str):
        """
        Планирование напоминаний для встречи
        
        Args:
            user_id: ID пользователя
            event_id: ID события
            event_datetime: Дата и время встречи
            title: Название встречи
        """
        reminders_added = []
        
        for reminder_type, config in self.REMINDER_TYPES.items():
            send_at = self._calculate_reminder_time(event_datetime, config)
            
            if send_at and send_at > datetime.now(self.timezone):
                message = self._build_reminder_message(title, event_datetime, reminder_type)
                
                self.scheduler.add_job(
                    self._send_reminder,
                    trigger=DateTrigger(run_date=send_at),
                    args=[user_id, event_id, reminder_type, message],
                    id=f"{event_id}_{reminder_type}"
                )
                
                reminders_added.append(reminder_type)
        
        logger.log_response(user_id, "schedule_reminders", {
            "event_id": event_id,
            "reminders": reminders_added
        }, 0)
    
    def _calculate_reminder_time(self, event_datetime: datetime, 
                                  config: dict) -> Optional[datetime]:
        """Расчет времени отправки напоминания"""
        if 'hour' in config:
            # 10:00 дня встречи
            return event_datetime.replace(
                hour=config['hour'], 
                minute=config.get('minute', 0),
                second=0,
                microsecond=0
            )
        else:
            # Относительное время (48h, 24h, 30min)
            delta = timedelta(**config)
            return event_datetime - delta
    
    def _build_reminder_message(self, title: str, event_datetime: datetime,
                                reminder_type: str) -> str:
        """Построение текста напоминания"""
        type_labels = {
            '48h': '⏰ Напоминание за 48 часов',
            '24h': '⏰ Напоминание за 24 часа',
            '10am': '🌅 Сегодня в 10:00',
            '30min': '⚡ Встреча через 30 минут',
        }
        
        label = type_labels.get(reminder_type, 'Напоминание')
        
        return (f"{label}\n\n"
                f"📅 {title}\n"
                f"🕐 {event_datetime.strftime('%d.%m.%Y %H:%MSK')}")
    
    async def _send_reminder(self, user_id: int, event_id: str,
                            reminder_type: str, message: str):
        """Отправка напоминания (через tg_gateway)"""
        logger.log_request(user_id, "send_reminder", {
            "event_id": event_id,
            "type": reminder_type
        })
        
        # TODO: Интеграция с tg_gateway для отправки
        print(f"Reminder to user {user_id}: {message}")
        
        logger.log_response(user_id, "send_reminder", {"status": "sent"}, 0)


class DailySummaryJob:
    """Ежедневная сводка (п. 2.4)"""
    
    def __init__(self, scheduler: ReminderScheduler):
        self.scheduler = scheduler.scheduler
        self.run_time = "10:00"  # Время отправки сводки
    
    def schedule_daily(self):
        """Планирование ежедневной сводки"""
        self.scheduler.add_job(
            self.send_daily_summary,
            trigger='cron',
            hour=10,
            minute=0,
            timezone=settings.SCHEDULER_TIMEZONE,
            id='daily_summary'
        )
    
    async def send_daily_summary(self):
        """Отправка ежедневной сводки"""
        logger.log_request(0, "daily_summary", {"time": self.run_time})
        
        # TODO: Получение встреч на день из календаря
        # TODO: Формирование сводки
        # TODO: Отправка через tg_gateway
        
        logger.log_response(0, "daily_summary", {"status": "sent"}, 0)


# Глобальный экземпляр
reminder_scheduler = ReminderScheduler(settings.SCHEDULER_TIMEZONE)
daily_summary = DailySummaryJob(reminder_scheduler)


def start_scheduler():
    """Запуск планировщика"""
    reminder_scheduler.start()
    daily_summary.schedule_daily()
    logger.log_request(0, "scheduler_init", {"status": "started"})


if __name__ == "__main__":
    import asyncio
    
    start_scheduler()
    
    # Тестовое планирование
    test_event = datetime.now(ZoneInfo(settings.TIMEZONE)) + timedelta(days=1)
    reminder_scheduler.schedule_meeting_reminders(
        user_id=123,
        event_id="test_event",
        event_datetime=test_event,
        title="Тестовая встреча"
    )
    
    print("Scheduler started. Press Ctrl+C to stop.")
    try:
        while True:
            asyncio.run(asyncio.sleep(1))
    except KeyboardInterrupt:
        reminder_scheduler.stop()

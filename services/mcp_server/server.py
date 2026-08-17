"""
MCP Server - FastMCP сервер инструментов
"""

from fastmcp import FastMCP
from datetime import datetime, timedelta
from typing import List, Optional
from zoneinfo import ZoneInfo
from shared.config import settings
from shared.logging.tracing import get_logger

logger = get_logger("mcp_server", settings.LOG_LEVEL)

# Инициализация MCP сервера
mcp = FastMCP("Personal Planner MCP")


@mcp.tool()
def get_date() -> str:
    """
    Получить текущую дату (якорь для относительных дат, п. R-04)
    
    Returns:
        Текущая дата в формате ISO 8601 с часовым поясом МСК
    """
    tz = ZoneInfo(settings.TIMEZONE)
    now = datetime.now(tz)
    return now.isoformat()


@mcp.tool()
def calendar_read(start_date: str, end_date: Optional[str] = None) -> dict:
    """
    Чтение событий календаря
    
    Args:
        start_date: Дата начала в формате YYYY-MM-DD
        end_date: Дата окончания (опционально)
    
    Returns:
        Словарь с событиями календаря
    """
    logger.log_request(0, "calendar_read", {"start": start_date, "end": end_date})
    
    # TODO: Интеграция с Google Calendar API
    # Здесь будет вызов connectors/google_calendar.py
    
    return {
        "events": [],
        "status": "ok"
    }


@mcp.tool()
def calendar_create(title: str, datetime_str: str, duration_minutes: int = 60, 
                   participants: Optional[List[str]] = None) -> dict:
    """
    Создание события в календаре
    
    Args:
        title: Название события
        datetime_str: Дата и время в формате ISO 8601
        duration_minutes: Длительность в минутах
        participants: Список участников
    
    Returns:
        Результат создания
    """
    logger.log_request(0, "calendar_create", {
        "title": title,
        "datetime": datetime_str,
        "duration": duration_minutes
    })
    
    # Проверка буфера 120 минут (п. 3.3)
    buffer_check = check_time_buffer(datetime_str, duration_minutes)
    if not buffer_check["is_ok"]:
        return {
            "status": "conflict",
            "message": "Обнаружено пересечение с другим событием",
            "alternative_slots": buffer_check.get("alternatives", [])
        }
    
    # TODO: Создание через Google Calendar API
    
    return {
        "status": "created",
        "event_id": "new_event_id"
    }


@mcp.tool()
def availability_check(datetime_str: str) -> dict:
    """
    Проверка доступности времени (п. 3.10)
    
    Args:
        datetime_str: Дата и время для проверки
    
    Returns:
        Ответ о доступности: «свободно» / «занято»
    """
    logger.log_request(0, "availability_check", {"datetime": datetime_str})
    
    # TODO: Проверка через Google Calendar API
    
    is_available = True  # Заглушка
    
    return {
        "is_available": is_available,
        "message": "свободно" if is_available else "занято",
        "requested_datetime": datetime_str
    }


@mcp.tool()
def task_tools(action: str, task_id: Optional[str] = None, 
              title: Optional[str] = None) -> dict:
    """
    Инструменты для управления задачами
    
    Args:
        action: Действие (create, update, status, move, ask_reason)
        task_id: ID задачи
        title: Название задачи
    
    Returns:
        Результат операции
    """
    logger.log_request(0, "task_tools", {"action": action, "task_id": task_id})
    
    # TODO: Интеграция с Google Tasks API
    
    return {
        "status": "ok",
        "data": {}
    }


@mcp.tool()
def meeting_notes(meeting_id: str) -> dict:
    """
    Получение карточки итогов встречи
    
    Args:
        meeting_id: ID встречи
    
    Returns:
        Карточка встречи с решениями и следующими шагами
    """
    logger.log_request(0, "meeting_notes", {"meeting_id": meeting_id})
    
    # TODO: Получение из хранилища карточек
    
    return {
        "meeting_id": meeting_id,
        "title": "",
        "participants": [],
        "key_decisions": [],
        "action_items": [],
        "next_steps": []
    }


def check_time_buffer(datetime_str: str, duration_minutes: int) -> dict:
    """
    Проверка буфера 120 минут между встречами (п. 3.3)
    
    Args:
        datetime_str: Дата и время нового события
        duration_minutes: Длительность нового события
    
    Returns:
        Результат проверки с альтернативными слотами при конфликте
    """
    BUFFER_MINUTES = 120
    
    try:
        new_start = datetime.fromisoformat(datetime_str)
        new_end = new_start + timedelta(minutes=duration_minutes)
        
        # TODO: Получить существующие события из календаря
        existing_events = []  # Заглушка
        
        for event in existing_events:
            event_start = datetime.fromisoformat(event["start"])
            event_end = datetime.fromisoformat(event["end"])
            
            # Проверка пересечения с буфером
            if (new_start < event_end + timedelta(minutes=BUFFER_MINUTES) and
                new_end + timedelta(minutes=BUFFER_MINUTES) > event_start):
                
                # Конфликт найден, предложить альтернативы
                alternatives = suggest_alternative_slots(new_start, duration_minutes)
                
                return {
                    "is_ok": False,
                    "conflicting_event": event,
                    "alternatives": alternatives
                }
        
        return {"is_ok": True}
        
    except Exception as e:
        logger.log_error(0, "buffer_check", str(e))
        return {"is_ok": True}  # При ошибке пропускаем


def suggest_alternative_slots(base_datetime: datetime, duration_minutes: int) -> List[str]:
    """Предложение альтернативных слотов при конфликте (п. 3.4)"""
    alternatives = []
    
    # Предложить слоты на следующий день
    next_day = base_datetime.replace(hour=10, minute=0, second=0) + timedelta(days=1)
    
    for i in range(5):
        slot = next_day + timedelta(hours=i * 2)
        alternatives.append(slot.isoformat())
    
    return alternatives


if __name__ == "__main__":
    # Запуск MCP сервера
    mcp.run()

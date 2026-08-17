"""
Извлечение и валидация сущностей (даты, участники)
Валидация дат кодом (п. 10.1, R-04)
"""

import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from zoneinfo import ZoneInfo
from shared.config import settings
from shared.logging.tracing import get_logger

logger = get_logger("agent_core", settings.LOG_LEVEL)


class DateExtractor:
    """Извлечение и валидация дат"""
    
    # Дни недели
    DAYS_OF_WEEK = {
        'понедельник': 0, 'вторник': 1, 'среда': 2, 'четверг': 3,
        'пятница': 4, 'суббота': 5, 'воскресенье': 6
    }
    
    # Относительные даты
    RELATIVE_DATES = {
        'завтра': 1,
        'послезавтра': 2,
        'сегодня': 0,
    }
    
    def __init__(self, timezone: str = "Europe/Moscow"):
        self.timezone = ZoneInfo(timezone)
    
    def get_current_date(self) -> datetime:
        """Получение текущей даты (инструмент get_date, п. R-04)"""
        return datetime.now(self.timezone)
    
    def parse_relative_date(self, text: str, base_date: Optional[datetime] = None) -> Optional[datetime]:
        """Парсинг относительных дат"""
        if base_date is None:
            base_date = self.get_current_date()
        
        text_lower = text.lower()
        
        # Проверка относительных дат
        for rel_word, days_offset in self.RELATIVE_DATES.items():
            if rel_word in text_lower:
                return base_date + timedelta(days=days_offset)
        
        # Проверка дней недели
        for day_name, weekday_num in self.DAYS_OF_WEEK.items():
            if day_name in text_lower:
                current_weekday = base_date.weekday()
                days_until = (weekday_num - current_weekday) % 7
                if days_until == 0:
                    days_until = 7
                return base_date + timedelta(days=days_until)
        
        if 'через неделю' in text_lower:
            return base_date + timedelta(weeks=1)
        
        return None
    
    def parse_time(self, text: str) -> Optional[str]:
        """Парсинг времени из текста"""
        time_patterns = [
            r'(\d{1,2})[:.\-](\d{2})',
            r'(\d{1,2})\s*час(?:а|ов)?\s*(?:дня|утра|вечера)?',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return f"{match.group(1)}:{match.group(2)}"
                else:
                    hour = int(match.group(1))
                    if 'вечера' in text or 'ночи' in text:
                        if hour < 12:
                            hour += 12
                    elif 'утра' in text and hour == 12:
                        hour = 0
                    return f"{hour:02d}:00"
        
        return None
    
    def parse_absolute_date(self, text: str) -> Optional[datetime]:
        """Парсинг абсолютных дат"""
        date_patterns = [
            (r'(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})', '%d.%m.%Y'),
            (r'(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})', '%Y.%m.%d'),
        ]
        
        for pattern, fmt in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    date_str = match.group(0).replace('/', '.').replace('-', '.')
                    return datetime.strptime(date_str, fmt.replace('/', '.').replace('-', '.'))
                except ValueError:
                    continue
        
        return None
    
    def validate_datetime(self, dt: datetime) -> bool:
        """Валидация даты (п. 10.1)"""
        now = self.get_current_date()
        
        if dt < now - timedelta(days=1):
            return False
        
        if dt > now + timedelta(days=365):
            return False
        
        return True
    
    def extract_datetime(self, text: str) -> Optional[datetime]:
        """Извлечение полной даты и времени из текста"""
        date = self.parse_absolute_date(text)
        
        if date is None:
            date = self.parse_relative_date(text)
        
        if date:
            time_str = self.parse_time(text)
            if time_str:
                hour, minute = map(int, time_str.split(':'))
                date = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if date and not self.validate_datetime(date):
            logger.log_error(0, "date_validation", f"Invalid date: {date}")
            return None
        
        return date


class ParticipantExtractor:
    """Извлечение участников из текста"""
    
    PARTICIPANT_PATTERNS = [
        r'с\s+([А-Я][а-я]+(?:\s+[А-Я][а-я]+)?)',
        r'и\s+([А-Я][а-я]+)',
        r'участники?:?\s*([^\n]+)',
        r'команда',
    ]
    
    def extract(self, text: str) -> List[str]:
        """Извлечение списка участников"""
        participants = []
        
        for pattern in self.PARTICIPANT_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                
                participant = match.strip().rstrip(',.!')
                
                if participant and participant not in participants:
                    participants.append(participant)
        
        return participants


# Глобальные экземпляры
date_extractor = DateExtractor(settings.TIMEZONE)
participant_extractor = ParticipantExtractor()


def extract_entities(text: str) -> Dict[str, Any]:
    """Извлечение всех сущностей из текста"""
    return {
        'datetime': date_extractor.extract_datetime(text),
        'participants': participant_extractor.extract(text),
    }


if __name__ == "__main__":
    test_texts = [
        "Завтра в 15:00",
        "В пятницу в 14:00",
        "Через неделю с командой",
        "15.01.2024 в 10:00",
    ]
    
    for text in test_texts:
        entities = extract_entities(text)
        print(f"Текст: {text}")
        print(f"Дата/время: {entities['datetime']}")
        print(f"Участники: {entities['participants']}")
        print("-" * 40)

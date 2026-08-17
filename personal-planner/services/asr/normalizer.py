"""
Нормализация текста после транскрибации
Очистка артефактов речи, нормализация дат и имен
"""

import re
from datetime import datetime
from typing import List, Tuple
from shared.logging.tracing import get_logger
from shared.config import settings

logger = get_logger("asr_service", settings.LOG_LEVEL)


class TextNormalizer:
    """Нормализация текста после ASR"""
    
    # Артефакты речи для удаления
    SPEECH_ARTIFACTS = [
        r'\bэ-э\b',
        r'\bммм\b',
        r'\bэээ\b',
        r'\bну\b',
        r'\bтак сказать\b',
        r'\bв общем\b',
        r'\bкороче\b',
    ]
    
    # Замена числительных
    NUMBER_WORDS = {
        'один': '1', 'одна': '1', 'одно': '1',
        'два': '2', 'две': '2',
        'три': '3', 'четыре': '4', 'пять': '5',
        'шесть': '6', 'семь': '7', 'восемь': '8', 'девять': '9',
        'десять': '10', 'пятнадцать': '15', 'двадцать': '20',
        'тридцать': '30', 'сорок': '40', 'пятьдесят': '50',
        'час': 'час', 'часа': 'часа', 'часов': 'часов',
        'минута': 'минута', 'минуты': 'минуты', 'минут': 'минут',
    }
    
    def __init__(self):
        self.artifact_patterns = [re.compile(p, re.IGNORECASE) for p in self.SPEECH_ARTIFACTS]
    
    def remove_artifacts(self, text: str) -> str:
        """Удаление артефактов речи"""
        cleaned = text
        for pattern in self.artifact_patterns:
            cleaned = pattern.sub('', cleaned)
        
        # Удаление множественных пробелов
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()
    
    def normalize_numbers(self, text: str) -> str:
        """Нормализация числительных"""
        normalized = text
        for word, number in self.NUMBER_WORDS.items():
            normalized = re.sub(
                rf'\b{word}\b',
                number,
                normalized,
                flags=re.IGNORECASE
            )
        return normalized
    
    def normalize_punctuation(self, text: str) -> str:
        """Нормализация пунктуации"""
        # Исправление двойной пунктуации
        text = re.sub(r'([.,!?;:])\1+', r'\1', text)
        
        # Пробелы после знаков препинания
        text = re.sub(r'([.,!?;:])([^\s])', r'\1 \2', text)
        
        return text
    
    def extract_datetime_mentions(self, text: str) -> List[Tuple[str, str]]:
        """
        Извлечение упоминаний дат и времени
        
        Returns:
            Список кортежей (тип, значение)
        """
        mentions = []
        
        # Время в формате 14:00, 14.00, 14-00
        time_pattern = r'\b(\d{1,2})[:.\-](\d{2})\b'
        for match in re.finditer(time_pattern, text):
            mentions.append(('time', match.group()))
        
        # Относительные даты
        relative_dates = [
            'завтра', 'послезавтра', 'сегодня',
            'в понедельник', 'во вторник', 'в среду', 'в четверг', 'в пятницу', 'в субботу', 'в воскресенье',
            'на следующей неделе', 'через неделю',
        ]
        for date_word in relative_dates:
            if date_word in text.lower():
                mentions.append(('relative_date', date_word))
        
        return mentions
    
    def normalize(self, text: str) -> str:
        """Полная нормализация текста"""
        try:
            logger.log_request(0, "normalize", {"input_length": len(text)})
            
            # Шаги нормализации
            text = self.remove_artifacts(text)
            text = self.normalize_punctuation(text)
            text = self.normalize_numbers(text)
            
            logger.log_response(0, "normalize", {"output_length": len(text)}, 0)
            return text
            
        except Exception as e:
            logger.log_error(0, "normalize", str(e))
            return text  # Возвращаем исходный текст при ошибке


# Глобальный экземпляр
normalizer = TextNormalizer()


def normalize_text(text: str) -> str:
    """Удобная функция для нормализации"""
    return normalizer.normalize(text)


def extract_datetime_info(text: str) -> List[Tuple[str, str]]:
    """Извлечение информации о дате/времени"""
    return normalizer.extract_datetime_mentions(text)


if __name__ == "__main__":
    # Тестирование
    test_text = "Э-э, встреча завтра в 14:00, ммм, с командой"
    normalized = normalize_text(test_text)
    print(f"Исходный: {test_text}")
    print(f"Нормализованный: {normalized}")
    print(f"Дата/время: {extract_datetime_info(normalized)}")

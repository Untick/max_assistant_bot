"""
PII-фильтр для защиты персональных данных
"""

import re
from typing import List, Tuple


class PIIFilter:
    """Фильтр персональной информации (PII)"""
    
    # Паттерны для обнаружения PII
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone_ru': r'\b(?:\+7|8)\s?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}\b',
        'passport': r'\b\d{4}\s?\d{6}\b',
        'snils': r'\b\d{3}-\d{3}-\d{3}\s?\d{2}\b',
        'inn': r'\b\d{10}\b|\b\d{12}\b',
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
    }
    
    REPLACEMENT_TOKENS = {
        'email': '[EMAIL]',
        'phone_ru': '[PHONE]',
        'passport': '[PASSPORT]',
        'snils': '[SNILS]',
        'inn': '[INN]',
        'credit_card': '[CREDIT_CARD]',
    }
    
    def __init__(self):
        self.compiled_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.PATTERNS.items()
        }
    
    def filter_text(self, text: str) -> Tuple[str, List[dict]]:
        """
        Фильтрация PII из текста
        
        Args:
            text: Исходный текст
            
        Returns:
            Tuple отфильтрованного текста и списка найденных PII
        """
        found_pii = []
        filtered_text = text
        
        for pii_type, pattern in self.compiled_patterns.items():
            matches = list(pattern.finditer(filtered_text))
            for match in matches:
                found_pii.append({
                    'type': pii_type,
                    'value': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
                replacement = self.REPLACEMENT_TOKENS.get(pii_type, '[REDACTED]')
                filtered_text = filtered_text[:match.start()] + replacement + filtered_text[match.end():]
        
        return filtered_text, found_pii
    
    def contains_pii(self, text: str) -> bool:
        """Проверка наличия PII в тексте"""
        _, found = self.filter_text(text)
        return len(found) > 0
    
    def get_pii_types(self, text: str) -> List[str]:
        """Получение типов PII в тексте"""
        _, found = self.filter_text(text)
        return list(set(item['type'] for item in found))


# Глобальный экземпляр
pii_filter = PIIFilter()


def filter_pii(text: str) -> str:
    """Удобная функция для фильтрации PII"""
    filtered, _ = pii_filter.filter_text(text)
    return filtered


def check_pii(text: str) -> bool:
    """Проверка наличия PII"""
    return pii_filter.contains_pii(text)

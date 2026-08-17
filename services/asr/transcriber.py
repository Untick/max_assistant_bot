"""
ASR Service - транскрибация голосовых сообщений через Whisper
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional
import whisper
from shared.config import settings
from shared.logging.tracing import get_logger

logger = get_logger("asr_service", settings.LOG_LEVEL)


class TranscriberInterface(ABC):
    """Абстрактный интерфейс для транскрибера (п. 10.3 - защита от vendor lock-in)"""
    
    @abstractmethod
    async def transcribe(self, audio_file_path: str) -> str:
        """
        Транскрибация аудиофайла
        
        Args:
            audio_file_path: Путь к аудиофайлу
            
        Returns:
            Распознанный текст
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Проверка доступности сервиса"""
        pass


class WhisperTranscriber(TranscriberInterface):
    """Реализация транскрибера на основе Whisper"""
    
    def __init__(self, model_size: str = "base", language: str = "ru"):
        """
        Инициализация транскрибера
        
        Args:
            model_size: Размер модели (tiny, base, small, medium, large)
            language: Язык распознавания
        """
        self.model_size = model_size
        self.language = language
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Загрузка модели Whisper"""
        try:
            logger.log_request(0, "load_model", {"model_size": self.model_size})
            self.model = whisper.load_model(self.model_size)
            logger.log_response(0, "load_model", {"status": "loaded"}, 0)
        except Exception as e:
            logger.log_error(0, "load_model", str(e))
            raise
    
    async def transcribe(self, audio_file_path: str) -> str:
        """Транскрибация аудиофайла"""
        try:
            logger.log_request(0, "transcribe", {"file": audio_file_path})
            
            if self.model is None:
                raise RuntimeError("Модель не загружена")
            
            # Транскрибация с настройками
            options = {
                "language": self.language,
                "task": "transcribe",
                "fp16": False,  # Для совместимости с CPU
            }
            
            result = self.model.transcribe(audio_file_path, **options)
            text = result["text"].strip()
            
            logger.log_response(0, "transcribe", {"text_length": len(text)}, 0)
            return text
            
        except Exception as e:
            logger.log_error(0, "transcribe", str(e))
            raise
    
    async def is_available(self) -> bool:
        """Проверка доступности"""
        return self.model is not None


# Глобальный экземпляр
_transcriber: Optional[TranscriberInterface] = None


def get_transcriber() -> TranscriberInterface:
    """Получение экземпляра транскрибера"""
    global _transcriber
    if _transcriber is None:
        _transcriber = WhisperTranscriber(
            model_size=settings.ASR_MODEL_SIZE,
            language=settings.ASR_LANGUAGE
        )
    return _transcriber


async def transcribe_audio(audio_file_path: str) -> str:
    """Удобная функция для транскрибации"""
    transcriber = get_transcriber()
    return await transcriber.transcribe(audio_file_path)


if __name__ == "__main__":
    # Тестирование
    import asyncio
    
    async def test():
        transcriber = get_transcriber()
        print(f"Модель загружена: {await transcriber.is_available()}")
    
    asyncio.run(test())

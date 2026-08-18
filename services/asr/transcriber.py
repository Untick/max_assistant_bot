"""
ASR Service - транскрибация голосовых сообщений через Whisper или Yandex SpeechKit
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional
import whisper
import aiohttp
from shared.config import settings
from shared.logging.tracing import get_logger

logger = get_logger("asr_service", settings.LOG_LEVEL)


class BaseTranscriber(ABC):
    """Абстрактный интерфейс для транскрибера (п. 3.1 и п. 10.3 - защита от vendor lock-in)"""
    
    @abstractmethod
    async def transcribe(self, audio_bytes: bytes) -> str:
        """
        Транскрибация аудио
        
        Args:
            audio_bytes: Сырые байты аудиофайла
            
        Returns:
            Распознанный текст
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Проверка доступности сервиса"""
        pass


class WhisperTranscriber(BaseTranscriber):
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
    
    async def transcribe(self, audio_bytes: bytes) -> str:
        """Транскрибация аудио из байтов"""
        try:
            # Сохраняем байты во временный файл для Whisper
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_bytes)
                temp_path = f.name
            
            try:
                logger.log_request(0, "transcribe", {"file_size": len(audio_bytes)})
                
                if self.model is None:
                    raise RuntimeError("Модель не загружена")
                
                # Транскрибация с настройками
                options = {
                    "language": self.language,
                    "task": "transcribe",
                    "fp16": False,  # Для совместимости с CPU
                }
                
                result = self.model.transcribe(temp_path, **options)
                text = result["text"].strip()
                
                logger.log_response(0, "transcribe", {"text_length": len(text)}, 0)
                return text
            finally:
                os.unlink(temp_path)
                
        except Exception as e:
            logger.log_error(0, "transcribe", str(e))
            raise
    
    async def is_available(self) -> bool:
        """Проверка доступности"""
        return self.model is not None


class YandexSpeechKitTranscriber(BaseTranscriber):
    """Реализация транскрибера на основе Yandex SpeechKit STT API"""
    
    def __init__(
        self,
        api_key: str,
        folder_id: str,
        lang: str = "ru-RU",
        format_: str = "oggopus",
        model: str = "general:rc"
    ):
        """
        Инициализация транскрибера Yandex SpeechKit
        
        Args:
            api_key: API ключ Яндекс.Облака
            folder_id: ID каталога Яндекс.Облака
            lang: Язык распознавания
            format_: Формат аудио (oggopus для Telegram voice)
            model: Модель распознавания
        """
        self.api_key = api_key
        self.folder_id = folder_id
        self.lang = lang
        self.format_ = format_
        self.model = model
        self.endpoint = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Получение HTTP сессии"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Закрытие сессии"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def transcribe(self, audio_bytes: bytes) -> str:
        """Транскрибация аудио через Yandex SpeechKit API"""
        try:
            logger.log_request(0, "yandex_transcribe", {"file_size": len(audio_bytes)})
            
            session = await self._get_session()
            
            # Параметры запроса
            params = {
                "lang": self.lang,
                "format": self.format_,
                "profanityFilter": "true",
                "model": self.model,
                "folderId": self.folder_id,
            }
            
            headers = {
                "Authorization": f"Api-Key {self.api_key}",
            }
            
            async with session.post(
                self.endpoint,
                params=params,
                data=audio_bytes,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"Yandex SpeechKit API error: {response.status} - {error_text}")
                
                result = await response.json()
                
                if "result" not in result:
                    error_message = result.get("errorDetails", "Unknown error")
                    raise RuntimeError(f"Yandex SpeechKit error: {error_message}")
                
                text = result["result"].strip()
                logger.log_response(0, "yandex_transcribe", {"text_length": len(text)}, 0)
                return text
                
        except aiohttp.ClientError as e:
            logger.log_error(0, "yandex_transcribe", f"Network error: {str(e)}")
            raise
        except Exception as e:
            logger.log_error(0, "yandex_transcribe", str(e))
            raise
    
    async def is_available(self) -> bool:
        """Проверка доступности сервиса"""
        return bool(self.api_key and self.folder_id)


class FallbackTranscriber(BaseTranscriber):
    """Транскрибер с fallback-логикой: основной провайдер → Whisper"""
    
    def __init__(self, primary: BaseTranscriber, fallback: WhisperTranscriber):
        """
        Инициализация fallback-транскрибера
        
        Args:
            primary: Основной транскрибер
            fallback: Резервный транскрибер (Whisper)
        """
        self.primary = primary
        self.fallback = fallback
    
    async def transcribe(self, audio_bytes: bytes) -> str:
        """Транскрибация с fallback на Whisper при ошибке"""
        try:
            return await self.primary.transcribe(audio_bytes)
        except Exception as e:
            # Логирование события fallback через модуль трассировки (п. 9.2 ТЗ)
            logger.log_error(
                0,
                "fallback_triggered",
                f"Primary ASR provider failed, switching to Whisper: {str(e)}"
            )
            # Используем fallback
            return await self.fallback.transcribe(audio_bytes)
    
    async def is_available(self) -> bool:
        """Проверка доступности хотя бы одного провайдера"""
        return await self.primary.is_available() or await self.fallback.is_available()


# Глобальный экземпляр
_transcriber: Optional[BaseTranscriber] = None


def create_transcriber() -> BaseTranscriber:
    """Фабрика транскриберов по значению ASR_PROVIDER"""
    whisper_transcriber = WhisperTranscriber(
        model_size=settings.ASR_MODEL_SIZE,
        language=settings.ASR_LANGUAGE
    )
    
    provider = settings.ASR_PROVIDER.lower()
    
    if provider == "yandex":
        if not settings.YANDEX_API_KEY or not settings.YANDEX_FOLDER_ID:
            logger.log_error(
                0,
                "create_transcriber",
                "Yandex provider selected but YANDEX_API_KEY or YANDEX_FOLDER_ID not set, using Whisper"
            )
            return whisper_transcriber
        
        yandex_transcriber = YandexSpeechKitTranscriber(
            api_key=settings.YANDEX_API_KEY,
            folder_id=settings.YANDEX_FOLDER_ID
        )
        
        # Возвращаем транскрибер с fallback-логикой
        return FallbackTranscriber(
            primary=yandex_transcriber,
            fallback=whisper_transcriber
        )
    
    # По умолчанию или явно указан whisper
    return whisper_transcriber


def get_transcriber() -> BaseTranscriber:
    """Получение экземпляра транскрибера"""
    global _transcriber
    if _transcriber is None:
        _transcriber = create_transcriber()
    return _transcriber


async def transcribe_audio(audio_bytes: bytes) -> str:
    """Удобная функция для транскрибации"""
    transcriber = get_transcriber()
    return await transcriber.transcribe(audio_bytes)


if __name__ == "__main__":
    # Тестирование
    import asyncio
    
    async def test():
        transcriber = get_transcriber()
        print(f"Транскрибер: {type(transcriber).__name__}")
        print(f"Доступен: {await transcriber.is_available()}")
    
    asyncio.run(test())

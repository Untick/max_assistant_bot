"""
ASR Service - HTTP сервер для транскрибации голосовых сообщений
"""

import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from shared.config import settings
from shared.logging.tracing import get_logger
from .transcriber import get_transcriber, transcribe_audio

logger = get_logger("asr_service", settings.LOG_LEVEL)

app = FastAPI(
    title="ASR Service",
    description="Сервис транскрибации голосовых сообщений (Whisper / Yandex SpeechKit)",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Инициализация при старте"""
    logger.log_request(0, "startup", {"provider": settings.ASR_PROVIDER})
    transcriber = get_transcriber()
    logger.log_response(0, "startup", {"status": "ready", "transcriber": type(transcriber).__name__}, 0)


@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при остановке"""
    logger.log_request(0, "shutdown", {})
    # Закрытие сессий если нужно
    logger.log_response(0, "shutdown", {"status": "stopped"}, 0)


@app.post("/transcribe", response_model=dict)
async def transcribe_endpoint(file: UploadFile = File(...)):
    """
    Транскрибация аудиофайла
    
    Args:
        file: Аудиофайл (ogg, wav, mp3, oggopus)
        
    Returns:
        JSON с распознанным текстом
    """
    try:
        # Чтение файла
        audio_bytes = await file.read()
        
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty file")
        
        logger.log_request(
            0,
            "transcribe_endpoint",
            {"filename": file.filename, "content_type": file.content_type, "size": len(audio_bytes)}
        )
        
        # Транскрибация
        text = await transcribe_audio(audio_bytes)
        
        logger.log_response(
            0,
            "transcribe_endpoint",
            {"text_length": len(text), "text_preview": text[:50]},
            0
        )
        
        return {"text": text, "status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(0, "transcribe_endpoint", str(e))
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    transcriber = get_transcriber()
    available = await transcriber.is_available()
    
    return {
        "status": "healthy" if available else "degraded",
        "transcriber": type(transcriber).__name__,
        "available": available
    }


@app.get("/")
async def root():
    """Информация о сервисе"""
    return {
        "service": "ASR Service",
        "version": "1.0.0",
        "provider": settings.ASR_PROVIDER,
        "endpoints": ["/transcribe", "/health"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "services.asr.server:app",
        host="0.0.0.0",
        port=settings.ASR_SERVICE_PORT if hasattr(settings, 'ASR_SERVICE_PORT') else 8000,
        log_level=settings.LOG_LEVEL.lower()
    )

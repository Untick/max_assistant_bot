"""
Конфигурация приложения Personal Planner
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    
    # LLM
    LLM_API_BASE_URL: str = "https://api.openai.com/v1"
    LLM_API_KEY: str = ""
    LLM_MODEL_NAME: str = "qwen-2.5-7b-instruct"
    LLM_MAX_TOKENS: int = 1024
    LLM_TEMPERATURE: float = 0.1
    LLM_RETRY_COUNT: int = 3
    LLM_TIMEOUT: int = 30
    
    # ASR (Whisper)
    ASR_MODEL_SIZE: str = "base"
    ASR_LANGUAGE: str = "ru"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/personal_planner"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Timezone
    TIMEZONE: str = "Europe/Moscow"
    
    # RAG
    RAG_CHUNK_SIZE: int = 500
    RAG_TOP_K: int = 3
    RAG_SIMILARITY_THRESHOLD: float = 0.75
    
    # Scheduler
    SCHEDULER_TIMEZONE: str = "Europe/Moscow"
    
    # Security
    ENCRYPTION_KEY: str = ""  # 32 bytes
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Service URLs
    RAG_SERVICE_URL: str = "http://rag_service:8002"
    MCP_SERVER_URL: str = "http://mcp_server:8003"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Глобальный экземпляр настроек
settings = Settings()


def get_settings() -> Settings:
    """Получить настройки приложения"""
    return settings

"""
Pydantic-схемы для обмена данными между сервисами
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class EventEntity(BaseModel):
    """Сущность события календаря"""
    title: str = Field(..., description="Название события")
    datetime: Optional[datetime] = Field(None, description="Дата и время начала")
    duration_minutes: int = Field(default=60, description="Длительность в минутах")
    participants: List[str] = Field(default_factory=list, description="Участники")
    description: str = Field(default="", description="Описание")
    location: Optional[str] = Field(None, description="Место проведения")


class TaskEntity(BaseModel):
    """Сущность задачи"""
    title: str = Field(..., description="Название задачи")
    deadline: Optional[datetime] = Field(None, description="Дедлайн")
    description: str = Field(default="", description="Описание")
    priority: str = Field(default="medium", description="Приоритет: low, medium, high")
    status: str = Field(default="pending", description="Статус: pending, in_progress, completed")


class AgentResponse(BaseModel):
    """Ответ от agent_core"""
    action: str = Field(..., description="Действие: create_event, read_events, create_task, etc.")
    entities: Optional[dict] = Field(None, description="Извлеченные сущности")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Уверенность модели")
    requires_clarification: bool = Field(default=False, description="Требуется ли уточнение")
    clarification_question: str = Field(default="", description="Вопрос для уточнения")
    error_message: Optional[str] = Field(None, description="Сообщение об ошибке")


class CalendarEvent(BaseModel):
    """Событие календаря (Google Calendar format)"""
    id: str
    summary: str
    start: dict  # dateTime или date
    end: dict  # dateTime или date
    attendees: Optional[List[dict]] = None
    description: Optional[str] = None
    location: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class AvailabilityResponse(BaseModel):
    """Ответ о доступности времени"""
    is_available: bool = Field(..., description="Свободно ли время")
    requested_datetime: datetime
    conflicting_event: Optional[CalendarEvent] = Field(None, description="Конфликтующее событие")
    alternative_slots: List[datetime] = Field(default_factory=list, description="Альтернативные слоты")


class MeetingNote(BaseModel):
    """Карточка итогов встречи"""
    meeting_id: str
    title: str
    date: datetime
    participants: List[str]
    key_decisions: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    raw_transcript: Optional[str] = None


class RAGSearchRequest(BaseModel):
    """Запрос на поиск в RAG"""
    query: str
    top_k: int = Field(default=3)
    similarity_threshold: float = Field(default=0.75)
    filters: Optional[dict] = Field(None, description="Фильтры по метаданным")


class RAGSearchResult(BaseModel):
    """Результат поиска в RAG"""
    chunk_id: str
    content: str
    similarity_score: float
    metadata: dict
    source: str  # meeting_notes, transcript, dialog_history


class SchedulerReminder(BaseModel):
    """Напоминание планировщика"""
    user_id: int
    event_id: str
    reminder_type: str  # 48h, 24h, 10am, 30min
    send_at: datetime
    message: str


class LogEntry(BaseModel):
    """Запись журнала трассировки"""
    timestamp: datetime
    service: str
    user_id: int
    action: str
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    latency_ms: Optional[int] = None
    error: Optional[str] = None

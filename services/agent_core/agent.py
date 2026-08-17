"""
Agent Core - LLM Agent на основе LangChain/LangGraph
"""

import json
import asyncio
from typing import Optional, Dict, Any
from shared.config import settings
from shared.logging.tracing import get_logger
from shared.schemas.models import AgentResponse
from shared.security.pii_filter import filter_pii

logger = get_logger("agent_core", settings.LOG_LEVEL)


class LLMClient:
    """Клиент для работы с LLM (п. R-02 - retry + fallback)"""
    
    def __init__(self):
        self.api_base = settings.LLM_API_BASE_URL
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL_NAME
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE
        self.retry_count = settings.LLM_RETRY_COUNT
        self.timeout = settings.LLM_TIMEOUT
    
    async def generate(self, prompt: str, system_prompt: str) -> str:
        """Генерация ответа с retry и fallback"""
        for attempt in range(self.retry_count):
            try:
                # TODO: Интеграция с реальным LLM API
                # Здесь будет вызов через httpx/aiohttp
                logger.log_request(0, "llm_generate", {
                    "prompt_length": len(prompt),
                    "attempt": attempt + 1
                })
                
                # Имитация ответа для демонстрации
                await asyncio.sleep(0.5)
                
                response_text = self._mock_response(prompt)
                
                logger.log_response(0, "llm_generate", {"response_length": len(response_text)}, 0)
                return response_text
                
            except Exception as e:
                logger.log_error(0, "llm_generate", f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.retry_count - 1:
                    # Fallback
                    logger.log_error(0, "llm_fallback", "All retries failed, using fallback")
                    return self._fallback_response(prompt)
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise RuntimeError("LLM generation failed after all retries")
    
    def _mock_response(self, prompt: str) -> str:
        """Мокирование ответа для демонстрации"""
        # В продакшене здесь будет реальный вызов API
        return json.dumps({
            "action": "clarify_date",
            "entities": {"title": "Пример задачи"},
            "confidence": 0.9,
            "requires_clarification": True,
            "clarification_question": "К какому сроку нужно выполнить эту задачу?"
        }, ensure_ascii=False)
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback ответ при недоступности LLM"""
        return json.dumps({
            "action": "error",
            "entities": None,
            "confidence": 0.0,
            "requires_clarification": False,
            "error_message": "Сервис временно недоступен. Пожалуйста, попробуйте позже."
        }, ensure_ascii=False)


class AgentCore:
    """Основной агент для обработки запросов"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """Загрузка системного промпта"""
        # TODO: Загрузка из docs/prompts/system_prompt_v1.md
        return """Вы — персональный ассистент-планировщик.
Ваша задача — помогать пользователю управлять встречами и задачами.
Всегда возвращайте ответ в формате JSON.
Соблюдайте нейтрально-деловой тон."""
    
    async def process_request(self, user_id: int, text: str) -> AgentResponse:
        """Обработка входящего запроса"""
        try:
            logger.log_request(user_id, "process_request", {"text": text[:100]})
            
            # PII-фильтрация перед отправкой в LLM (п. 6.6)
            filtered_text = filter_pii(text)
            
            # Формирование промпта
            prompt = self._build_prompt(filtered_text)
            
            # Генерация ответа через LLM
            llm_response = await self.llm_client.generate(prompt, self.system_prompt)
            
            # Парсинг JSON ответа (п. R-02 - строгий парсинг)
            parsed = self._parse_json_response(llm_response)
            
            # Валидация ответа
            response = AgentResponse(**parsed)
            
            logger.log_response(user_id, "process_request", {"action": response.action}, 0)
            return response
            
        except Exception as e:
            logger.log_error(user_id, "process_request", str(e))
            return AgentResponse(
                action="error",
                confidence=0.0,
                error_message=f"Ошибка обработки: {str(e)}"
            )
    
    def _build_prompt(self, user_text: str) -> str:
        """Построение промпта для LLM"""
        current_date = "2024-01-15"  # TODO: Получать через get_date инструмент
        
        return f"""{self.system_prompt}

Текущая дата: {current_date} (используй как якорь для относительных дат)

Пользователь: {user_text}

Ответ в формате JSON:"""
    
    def _parse_json_response(self, response_text: str) -> dict:
        """Строгий парсинг JSON ответа"""
        try:
            # Поиск JSON в ответе
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start == -1 or end == 0:
                raise ValueError("JSON не найден в ответе")
            
            json_str = response_text[start:end]
            return json.loads(json_str)
            
        except json.JSONDecodeError as e:
            logger.log_error(0, "json_parse", f"Invalid JSON: {e}")
            raise ValueError(f"Некорректный формат ответа: {e}")


# Глобальный экземпляр
_agent: Optional[AgentCore] = None


def get_agent() -> AgentCore:
    """Получение экземпляра агента"""
    global _agent
    if _agent is None:
        _agent = AgentCore()
    return _agent


async def process_user_request(user_id: int, text: str) -> AgentResponse:
    """Удобная функция для обработки запроса"""
    agent = get_agent()
    return await agent.process_request(user_id, text)


if __name__ == "__main__":
    # Тестирование
    async def test():
        agent = get_agent()
        response = await agent.process_request(123, "Запиши встречу завтра в 15:00")
        print(f"Action: {response.action}")
        print(f"Confidence: {response.confidence}")
    
    asyncio.run(test())

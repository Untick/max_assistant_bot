"""
Сквозное логирование и трассировка запросов
"""

import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import contextmanager
import time


class TracingLogger:
    """Логгер с трассировкой запросов"""
    
    def __init__(self, service_name: str, log_level: str = "INFO"):
        """
        Инициализация логгера
        
        Args:
            service_name: Имя сервиса
            log_level: Уровень логирования
        """
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Форматтер с JSON
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_request(
        self,
        user_id: int,
        action: str,
        input_data: Dict[str, Any],
        request_id: Optional[str] = None
    ):
        """Логирование входящего запроса"""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': self.service_name,
            'user_id': user_id,
            'action': action,
            'direction': 'inbound',
            'data': input_data,
            'request_id': request_id
        }
        self.logger.info(f"REQUEST: {json.dumps(entry, ensure_ascii=False)}")
    
    def log_response(
        self,
        user_id: int,
        action: str,
        output_data: Dict[str, Any],
        latency_ms: int,
        request_id: Optional[str] = None
    ):
        """Логирование ответа"""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': self.service_name,
            'user_id': user_id,
            'action': action,
            'direction': 'outbound',
            'data': output_data,
            'latency_ms': latency_ms,
            'request_id': request_id
        }
        self.logger.info(f"RESPONSE: {json.dumps(entry, ensure_ascii=False)}")
    
    def log_error(
        self,
        user_id: int,
        action: str,
        error: str,
        request_id: Optional[str] = None
    ):
        """Логирование ошибки"""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': self.service_name,
            'user_id': user_id,
            'action': action,
            'error': error,
            'request_id': request_id
        }
        self.logger.error(f"ERROR: {json.dumps(entry, ensure_ascii=False)}")
    
    @contextmanager
    def trace_request(self, user_id: int, action: str, input_data: Dict[str, Any]):
        """Контекстный менеджер для трассировки запроса"""
        request_id = f"{self.service_name}_{int(time.time())}_{user_id}"
        start_time = time.time()
        
        self.log_request(user_id, action, input_data, request_id)
        
        try:
            yield request_id
            latency_ms = int((time.time() - start_time) * 1000)
            self.logger.info(f"Request {request_id} completed in {latency_ms}ms")
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            self.log_error(user_id, action, str(e), request_id)
            raise


# Глобальные логгеры для сервисов
_loggers = {}


def get_logger(service_name: str, log_level: str = "INFO") -> TracingLogger:
    """Получение логгера для сервиса"""
    if service_name not in _loggers:
        _loggers[service_name] = TracingLogger(service_name, log_level)
    return _loggers[service_name]


# Предопределенные логгеры
tg_gateway_logger = get_logger("tg_gateway")
asr_logger = get_logger("asr_service")
agent_logger = get_logger("agent_core")
mcp_logger = get_logger("mcp_server")
rag_logger = get_logger("rag_service")
scheduler_logger = get_logger("scheduler_service")

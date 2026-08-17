"""
RAG Service - Ингестия данных для поиска
Чанкинг до 500 токенов (п. 4.3)
"""

from typing import List, Dict, Any
from shared.config import settings
from shared.logging.tracing import get_logger

logger = get_logger("rag_service", settings.LOG_LEVEL)


class Chunker:
    """Разбиение текста на чанки (п. 4.3)"""
    
    def __init__(self, chunk_size: int = None):
        self.chunk_size = chunk_size or settings.RAG_CHUNK_SIZE
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Разбиение текста на логические блоки
        
        Args:
            text: Исходный текст
            metadata: Метаданные для каждого чанка
        
        Returns:
            Список чанков с метаданными
        """
        chunks = []
        
        # Простое разбиение по предложениям
        sentences = text.split('.')
        current_chunk = ""
        current_tokens = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Оценка количества токенов (приблизительно)
            sentence_tokens = len(sentence) // 4
            
            if current_tokens + sentence_tokens > self.chunk_size:
                # Сохранить текущий чанк и начать новый
                if current_chunk:
                    chunks.append({
                        "content": current_chunk.strip(),
                        "metadata": metadata or {},
                        "token_count": current_tokens
                    })
                
                current_chunk = sentence + ". "
                current_tokens = sentence_tokens
            else:
                current_chunk += sentence + ". "
                current_tokens += sentence_tokens
        
        # Добавить последний чанк
        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "metadata": metadata or {},
                "token_count": current_tokens
            })
        
        return chunks


# Глобальный экземпляр
chunker = Chunker(settings.RAG_CHUNK_SIZE)


def ingest_document(text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Ингестия документа с чанкингом"""
    logger.log_request(0, "ingest_document", {"text_length": len(text)})
    chunks = chunker.chunk_text(text, metadata)
    logger.log_response(0, "ingest_document", {"chunks_count": len(chunks)}, 0)
    return chunks


if __name__ == "__main__":
    # Тестирование
    test_text = "Это первая встреча. Обсудили проект. Решили двигаться дальше. " * 50
    chunks = ingest_document(test_text, {"source": "test"})
    print(f"Создано чанков: {len(chunks)}")
    for i, chunk in enumerate(chunks[:3]):
        print(f"Чанк {i}: {chunk['token_count']} токенов")

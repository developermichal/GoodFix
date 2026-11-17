import redis
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RedisContextManager:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.logger = logger

    def set_context(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """Ustawia kontekst w Redis z opcjonalnym czasem ważności"""
        try:
            # Konwertuj wartość do JSON
            if isinstance(value, dict):
                json_value = json.dumps(value)
            else:
                json_value = str(value)
            
            # Ustaw wartość z czasem ważności
            self.redis_client.setex(key, expire_seconds, json_value)
            self.logger.info(f"Ustawiono kontekst: {key}")
            return True
        except Exception as e:
            self.logger.error(f"Błąd podczas ustawiania kontekstu {key}: {e}")
            return False

    def get_context(self, key: str) -> Optional[Any]:
        """Pobiera kontekst z Redis"""
        try:
            value = self.redis_client.get(key)
            if value:
                # Spróbuj zdekodować JSON
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania kontekstu {key}: {e}")
            return None

    def delete_context(self, key: str) -> bool:
        """Usuwa kontekst z Redis"""
        try:
            result = self.redis_client.delete(key)
            self.logger.info(f"Usunięto kontekst: {key}")
            return result > 0
        except Exception as e:
            self.logger.error(f"Błąd podczas usuwania kontekstu {key}: {e}")
            return False

    def list_context_keys(self, pattern: str = "context:*") -> list:
        """Listuje wszystkie klucze kontekstu"""
        try:
            keys = self.redis_client.keys(pattern)
            return keys
        except Exception as e:
            self.logger.error(f"Błąd podczas listowania kluczy kontekstu: {e}")
            return []

    def clear_all_context(self) -> bool:
        """Czyści cały kontekst"""
        try:
            keys = self.redis_client.keys("context:*")
            if keys:
                self.redis_client.delete(*keys)
            self.logger.info("Wyczyszczono cały kontekst")
            return True
        except Exception as e:
            self.logger.error(f"Błąd podczas czyszczenia kontekstu: {e}")
            return False

    def get_context_summary(self) -> str:
        """Generuje podsumowanie kontekstu"""
        try:
            keys = self.list_context_keys()
            summary = "Podsumowanie kontekstu:\n"
            for key in keys:
                value = self.get_context(key)
                if value:
                    summary += f"- {key}: {str(value)[:100]}...\n"
            return summary
        except Exception as e:
            self.logger.error(f"Błąd podczas generowania podsumowania: {e}")
            return "Błąd podczas generowania podsumowania kontekstu"

# Przykład użycia:
if __name__ == "__main__":
    context_manager = RedisContextManager()
    
    # Ustawienie kontekstu
    context_manager.set_context("user:123:project", {"name": "GoodFix", "status": "active"})
    
    # Pobranie kontekstu
    context = context_manager.get_context("user:123:project")
    print(context)
    
    # Wygenerowanie podsumowania
    summary = context_manager.get_context_summary()
    print(summary)
import redis
import json
from typing import Dict, Any

class RedisService:
    def __init__(self, redis_host='redis', redis_port=6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

    def save_context(self, key: str, context: Dict[str, Any]) -> bool:
        """Zapisuje kontekst w Redis"""
        try:
            self.redis_client.set(key, json.dumps(context))
            return True
        except Exception as e:
            print(f"Błąd zapisu kontekstu: {e}")
            return False

    def load_context(self, key: str) -> Dict[str, Any]:
        """Ładuje kontekst z Redis"""
        try:
            context_data = self.redis_client.get(key)
            if context_data:
                return json.loads(context_data)
            return {}
        except Exception as e:
            print(f"Błąd odczytu kontekstu: {e}")
            return {}

    def delete_context(self, key: str) -> bool:
        """Usuwa kontekst"""
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Błąd usuwania kontekstu: {e}")
            return False

    def save_persistent_context(self, key: str, context: Dict[str, Any]) -> bool:
        """Zapisuje kontekst na stałe"""
        try:
            # Ustawienie kontekstu bez limitu czasowego
            self.redis_client.set(key, json.dumps(context))
            return True
        except Exception as e:
            print(f"Błąd zapisu trwałego kontekstu: {e}")
            return False

# Przykład użycia:
# service = RedisService()
# service.save_context('general_context', {'user': 'Michal'})

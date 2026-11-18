import os
import redis
import json
from typing import Dict, Any

class EducationalService:
    def __init__(self, redis_host='redis', redis_port=6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.context_key = 'educational_context'

    def save_context(self, context: Dict[str, Any]):
        """Zapisuje kontekst edukacyjny w Redis"""
        try:
            self.redis_client.set(self.context_key, json.dumps(context))
            return True
        except Exception as e:
            print(f"Błąd zapisu kontekstu: {e}")
            return False

    def load_context(self) -> Dict[str, Any]:
        """Ładuje kontekst edukacyjny z Redis"""
        try:
            context_data = self.redis_client.get(self.context_key)
            if context_data:
                return json.loads(context_data)
            return {}
        except Exception as e:
            print(f"Błąd odczytu kontekstu: {e}")
            return {}

    def clear_context(self):
        """Czyści kontekst edukacyjny"""
        try:
            self.redis_client.delete(self.context_key)
            return True
        except Exception as e:
            print(f"Błąd czyszczenia kontekstu: {e}")
            return False

# Przykład użycia:
# service = EducationalService()
# service.save_context({'user': 'Ewelina', 'level': 'beginner'})

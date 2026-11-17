import redis
import json
from typing import Dict, Any

class RedisContextManager:
    def __init__(self, redis_host='redis', redis_port=6379):
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
        self.context_key = 'general_context'

    def update_context(self, context: Dict[str, Any]):
        """
        Aktualizacja ogólnego kontekstu
        """
        # Pobierz istniejący kontekst
        existing_context = self.get_context()
        
        # Zaktualizuj kontekst
        updated_context = {**existing_context, **context}
        
        # Zapisz zaktualizowany kontekst
        self.redis_client.set(self.context_key, json.dumps(updated_context))

    def get_context(self) -> Dict[str, Any]:
        """
        Pobranie ogólnego kontekstu
        """
        context_data = self.redis_client.get(self.context_key)
        if context_data:
            return json.loads(context_data)
        return {}

    def clear_context(self):
        """
        Wyczyszczenie ogólnego kontekstu
        """
        self.redis_client.delete(self.context_key)

    def get_context_keys(self) -> list:
        """
        Pobranie kluczy ogólnego kontekstu
        """
        context = self.get_context()
        return list(context.keys())

# Singleton
redis_context_manager = RedisContextManager()
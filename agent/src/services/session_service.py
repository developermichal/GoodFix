import redis
import json
import time
from typing import Dict, Any

class SessionService:
    def __init__(self, redis_host='redis', redis_port=6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.session_timeout = 900  # 15 minut

    def create_session(self, session_id: str, context: Dict[str, Any]) -> bool:
        """Tworzy nową sesję"""
        try:
            session_data = {
                'context': context,
                'created_at': time.time(),
                'last_activity': time.time()
            }
            self.redis_client.setex(
                f"session:{session_id}",
                self.session_timeout,
                json.dumps(session_data)
            )
            return True
        except Exception as e:
            print(f"Błąd tworzenia sesji: {e}")
            return False

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Pobiera dane sesji"""
        try:
            session_data = self.redis_client.get(f"session:{session_id}")
            if session_data:
                data = json.loads(session_data)
                # Odśwież czas aktywności
                data['last_activity'] = time.time()
                self.redis_client.setex(
                    f"session:{session_id}",
                    self.session_timeout,
                    json.dumps(data)
                )
                return data
            return None
        except Exception as e:
            print(f"Błąd pobierania sesji: {e}")
            return None

    def delete_session(self, session_id: str) -> bool:
        """Usuwa sesję"""
        try:
            self.redis_client.delete(f"session:{session_id}")
            return True
        except Exception as e:
            print(f"Błąd usuwania sesji: {e}")
            return False

    def is_session_active(self, session_id: str) -> bool:
        """Sprawdza czy sesja jest aktywna"""
        session_data = self.get_session(session_id)
        if not session_data:
            return False
        
        current_time = time.time()
        last_activity = session_data.get('last_activity', 0)
        return (current_time - last_activity) < self.session_timeout

# Przykład użycia:
# service = SessionService()
# service.create_session('session123', {'user': 'Ewelina'})

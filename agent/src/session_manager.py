import redis
import json
import uuid
from typing import Dict, Any

class SessionManager:
    def __init__(self, redis_host='redis', redis_port=6379):
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
        self.sessions = {}

    def create_session(self, session_id: str = None) -> str:
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Inicjalizacja kontekstu sesji
        session_data = {
            'session_id': session_id,
            'context': {},
            'created_at': self._get_timestamp(),
            'last_active': self._get_timestamp()
        }
        
        # Zapisz sesję w Redis
        self.redis_client.setex(f"session:{session_id}", 900, json.dumps(session_data))  # 15 min
        
        # Zapisz referencję do sesji
        self.redis_client.sadd('active_sessions', session_id)
        
        return session_id

    def get_session(self, session_id: str) -> Dict[str, Any]:
        session_data = self.redis_client.get(f"session:{session_id}")
        if session_data:
            return json.loads(session_data)
        return None

    def update_session_context(self, session_id: str, context: Dict[str, Any]):
        session_data = self.get_session(session_id)
        if session_data:
            session_data['context'].update(context)
            session_data['last_active'] = self._get_timestamp()
            self.redis_client.setex(f"session:{session_id}", 900, json.dumps(session_data))

    def delete_session(self, session_id: str):
        self.redis_client.delete(f"session:{session_id}")
        self.redis_client.srem('active_sessions', session_id)

    def get_all_active_sessions(self):
        session_ids = self.redis_client.smembers('active_sessions')
        return [self.get_session(sid) for sid in session_ids if sid]

    def _get_timestamp(self):
        import time
        return time.time()

    def cleanup_expired_sessions(self):
        # Wyczyść sesje po 15 minutach nieaktywności
        pass

# Singleton
session_manager = SessionManager()
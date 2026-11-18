import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from agent.app.session_manager import SessionManager
from agent.app.redis_context_manager import RedisContextManager
from agent.app.email_handler import EmailHandler

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EducationalContext:
    user_name: str = "Ewelina"
    user_surname: str = "Żukowska"
    user_email: str = "ewelinazukowska@icloud.com"
    agent_name: str = "Michał Wiśniewski"
    agent_email: str = "michalwmobile@gmail.com"
    learning_level: int = 0  # 0-100
    personality_context: Dict = None
    session_id: str = None
    sarkasm_level: int = 1  # 1-100
    
    def __post_init__(self):
        if self.personality_context is None:
            self.personality_context = {}


class EducationalAgent:
    def __init__(self):
        self.session_manager = SessionManager()
        self.redis_manager = RedisContextManager()
        self.email_handler = EmailHandler()
        self.contexts = {}
        self.learning_materials = {
            "books": [],
            "articles": [],
            "videos": []
        }
        
    def create_educational_session(self, user_email: str = "ewelinazukowska@icloud.com") -> str:
        """Tworzy nową sesję edukacyjną dla Eweliny"""
        session_id = self.session_manager.create_session(
            session_type="educational",
            user_email=user_email
        )
        
        # Inicjalizacja kontekstu edukacyjnego
        context = EducationalContext(
            user_name="Ewelina",
            user_surname="Żukowska",
            user_email=user_email,
            agent_name="Michał Wiśniewski",
            agent_email="michalwmobile@gmail.com",
            learning_level=0,
            sarkasm_level=1
        )
        
        self.contexts[session_id] = context
        
        # Zapisz kontekst w Redis
        self.redis_manager.save_context(session_id, context)
        
        logger.info(f"Utworzono sesję edukacyjną: {session_id}")
        return session_id
        
    def get_educational_context(self, session_id: str) -> EducationalContext:
        """Pobiera kontekst edukacyjny dla sesji"""
        if session_id in self.contexts:
            return self.contexts[session_id]
        
        # Spróbuj wczytać z Redis
        context_data = self.redis_manager.load_context(session_id)
        if context_data:
            context = EducationalContext(**context_data)
            self.contexts[session_id] = context
            return context
        
        return None
        
    def update_learning_level(self, session_id: str, level: int):
        """Aktualizuje poziom nauki Eweliny"""
        context = self.get_educational_context(session_id)
        if context:
            context.learning_level = max(0, min(100, level))
            self.redis_manager.save_context(session_id, context)
            logger.info(f"Zaktualizowano poziom nauki dla sesji {session_id}: {context.learning_level}%")
            
    def update_sarkasm_level(self, session_id: str, level: int):
        """Aktualizuje poziom sarkazmu"""
        context = self.get_educational_context(session_id)
        if context:
            context.sarkasm_level = max(1, min(100, level))
            self.redis_manager.save_context(session_id, context)
            logger.info(f"Zaktualizowano poziom sarkazmu dla sesji {session_id}: {context.sarkasm_level}%")
            
    def add_learning_material(self, session_id: str, material_type: str, title: str, content: str):
        """Dodaje materiał edukacyjny"""
        if material_type in self.learning_materials:
            self.learning_materials[material_type].append({
                "title": title,
                "content": content,
                "added_at": datetime.now().isoformat()
            })
            logger.info(f"Dodano materiał edukacyjny typu {material_type}: {title}")
            
    def get_learning_materials(self, material_type: str) -> List[Dict]:
        """Pobiera materiały edukacyjne"""
        return self.learning_materials.get(material_type, [])
        
    def analyze_personality_context(self, session_id: str, analysis: Dict):
        """Analizuje kontekst osobowości Eweliny"""
        context = self.get_educational_context(session_id)
        if context:
            context.personality_context.update(analysis)
            self.redis_manager.save_context(session_id, context)
            logger.info(f"Zaktualizowano kontekst osobowości dla sesji {session_id}")
            
    def send_educational_email(self, session_id: str, subject: str, content: str) -> bool:
        """Wysyła edukacyjny email do Eweliny"""
        context = self.get_educational_context(session_id)
        if not context:
            logger.error(f"Brak kontekstu dla sesji {session_id}")
            return False
            
        try:
            # Wysyłanie emaila
            self.email_handler.send_email(
                to_email=context.user_email,
                from_email=context.agent_email,
                subject=subject,
                content=content
            )
            logger.info(f"Wysłano email do {context.user_email}")
            return True
        except Exception as e:
            logger.error(f"Błąd podczas wysyłania emaila: {str(e)}")
            return False
            
    def get_personality_analysis(self, session_id: str) -> Dict:
        """Pobiera analizę kontekstu osobowości"""
        context = self.get_educational_context(session_id)
        if context:
            return context.personality_context
        return {}
        
    def get_session_status(self, session_id: str) -> Dict:
        """Pobiera status sesji edukacyjnej"""
        context = self.get_educational_context(session_id)
        if context:
            return {
                "session_id": session_id,
                "user_name": context.user_name,
                "learning_level": context.learning_level,
                "sarkasm_level": context.sarkasm_level,
                "personality_context": context.personality_context
            }
        return {}
        
    def get_educational_suggestions(self, session_id: str) -> List[str]:
        """Zwraca sugestie edukacyjne"""
        context = self.get_educational_context(session_id)
        if not context:
            return []
            
        suggestions = []
        if context.learning_level < 30:
            suggestions.append("Zacznij od podstawowych materiałów")
        elif context.learning_level < 70:
            suggestions.append("Przejdź do bardziej zaawansowanych tematów")
        else:
            suggestions.append("Zaprezentuj zaawansowane koncepty")
            
        return suggestions
        
    def generate_response(self, session_id: str, user_input: str) -> str:
        """Generuje odpowiedź agenta z uwzględnieniem kontekstu edukacyjnego"""
        context = self.get_educational_context(session_id)
        if not context:
            return "Nie mogę zidentyfikować sesji edukacyjnej. Proszę zainicjalizować nową sesję."
            
        # Analiza poziomu sarkazmu
        sarkasm_level = context.sarkasm_level
        
        # Prosta logika odpowiedzi
        if sarkasm_level > 20:
            # Odpowiedź z większym sarkazmem
            return f"To pytanie jest bardzo ciekawe, ale nie jestem pewien, czy to jest odpowiednie pytanie dla Eweliny. Czy nie powinnaś najpierw przeczytać książki?"
        else:
            # Odpowiedź z niskim sarkazmem
            return f"To bardzo dobre pytanie, Ewelino. Zajrzyj do książki o AI, która została wysłana do Ciebie."
            
    def close_session(self, session_id: str):
        """Zamyka sesję edukacyjną"""
        if session_id in self.contexts:
            del self.contexts[session_id]
        self.redis_manager.delete_context(session_id)
        logger.info(f"Zamknięto sesję edukacyjną: {session_id}")
        
# Inicjalizacja agenta
educational_agent = EducationalAgent()
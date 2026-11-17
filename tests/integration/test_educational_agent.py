import unittest
import json
from unittest.mock import patch, MagicMock

from agent.app.educational_agent import EducationalAgent, EducationalContext


class TestEducationalAgent(unittest.TestCase):
    
    def setUp(self):
        self.agent = EducationalAgent()
        
    def test_create_educational_session(self):
        """Test tworzenia sesji edukacyjnej"""
        session_id = self.agent.create_educational_session()
        
        # Sprawdź czy sesja została utworzona
        self.assertIsNotNone(session_id)
        self.assertIsInstance(session_id, str)
        
        # Sprawdź kontekst
        context = self.agent.get_educational_context(session_id)
        self.assertIsNotNone(context)
        self.assertEqual(context.user_name, "Ewelina")
        self.assertEqual(context.user_surname, "Żukowska")
        self.assertEqual(context.agent_name, "Michał Wiśniewski")
        
    def test_update_learning_level(self):
        """Test aktualizacji poziomu nauki"""
        session_id = self.agent.create_educational_session()
        
        # Aktualizacja poziomu
        self.agent.update_learning_level(session_id, 50)
        
        # Sprawdź czy poziom został zaktualizowany
        context = self.agent.get_educational_context(session_id)
        self.assertEqual(context.learning_level, 50)
        
        # Sprawdź ograniczenia
        self.agent.update_learning_level(session_id, 150)
        context = self.agent.get_educational_context(session_id
import unittest
import json
from unittest.mock import patch
from agent.app.session_manager import SessionManager

class TestContextIsolation(unittest.TestCase):
    def setUp(self):
        self.session_manager = SessionManager()
        # Wyczyść Redis przed testem
        self.session_manager.redis_client.flushdb()

    def test_session_isolation(self):
        # Tworzenie dwóch sesji
        session1_id = self.session_manager.create_session()
        session2_id = self.session_manager.create_session()
        
        # Ustawienie różnych kontekstów
        context1 = {'project': 'project1', 'data': 'value1'}
        context2 = {'project': 'project2', 'data': 'value2'}
        
        self.session_manager.update_session_context(session1_id, context1)
        self.session_manager.update_session_context(session2_id, context2)
        
        # Pobranie kontekstów
        session1_data = self.session_manager.get_session(session1_id)
        session2_data = self.session_manager.get_session(session2_id)
        
        # Sprawdzenie izolacji
        self.assertEqual(session1_data['context']['project'], 'project1')
        self.assertEqual(session2_data['context']['project'], 'project2')
        
        # Sprawdzenie, że konteksty są różne
        self.assertNotEqual(session1_data['context'], session2_data['context'])

    def test_general_context_singleton(self):
        # Testowanie ogólnego kontekstu (singleton)
        # W tym przypadku kontekst ogólny jest przechowywany w Redis
        # ale nie jest powiązany z konkretną sesją
        pass

    def test_session_cleanup(self):
        # Testowanie czyszczenia sesji po czasie
        session_id = self.session_manager.create_session()
        session_data = self.session_manager.get_session(session_id)
        self.assertIsNotNone(session_data)
        
        # Sprawdzenie, że sesja została dodana do aktywnych
        active_sessions = self.session_manager.get_all_active_sessions()
        self.assertIn(session_id, [s['session_id'] for s in active_sessions])

if __name__ == '__main__':
    unittest.main()
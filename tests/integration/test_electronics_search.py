import pytest
import requests
from unittest.mock import Mock, patch
from agent.app.electronics_search import search_electronics_schematics

def test_search_electronics_schematics():
    # Testowanie funkcji wyszukiwania schematów
    with patch('agent.app.electronics_search.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': [{'name': 'test', 'url': 'http://test.com'}]}
        mock_get.return_value = mock_response
        
        result = search_electronics_schematics('test device')
        assert result is not None
        assert len(result) > 0

def test_search_electronics_schematics_failure():
    # Testowanie błędów wyszukiwania
    with patch('agent.app.electronics_search.requests.get') as mock_get:
        mock_get.side_effect = requests.RequestException()
        
        result = search_electronics_schematics('test device')
        assert result is None
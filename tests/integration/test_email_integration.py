import pytest
import os
from unittest.mock import Mock, patch
from agent.app.email_handler import EmailHandler


class TestEmailHandler:
    
    @pytest.fixture
    def email_handler(self):
        # Ustawienie zmiennych środowiskowych
        os.environ["AGENT_EMAIL"] = "michalwmobile@gmail.com"
        os.environ["AGENT_PASSWORD"] = "test_password"
        return EmailHandler()
    
    @patch('agent.app.email_handler.imaplib.IMAP4_SSL')
    @patch('agent.app.email_handler.email.message_from_bytes')
    def test_fetch_emails(self, mock_message_from_bytes, mock_imap):
        # Mockowanie odpowiedzi
        mock_mail = Mock()
        mock_imap.return_value = mock_mail
        mock_mail.search.return_value = ('OK', [b'1 2 3'])
        mock_mail.fetch.return_value = ('OK', [(b'1', b'\nFrom: ewelinazukowska@icloud.com\nSubject: Test\n\nTest body')])
        
        # Tworzenie mockowanego message
        mock_msg = Mock()
        mock_msg.is_multipart.return_value = False
        mock_msg.get_payload.return_value = b'Test body'
        mock_msg['From'] = 'ewelinazukowska@icloud.com'
        mock_msg['Subject'] = 'Test'
        mock_msg['Date'] = 'Mon, 1 Jan 2023 00:00:00 +0000'
        
        mock_message_from_bytes.return_value = mock_msg
        
        handler = EmailHandler()
        emails = handler.fetch_emails()
        
        assert len(emails) == 1
        assert emails[0]['from'] == 'ewelinazukowska@icloud.com'
        assert emails[0]['subject'] == 'Test'
        
    def test_email_body_parsing(self, email_handler):
        # Testowanie parsowania treści maila
        mock_msg = Mock()
        mock_msg.is_multipart.return_value = False
        mock_msg.get_payload.return_value = b'Test body'
        
        body = email_handler.get_email_body(mock_msg)
        assert body == 'Test body'

    def test_allowed_sender_filtering(self):
        # Testowanie filtrowania nadawców
        handler = EmailHandler()
        assert handler.allowed_sender == "ewelinazukowska@icloud.com"

if __name__ == "__main__":
    pytest.main(["-v"])
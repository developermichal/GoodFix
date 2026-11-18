import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any


class EmailService:
    def __init__(self):
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Wysyła email"""
        try:
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = to_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = message.as_string()
            server.sendmail(self.sender_email, to_email, text)
            server.quit()
            return True
        except Exception as e:
            print(f"Błąd wysyłania emaila: {e}")
            return False

    def validate_recipient(self, email: str) -> bool:
        """Sprawdza czy odbiorca jest dozwolony"""
        allowed_email = os.getenv('ALLOWED_RECIPIENT')
        return email == allowed_email

# Przykład użycia:
# service = EmailService()
# service.send_email('ewelinazukowska@icloud.com', 'Test', 'Treść testowa')

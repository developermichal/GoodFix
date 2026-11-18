import os
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional

class EmailHandler:
    def __init__(self):
        self.email = os.getenv('AGENT_EMAIL')
        self.password = os.getenv('AGENT_PASSWORD')
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.imap_server = "imap.gmail.com"
        self.allowed_sender = "ewelinazukowska@icloud.com"

    def connect_imap(self):
        mail = imaplib.IMAP4_SSL(self.imap_server)
        mail.login(self.email, self.password)
        return mail

    def fetch_emails(self) -> List[Dict]:
        try:
            mail = self.connect_imap()
            mail.select('inbox')
            status, messages = mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()
            emails = []
            
            for email_id in email_ids[-5:]:  # Ostatnie 5 maili
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                
                if msg['From'] == self.allowed_sender:
                    email_data = {
                        'subject': msg['Subject'],
                        'from': msg['From'],
                        'date': msg['Date'],
                        'body': self.get_email_body(msg)
                    }
                    emails.append(email_data)
            
            mail.close()
            mail.logout()
            return emails
        except Exception as e:
            print(f"Błąd podczas pobierania maili: {e}")
            return []

    def get_email_body(self, msg) -> str:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode('utf-8')
        else:
            return msg.get_payload(decode=True).decode('utf-8')

    def send_email(self, to: str, subject: str, body: str):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Błąd podczas wysyłania maila: {e}")

# Przykład użycia:
# email_handler = EmailHandler()
# emails = email_handler.fetch_emails()
# print(emails)
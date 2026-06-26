import logging
import time
import os.path
import pickle
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class GmailSender:
    def __init__(self, credentials_file: str = config.GMAIL_CREDENTIALS_FILE):
        self.credentials_file = credentials_file
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticate with Gmail API."""
        creds = None

        token_file = config.GMAIL_TOKEN_FILE
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    logger.warning(
                        f"Credentials file not found: {self.credentials_file}. "
                        "Please set up Gmail API credentials first. "
                        "See README.md for setup instructions."
                    )
                    raise FileNotFoundError(
                        f"Gmail credentials file not found. "
                        f"Please create {self.credentials_file} with your credentials."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Successfully authenticated with Gmail API")

    def send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> bool:
        """Send an email using Gmail API."""
        try:
            from_name = from_name or config.EMAIL_FROM_NAME
            from_email = config.GMAIL_USER_EMAIL

            message = MIMEMultipart('alternative')
            message['To'] = to_email
            message['From'] = f'{from_name} <{from_email}>'
            message['Subject'] = subject

            part1 = MIMEText(body_text, 'plain')
            message.attach(part1)

            if body_html:
                part2 = MIMEText(body_html, 'html')
                message.attach(part2)

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            send_message = {'raw': raw_message}

            result = self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()

            logger.info(f"Email sent successfully to {to_email} (Message ID: {result['id']})")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_batch_emails(
        self,
        contacts: List[Dict],
        subject_template: str,
        body_template: str,
        html_template: Optional[str] = None,
        batch_size: int = config.BATCH_SIZE,
        delay: int = config.DELAY_BETWEEN_SENDS
    ) -> Dict:
        """Send emails to multiple contacts in batches."""
        stats = {
            'total': len(contacts),
            'sent': 0,
            'failed': 0,
            'failed_emails': []
        }

        for i, contact in enumerate(contacts):
            subject = self.personalize_template(subject_template, contact)
            body = self.personalize_template(body_template, contact)
            html_body = None
            if html_template:
                html_body = self.personalize_template(html_template, contact)

            success = self.send_email(
                contact.get('email'),
                subject,
                body,
                html_body
            )

            if success:
                stats['sent'] += 1
            else:
                stats['failed'] += 1
                stats['failed_emails'].append(contact.get('email'))

            if (i + 1) % batch_size == 0:
                logger.info(f"Processed {i + 1}/{len(contacts)} emails. Waiting {delay}s...")
                time.sleep(delay)

        logger.info(f"Email batch complete. Sent: {stats['sent']}, Failed: {stats['failed']}")
        return stats

    def personalize_template(self, template: str, contact: Dict) -> str:
        """Replace template variables with contact information."""
        result = template
        for key, value in contact.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value or ''))
        return result

    def load_email_template(self, file_path: str) -> str:
        """Load email template from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading template from {file_path}: {e}")
            return ""

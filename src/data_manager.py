import csv
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import config

logger = logging.getLogger(__name__)

HEADERS = [
    'company_name',
    'location',
    'ceo_name',
    'email',
    'phone',
    'linkedin_profile',
    'whatsapp',
    'data_source',
    'extraction_date',
    'email_sent',
    'send_date'
]

class ContactManager:
    def __init__(self, csv_file: str = config.CONTACTS_CSV):
        self.csv_file = csv_file
        self.contacts = []
        self.load_contacts()

    def load_contacts(self):
        """Load existing contacts from CSV."""
        if Path(self.csv_file).exists():
            try:
                with open(self.csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.contacts = list(reader)
                logger.info(f"Loaded {len(self.contacts)} contacts from {self.csv_file}")
            except Exception as e:
                logger.error(f"Error loading contacts: {e}")
                self.contacts = []
        else:
            logger.info(f"No existing contacts file found at {self.csv_file}")
            self.contacts = []

    def save_contacts(self):
        """Save contacts to CSV."""
        try:
            Path(self.csv_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=HEADERS)
                writer.writeheader()
                writer.writerows(self.contacts)
            logger.info(f"Saved {len(self.contacts)} contacts to {self.csv_file}")
        except Exception as e:
            logger.error(f"Error saving contacts: {e}")

    def add_contact(self, contact: Dict) -> bool:
        """Add a new contact or update existing one."""
        if not contact.get('email'):
            logger.warning(f"Skipping contact without email: {contact.get('company_name')}")
            return False

        if not self.validate_email(contact.get('email', '')):
            logger.warning(f"Invalid email format: {contact.get('email')}")
            return False

        existing = next(
            (c for c in self.contacts if c.get('email') == contact.get('email')),
            None
        )

        if existing:
            existing.update(contact)
            logger.info(f"Updated contact: {contact.get('company_name')}")
        else:
            contact['extraction_date'] = contact.get('extraction_date', datetime.now().isoformat())
            contact['email_sent'] = contact.get('email_sent', 'False')
            self.contacts.append(contact)
            logger.info(f"Added new contact: {contact.get('company_name')}")

        return True

    def add_contacts_bulk(self, contacts: List[Dict]) -> int:
        """Add multiple contacts at once."""
        count = 0
        for contact in contacts:
            if self.add_contact(contact):
                count += 1
        self.save_contacts()
        return count

    def get_contacts_to_email(self) -> List[Dict]:
        """Get all contacts that haven't been emailed yet."""
        return [c for c in self.contacts if c.get('email_sent') != 'True' and c.get('email')]

    def mark_as_sent(self, email: str, send_date: str = None):
        """Mark a contact as having received an email."""
        contact = next((c for c in self.contacts if c.get('email') == email), None)
        if contact:
            contact['email_sent'] = 'True'
            contact['send_date'] = send_date or datetime.now().isoformat()
            self.save_contacts()
            logger.info(f"Marked email sent for: {email}")

    def get_contact_by_email(self, email: str) -> Dict:
        """Retrieve a contact by email."""
        return next((c for c in self.contacts if c.get('email') == email), None)

    def validate_email(self, email: str) -> bool:
        """Basic email validation."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def get_stats(self) -> Dict:
        """Get statistics about the contact list."""
        total = len(self.contacts)
        with_email = sum(1 for c in self.contacts if c.get('email'))
        sent = sum(1 for c in self.contacts if c.get('email_sent') == 'True')

        return {
            'total_contacts': total,
            'with_email': with_email,
            'sent_emails': sent,
            'pending': with_email - sent
        }

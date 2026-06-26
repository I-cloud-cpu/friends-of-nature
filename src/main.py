#!/usr/bin/env python3
import argparse
import logging
import sys
from pathlib import Path

import config
from image_processor import extract_companies_from_image
from contact_researcher import ContactResearcher
from data_manager import ContactManager
from email_sender import GmailSender

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE_EXTRACTION),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def setup_logging_files():
    """Ensure log files are set up."""
    Path(config.LOG_FILE_EXTRACTION).parent.mkdir(parents=True, exist_ok=True)
    Path(config.LOG_FILE_EMAIL).parent.mkdir(parents=True, exist_ok=True)

def extract_companies(image_path: str) -> None:
    """Extract company names and locations from infographic."""
    logger.info(f"Starting company extraction from image: {image_path}")

    try:
        companies = extract_companies_from_image(image_path)
        logger.info(f"Extracted {len(companies)} companies")

        manager = ContactManager()
        for company in companies:
            manager.add_contact(company)

        manager.save_contacts()
        logger.info(f"Companies saved to {config.CONTACTS_CSV}")
        print(f"✓ Successfully extracted {len(companies)} companies")
    except Exception as e:
        logger.error(f"Error extracting companies: {e}")
        print(f"✗ Error: {e}")
        sys.exit(1)

def research_contacts() -> None:
    """Research contact information for all companies."""
    logger.info("Starting contact research")

    try:
        manager = ContactManager()
        contacts_to_research = [
            c for c in manager.contacts
            if not c.get('email') or c.get('email').strip() == ''
        ]

        if not contacts_to_research:
            logger.info("All contacts already have email addresses")
            print("ℹ All contacts already have email addresses")
            return

        researcher = ContactResearcher()
        logger.info(f"Researching {len(contacts_to_research)} companies")

        for contact in contacts_to_research:
            try:
                result = researcher.research_company(
                    contact.get('company_name', ''),
                    contact.get('location', '')
                )
                if result:
                    contact.update(result)
                    logger.info(f"Found email for {contact.get('company_name')}: {result.get('email')}")
            except Exception as e:
                logger.error(f"Error researching {contact.get('company_name')}: {e}")

        manager.save_contacts()
        stats = manager.get_stats()
        logger.info(f"Research complete. Stats: {stats}")
        print(f"✓ Research complete")
        print(f"  Total contacts: {stats['total_contacts']}")
        print(f"  With email: {stats['with_email']}")
        print(f"  Pending: {stats['pending']}")
    except Exception as e:
        logger.error(f"Error during research: {e}")
        print(f"✗ Error: {e}")
        sys.exit(1)

def send_emails(message_file: str, dry_run: bool = False) -> None:
    """Send emails to contacts."""
    logger.info(f"Starting email sending (dry_run={dry_run})")

    try:
        if not Path(message_file).exists():
            logger.error(f"Message file not found: {message_file}")
            raise FileNotFoundError(f"Message file not found: {message_file}")

        with open(message_file, 'r', encoding='utf-8') as f:
            message_content = f.read()

        manager = ContactManager()
        contacts_to_email = manager.get_contacts_to_email()

        if not contacts_to_email:
            logger.info("No contacts to email")
            print("ℹ No pending contacts to email")
            return

        logger.info(f"Found {len(contacts_to_email)} contacts to email")
        print(f"Found {len(contacts_to_email)} contacts to email")

        if dry_run:
            logger.info("DRY RUN MODE - Emails will not be sent")
            print("\n[DRY RUN MODE]\n")
            for contact in contacts_to_email[:3]:
                print(f"Would send email to: {contact.get('email')}")
                print(f"Company: {contact.get('company_name')}")
                print(f"Contact: {contact.get('ceo_name')}\n")
            return

        subject = f"{config.EMAIL_SUBJECT_PREFIX} Partnership Opportunity"
        sender = GmailSender()

        stats = sender.send_batch_emails(
            contacts_to_email,
            subject,
            message_content
        )

        for contact in contacts_to_email:
            if contact.get('email') not in stats.get('failed_emails', []):
                manager.mark_as_sent(contact.get('email'))

        logger.info(f"Email sending complete. Stats: {stats}")
        print(f"✓ Emails sent successfully")
        print(f"  Sent: {stats['sent']}")
        print(f"  Failed: {stats['failed']}")
    except Exception as e:
        logger.error(f"Error during email sending: {e}")
        print(f"✗ Error: {e}")
        sys.exit(1)

def show_status() -> None:
    """Show status of contacts and email sending."""
    try:
        manager = ContactManager()
        stats = manager.get_stats()

        print("\n📊 Friends of Nature - Contact Status")
        print("=" * 50)
        print(f"Total contacts: {stats['total_contacts']}")
        print(f"With email address: {stats['with_email']}")
        print(f"Emails sent: {stats['sent']}")
        print(f"Pending emails: {stats['pending']}")
        print("=" * 50 + "\n")
    except Exception as e:
        logger.error(f"Error showing status: {e}")
        print(f"✗ Error: {e}")

def main():
    """Main entry point."""
    setup_logging_files()

    parser = argparse.ArgumentParser(
        description='Friends of Nature - Company Contact Extraction & Email Automation'
    )
    parser.add_argument('--extract-companies', metavar='IMAGE_PATH',
                        help='Extract companies from infographic image')
    parser.add_argument('--research-contacts', action='store_true',
                        help='Research contact information for companies')
    parser.add_argument('--send-emails', metavar='MESSAGE_FILE',
                        help='Send emails to contacts with message from file')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview emails without sending')
    parser.add_argument('--status', action='store_true',
                        help='Show contact status')

    args = parser.parse_args()

    if args.extract_companies:
        extract_companies(args.extract_companies)
    elif args.research_contacts:
        research_contacts()
    elif args.send_emails:
        send_emails(args.send_emails, args.dry_run)
    elif args.status:
        show_status()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

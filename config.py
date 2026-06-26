import os
from dotenv import load_dotenv

load_dotenv()

GMAIL_CREDENTIALS_FILE = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
GMAIL_TOKEN_FILE = os.getenv('GMAIL_TOKEN_FILE', 'token.pickle')
GMAIL_USER_EMAIL = os.getenv('GMAIL_USER_EMAIL', 'noreply@friendsofnature.org')

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

EMAIL_FROM_NAME = os.getenv('EMAIL_FROM_NAME', 'Friends of Nature')
EMAIL_SUBJECT_PREFIX = os.getenv('EMAIL_SUBJECT_PREFIX', '[Friends of Nature]')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 10))
DELAY_BETWEEN_SENDS = int(os.getenv('DELAY_BETWEEN_SENDS', 2))

REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 10))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE_EXTRACTION = os.getenv('LOG_FILE_EXTRACTION', 'logs/extraction.log')
LOG_FILE_EMAIL = os.getenv('LOG_FILE_EMAIL', 'logs/email_delivery.log')

CONTACTS_CSV = 'data/contacts.csv'
DATA_DIR = 'data'
LOGS_DIR = 'logs'

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

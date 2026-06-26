# Friends of Nature - Company Contact Extraction & Email Automation

Automated system to extract company information from infographics, research executive contacts, and send targeted emails on behalf of Friends of Nature.

## Features

- **Image Analysis**: Extract company names and locations from infographics using Claude Vision API
- **Contact Research**: Web scraping and research to find executive contact information
- **CSV Storage**: Organized contact database with detailed information
- **Gmail Integration**: Send personalized emails via Gmail API with rate limiting
- **Batch Processing**: Handle large contact lists efficiently
- **Logging**: Comprehensive logging for tracking and debugging

## Project Structure

```
friends-of-nature/
├── src/
│   ├── image_processor.py    # Extract companies from images
│   ├── contact_researcher.py # Research contact information
│   ├── data_manager.py       # Manage contact CSV database
│   ├── email_sender.py       # Send emails via Gmail API
│   └── main.py               # CLI orchestration
├── data/
│   ├── infographic.png       # Input image (add your image here)
│   └── contacts.csv          # Output contact database
├── logs/                      # Logging output
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
└── README.md
```

## Prerequisites

- Python 3.8+
- Gmail account with Gmail API enabled
- Anthropic API key for Claude Vision

## Setup Instructions

### 1. Clone and Install

```bash
git clone <repository-url>
cd friends-of-nature
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
```
GMAIL_USER_EMAIL=your-email@gmail.com
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 3. Set Up Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop Application)
5. Download credentials as JSON file
6. Save as `credentials.json` in the project root

First run will open a browser for OAuth authentication.

### 4. Prepare Input Image

Place your infographic image in `data/infographic.png` (supports PNG, JPG)

## Usage

### Step 1: Extract Companies from Image

```bash
python src/main.py --extract-companies data/infographic.png
```

This will:
- Analyze the infographic using Claude Vision
- Extract company names and locations
- Save to `data/contacts.csv`

### Step 2: Research Contact Information

```bash
python src/main.py --research-contacts
```

This will:
- Research each company to find executive contacts
- Search for CEO/executive information
- Extract emails and phone numbers
- Update `data/contacts.csv`

### Step 3: Check Status

```bash
python src/main.py --status
```

Shows:
- Total contacts found
- Contacts with email addresses
- Emails already sent
- Pending emails

### Step 4: Prepare Email Message

Create a message file (e.g., `message.txt`):

```
Dear {{ceo_name}},

I hope this message finds you well. As a key decision-maker at {{company_name}} located in {{location}}, we believe your organization shares our commitment to environmental sustainability.

[Your message content here]

Best regards,
Friends of Nature Team
```

Template variables available:
- `{{company_name}}` - Company name
- `{{ceo_name}}` - CEO/Executive name
- `{{location}}` - Company location
- `{{email}}` - Email address
- `{{phone}}` - Phone number
- `{{linkedin_profile}}` - LinkedIn profile URL

### Step 5: Send Emails (with Dry Run)

First, preview emails without sending:

```bash
python src/main.py --send-emails message.txt --dry-run
```

### Step 6: Send Actual Emails

```bash
python src/main.py --send-emails message.txt
```

This will:
- Send personalized emails to all contacts
- Include rate limiting to comply with Gmail API quotas
- Track delivery status
- Update `data/contacts.csv` with send status

## Configuration

Edit `config.py` or `.env` to customize:

- **Email Settings**
  - `EMAIL_FROM_NAME`: Sender name
  - `EMAIL_SUBJECT_PREFIX`: Email subject prefix
  - `BATCH_SIZE`: Emails per batch before pausing
  - `DELAY_BETWEEN_SENDS`: Seconds between batches

- **Research Settings**
  - `REQUEST_TIMEOUT`: HTTP request timeout (seconds)
  - `MAX_RETRIES`: Retry attempts for failed requests
  - `USER_AGENT`: HTTP User-Agent header

- **API Settings**
  - `ANTHROPIC_API_KEY`: Claude API key
  - `GMAIL_CREDENTIALS_FILE`: OAuth credentials file
  - `GMAIL_TOKEN_FILE`: OAuth token storage

## Contact CSV Format

The `data/contacts.csv` file contains:

| Field | Description |
|-------|-------------|
| company_name | Name of company |
| location | Geographic location |
| ceo_name | CEO or executive name |
| email | Contact email address |
| phone | Phone number (if found) |
| linkedin_profile | LinkedIn profile URL |
| whatsapp | WhatsApp contact (if found) |
| data_source | Source of information |
| extraction_date | Date extracted |
| email_sent | Whether email was sent |
| send_date | Date email was sent |

## Logging

Logs are written to:
- `logs/extraction.log` - Company extraction and research logs
- `logs/email_delivery.log` - Email sending logs
- Console output for real-time feedback

## API Rate Limits

**Gmail API:**
- Quota: ~500 emails/day per account
- The system includes batch processing and delays to respect limits
- Use `--dry-run` to test without consuming quota

**Claude Vision API:**
- Standard rate limits apply
- Image processing happens sequentially with delays

## Troubleshooting

### "Credentials file not found"
- Ensure `credentials.json` is in the project root
- Follow the Gmail API setup instructions above

### "Invalid email format"
- The system validates email addresses
- Check that extracted emails are correctly formatted
- Use `--status` to review contact data

### Gmail API errors
- Verify OAuth token is valid (delete `token.pickle` to re-authenticate)
- Check Gmail API is enabled in Google Cloud Console
- Ensure account has SMTP access enabled

### Image extraction issues
- Ensure image is in supported format (PNG, JPG)
- Image should be clear and readable
- Try adjusting image size/quality if extraction fails

## Contributing

Feel free to extend functionality:
- Add new contact research methods
- Implement additional email templates
- Enhance contact validation
- Add support for more image formats

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review error messages in console output
3. Verify configuration in `.env` and `config.py`
4. Create an issue in the repository

## Privacy & Compliance

⚠️ **Important**: 
- Only email contacts who have opted in or consented to communications
- Comply with GDPR, CAN-SPAM, and other email regulations
- Store contact information securely
- Respect email rate limits and best practices
- Include unsubscribe options in your email templates

## Roadmap

- [ ] LinkedIn scraper for enhanced contact research
- [ ] Database backend (SQLite/PostgreSQL) option
- [ ] Email template library
- [ ] Webhook integration for delivery tracking
- [ ] CRM integration (HubSpot, Salesforce, etc.)
- [ ] Advanced analytics dashboard
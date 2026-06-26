# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working Style (token discipline)

- **Think like a caveman.** Short words. No fluff. No filler. Answer, then stop.
- Do work, don't narrate it. Skip preambles ("Great question", "Let me explain").
- Update this CLAUDE.md only at **session end**, not after every chat — saves tokens.
- No fake data ever. Real contacts/emails only, source-backed. Empty beats fabricated.

## Overview

**Friends of Nature** is a Python-based automation system that:
1. Extracts company information from infographics using Claude Vision API
2. Researches executive contact information via web scraping
3. Stores contacts in a CSV database
4. Sends personalized outreach emails via Gmail API

The system implements a strict 4-phase workflow that must be followed in order.

## Architecture & Data Flow

### Phase 1: Image Processing (`src/image_processor.py`)
- Takes an infographic image as input
- Uses Claude Vision API (claude-3-5-sonnet-20241022) to analyze and extract company names + locations
- Returns structured JSON with `company_name` and `location` fields
- Includes fallback text parsing if JSON extraction fails
- **Key function**: `extract_companies_from_image(image_path: str) -> List[Dict]`

### Phase 2: Contact Research (`src/contact_researcher.py`)
- For each company with missing contact info, performs multi-strategy research:
  - Finds company website via Google search scraping
  - Extracts emails and phone numbers from website HTML
  - Attempts common domain patterns (info@, contact@, hello@)
  - Searches for CEO information and names
- Uses `requests` for HTTP calls with configurable timeout and User-Agent
- Includes 2-second delays between batches to avoid blocking
- **Key class**: `ContactResearcher` with `research_company(company_name, location)` method

### Phase 3: Data Storage (`src/data_manager.py`)
- CSV-based contact database with 11 fields (company_name, location, ceo_name, email, phone, linkedin_profile, whatsapp, data_source, extraction_date, email_sent, send_date)
- Deduplicates by email address
- Validates email format before storing
- Tracks which contacts have been emailed
- **Key class**: `ContactManager` - loads/saves CSV, manages contact lifecycle

### Phase 4: Email Sending (`src/email_sender.py`)
- OAuth2 authentication with Gmail API
- Personalizes templates with contact fields (e.g., `{{company_name}}`, `{{ceo_name}}`)
- Sends emails in batches with configurable delays (default: 10 emails per batch, 2-second delay)
- Tracks send success/failure status
- **Key class**: `GmailSender` - authenticates, sends individual/batch emails

### Orchestration (`src/main.py`)
- CLI tool with `argparse` that coordinates all phases
- Commands:
  - `--extract-companies IMAGE_PATH`: Run phase 1
  - `--research-contacts`: Run phase 2
  - `--send-emails MESSAGE_FILE [--dry-run]`: Run phase 4
  - `--status`: Show statistics
- Logs to both file and stdout

## Key Configuration

Configuration comes from two sources (in priority order):
1. **`.env` file** - Environment variables loaded via `python-dotenv`
2. **`config.py`** - Defines defaults and imports from `.env`

### Important Environment Variables
- `ANTHROPIC_API_KEY` - Required for Claude Vision API
- `GMAIL_CREDENTIALS_FILE` - Path to `credentials.json` (OAuth2 config)
- `GMAIL_TOKEN_FILE` - Path to `token.pickle` (OAuth2 token)
- `GMAIL_USER_EMAIL` - Gmail account to send from
- `EMAIL_FROM_NAME` - Display name in "From" header
- `EMAIL_SUBJECT_PREFIX` - Prefix for all email subjects
- `BATCH_SIZE` - Emails per batch before delay
- `DELAY_BETWEEN_SENDS` - Seconds between batches (respects Gmail quota)
- `REQUEST_TIMEOUT`, `MAX_RETRIES`, `USER_AGENT` - HTTP request config
- `LOG_LEVEL`, `LOG_FILE_EXTRACTION`, `LOG_FILE_EMAIL` - Logging

### File Paths
- `data/contacts.csv` - Contact database
- `data/infographic.png` - Input image (user supplies)
- `logs/extraction.log` - Company extraction & research logs
- `logs/email_delivery.log` - Email sending logs

## Setup & Running

### Installation
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration
1. Copy `.env.example` to `.env` and fill in API keys
2. Set up Gmail API:
   - Go to Google Cloud Console, create project
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop app type)
   - Download JSON credentials as `credentials.json` in project root
3. Place input image at `data/infographic.png`

### Workflow
```bash
# Step 1: Extract companies from image
python src/main.py --extract-companies data/infographic.png

# Step 2: Research contacts for companies without emails
python src/main.py --research-contacts

# Step 3: Check status
python src/main.py --status

# Step 4: Prepare message.txt with content (see message_template.txt for example)

# Step 5: Preview emails without sending
python src/main.py --send-emails message.txt --dry-run

# Step 6: Send actual emails
python src/main.py --send-emails message.txt
```

## Important Design Patterns

### Email Personalization
Templates support variable substitution using `{{field}}` syntax:
```
Dear {{ceo_name}},

Your company {{company_name}} in {{location}}...
```
All fields from the contact dict are available for substitution.

### Rate Limiting
- Email sending respects Gmail API quota (~500/day) via configurable batch delays
- Web scraping includes delays between requests to avoid blocking
- Always test with `--dry-run` before sending to real contacts

### Error Handling
- Phase 1 (image): Fallback text parsing if JSON extraction fails
- Phase 2 (research): Graceful degradation - returns None if no email found, continues with other companies
- Phase 3 (CSV): Creates `data/` and `logs/` directories automatically
- Phase 4 (email): Tracks failed emails separately, allows partial success

### Logging
- Two separate log files: extraction/research vs. email delivery
- Console output mirrors file logs for real-time feedback
- Log level and file paths configurable via environment

## Critical Implementation Details

### Image Processing
- Expects PNG format (or JPG - update media_type as needed)
- Uses base64 encoding for API transmission
- Prompts Claude to return JSON array of objects with specific keys

### Contact Research
- **Google scraping caveat**: Direct Google scraping may fail due to blocking; consider alternative research methods if this becomes unreliable
- Email extraction filters out example/test/noreply domains
- Phone number patterns support US format and international format
- CEO search extracts first name + last name pattern only

### Data Manager
- CSV headers are fixed (see `HEADERS` constant) - do not add/remove fields
- Email validation uses regex pattern - updates to pattern affect all validation
- Deduplication is email-based (not company-based) - duplicate companies with different emails are stored separately
- `email_sent` and `send_date` fields updated automatically during sending

### Gmail Integration
- First OAuth2 flow opens browser for user authorization
- Token cached in `token.pickle` - delete to re-authenticate
- Must enable "Less secure app access" or use Gmail App Passwords (depending on account setup)
- MIME message structure: multipart alternative (text + optional HTML)

## Testing Checklist

When modifying phases, verify:
1. **Image extraction**: Does JSON parse correctly for various infographic formats?
2. **Contact research**: Are emails validated before storing? Do fallback strategies work?
3. **CSV storage**: Are duplicates handled correctly? Does data persist across runs?
4. **Email sending**: Does personalization replace all template variables? Are rate limits respected?

## Common Issues

### "Gmail credentials file not found"
- Create `credentials.json` via Google Cloud Console OAuth2 flow
- Path must be `./credentials.json` (project root) or set `GMAIL_CREDENTIALS_FILE` in `.env`

### "Anthropic API key missing"
- Set `ANTHROPIC_API_KEY` in `.env`
- Ensure key is valid and not expired

### Image extraction returns empty
- Image may be in non-PNG format; verify media_type in image_processor.py
- Claude may not recognize infographic format - test with sample company data manually

### Email send fails after authentication
- Check Gmail account has SMTP access enabled
- Delete `token.pickle` to force re-authentication
- Verify `GMAIL_USER_EMAIL` matches authenticated account

### Contact research finds no emails
- Web scraping limitations: websites may not expose emails in scrapeable HTML
- Consider adding API-based research (e.g., Hunter.io, RocketReach) as fallback
- Manual augmentation of CSV may be necessary for some companies

## Future Enhancements

Roadmap items in README suggest:
- LinkedIn scraper for enhanced contact research
- Database backend (SQLite/PostgreSQL) instead of CSV
- CRM integration (HubSpot, Salesforce)
- Webhook integration for delivery tracking

When implementing these, maintain phase separation and don't couple data flow.

## Branch & Deployment

- Development branch: `claude/extract-company-contacts-rfp2mg`
- Commits must include descriptive messages (not CLI commands)
- Never force-push to main/master
- Test with `--dry-run` before pushing changes that affect email sending

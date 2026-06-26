# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repo.

## Working Style (token discipline)

- **Think like a caveman.** Short words. No fluff. No filler. Answer, then stop.
- Do work, don't narrate it. Skip preambles ("Great question", "Let me explain").
- Update this CLAUDE.md only at **session end**, not after every chat — saves tokens.
- No fake data ever. Real contacts/emails only, source-backed. Empty beats fabricated.
- Infographic is a **starting point, not a limit**. Research data center companies
  worldwide — colos, REITs, crypto→AI compute, regional operators — all fair game.

## Overview

**Friends of Nature** is a Python automation system that:
1. Extracts company info from infographics via Claude Vision API
2. Researches contact info via web scraping/search
3. Stores contacts in CSV
4. Sends personalized outreach emails via Gmail API

Strict 4-phase workflow, run in order.

## Architecture & Data Flow

### Phase 1: Image Processing (`src/image_processor.py`)
- Input: infographic image. Uses Claude Vision (claude-3-5-sonnet-20241022).
- Returns JSON with `company_name` + `location`; falls back to text parse.
- **Key fn**: `extract_companies_from_image(image_path) -> List[Dict]`

### Phase 2: Contact Research (`src/contact_researcher.py`)
- Per company: find website, scrape emails/phones, try common patterns
  (info@, contact@, hello@), search CEO name.
- `requests` with configurable timeout/User-Agent; 2s delays between batches.
- **Key class**: `ContactResearcher.research_company(company_name, location)`

### Phase 3: Data Storage (`src/data_manager.py`)
- CSV DB, 11 fields: company_name, location, ceo_name, email, phone,
  linkedin_profile, whatsapp, data_source, extraction_date, email_sent, send_date.
- Dedup by email. Validates email format. Tracks emailed contacts.
- **Key class**: `ContactManager` — load/save CSV, manage lifecycle.

### Phase 4: Email Sending (`src/email_sender.py`)
- Gmail API OAuth2. Personalizes templates (`{{company_name}}`, `{{ceo_name}}`).
- Batches with delays (default 10/batch, 2s). Tracks success/failure.
- **Key class**: `GmailSender` — auth, send individual/batch.

### Orchestration (`src/main.py`)
- `argparse` CLI coordinating all phases. Logs to file + stdout. Commands:
  - `--extract-companies IMAGE_PATH` — phase 1
  - `--research-contacts` — phase 2
  - `--send-emails MESSAGE_FILE [--dry-run]` — phase 4
  - `--status` — stats

## Configuration

Two sources, priority order: **`.env`** (via `python-dotenv`), then **`config.py`** (defaults).

### Env Variables
- `ANTHROPIC_API_KEY` — Claude Vision API (required)
- `GMAIL_CREDENTIALS_FILE` / `GMAIL_TOKEN_FILE` — OAuth2 config / token
- `GMAIL_USER_EMAIL` — send-from account
- `EMAIL_FROM_NAME` / `EMAIL_SUBJECT_PREFIX` — From header / subject prefix
- `BATCH_SIZE` / `DELAY_BETWEEN_SENDS` — batch size / delay (Gmail quota)
- `REQUEST_TIMEOUT`, `MAX_RETRIES`, `USER_AGENT` — HTTP config
- `LOG_LEVEL`, `LOG_FILE_EXTRACTION`, `LOG_FILE_EMAIL` — logging

### File Paths
- `data/contacts.csv` — pipeline contact DB (gitignored)
- `data/company_contacts.csv` / `.xlsx` — researched outreach list (source-backed,
  confidence-rated: high/medium/low). Excel is the deliverable format.
- `data/infographic.png` — input image (user supplies)
- `logs/extraction.log`, `logs/email_delivery.log`

## Setup & Running

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Config steps:
1. Copy `.env.example` to `.env`, fill API keys.
2. Gmail API: Google Cloud Console → enable Gmail API → OAuth2 creds
   (Desktop app) → download as `credentials.json` in root.
3. Place image at `data/infographic.png`.

Workflow:
```bash
python src/main.py --extract-companies data/infographic.png  # 1
python src/main.py --research-contacts                       # 2
python src/main.py --status                                  # check
python src/main.py --send-emails message.txt --dry-run       # preview
python src/main.py --send-emails message.txt                 # send
```

## Design Patterns

### Email Personalization
`{{field}}` substitution; all contact dict fields available:
```
Dear {{ceo_name}}, Your company {{company_name}} in {{location}}...
```

### Rate Limiting
- Gmail quota ~500/day via batch delays. Web scraping delays avoid blocking.
- **Always `--dry-run` before sending to real contacts.**

### Error Handling
- P1: fallback text parse if JSON fails.
- P2: graceful degradation — returns None, continues other companies.
- P3: auto-creates `data/` and `logs/`.
- P4: tracks failures separately, allows partial success.

### Logging
Two log files (extraction/research vs email). Console mirrors files.

## Critical Implementation Details

### Image Processing
- PNG expected (or JPG — update media_type). Base64 transmission.
- Prompts Claude for JSON array with specific keys.

### Contact Research
- **Google scraping caveat**: direct scraping may be blocked; use alt methods.
- Filters example/test/noreply domains. US + intl phone patterns.
- CEO search: first + last name pattern only.
- Env may block direct page fetches (403) — use search snippets, corroborate
  across sources, mark confidence accordingly.

### Data Manager
- CSV headers fixed (`HEADERS` constant) — don't add/remove fields.
- Email-based dedup (not company) — same company, different emails kept separate.
- `email_sent` / `send_date` auto-updated during sending.

### Gmail Integration
- First OAuth2 flow opens browser. Token cached in `token.pickle` (delete to re-auth).
- May need App Passwords depending on account. MIME: multipart alternative.

## Common Issues

- **"Gmail credentials not found"**: create `credentials.json` via OAuth2 flow;
  path = root or set `GMAIL_CREDENTIALS_FILE`.
- **"Anthropic API key missing"**: set valid `ANTHROPIC_API_KEY` in `.env`.
- **Image extraction empty**: check media_type / format; test with sample data.
- **Email send fails post-auth**: enable SMTP; delete `token.pickle`; verify
  `GMAIL_USER_EMAIL` matches authed account.
- **Research finds no emails**: sites may not expose emails; consider Hunter.io/
  RocketReach fallback; manual CSV augmentation may be needed.

## Future Enhancements

LinkedIn scraper, DB backend (SQLite/Postgres), CRM integration, delivery webhooks.
Maintain phase separation — don't couple data flow.

## Branch & Deployment

- Branch: `claude/extract-company-contacts-rfp2mg`
- Descriptive commit messages. Never force-push main/master.
- `--dry-run` before pushing changes affecting email sending.

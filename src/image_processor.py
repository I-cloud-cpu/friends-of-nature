import logging
import base64
from pathlib import Path
from typing import List, Dict
import anthropic
import config

logger = logging.getLogger(__name__)

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, 'rb') as image_file:
        return base64.standard_b64encode(image_file.read()).decode('utf-8')

def extract_companies_from_image(image_path: str) -> List[Dict[str, str]]:
    """
    Extract company names and locations from infographic using Claude Vision API.
    Returns list of dicts with 'company_name' and 'location' keys.
    """
    if not Path(image_path).exists():
        logger.error(f"Image file not found: {image_path}")
        raise FileNotFoundError(f"Image file not found: {image_path}")

    logger.info(f"Processing image: {image_path}")

    image_data = encode_image_to_base64(image_path)

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": """Analyze this infographic and extract all company names and their locations.

Please provide the output as a JSON array with objects containing 'company_name' and 'location' fields.
For companies with multiple locations, create separate entries for each location.

Example format:
[
  {"company_name": "Google", "location": "Mesa, Arizona"},
  {"company_name": "Meta", "location": "Dallas, Oregon"},
  ...
]

Ensure all company names and locations are accurately extracted. If a location has a region or country, include it.
Return ONLY the JSON array, no other text."""
                    }
                ],
            }
        ],
    )

    response_text = message.content[0].text
    logger.info(f"Raw response length: {len(response_text)} characters")

    try:
        import json
        companies = json.loads(response_text)
        logger.info(f"Successfully extracted {len(companies)} company locations")
        return companies
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.error(f"Response text: {response_text[:500]}")
        return parse_companies_from_text(response_text)

def parse_companies_from_text(text: str) -> List[Dict[str, str]]:
    """Fallback parser if JSON parsing fails."""
    import json
    import re

    json_match = re.search(r'\[.*\]', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    companies = []
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('[') and not line.startswith(']'):
            parts = [p.strip() for p in line.split('-')]
            if len(parts) >= 2:
                companies.append({
                    'company_name': parts[0].strip('"{},'),
                    'location': parts[1].strip('"{},')
                })

    return companies

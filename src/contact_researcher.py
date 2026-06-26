import logging
import time
from typing import Dict, Optional, List
import requests
from bs4 import BeautifulSoup
import re
import config

logger = logging.getLogger(__name__)

class ContactResearcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.USER_AGENT})
        self.session.timeout = config.REQUEST_TIMEOUT
        self.cache = {}

    def research_company(self, company_name: str, location: str) -> Optional[Dict]:
        """
        Research a company and extract contact information.
        Returns dict with CEO name, email, phone, LinkedIn profile, etc.
        """
        logger.info(f"Researching {company_name} in {location}")

        result = {
            'company_name': company_name,
            'location': location,
            'ceo_name': '',
            'email': '',
            'phone': '',
            'linkedin_profile': '',
            'whatsapp': '',
            'data_source': 'web_research'
        }

        try:
            website = self.find_company_website(company_name)
            if website:
                result['website'] = website
                logger.info(f"Found website: {website}")

                contact_info = self.extract_contact_from_website(website)
                result.update(contact_info)

            if not result.get('email'):
                email = self.search_company_email(company_name)
                if email:
                    result['email'] = email

            if not result.get('ceo_name'):
                ceo_info = self.search_company_ceo(company_name)
                if ceo_info:
                    result['ceo_name'] = ceo_info.get('name', '')
                    if ceo_info.get('email') and not result.get('email'):
                        result['email'] = ceo_info.get('email')

            logger.info(f"Research complete for {company_name}")
        except Exception as e:
            logger.error(f"Error researching {company_name}: {e}")

        return result if result.get('email') else None

    def find_company_website(self, company_name: str, location: str = '') -> Optional[str]:
        """Find company website using search."""
        try:
            query = f"{company_name} official website"
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                links = soup.find_all('a', href=True)

                for link in links:
                    href = link['href']
                    if 'url?q=' in href and 'webcache' not in href:
                        url = href.split('url?q=')[1].split('&')[0]
                        if url.startswith('http'):
                            return url
        except Exception as e:
            logger.debug(f"Error finding website for {company_name}: {e}")

        return None

    def extract_contact_from_website(self, website: str) -> Dict:
        """Extract contact information from company website."""
        result = {
            'email': '',
            'phone': '',
            'ceo_name': ''
        }

        try:
            response = self.session.get(website, timeout=config.REQUEST_TIMEOUT)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()

                email = self.extract_email_from_text(text)
                if email:
                    result['email'] = email

                phone = self.extract_phone_from_text(text)
                if phone:
                    result['phone'] = phone
        except Exception as e:
            logger.debug(f"Error extracting contact from website: {e}")

        return result

    def extract_email_from_text(self, text: str) -> Optional[str]:
        """Extract email from text using regex."""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        matches = re.findall(pattern, text)

        if matches:
            valid_domains = ['@' + company.lower().split()[-1].replace(',', '') for company in ['']]

            for email in matches:
                if not any(x in email.lower() for x in ['example', 'test', 'noreply']):
                    return email

        return None

    def extract_phone_from_text(self, text: str) -> Optional[str]:
        """Extract phone number from text."""
        patterns = [
            r'\+?1?\s*\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})',
            r'\+\d{1,3}\s?\d{6,14}',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0] if isinstance(matches[0], str) else '-'.join(matches[0])

        return None

    def search_company_email(self, company_name: str) -> Optional[str]:
        """Search for company email address."""
        try:
            patterns = [
                f"info@{company_name.lower().replace(' ', '')}.com",
                f"contact@{company_name.lower().replace(' ', '')}.com",
                f"hello@{company_name.lower().replace(' ', '')}.com",
            ]

            for email in patterns:
                if self.is_valid_email(email):
                    return email
        except Exception as e:
            logger.debug(f"Error searching for email: {e}")

        return None

    def search_company_ceo(self, company_name: str) -> Optional[Dict]:
        """Search for company CEO information."""
        try:
            query = f"{company_name} CEO"

            response = self.session.get(
                f"https://www.google.com/search?q={query.replace(' ', '+')}",
                timeout=config.REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()

                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if 'CEO' in line and i > 0:
                        ceo_line = line.strip()
                        name_match = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)', ceo_line)
                        if name_match:
                            return {'name': name_match.group(1)}
        except Exception as e:
            logger.debug(f"Error searching CEO info: {e}")

        return None

    def is_valid_email(self, email: str) -> bool:
        """Basic email validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def research_companies(self, companies: List[Dict]) -> List[Dict]:
        """Research multiple companies."""
        results = []
        for i, company in enumerate(companies):
            try:
                result = self.research_company(
                    company.get('company_name', ''),
                    company.get('location', '')
                )
                if result:
                    results.append(result)

                if (i + 1) % 5 == 0:
                    time.sleep(2)
            except Exception as e:
                logger.error(f"Error processing company: {e}")

        return results

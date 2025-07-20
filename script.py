import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import time

# Base URL to start crawling from
BASE_URL = "https://www.greenfieldpuppies.com"


visited_urls = set()

found_numbers = set()

# Regex for US-style phone numbers
phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')

def is_internal_link(href):
    """Check if the link is internal to the base domain."""
    if not href:
        return False
    parsed_href = urlparse(urljoin(BASE_URL, href))
    return parsed_href.netloc == urlparse(BASE_URL).netloc

def extract_phone_numbers_from_text(text):
    """Find phone numbers in text using regex."""
    return phone_pattern.findall(text)

def crawl(url, max_pages=300):
    """Recursively crawl internal links and extract phone numbers."""
    if url in visited_urls or len(visited_urls) >= max_pages:
        return

    print(f"🔍 Visiting: {url}")
    visited_urls.add(url)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')


    page_text = soup.get_text(separator=' ')
    numbers = extract_phone_numbers_from_text(page_text)
    for number in numbers:
        cleaned = number.strip()
        if cleaned not in found_numbers:
            print(f"📞 Found: {cleaned}")
            found_numbers.add(cleaned)


    for link in soup.find_all("a", href=True):
        href = link['href']
        full_url = urljoin(BASE_URL, href)
        if is_internal_link(full_url):
            crawl(full_url, max_pages)


crawl(BASE_URL, max_pages=300)


with open("phone_numbers.txt", "w") as f:
    for number in sorted(found_numbers):
        f.write(number + "\n")

print(f"\n✅ Done! Found {len(found_numbers)} phone numbers. Saved to phone_numbers.txt.")

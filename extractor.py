import re
from bs4 import BeautifulSoup

PRICE_REGEX = r"(\d{1,3}(?:[ .]\d{3})*(?:,\d{2})?)\s*Kč"

def extract_price(html_text: str):
    match = re.search(PRICE_REGEX, html_text)
    if not match:
        return None
    
    raw = match.group(1)
    normalized = raw.replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(normalized)
    except:
        return None

def extract_availability(html_text: str):
    text = html_text.lower()
    if "skladem" in text:
        return "skladem"
    if "není skladem" in text or "nedostupné" in text:
        return "nedostupné"
    return "nejasné"

def extract_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    raw_text = soup.get_text(" ", strip=True)

    return {
        "price": extract_price(raw_text),
        "availability": extract_availability(raw_text)
    }

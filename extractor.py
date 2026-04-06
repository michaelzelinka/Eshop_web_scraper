import re
from bs4 import BeautifulSoup

PRICE_REGEX = r"(\d{1,3}(?:[ .]\d{3})*(?:,\d{2})?)\s*Kč"


def extract_price(html_text: str):
    """Extract price in Kč using regex. Returns float or None."""
    match = re.search(PRICE_REGEX, html_text)
    if not match:
        return None

    raw = match.group(1)
    cleaned = (
        raw.replace(" ", "")
        .replace(".", "")
        .replace(",", ".")
    )

    try:
        return float(cleaned)
    except:
        return None


def extract_availability(html_text: str):
    """Detect availability from Czech eshops."""
    t = html_text.lower()

    if "skladem" in t:
        return "skladem"
    if "není skladem" in t or "nedostupné" in t:
        return "nedostupné"

    return "nejasné"


def extract_data(html: str):
    """Parse HTML into clean text and extract price + availability."""
    soup = BeautifulSoup(html, "html.parser")
    raw_text = soup.get_text(" ", strip=True)

    return {
        "price": extract_price(raw_text),
        "availability": extract_availability(raw_text)
    }

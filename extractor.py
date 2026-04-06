import re
import json
from bs4 import BeautifulSoup

# --------------------------------------------------------
# HELPERS
# --------------------------------------------------------

def _to_float(raw):
    if not raw:
        return None
    cleaned = (
        raw.replace(" ", "")
            .replace("\xa0", "")
            .replace(".", "")
            .replace(",", ".")
    )
    try:
        return float(cleaned)
    except:
        return None


def extract_price_regex(text):
    PRICE_REGEX = r"(?:\b|^)(\d{1,3}(?:[ .]\d{3})*(?:,\d{2})?)\s*Kč"
    matches = re.findall(PRICE_REGEX, text)

    prices = []
    for m in matches:
        f = _to_float(m)
        if f and 10 < f < 20000:
            prices.append(f)

    if not prices:
        return None

    return min(prices)


def extract_availability(text):
    t = text.lower()

    rules = {
        "skladem": "skladem",
        "do 24 hodin": "dostupné do 24 hodin",
        "do 48 hodin": "dostupné do 48 hodin",
        "do 3 dn": "dostupné do 3 dnů",
        "do 7 dn": "dostupné do 7 dnů",
        "odesíláme": "odesíláme do X",
        "na objednávku": "na objednávku",
        "vyprodáno": "nedostupné",
        "nedostupné": "nedostupné",
    }

    for key, val in rules.items():
        if key in t:
            return val

    return "nejasné"


# --------------------------------------------------------
# SHOPTET PARSER
# --------------------------------------------------------

def extract_shoptet_price(soup):
    selectors = [
        ".price-final",
        ".price-value",
        ".product-detail-price",
        ".product-price",
        "strong",
    ]

    prices = []

    for sel in selectors:
        for el in soup.select(sel):
            txt = el.get_text(strip=True)
            if "Kč" in txt:
                f = _to_float(txt.replace("Kč", ""))
                if f and 10 < f < 20000:
                    prices.append(f)

    if prices:
        return min(prices)

    return None


def extract_shoptet_availability(soup):
    els = soup.select(
        ".availability, .availability-value, .product-availability"
    )
    if els:
        text = els[0].get_text(" ", strip=True)
        return extract_availability(text)

    return None


# --------------------------------------------------------
# WOOCOMMERCE PARSER (Spokojenypes.cz)
# --------------------------------------------------------

def extract_woocommerce_json(html):
    if "dataLayer.push" not in html:
        return None, None

    try:
        start = html.index("dataLayer.push({") + 15
        end = html.index("});", start)
        block = html[start:end]

        data = json.loads(block)

        price = data.get("page.detail.products", {}).get("priceWithVat")
        availability = data.get("page.detail.products", {}).get("available")

        if price:
            return float(price), availability
        return None, None
    except:
        return None, None


# --------------------------------------------------------
# MAIN DOM EXTRACTOR
# --------------------------------------------------------

def extract_data_from_dom(html):
    soup = BeautifulSoup(html, "html.parser")
    raw = soup.get_text(" ", strip=True)

    # 1) WooCommerce JSON
    price_json, avail_json = extract_woocommerce_json(html)
    if price_json:
        return {
            "price": price_json,
            "availability": extract_availability(avail_json or raw)
        }

    # 2) Shoptet
    price = extract_shoptet_price(soup)
    availability = extract_shoptet_availability(soup)

    # 3) fallback
    if not price:
        price = extract_price_regex(raw)
    if not availability:
        availability = extract_availability(raw)

    return {
        "price": price,
        "availability": availability
    }

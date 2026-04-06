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
            .replace("\u00a0", "")
            .replace(".", "")
            .replace(",", ".")
    )
    try:
        return float(cleaned)
    except Exception:
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
    """
    Shoptet: cena produktu je v .price-final nebo .product-detail-price.
    ZÁMĚRNĚ vynecháváme generický `strong`, který zachytává
    ceny v sekcích "Související produkty" (.top-products-content).
    """
    # Nejprve zkusíme specifické Shoptet selektory pro hlavní cenu
    specific_selectors = [
        ".price-final .price-value",
        ".price-final",
        ".product-detail-price .price-value",
        ".product-detail-price",
        "[itemprop='price']",
        ".product-price .price-value",
        ".product-price",
    ]
    for sel in specific_selectors:
        for el in soup.select(sel):
            # Přeskočíme elementy uvnitř .top-products-content (související produkty)
            if el.find_parent(class_="top-products-content"):
                continue
            if el.find_parent(class_="top-products"):
                continue
            txt = el.get_text(strip=True)
            # itemprop=price může mít hodnotu v atributu content
            if el.get("content"):
                try:
                    f = float(el["content"])
                    if 10 < f < 20000:
                        return f
                except Exception:
                    pass
            if "Kč" in txt or txt.replace(",", "").replace(".", "").strip().isdigit():
                f = _to_float(txt.replace("Kč", "").strip())
                if f and 10 < f < 20000:
                    return f
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
# DATALAYER PARSER (Shoptet / WooCommerce)
# Hledáme VŠECHNY dataLayer.push bloky a vracíme první,
# který obsahuje priceWithVat.
# --------------------------------------------------------

def extract_datalayer_price(html):
    """
    Projde všechny dataLayer.push({...}) bloky v HTML a vrátí
    (priceWithVat, available) z prvního bloku, který tyto klíče obsahuje.
    """
    # Najdeme všechny výskyty dataLayer.push({
    pattern = re.compile(r"dataLayer\.push\s*\(\s*(\{.*?\})\s*\)", re.DOTALL)
    matches = pattern.findall(html)

    for block in matches:
        # Odstraníme undefined hodnoty (není validní JSON)
        block_clean = re.sub(r':\s*undefined', ': null', block)
        try:
            data = json.loads(block_clean)
        except Exception:
            continue

        # Hledáme priceWithVat přímo nebo zanořeně pod libovolným klíčem
        price = data.get("priceWithVat")
        available = data.get("available")

        if price is None:
            # Shoptet někdy zabalí data pod klíč 'page.detail.products'
            for v in data.values():
                if isinstance(v, dict):
                    price = v.get("priceWithVat")
                    available = v.get("available")
                    if price is not None:
                        break

        if price is not None:
            try:
                return float(price), available
            except Exception:
                continue

    return None, None


# --------------------------------------------------------
# MAIN DOM EXTRACTOR
# --------------------------------------------------------

def extract_data_from_dom(html):
    soup = BeautifulSoup(html, "html.parser")
    raw = soup.get_text(" ", strip=True)

    # 1) dataLayer (funguje pro Shoptet i WooCommerce)
    price_dl, avail_dl = extract_datalayer_price(html)
    if price_dl:
        return {
            "price": price_dl,
            "availability": extract_availability(avail_dl or raw)
        }

    # 2) Shoptet DOM selektory (specifické, bez `strong`)
    price = extract_shoptet_price(soup)
    availability = extract_shoptet_availability(soup)

    # 3) Regex fallback (text celé stránky)
    if not price:
        price = extract_price_regex(raw)
    if not availability:
        availability = extract_availability(raw)

    return {
        "price": price,
        "availability": availability
    }

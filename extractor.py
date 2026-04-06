import re
import json
from bs4 import BeautifulSoup

PRICE_REGEX = r"(?:\b|^)(\d{1,3}(?:[ .]\d{3})*(?:,\d{2})?)\s*Kč"

# ---------------------------------------------
# ✅ HELPERY
# ---------------------------------------------

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


# ---------------------------------------------
# ✅ 1) SHOPTET – přesný selektor
# ---------------------------------------------
def extract_shoptet_price(soup):
    """
    Shoptet má cenu v <strong> v sekci top-products-content.
    Je to přesně to, co jsi poslal jako HTML ukázku.
    """
    candidates = soup.select("strong")
    prices = []

    for c in candidates:
        txt = c.get_text(strip=True)
        if "Kč" in txt:
            val = _to_float(txt.replace("Kč", "").strip())
            if val:
                prices.append(val)

    if not prices:
        return None

    # Nejnižší je obvykle správná
    return min(prices)


def extract_shoptet_availability(soup):
    """
    Shoptet dostupnost bývá v .availability nebo .availability-value.
    Pokud není, padáme na textovou heuristiku.
    """
    els = soup.select(".availability, .availability-value, .product-availability")
    if els:
        t = els[0].get_text(" ", strip=True).lower()

        if "skladem" in t:
            return t  # např. "skladem do 3 dnů"
        if "není" in t or "nedostupné" in t:
            return "nedostupné"
        return t

    return None


# ---------------------------------------------
# ✅ 2) WOO COMMERCE – spokojenypes.cz
# ---------------------------------------------
def extract_woocommerce_from_json(html):
    """
    WooCommerce (Spokojenypes.cz) dává cenu do dataLayer JSON.
    Tento JSON máme v ukázce.
    """
    if "dataLayer.push" not in html:
        return None, None

    # Pokusíme se izolovat JSON objekt
    try:
        start = html.index("dataLayer.push({")
        end = html.index("});", start) + 1
        json_block = html[start+15:end-1]

        data = json.loads(json_block)
        price = data.get("page.detail.products", {}).get("priceWithVat")
        availability = data.get("page.detail.products", {}).get("available")

        return price, availability
    except:
        return None, None


# ---------------------------------------------
# ✅ 3) GENERICKÁ DOSTUPNOST
# ---------------------------------------------
def extract_availability_generic(text):
    t = text.lower()

    patterns = {
        "skladem": "skladem",
        "do 24 hodin": "dostupné do 24 hodin",
        "do 48 hodin": "dostupné do 48 hodin",
        "do 3 dn": "dostupné do 3 dnů",
        "do 7 dn": "dostupné do 7 dnů",
        "odesíláme": "odesíláme brzy",
        "na objednávku": "na objednávku",
        "vyprodáno": "nedostupné",
        "nedostupné": "nedostupné"
    }

    for key, val in patterns.items():
        if key in t:
            return val

    return "nejasné"


# ---------------------------------------------
# ✅ 4) FALLBACK PRICE – regex
# ---------------------------------------------
def extract_price_regex(text):
    matches = re.findall(PRICE_REGEX, text)
    prices = [_to_float(m) for m in matches if _to_float(m)]
    prices = [p for p in prices if 10 < p < 20000]

    if not prices:
        return None

    return min(prices)


# ---------------------------------------------
# ✅ FINÁLNÍ EXTRAKTOR
# ---------------------------------------------
def extract_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    raw_text = soup.get_text(" ", strip=True)

    price, availability = None, None

    # 1) WooCommerce JSON (Spokojenypes.cz)
    p_json, a_json = extract_woocommerce_from_json(html)
    if p_json:
        price = p_json
        availability = a_json

    # 2) Shoptet (Goddo.cz, MujPsidum.cz)
    if not price:
        price = extract_shoptet_price(soup)

    if not availability:
        availability = extract_shoptet_availability(soup)

    # 3) fallback dostupnost
    if not availability:
        availability = extract_availability_generic(raw_text)

    # 4) fallback cena přes regex
    if not price:
        price = extract_price_regex(raw_text)

    return {
        "price": price,
        "availability": availability
    }

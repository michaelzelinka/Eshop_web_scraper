import re
import json
from bs4 import BeautifulSoup

PRICE_SELECTORS = [
    ".price-final",                 # Shoptet
    ".price-value",                 # Shoptet
    ".product-price",               # WooCommerce custom
    ".woocommerce-Price-amount",    # WooCommerce
    ".product-detail__price-main",  # některé Shoptet šablony
    "meta[itemprop='price']",       # microdata
]

AVAIL_SELECTORS = [
    ".availability", 
    ".availability-value",
    ".product-availability",
    ".stock",                       # WooCommerce (In stock)
]


def extract_data_from_dom(html):
    soup = BeautifulSoup(html, "html.parser")

    # -----------------------
    # ✅ 1) Shoptet/WooCommerce ceny z DOM
    # -----------------------
    for selector in PRICE_SELECTORS:
        el = soup.select_one(selector)
        if el:
            txt = el.get_text(strip=True) if not el.name == "meta" else el.get("content")
            if "Kč" in txt or txt.replace(".", "").replace(",", "").isdigit():
                return _clean_extracted_price(soup, txt)

    # -----------------------
    # ✅ 2) WooCommerce JSON (dataLayer)
    # -----------------------
    if "dataLayer.push" in html:
        try:
            start = html.index("dataLayer.push({") + 15
            end = html.index("});", start)
            block = html[start:end]
            data = json.loads(block)

            price = data.get("page.detail.products", {}).get("priceWithVat")
            availability = data.get("page.detail.products", {}).get("available")
            if price:
                return {
                    "price": float(price),
                    "availability": availability
                }
        except:
            pass

    # -----------------------
    # ✅ 3) Čistý fallback regex
    # -----------------------
    text = soup.get_text(" ", strip=True)
    price = extract_price_regex(text)
    availability = extract_availability(text)

    return {
        "price": price,
        "availability": availability
    }



# OSTATNÍ FUNKCE ZDE — price regex, availability regex atd.
# (nemusíme to zde tisknout celé, ponecháme cenu a dostupnost správně definovanou)

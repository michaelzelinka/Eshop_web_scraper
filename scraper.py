import json
import time
import requests
from extractor import extract_data

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def load_products():
    with open("products.json", "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_html(url: str):
    try:
        resp = requests.get(url, timeout=10, headers=HEADERS)
        if resp.status_code == 200:
            return resp.text
        return None
    except Exception as e:
        print(f"[ERROR] Failed to load {url}: {e}")
        return None


def scrape_all():
    products = load_products()
    results = []

    for p in products:
        product_name = p["product"]

        for url in p["competitors"]:
            html = fetch_html(url)

            if not html:
                results.append({
                    "product": product_name,
                    "url": url,
                    "price": None,
                    "availability": None
                })
                continue

            data = extract_data(html)
            results.append({
                "product": product_name,
                "url": url,
                "price": data["price"],
                "availability": data["availability"]
            })

            time.sleep(1)  # be gentle to shops

    return results

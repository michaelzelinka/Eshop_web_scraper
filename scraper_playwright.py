from playwright.sync_api import sync_playwright
import json
from extractor import extract_data_from_dom


def scrape_with_playwright(products):
    """
    Hlavní Playwright scraper:
    - otevře každou URL
    - počká, až se načte JS i DOM
    - extrahuje celý DOM HTML
    - pošle jej extractor.py, který extrahuje cenu a dostupnost
    """

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for product in products:
            name = product["product"]

            for url in product["competitors"]:
                print(f"▶ Scraping {url}...")
                try:
                    page.goto(url, timeout=30000, wait_until="networkidle")

                    # Vytáhneme skutečný DOM
                    html = page.content()

                    # extrakce ceny + dostupnosti
                    data = extract_data_from_dom(html)

                    results.append({
                        "product": name,
                        "url": url,
                        "price": data["price"],
                        "availability": data["availability"]
                    })

                except Exception as e:
                    print(f"❌ Chyba při scrapování {url}: {e}")
                    results.append({
                        "product": name,
                        "url": url,
                        "price": None,
                        "availability": None
                    })

        browser.close()

    return results

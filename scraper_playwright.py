from playwright.sync_api import sync_playwright
import json
import time
from extractor import extract_data_from_dom


def scrape_with_playwright(products):
    """
    Stabilní Playwright scraper pro CZ e‑shopy:
    - realistic user-agent
    - domcontentloaded místo networkidle
    - retry mechanismus
    - scroll page (Shoptet lazy-load)
    - delší timeout
    """

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0 Safari/537.36"
            ),
            locale="cs-CZ",
            viewport={"width": 1280, "height": 900},
        )

        page = context.new_page()

        # ---------------------------------------------------------
        # INTERNÍ FUNKCE – robustní načtení URL
        # ---------------------------------------------------------
        def load_url(url):
            retries = 3
            for attempt in range(retries):
                try:
                    page.goto(
                        url,
                        timeout=45000,              # 45s
                        wait_until="domcontentloaded"
                    )

                    # Scroll dolů, Shoptet někdy lazy-loaduje část stránky
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(0.5)

                    return page.content()

                except Exception as e:
                    print(f"⚠️ Retry {attempt+1}/{retries} for {url}: {e}")
                    time.sleep(1)
            
            print(f"❌ Final fail for {url}")
            return None

        # ---------------------------------------------------------
        # SCRAPING
        # ---------------------------------------------------------
        for product in products:
            name = product["product"]

            for url in product["competitors"]:
                print(f"▶ Scraping {url}...")

                html = load_url(url)

                if not html:
                    results.append({
                        "product": name,
                        "url": url,
                        "price": None,
                        "availability": None
                    })
                    continue

                try:
                    data = extract_data_from_dom(html)
                except Exception as e:
                    print(f"❌ Extractor crash on {url}: {e}")
                    data = {"price": None, "availability": None}

                results.append({
                    "product": name,
                    "url": url,
                    "price": data["price"],
                    "availability": data["availability"]
                })

        browser.close()
        return results

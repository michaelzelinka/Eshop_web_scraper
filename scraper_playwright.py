from playwright.sync_api import sync_playwright
import json
import time
import random
from extractor import extract_data_from_dom


def scrape_with_playwright(products):
    """
    Stabilní Playwright scraper pro CZ e‑shopy:
    - HTTP/2 vypnutý (řeší ERR_HTTP2_PROTOCOL_ERROR)
    - realistic user-agent + plné HTTP headers
    - nová page pro každý request (čistá session)
    - exponential backoff při retry
    - scroll page (Shoptet lazy-load)
    """
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-http2",   # klíčové: řeší ERR_HTTP2_PROTOCOL_ERROR
                "--disable-quic",
            ]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="cs-CZ",
            timezone_id="Europe/Prague",
            viewport={"width": 1280, "height": 900},
            extra_http_headers={
                "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            }
        )

        # ---------------------------------------------------------
        # INTERNÍ FUNKCE – robustní načtení URL
        # ---------------------------------------------------------
        def load_url(url):
            retries = 3
            for attempt in range(retries):
                page = context.new_page()
                try:
                    page.goto(
                        url,
                        timeout=45000,
                        wait_until="domcontentloaded"
                    )
                    # Scroll dolů, Shoptet někdy lazy-loaduje část stránky
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(0.5)
                    content = page.content()
                    page.close()
                    return content
                except Exception as e:
                    print(f"⚠️ Retry {attempt+1}/{retries} for {url}: {e}")
                    page.close()
                    # Exponential backoff: 1s, 2s, 4s
                    time.sleep(2 ** attempt)

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
                else:
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

                # Pauza mezi requesty – snižuje riziko throttlingu
                time.sleep(random.uniform(1.5, 3.5))

        browser.close()
        return results

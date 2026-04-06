from scraper_playwright import scrape_with_playwright
from utilities import save_csv, upload_to_sheets, validate_results, send_discord_alert
import json

SHEET_ID = "1A1tylaob6it1_BKXqTkbwv_Duqm6rQrSqYU9FEnAHf8"

if __name__ == "__main__":
    print("▶ Spouštím Playwright scraper…")

    with open("products.json") as f:
        products = json.load(f)

    results = scrape_with_playwright(products)

    if not validate_results(results):
        save_csv(results)
    else:
        save_csv(results)
        upload_to_sheets(results, SHEET_ID)

    print("✅ Hotovo.")

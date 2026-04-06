from scraper import scrape_all
from utilities import (
    save_csv,
    upload_to_sheets,
    validate_results,
    send_discord_alert
)

SHEET_ID = "1A1tylaob6it1_BKXqTkbwv_Duqm6rQrSqYU9FEnAHf8"


if __name__ == "__main__":
    print("▶ Spouštím scraper…")

    # 1) Scrapování
    results = scrape_all()

    # 2) Validace
    if not validate_results(results):
        print("⚠️ Scraper dokončen s chybami.")
        # Upozornění šlo již přes Discord → nemusíme pokračovat dál
        # ale CSV uložíme vždy, kvůli debug účelům
        save_csv(results)
    else:
        print("✅ Scraper dokončen bez kritických chyb.")
        save_csv(results)

        # 3) Google Sheet export
        if SHEET_ID and SHEET_ID != "TVŮJ_SHEET_ID":
            try:
                upload_to_sheets(results, SHEET_ID)
            except Exception as e:
                print(f"❌ Chyba při uploadu do Sheets: {e}")
                send_discord_alert(f"Google Sheets upload selhal: {e}")

    print("✅ Hotovo.")

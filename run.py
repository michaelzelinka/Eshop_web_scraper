from scraper import scrape_all
from utilities import save_csv, upload_to_sheets
from send_alert import send_discord_alert   # ✅ přidáno

SHEET_ID = "1A1tylaob6it1_BKXqTkbwv_Duqm6rQrSqYU9FEnAHf8"   

if __name__ == "__main__":
    print("▶ Running scraper...")

    results = scrape_all()

    # ✅ Error detection — pošli alert jen tobě
    if any(r["price"] is None for r in results):
        send_discord_alert("Některé ceny se nepodařilo načíst. Zkontroluj scraper!")

    save_csv(results)

    if SHEET_ID:
        upload_to_sheets(results, SHEET_ID)

    print("✅ Done.")

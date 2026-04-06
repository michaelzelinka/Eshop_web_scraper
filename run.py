from scraper import scrape_all
from utilities import save_csv, upload_to_sheets, send_alert_email

SHEET_ID = "TVŮJ_GOOGLE_SHEET_ID"  #Název souboru dle klienta


if __name__ == "__main__":
    print("▶ Running scraper...")

    results = scrape_all()

    # Error detection
    if any(r["price"] is None for r in results):
        send_alert_email("⚠️ Scraper: Některé ceny se nepodařilo načíst.")

    save_csv(results)

    if SHEET_ID:
        upload_to_sheets(results, SHEET_ID)

    print("✅ Done.")

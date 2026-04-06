import os
import json
import requests
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# ---------------------------------------------
# ✅ DISCORD ALERT
# ---------------------------------------------
def send_discord_alert(message: str):
    """
    Odeslání alertu do Discordu přes webhook.
    URL webhooku se načítá z GitHub Secrets (DISCORD_WEBHOOK).
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK")

    if not webhook_url:
        print("⚠️ DISCORD_WEBHOOK není nastaven.")
        return

    payload = {
        "content": f"⚠️ **Scraper Alert**\n{message}"
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code in (200, 204):
            print("✅ Discord alert odeslán.")
        else:
            print(f"❌ Discord webhook selhal, status {response.status_code}")
    except Exception as e:
        print(f"❌ Chyba při odesílání Discord alertu: {e}")


# ---------------------------------------------
# ✅ GOOGLE CREDS → vytvoření service_account.json
# ---------------------------------------------
def write_google_creds():
    """
    Vytvoří service_account.json z environment variable GOOGLE_CREDS.
    GitHub Secrets obsahuje celý JSON jako text.
    """
    creds_json = os.getenv("GOOGLE_CREDS")

    if not creds_json:
        raise RuntimeError("Missing GOOGLE_CREDS secret.")

    try:
        with open("service_account.json", "w", encoding="utf-8") as f:
            f.write(creds_json)
        print("✅ service_account.json vytvořen.")
    except Exception as e:
        print(f"❌ Chyba při zapisování service_account.json: {e}")
        raise


# ---------------------------------------------
# ✅ CSV export
# ---------------------------------------------
def save_csv(results, path="output.csv"):
    """
    Uloží výsledky do CSV, přidá timestamp.
    """
    df = pd.DataFrame(results)
    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"✅ CSV uloženo: {path}")


# ---------------------------------------------
# ✅ GOOGLE SHEETS export
# ---------------------------------------------
def upload_to_sheets(results, sheet_id: str):
    """
    Nahraje výsledky do Google Sheets.
    sheet_id = ID dokumentu (část URL mezi /d/ a /edit)
    """
    # 1️⃣ vytvoříme service_account.json
    write_google_creds()

    # 2️⃣ připravíme credentials
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "service_account.json",
            scope
        )
        client = gspread.authorize(creds)
    except Exception as e:
        print(f"❌ Nepodařilo se autorizovat Google Sheets: {e}")
        send_discord_alert("Nepodařilo se autorizovat Google Sheets API.")
        return

    # 3️⃣ Otevřeme sheet
    try:
        sheet = client.open_by_key(sheet_id).sheet1
    except Exception as e:
        print(f"❌ Nepodařilo se otevřít Google Sheet: {e}")
        send_discord_alert("Nepodařilo se otevřít Google Sheet (špatné ID?).")
        return

    # 4️⃣ Připravíme data
    df = pd.DataFrame(results)
    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 5️⃣ Nahrajeme data
    try:
        sheet.clear()
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
        print("✅ Google Sheet aktualizován.")
    except Exception as e:
        print(f"❌ Chyba při nahrávání dat do Google Sheets: {e}")
        send_discord_alert("Chyba při uploadu dat do Google Sheets.")


# ---------------------------------------------
# ✅ VALIDACE
# ---------------------------------------------
def validate_results(results):
    """
    Vrací True pokud jsou data OK.
    Pokud jsou nějaké problémy → pošle alert a vrátí False.
    """
    if not results:
        send_discord_alert("Scraper vrátil prázdný výsledek.")
        return False

    if any(r["price"] is None for r in results):
        send_discord_alert("Některé ceny se nepodařilo načíst.")
        return False

    return True

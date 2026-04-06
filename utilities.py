import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def save_csv(results, path="output.csv"):
    df = pd.DataFrame(results)
    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"✅ Saved CSV to {path}")


def upload_to_sheets(results, sheet_id: str):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "service_account.json",
        scope
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1

    df = pd.DataFrame(results)
    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

    print("✅ Google Sheet updated.")


def send_client_email(recipient, sheet_url=None):
    msg = MIMEText(f"Aktuální monitoring konkurence:\n\n{sheet_url}")
    msg["Subject"] = "Denní report konkurence"
    msg["From"] = "noreply@monitor"
    msg["To"] = recipient

    with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as server:
        server.login("EMAIL_LOGIN", "EMAIL_PASSWORD")
        server.send_message(msg)

    print("✅ Report sent to client")


def send_alert_email(message: str):
    msg = MIMEText(message)
    msg["Subject"] = "Scraper ERROR"
    msg["From"] = "alert@monitor"
    msg["To"] = "tvuj-email@domena.cz"

    with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as server:
        server.login("ALERT_EMAIL_LOGIN", "ALERT_EMAIL_PASS")
        server.send_message(msg)

    print("⚠️ Alert sent to you")

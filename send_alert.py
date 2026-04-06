import os
import requests

def send_discord_alert(message: str):
    """
    Send alert to Discord via webhook.
    The webhook URL is stored safely in GitHub Secrets as DISCORD_WEBHOOK.
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK")

    if not webhook_url:
        print("⚠️ WARNING: DISCORD_WEBHOOK is not set.")
        return

    payload = {
        "content": f"⚠️ **Scraper Alert**\n{message}"
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code in (200, 204):
            print("✅ Discord alert sent.")
        else:
            print(f"❌ Discord webhook returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to send Discord alert: {e}")

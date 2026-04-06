# 🛒 Price Monitoring Scraper (CZ E‑shops)

Jednoduchý, spolehlivý a automatizovaný nástroj pro monitoring cen a dostupnosti produktů u českých e‑shopů.

Projekt byl navržen jako:
- reálné **MVP pro malé e‑shopy** (bez nákladných SaaS řešení)
- snadno rozšiřitelný scraping backend
- automatický denní/týdenní report do CSV a Google Sheets
- bezpečný cron runner přes GitHub Actions
- robustní error monitoring přes Discord alerty

## ✅ Funkce

### 🔍 Scraping konkurence
- stažení HTML z konkurenčních e‑shopů
- extrakce ceny pomocí robustních CZ regexů
- detekce dostupnosti: *skladem / nedostupné / nejasné*
- fallback na chybějící hodnoty (loguje do Discordu)

### 📄 CSV export
- ukládá `output.csv` s timestampem
- vhodné pro e‑mailovou distribuci nebo archivaci

### 📊 Google Sheets export
- automatické nahrání výsledků do Google Sheets (API)
- přehledný živý dokument s výsledky
- historie se řeší verzováním v Sheets

### 🚨 Discord alerty
- chyby scraperu se posílají do privátního Discord kanálu
- klient chyby nevidí
- upozornění při:
  - změně HTML struktury
  - chybějících cenách
  - selhání requestů
  - chybě GitHub Actions workflow

### ⏱️ GitHub Actions cron
- běží denně v 7:00 (lze změnit)
- automaticky spouští scraper + export
- žádný backend / žádný hosting / 0 Kč měsíčně

---

## ✅ Architektura projektu

.
├── extractor.py        # extrakce ceny + dostupnosti z HTML
├── scraper.py          # hlavní logika skriptu
├── products.json       # seznam produktů a konkurenčních URL
├── run.py              # orchestrátor – scraping → CSV → Sheets → alerty
├── utilities.py        # CSV export, Google Sheets API, Discord alerty
├── send_alert.py       # modul pro odeslání Discord alertu (volitelné)
├── requirements.txt    # knihovny (requests, bs4, pandas…)
└── .github/workflows/scrape.yml  # cron job přes GitHub Actions

---

## ✅ Jak to běží (high‑level)

1. GitHub Actions spustí skript 1× denně.
2. `scraper.py` načte `products.json`, stáhne HTML a extrahuje data.
3. `utilities.py` uloží CSV a aktualizuje Google Sheet.
4. Pokud scraping selže → Discord dostane alert.
5. Data jsou dostupná klientovi / e‑shopu ke kontrole nebo automatické analýze.

---

## ✅ products.json – příklad

```
[
  {
    "product": "Název produktu",
    "competitors": [
      "https://www.konkurence.cz/produkt/",
      "https://www.konkurence2.cz/produkt/"
    ]
  }
]
```

---

✅ Local run
Shellpip install -r requirements.txtpython run.pyZobrazit více řádků
Tím se vytvoří:

output.csv
případně aktualizuje Google Sheet (pokud je SHEET_ID vyplněný)


✅ Secrets (GitHub Actions)
V repozitáři → Settings → Secrets → Actions

Secret name - Popis
DISCORD_WEBHOOKURL - webhooku z Discord serveru (jen pro alerty)
GOOGLE_CREDS - celý obsah service_account.json (Google API)
EMAIL_LOGIN - email pro odeslání CSV (volitelné)
EMAIL_PASSWORD - SMTP heslo (volitelné)
Google Sheet - musí být sdílen s účtem: your-service-account@project-id.iam.gserviceaccount.com


✅ GitHub Actions (cron)
Workflow je v:
.github/workflows/scrape.yml

Běží denně v 07:00 a provádí:

scraping
CSV export
export do Google Sheets
odeslání alertů při selhání


✅ Pro koho je projekt určen?

malé e‑shopy (Shoptet, WooCommerce, Shopify, custom CMS)
kteří chtějí:

denní přehled konkurence
sledovat „vyprodáno“
sledovat zlevňování
jednoduchý přehled bez velkého SaaS řešení


✅ Co by mohlo následovat (roadmap)

webové UI pro konfiguraci produktů
timeline grafy cen v Google Sheets
porovnání kategorií / brandů
alerty na změnu ceny přímo klientovi
jednoduchý hosted dashboard


✅ Licence
MIT


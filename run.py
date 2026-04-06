from scraper.scraper import scrape_all
from scraper.utils import save_to_csv

if __name__ == "__main__":
    print("▶ Spouštím scraper…")
    results = scrape_all()
    save_to_csv(results)
    print("✅ Hotovo.")
``

import re
from bs4 import BeautifulSoup

# Regex pro české ceny ve tvaru:
# 149 Kč
# 1 490 Kč
# 1.490 Kč
# 149,90 Kč
PRICE_REGEX = r"(?:\b|^)(\d{1,3}(?:[ .]\d{3})*(?:,\d{2})?)\s*Kč"


def extract_price(html_text: str):
    """
    Robustní extrakce ceny:
    1) najde všechny cenové výskyty v textu
    2) převede všechny na float
    3) odfiltruje extrémy (příliš nízké/vysoké, přeškrtnuté staré ceny)
    4) vrátí NEJNIŽŠÍ reálnou cenu (typicky správná koncová cena produktu)
    """

    matches = re.findall(PRICE_REGEX, html_text)
    if not matches:
        return None

    prices = []
    for raw in matches:
        cleaned = (
            raw.replace(" ", "")
               .replace(".", "")
               .replace(",", ".")
        )
        try:
            value = float(cleaned)
            prices.append(value)
        except:
            pass

    if not prices:
        return None

    # Filtr extrémních hodnot (např. 0.0 Kč nebo 100 000 Kč)
    filtered = [p for p in prices if 10 < p < 20000]

    if not filtered:
        filtered = prices

    # Vracíme nejnižší cenu — u CZ e‑shopů je to *téměř vždy* reálná aktuální cena
    return min(filtered)


def extract_availability(html_text: str):
    """
    Detekce dostupnosti pro české e‑shopy.
    Zvládá běžné varianty:
    - skladem
    - skladem do X dnů
    - dostupné do X hodin / dnů
    - odesíláme do X dnů
    - na objednávku
    - dočasně nedostupné
    - zboží na dotaz
    """

    t = html_text.lower()

    # ✅ jednoznačné skladem
    if "skladem" in t:
        # rozlišíme, jestli je to pouze "skladem" nebo "skladem do X"
        if "do" in t and "dn" in t:
            return "skladem do X dnů"
        if "do" in t and "hodin" in t:
            return "skladem do X hodin"
        if "více než" in t or "kus" in t:
            return "skladem (omezené množství)"
        return "skladem"

    # ✅ dostupnost s časem
    if "do" in t and "hodin" in t:
        return "dostupné do X hodin"
    if "do" in t and ("dn" in t or "den" in t):
        return "dostupné do X dnů"
    if "odesíláme do" in t:
        return "odesíláme do X dnů"

    # ✅ typické "nižší priorita" dostupnosti
    if "na objednávku" in t or "objednávku" in t:
        return "na objednávku"

    # ✅ klasické nedostupnosti
    if (
        "dočasně" in t
        or "nedostupné" in t
        or "vyprodáno" in t
        or "zboží na dotaz" in t
        or "není skladem" in t
    ):
        return "nedostupné"

    return "nejasné"


def extract_data(html: str):
    """
    Extrakce celé stránky:
    - z HTML → čistý text
    - extrakce ceny
    - extrakce dostupnosti
    """

    soup = BeautifulSoup(html, "html.parser")
    raw_text = soup.get_text(" ", strip=True)

    return {
        "price": extract_price(raw_text),
        "availability": extract_availability(raw_text)
    }

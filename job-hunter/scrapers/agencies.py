"""Scraper kariérních stránek vybraných pražských firem."""
import time
import requests
from bs4 import BeautifulSoup
from .base import JobOffer, parse_salary, HEADERS
from config import AGENCIES, LOCATION


class AgenciesScraper:
    name = "Kariérní stránky firem"

    def fetch(self) -> list[JobOffer]:
        offers = []
        for agency in AGENCIES:
            try:
                found = _scrape_career_page(agency)
                print(f"    {agency['name']}: {len(found)} marketingových pozic")
                offers.extend(found)
                time.sleep(1)
            except Exception as e:
                print(f"    {agency['name']}: chyba — {e}")
        return offers


def _scrape_career_page(agency: dict) -> list[JobOffer]:
    resp = requests.get(agency["url"], headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    keyword = agency.get("keyword", "marketing").lower()
    offers = []

    # Hledáme všechny <a> tagy obsahující klíčové slovo v textu nebo href
    for link in soup.find_all("a", href=True):
        text = link.get_text(strip=True)
        href = link["href"]

        if keyword not in text.lower() and keyword not in href.lower():
            continue

        # Filtrujeme příliš krátké texty (menu, ikony apod.)
        if len(text) < 5:
            continue

        url = href if href.startswith("http") else _absolute_url(agency["url"], href)

        offers.append(JobOffer(
            title=text,
            company=agency["name"],
            url=url,
            source=agency["name"],
            description=f"Nalezeno na kariérní stránce {agency['name']}",
            location=LOCATION,
        ))

    # Deduplikace podle URL
    seen = set()
    unique = []
    for o in offers:
        if o.url not in seen:
            seen.add(o.url)
            unique.append(o)

    return unique[:5]  # max 5 pozic na firmu


def _absolute_url(base: str, path: str) -> str:
    from urllib.parse import urljoin
    return urljoin(base, path)

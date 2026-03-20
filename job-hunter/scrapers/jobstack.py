"""Scraper pro Profesia.cz — HTML scraping výsledků hledání."""
import re
import time
import requests
from bs4 import BeautifulSoup
from .base import JobOffer, parse_salary, HEADERS
from config import LOCATION

BASE_URL = "https://www.profesia.cz"
SEARCH_URL = f"{BASE_URL}/prace/marketing/Praha/"


class JobstackScraper:
    name = "Profesia.cz"

    def fetch(self) -> list[JobOffer]:
        try:
            resp = requests.get(SEARCH_URL, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"  Profesia.cz: chyba: {e}")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        offers = []

        # Profesia.cz — aktuální struktura (li.list-row nebo article s data-id)
        cards = (
            soup.select("li.list-row")
            or soup.select("article[data-id]")
            or soup.select("div.offer-list-item")
        )

        for card in cards:
            # Titulek a URL
            title_el = (
                card.select_one("a.title")
                or card.select_one("h2 > a")
                or card.select_one("h3 > a")
                or card.select_one("a[href*='/ponuka/']")
                or card.select_one("a[href*='/prace/']")
            )
            # Firma
            company_el = (
                card.select_one("span.employer")
                or card.select_one("span[itemprop='name']")
                or card.select_one(".company-name")
                or card.select_one("strong")
            )
            # Plat
            salary_el = (
                card.select_one("span.label")
                or card.select_one(".salary")
                or card.select_one("[class*='salary']")
                or card.select_one("[class*='plat']")
            )

            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            url = title_el.get("href", "")
            if url and not url.startswith("http"):
                url = BASE_URL + url
            company = company_el.get_text(strip=True) if company_el else ""
            salary_text = salary_el.get_text(strip=True) if salary_el else ""
            description = card.get_text(" ", strip=True)

            if not title or not url or len(title) < 4:
                continue

            # Přeskočit pokud URL není na konkrétní nabídku
            if not re.search(r"/(prace|ponuka)/[^/]+/[^/]+", url):
                continue

            offers.append(JobOffer(
                title=title,
                company=company,
                url=url,
                source=self.name,
                description=description[:800],
                salary_text=salary_text,
                salary_min=parse_salary(salary_text),
                location=LOCATION,
            ))
            time.sleep(0.1)

        return offers

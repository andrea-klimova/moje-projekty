"""Scraper pro Profesia.cz (náhrada za nefunkční Jobstack.cz)."""
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
            print(f"  Profesia.cz: chyba při načítání: {e}")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        offers = []

        for card in soup.select("li.list-row, div.list-row, article[data-job-id]"):
            title_el = card.select_one("h2 a, h3 a, .title a, a.position-name")
            company_el = card.select_one(".employer, .company, span[itemprop='name']")
            salary_el = card.select_one(".label-group .label, .salary, [class*='salary']")
            link_el = card.select_one("a[href]")

            title = title_el.get_text(strip=True) if title_el else ""
            company = company_el.get_text(strip=True) if company_el else ""
            salary_text = salary_el.get_text(strip=True) if salary_el else ""
            url = (title_el or link_el or {}).get("href", "") if (title_el or link_el) else ""
            if url and not url.startswith("http"):
                url = BASE_URL + url
            description = card.get_text(" ", strip=True)

            if not title or not url:
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
            time.sleep(0.2)

        return offers

"""Scraper pro LinkedIn — veřejné výsledky hledání (bez přihlášení).

Poznámka: LinkedIn aktivně blokuje automatizované požadavky.
Scraper funguje na základě veřejného HTML, ale může přestat
fungovat bez varování. Výsledky jsou orientační.
"""
import time
import requests
from bs4 import BeautifulSoup
from .base import JobOffer, parse_salary, HEADERS
from config import LOCATION

SEARCH_URL = (
    "https://www.linkedin.com/jobs/search/"
    "?keywords=marketing&location=Praha%2C+Czech+Republic"
    "&f_WT=1%2C2%2C3"  # remote, hybrid, on-site
)

# LinkedIn vyžaduje specifické hlavičky
LI_HEADERS = {
    **HEADERS,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.linkedin.com/",
}


class LinkedInScraper:
    name = "LinkedIn"

    def fetch(self) -> list[JobOffer]:
        try:
            resp = requests.get(SEARCH_URL, headers=LI_HEADERS, timeout=20)
            if resp.status_code in (429, 999):
                print("  LinkedIn: přístup omezen (rate limit). Přeskakuji.")
                return []
            resp.raise_for_status()
        except Exception as e:
            print(f"  LinkedIn: chyba při načítání: {e}")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        offers = []

        # LinkedIn public search HTML struktura
        cards = soup.select("div.base-card, div.job-search-card, li.result-card")
        if not cards:
            print("  LinkedIn: žádné karty nenalezeny (struktura se mohla změnit).")
            return []

        for card in cards[:20]:
            title_el = card.select_one("h3.base-search-card__title, h3, .job-result-card__title")
            company_el = card.select_one("h4.base-search-card__subtitle, .job-result-card__subtitle")
            link_el = card.select_one("a[href*='/jobs/view/']")
            salary_el = card.select_one(".job-result-card__salary-info, [class*='salary']")

            title = title_el.get_text(strip=True) if title_el else ""
            company = company_el.get_text(strip=True) if company_el else ""
            url = link_el.get("href", "").split("?")[0] if link_el else ""
            salary_text = salary_el.get_text(strip=True) if salary_el else ""

            if not title or not url:
                continue

            offers.append(JobOffer(
                title=title,
                company=company,
                url=url,
                source=self.name,
                description=f"{title} @ {company}",
                salary_text=salary_text,
                salary_min=parse_salary(salary_text),
                location=LOCATION,
            ))
            time.sleep(0.3)

        return offers

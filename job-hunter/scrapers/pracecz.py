"""Scraper pro Prace.cz — HTML scraping."""
import re
import time
import requests
from bs4 import BeautifulSoup
from .base import JobOffer, parse_salary, HEADERS
from config import LOCATION

BASE_URL = "https://www.prace.cz"

SEARCH_URLS = [
    f"{BASE_URL}/prace/q-marketing/Praha/",
    f"{BASE_URL}/prace/q-brand-manager/Praha/",
    f"{BASE_URL}/prace/q-performance-marketing/Praha/",
    f"{BASE_URL}/prace/q-PPC-specialista/Praha/",
]


class PraceCzScraper:
    name = "Prace.cz"

    def fetch(self) -> list[JobOffer]:
        seen: set[str] = set()
        offers = []

        for url in SEARCH_URLS:
            try:
                resp = requests.get(url, headers=HEADERS, timeout=15)
                resp.raise_for_status()
            except Exception as e:
                print(f"  Prace.cz chyba ({url[-40:]}…): {e}")
                continue

            soup = BeautifulSoup(resp.text, "lxml")
            cards = (
                soup.select("article.search-result")
                or soup.select("div[data-jobad-id]")
                or soup.select("li.search-result__item")
                or soup.select("div.job-item")
            )

            for card in cards:
                title_el = card.select_one("h2 a, h3 a, a[data-link='title'], a.title")
                company_el = card.select_one(".employer, .company, span[class*='company']")
                salary_el = card.select_one(".salary, [class*='salary'], [class*='plat']")

                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                href = title_el.get("href", "")
                if not href.startswith("http"):
                    href = BASE_URL + href
                if href in seen or not href:
                    continue
                seen.add(href)

                company = company_el.get_text(strip=True) if company_el else ""
                salary_text = salary_el.get_text(strip=True) if salary_el else ""
                description = card.get_text(" ", strip=True)

                offers.append(JobOffer(
                    title=title,
                    company=company,
                    url=href,
                    source=self.name,
                    description=description[:800],
                    salary_text=salary_text,
                    salary_min=parse_salary(salary_text),
                    location=LOCATION,
                ))
            time.sleep(0.5)

        return offers

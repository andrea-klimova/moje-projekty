"""Scraper pro StartupJobs.cz — HTML scraping."""
import time
import requests
from bs4 import BeautifulSoup
from .base import JobOffer, parse_salary, HEADERS
from config import LOCATION

BASE_URL = "https://www.startupjobs.cz"
SEARCH_URL = f"{BASE_URL}/nabidky?superObor=marketing&misto=Praha"


class StartupJobsScraper:
    name = "StartupJobs.cz"

    def fetch(self) -> list[JobOffer]:
        try:
            resp = requests.get(SEARCH_URL, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"  StartupJobs: chyba při načítání: {e}")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        offers = []

        for card in soup.select("a.job-list-item, article.offer-item, div[data-jobid]"):
            title_el = card.select_one("h2, h3, .offer-title, .job-title")
            company_el = card.select_one(".company-name, .employer, .offer-company")
            salary_el = card.select_one(".salary, .offer-salary, [class*='salary']")
            url = card.get("href") or card.select_one("a[href]", {}).get("href", "")
            if url and not url.startswith("http"):
                url = BASE_URL + url

            title = title_el.get_text(strip=True) if title_el else ""
            company = company_el.get_text(strip=True) if company_el else ""
            salary_text = salary_el.get_text(strip=True) if salary_el else ""
            description = card.get_text(" ", strip=True)

            if not title or not url:
                continue

            offers.append(JobOffer(
                title=title,
                company=company,
                url=url,
                source=self.name,
                description=description[:1000],
                salary_text=salary_text,
                salary_min=parse_salary(salary_text),
                location=LOCATION,
            ))
            time.sleep(0.2)

        return offers

"""Scraper pro Prace.cz — HTML scraping výsledků hledání."""
import re
import time
import requests
from bs4 import BeautifulSoup
from .base import JobOffer, parse_salary, HEADERS
from config import LOCATION

BASE_URL = "https://www.prace.cz"
SEARCH_URL = f"{BASE_URL}/prace/marketing/?locality%5Bcity%5D=Praha"


class PraceCzScraper:
    name = "Prace.cz"

    def fetch(self) -> list[JobOffer]:
        try:
            resp = requests.get(SEARCH_URL, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"  Prace.cz chyba: {e}")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        offers = []

        # Prace.cz používá různé verze layoutu — zkusíme více selektorů
        cards = (
            soup.select("article.search-result-item")
            or soup.select("div.job-item")
            or soup.select("li[data-jobid]")
            or soup.select("div[class*='job-card']")
        )

        if not cards:
            # Fallback: hledáme všechny <a> s /prace/ v href
            for a in soup.find_all("a", href=re.compile(r"/prace/[^/]+/[^/]+")):
                title = a.get_text(strip=True)
                href = a.get("href", "")
                if not title or len(title) < 8:
                    continue
                url = href if href.startswith("http") else BASE_URL + href
                offers.append(JobOffer(
                    title=title,
                    company="",
                    url=url,
                    source=self.name,
                    description=title,
                    location=LOCATION,
                ))
            return offers

        for card in cards:
            title_el = card.select_one("h2 a, h3 a, a.title, a[href*='/prace/']")
            company_el = card.select_one(".employer, .company, .firma, strong")
            salary_el = card.select_one(".salary, .plat, [class*='salary']")

            title = title_el.get_text(strip=True) if title_el else ""
            company = company_el.get_text(strip=True) if company_el else ""
            salary_text = salary_el.get_text(strip=True) if salary_el else ""
            url = title_el.get("href", "") if title_el else ""
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

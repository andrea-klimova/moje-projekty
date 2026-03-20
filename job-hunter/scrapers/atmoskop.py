"""Scraper pro Atmoskop.cz — pracovní nabídky s hodnocením firem."""
import re
import requests
from bs4 import BeautifulSoup
from .base import JobOffer, parse_salary, HEADERS
from config import LOCATION

BASE_URL = "https://www.atmoskop.cz"
SEARCH_URL = f"{BASE_URL}/nabidky?q=marketing&lokace=Praha"


class AtmoskopScraper:
    name = "Atmoskop.cz"

    def fetch(self) -> list[JobOffer]:
        try:
            resp = requests.get(SEARCH_URL, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"  Atmoskop.cz chyba: {e}")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        offers = []
        seen: set[str] = set()

        # Atmoskop HTML selektory
        cards = (
            soup.select("div.job-offer-card")
            or soup.select("article.job-card")
            or soup.select("li.job-item")
            or soup.select("div[class*='JobCard']")
            or soup.select("div[class*='job-card']")
        )

        for card in cards:
            title_el = card.select_one("h2 a, h3 a, a[href*='/prace/']")
            company_el = card.select_one(".company, .employer, [class*='company']")
            salary_el = card.select_one(".salary, [class*='salary']")

            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            url = href if href.startswith("http") else BASE_URL + href
            if url in seen or len(title) < 4:
                continue
            seen.add(url)

            company = company_el.get_text(strip=True) if company_el else ""
            salary_text = salary_el.get_text(strip=True) if salary_el else ""
            description = card.get_text(" ", strip=True)

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

        # Fallback — hledáme jakékoliv <a> s /prace/ v href
        if not offers:
            for a in soup.find_all("a", href=re.compile(r"/prace/[^/]+$")):
                title = a.get_text(strip=True)
                href = a.get("href", "")
                url = href if href.startswith("http") else BASE_URL + href
                if url in seen or len(title) < 5:
                    continue
                seen.add(url)
                offers.append(JobOffer(
                    title=title, company="", url=url,
                    source=self.name, description=title,
                    location=LOCATION,
                ))

        return offers

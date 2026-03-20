"""Scraper pro Jobstack.cz — HTML scraping."""
import time
import requests
from bs4 import BeautifulSoup
from .base import JobOffer, parse_salary, HEADERS
from config import LOCATION

BASE_URL = "https://www.jobstack.cz"
SEARCH_URL = f"{BASE_URL}/prace/marketing/Praha"


class JobstackScraper:
    name = "Jobstack.cz"

    def fetch(self) -> list[JobOffer]:
        try:
            resp = requests.get(SEARCH_URL, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"  Jobstack: chyba při načítání: {e}")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        offers = []

        # Jobstack používá různé struktury — zkusíme obecné selektory
        selectors = [
            "div.job-item", "article.job", "div.offer", "li.job",
            "div[class*='job-card']", "div[class*='offer-item']",
        ]
        cards = []
        for sel in selectors:
            cards = soup.select(sel)
            if cards:
                break

        # Fallback: hledáme všechny <a> s /prace/ v href
        if not cards:
            links = soup.find_all("a", href=lambda h: h and "/prace/" in h)
            for link in links:
                title = link.get_text(strip=True)
                url = link.get("href", "")
                if not url.startswith("http"):
                    url = BASE_URL + url
                if title and "marketing" in title.lower():
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
            title_el = card.select_one("h2, h3, .job-title, .title, a[href*='/prace/']")
            company_el = card.select_one(".company, .employer, .firma")
            salary_el = card.select_one(".salary, .plat, [class*='salary']")
            link_el = card.select_one("a[href]")

            title = title_el.get_text(strip=True) if title_el else ""
            company = company_el.get_text(strip=True) if company_el else ""
            salary_text = salary_el.get_text(strip=True) if salary_el else ""
            url = link_el.get("href", "") if link_el else ""
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
                description=description[:1000],
                salary_text=salary_text,
                salary_min=parse_salary(salary_text),
                location=LOCATION,
            ))
            time.sleep(0.2)

        return offers

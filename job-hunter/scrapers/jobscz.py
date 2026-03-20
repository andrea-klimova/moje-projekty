"""Scrapery pro Jobs.cz a Indeed.cz."""
import re
import time
import requests
import feedparser
from bs4 import BeautifulSoup
from .base import JobOffer, parse_salary, HEADERS
from config import LOCATION

# --- Jobs.cz ---

JOBS_CZ_QUERIES = [
    "https://www.jobs.cz/prace/?q%5B%5D=marketing&locality%5Bradius%5D=0&locality%5Bcity%5D=Praha",
    "https://www.jobs.cz/prace/?q%5B%5D=brand+manager&locality%5Bradius%5D=0&locality%5Bcity%5D=Praha",
    "https://www.jobs.cz/prace/?q%5B%5D=performance+marketing&locality%5Bradius%5D=0&locality%5Bcity%5D=Praha",
    "https://www.jobs.cz/prace/?q%5B%5D=PPC+specialista&locality%5Bradius%5D=0&locality%5Bcity%5D=Praha",
]

# --- Indeed.cz (záloha) ---

INDEED_QUERIES = [
    "marketing", "brand+manager", "performance+marketing",
    "PPC+specialista", "SEM+specialista", "growth+marketing",
]
INDEED_BASE = "https://cz.indeed.com/rss?l=Praha&radius=25&sort=date&q="


class JobsCzScraper:
    name = "Jobs.cz"

    def fetch(self) -> list[JobOffer]:
        seen: set[str] = set()
        offers = _scrape_jobscz(seen)
        if not offers:
            print("  Jobs.cz: HTML scraping selhal, zkouším Indeed.cz zálohu…")
            offers = _scrape_indeed(seen)
        return offers


def _scrape_jobscz(seen: set) -> list[JobOffer]:
    offers = []
    for url in JOBS_CZ_QUERIES:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            # Jobs.cz ukládá data do JSON-LD nebo data atributů
            cards = (
                soup.select("article.SearchResultCard")
                or soup.select("div[data-jobad-id]")
                or soup.select("li.search-result__item")
                or soup.select("article[data-id]")
            )

            for card in cards:
                title_el = card.select_one("h2 a, h3 a, a.SearchResultCard__titleLink, a[data-link='title']")
                company_el = card.select_one(".SearchResultCard__company, .employer, span[class*='company']")
                salary_el = card.select_one(".SearchResultCard__salary, .salary, [class*='salary']")

                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                href = title_el.get("href", "")
                if not href.startswith("http"):
                    href = "https://www.jobs.cz" + href
                if href in seen:
                    continue
                seen.add(href)

                company = company_el.get_text(strip=True) if company_el else ""
                salary_text = salary_el.get_text(strip=True) if salary_el else ""
                description = card.get_text(" ", strip=True)

                offers.append(JobOffer(
                    title=title,
                    company=company,
                    url=href,
                    source="Jobs.cz",
                    description=description[:800],
                    salary_text=salary_text,
                    salary_min=parse_salary(salary_text),
                    location=LOCATION,
                ))
        except Exception as e:
            print(f"  Jobs.cz chyba ({url[-40:]}…): {e}")
        time.sleep(0.5)
    return offers


def _scrape_indeed(seen: set) -> list[JobOffer]:
    offers = []
    for query in INDEED_QUERIES:
        try:
            resp = requests.get(INDEED_BASE + query, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
        except Exception as e:
            print(f"  Indeed.cz ({query}) chyba: {e}")
            continue

        for entry in feed.entries:
            url = entry.get("link", "").split("?")[0]
            if url in seen:
                continue
            seen.add(url)
            summary = entry.get("summary", "") or entry.get("description", "")
            salary_text = _find_salary(summary)
            offers.append(JobOffer(
                title=entry.get("title", ""),
                company=entry.get("author", "") or _find_company(summary),
                url=url,
                source="Indeed.cz",
                description=_strip_html(summary)[:800],
                salary_text=salary_text,
                salary_min=parse_salary(salary_text),
                location=LOCATION,
            ))
        time.sleep(0.5)
    return offers


def _find_company(html: str) -> str:
    m = re.search(r"<b>(.*?)</b>", html, re.IGNORECASE)
    return m.group(1).strip() if m else ""

def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html).strip()

def _find_salary(text: str) -> str:
    m = re.search(r"(\d[\d\s]*(?:Kč|CZK|tis\.?\s*Kč|k\b)[^<\n]*)", text, re.IGNORECASE)
    return m.group(1).strip() if m else ""

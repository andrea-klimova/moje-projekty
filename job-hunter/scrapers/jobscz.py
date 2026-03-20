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
    "https://www.jobs.cz/prace/praha/marketing/",
    "https://www.jobs.cz/prace/praha/pr-komunikace/",
    "https://www.jobs.cz/prace/praha/marketing/?locality%5Bradius%5D=10",
]

# --- Indeed.cz (záloha) ---

INDEED_URLS = [
    "https://cz.indeed.com/jobs?q=marketing&l=Praha%2C+Hlavn%C3%AD+m%C4%9Bsto+Praha",
    "https://cz.indeed.com/jobs?q=brand+manager&l=Praha%2C+Hlavn%C3%AD+m%C4%9Bsto+Praha",
    "https://cz.indeed.com/jobs?q=performance+marketing&l=Praha%2C+Hlavn%C3%AD+m%C4%9Bsto+Praha",
    "https://cz.indeed.com/jobs?q=PPC+specialista&l=Praha%2C+Hlavn%C3%AD+m%C4%9Bsto+Praha",
]


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
    from bs4 import BeautifulSoup
    offers = []
    for url in INDEED_URLS:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"  Indeed.cz chyba: {e}")
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        cards = (
            soup.select("div.job_seen_beacon")
            or soup.select("div.jobsearch-ResultsList > li")
            or soup.select("div[data-jk]")
            or soup.select("td.resultContent")
        )
        for card in cards:
            title_el = card.select_one("h2.jobTitle a, h2 a, a[data-jk]")
            company_el = card.select_one("span.companyName, [data-testid='company-name']")
            salary_el = card.select_one("div.salary-snippet, [data-testid='attribute_snippet_testid']")

            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            job_url = f"https://cz.indeed.com{href}" if href.startswith("/") else href
            if job_url in seen or not title:
                continue
            seen.add(job_url)
            company = company_el.get_text(strip=True) if company_el else ""
            salary_text = salary_el.get_text(strip=True) if salary_el else ""
            offers.append(JobOffer(
                title=title,
                company=company,
                url=job_url,
                source="Indeed.cz",
                description=f"{title} @ {company}",
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

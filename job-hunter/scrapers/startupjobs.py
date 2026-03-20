"""Scraper pro StartupJobs.cz — extrakce dat ze stránky."""
import json
import re
import requests
from bs4 import BeautifulSoup
from .base import JobOffer, parse_salary, HEADERS
from config import LOCATION

BASE_URL = "https://www.startupjobs.cz"

SEARCH_URLS = [
    f"{BASE_URL}/nabidky?superObor=marketing&misto=Praha",
    f"{BASE_URL}/nabidky?superObor=marketing",  # záloha bez filtru města
]


class StartupJobsScraper:
    name = "StartupJobs.cz"

    def fetch(self) -> list[JobOffer]:
        for url in SEARCH_URLS:
            try:
                resp = requests.get(url, headers=HEADERS, timeout=20)
                resp.raise_for_status()
            except Exception as e:
                print(f"  StartupJobs chyba: {e}")
                continue

            # 1. Pokus: extrakce z __NEXT_DATA__ (Next.js)
            offers = _from_nextjs(resp.text)
            if offers:
                return offers

            # 2. Pokus: přímé HTML selektory
            offers = _from_html(resp.text)
            if offers:
                return offers

        return []


def _from_nextjs(html: str) -> list[JobOffer]:
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return []

    items = _deep_find_list(data)
    if not items:
        return []

    offers = []
    for item in items[:50]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("name") or item.get("title") or item.get("nazev") or "")
        company_raw = item.get("company") or item.get("firma") or {}
        company = (company_raw.get("name") or company_raw.get("nazev") or "") if isinstance(company_raw, dict) else str(company_raw)
        slug = str(item.get("slug") or item.get("url") or item.get("id") or "")
        url = slug if slug.startswith("http") else (f"{BASE_URL}/nabidka/{slug}" if slug else "")
        salary = str(item.get("salary") or item.get("plat") or "")
        location = str(item.get("city") or item.get("mesto") or LOCATION)

        if not title or len(title) < 4:
            continue
        offers.append(JobOffer(
            title=title,
            company=company,
            url=url,
            source="StartupJobs.cz",
            description=f"{title} @ {company}",
            salary_text=salary,
            salary_min=parse_salary(salary),
            location=location,
        ))
    return offers


def _from_html(html: str) -> list[JobOffer]:
    soup = BeautifulSoup(html, "lxml")
    offers = []
    seen: set[str] = set()

    # StartupJobs HTML selektory
    cards = (
        soup.select("div.offer-card")
        or soup.select("article.job-offer")
        or soup.select("div[class*='OfferCard']")
        or soup.select("div[class*='offer-item']")
    )

    for card in cards:
        title_el = card.select_one("h2 a, h3 a, a[href*='/nabidka/']")
        company_el = card.select_one(".company, .employer, [class*='company']")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        href = title_el.get("href", "")
        url = href if href.startswith("http") else BASE_URL + href
        if url in seen or not title:
            continue
        seen.add(url)
        company = company_el.get_text(strip=True) if company_el else ""
        offers.append(JobOffer(
            title=title, company=company, url=url,
            source="StartupJobs.cz", description=f"{title} @ {company}",
            location=LOCATION,
        ))

    if not offers:
        # Úplný fallback: hledáme <a href="/nabidka/...">
        for a in soup.find_all("a", href=re.compile(r"/nabidka/")):
            title = a.get_text(strip=True)
            href = a.get("href", "")
            url = href if href.startswith("http") else BASE_URL + href
            if url in seen or len(title) < 5:
                continue
            seen.add(url)
            offers.append(JobOffer(
                title=title, company="", url=url,
                source="StartupJobs.cz", description=title,
                location=LOCATION,
            ))

    return offers


def _deep_find_list(data, depth: int = 0) -> list:
    """Rekurzivně hledá seznam nabídek v Next.js JSON."""
    if depth > 6:
        return []
    if isinstance(data, list) and len(data) > 2 and isinstance(data[0], dict):
        if any(k in data[0] for k in ("name", "title", "nazev", "slug")):
            return data
    if isinstance(data, dict):
        for key in ("offers", "nabidky", "jobs", "items", "results", "data", "props", "pageProps"):
            if key in data:
                result = _deep_find_list(data[key], depth + 1)
                if result:
                    return result
        for v in data.values():
            result = _deep_find_list(v, depth + 1)
            if result:
                return result
    return []

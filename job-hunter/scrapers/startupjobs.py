"""Scraper pro StartupJobs.cz — extrakce dat z Next.js stránky."""
import json
import re
import requests
from .base import JobOffer, parse_salary, HEADERS
from config import LOCATION

BASE_URL = "https://www.startupjobs.cz"
SEARCH_URL = f"{BASE_URL}/nabidky?superObor=marketing&misto=Praha"


class StartupJobsScraper:
    name = "StartupJobs.cz"

    def fetch(self) -> list[JobOffer]:
        try:
            resp = requests.get(SEARCH_URL, headers=HEADERS, timeout=20)
            resp.raise_for_status()
        except Exception as e:
            print(f"  StartupJobs chyba: {e}")
            return []

        # StartupJobs je Next.js — data jsou v __NEXT_DATA__ JSON blogu
        offers = _extract_nextjs(resp.text)
        if offers:
            return offers

        # Fallback: hledáme <a> tagy s /nabidka/ v href
        return _extract_links(resp.text)


def _extract_nextjs(html: str) -> list[JobOffer]:
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return []

    # Prohledáme rekurzivně JSON strukturu pro seznam nabídek
    offers_raw = _find_list(data, ["offers", "nabidky", "jobs", "items", "results"])
    if not offers_raw:
        return []

    offers = []
    for item in offers_raw[:50]:
        if not isinstance(item, dict):
            continue
        title = item.get("name") or item.get("title") or item.get("nazev") or ""
        company_data = item.get("company") or item.get("firma") or {}
        company = company_data.get("name") or company_data.get("nazev") or "" if isinstance(company_data, dict) else str(company_data)
        slug = item.get("slug") or item.get("url") or ""
        url = slug if slug.startswith("http") else f"{BASE_URL}/nabidka/{slug}" if slug else ""
        salary = item.get("salary") or item.get("plat") or ""

        if not title:
            continue

        offers.append(JobOffer(
            title=title,
            company=company,
            url=url,
            source="StartupJobs.cz",
            description=f"{title} @ {company}",
            salary_text=str(salary),
            salary_min=parse_salary(str(salary)),
            location=LOCATION,
        ))
    return offers


def _find_list(data, keys: list) -> list:
    """Rekurzivně hledá seznam v JSON struktuře."""
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        return data
    if isinstance(data, dict):
        for key in keys:
            if key in data and isinstance(data[key], list):
                return data[key]
        for v in data.values():
            result = _find_list(v, keys)
            if result:
                return result
    return []


def _extract_links(html: str) -> list[JobOffer]:
    """Záložní extrakce odkazů na nabídky."""
    offers = []
    seen = set()
    for m in re.finditer(r'href="(/nabidka/[^"]+)"[^>]*>([^<]+)', html):
        href, title = m.group(1), m.group(2).strip()
        if href in seen or len(title) < 5:
            continue
        seen.add(href)
        offers.append(JobOffer(
            title=title,
            company="",
            url=BASE_URL + href,
            source="StartupJobs.cz",
            description=title,
            location=LOCATION,
        ))
    return offers

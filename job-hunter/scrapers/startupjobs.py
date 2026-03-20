"""Scraper pro StartupJobs.cz — JSON API."""
import requests
from .base import JobOffer, parse_salary, HEADERS
from config import LOCATION

# StartupJobs veřejné API
API_URL = "https://www.startupjobs.cz/api/nabidky.json"

PARAMS = {
    "limit": 50,
    "superObor[]": "marketing",
}


class StartupJobsScraper:
    name = "StartupJobs.cz"

    def fetch(self) -> list[JobOffer]:
        try:
            resp = requests.get(API_URL, params=PARAMS, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  StartupJobs API chyba: {e}")
            return _fallback_html()

        offers = []
        items = data if isinstance(data, list) else data.get("nabidky", data.get("offers", []))

        for item in items:
            title = item.get("name") or item.get("title") or item.get("nazev", "")
            company = (item.get("company") or {}).get("name") or item.get("firma", "")
            url = item.get("url") or item.get("link") or ""
            if url and not url.startswith("http"):
                url = "https://www.startupjobs.cz" + url
            salary_text = item.get("salary") or item.get("plat") or ""
            location = item.get("city") or item.get("mesto") or LOCATION
            description = item.get("description") or item.get("popis") or f"{title} @ {company}"

            if not title:
                continue

            offers.append(JobOffer(
                title=title,
                company=company,
                url=url,
                source="StartupJobs.cz",
                description=str(description)[:800],
                salary_text=str(salary_text),
                salary_min=parse_salary(str(salary_text)),
                location=location,
            ))

        return offers


def _fallback_html() -> list[JobOffer]:
    """Záložní HTML scraping pokud API selže."""
    import re
    from bs4 import BeautifulSoup

    BASE = "https://www.startupjobs.cz"
    url = f"{BASE}/nabidky?superObor=marketing&misto=Praha"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    offers = []

    for a in soup.find_all("a", href=re.compile(r"/nabidka/")):
        title = a.get_text(strip=True)
        href = a.get("href", "")
        if not title or len(title) < 5:
            continue
        full_url = href if href.startswith("http") else BASE + href
        offers.append(JobOffer(
            title=title,
            company="",
            url=full_url,
            source="StartupJobs.cz",
            description=title,
            location=LOCATION,
        ))

    return offers

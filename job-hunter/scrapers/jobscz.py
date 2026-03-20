"""Scraper pro Indeed.cz — RSS feed (náhrada za nefunkční Jobs.cz RSS)."""
import re
import time
import requests
import feedparser
from .base import JobOffer, parse_salary, HEADERS
from config import LOCATION

# Více dotazů = více typů marketingových pozic
RSS_QUERIES = [
    "marketing",
    "brand+manager",
    "performance+marketing",
    "PPC+specialista",
    "SEM+specialista",
    "growth+marketing",
    "digital+marketing",
]
RSS_BASE = "https://cz.indeed.com/rss?l=Praha&radius=25&sort=date&q="


class JobsCzScraper:
    name = "Indeed.cz"

    def fetch(self) -> list[JobOffer]:
        seen_urls: set[str] = set()
        all_offers = []

        for query in RSS_QUERIES:
            url = RSS_BASE + query
            try:
                resp = requests.get(url, headers=HEADERS, timeout=15)
                resp.raise_for_status()
                feed = feedparser.parse(resp.content)
            except Exception as e:
                print(f"  Indeed.cz ({query}) chyba: {e}")
                continue

            for entry in feed.entries:
                offer_url = entry.get("link", "").split("?")[0]
                if offer_url in seen_urls:
                    continue
                seen_urls.add(offer_url)

                title = entry.get("title", "")
                summary = entry.get("summary", "") or entry.get("description", "")
                company = entry.get("author", "") or _find_company(summary)
                salary_text = _find_salary(summary)

                all_offers.append(JobOffer(
                    title=title,
                    company=company,
                    url=offer_url,
                    source=self.name,
                    description=_strip_html(summary)[:800],
                    salary_text=salary_text,
                    salary_min=parse_salary(salary_text),
                    location=LOCATION,
                ))
            time.sleep(0.5)

        return all_offers


def _find_company(html: str) -> str:
    m = re.search(r"<b>(.*?)</b>", html, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html).strip()


def _find_salary(text: str) -> str:
    m = re.search(r"(\d[\d\s]*(?:Kč|CZK|tis\.?\s*Kč|k\b)[^<\n]*)", text, re.IGNORECASE)
    return m.group(1).strip() if m else ""

"""Scraper pro Prace.cz — RSS feed načítaný přes requests."""
import re
import time
import requests
import feedparser
from .base import JobOffer, parse_salary, HEADERS
from config import LOCATION

RSS_URLS = [
    "https://www.prace.cz/rss/?q%5B%5D=marketing&locality%5Bradius%5D=0&locality%5Bcity%5D=Praha",
    "https://www.prace.cz/rss/?q[]=marketing&locality[city]=Praha",
]


class PraceCzScraper:
    name = "Prace.cz"

    def fetch(self) -> list[JobOffer]:
        for url in RSS_URLS:
            try:
                resp = requests.get(url, headers=HEADERS, timeout=15)
                resp.raise_for_status()
                feed = feedparser.parse(resp.content)
                if feed.entries:
                    return _parse_entries(feed.entries)
            except Exception as e:
                print(f"  Prace.cz URL {url[:50]}… chyba: {e}")
        return []


def _parse_entries(entries) -> list[JobOffer]:
    offers = []
    for entry in entries:
        title = entry.get("title", "")
        url = entry.get("link", "")
        summary = entry.get("summary", "") or entry.get("description", "")
        company = entry.get("author", "") or _extract_tag(summary, "strong")
        salary_text = _find_salary(summary)
        offers.append(JobOffer(
            title=title,
            company=company,
            url=url,
            source="Prace.cz",
            description=_strip_html(summary)[:800],
            salary_text=salary_text,
            salary_min=parse_salary(salary_text),
            location=LOCATION,
        ))
        time.sleep(0.1)
    return offers


def _extract_tag(html: str, tag: str) -> str:
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", html, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html).strip()


def _find_salary(text: str) -> str:
    m = re.search(r"(\d[\d\s]*(?:Kč|CZK|tis\.?\s*Kč|k\b)[^<\n]*)", text, re.IGNORECASE)
    return m.group(1).strip() if m else ""

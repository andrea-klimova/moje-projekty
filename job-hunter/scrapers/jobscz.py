"""Scraper pro Indeed.cz — RSS feed (náhrada za nefunkční Jobs.cz RSS)."""
import re
import time
import requests
import feedparser
from .base import JobOffer, parse_salary, HEADERS
from config import LOCATION

RSS_URL = "https://cz.indeed.com/rss?q=marketing&l=Praha&radius=25&sort=date"


class JobsCzScraper:
    name = "Indeed.cz"

    def fetch(self) -> list[JobOffer]:
        try:
            resp = requests.get(RSS_URL, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
        except Exception as e:
            print(f"  Indeed.cz chyba: {e}")
            return []

        offers = []
        for entry in feed.entries:
            title = entry.get("title", "")
            url = entry.get("link", "").split("?")[0]
            summary = entry.get("summary", "") or entry.get("description", "")
            company = entry.get("author", "") or _find_company(summary)
            salary_text = _find_salary(summary)

            offers.append(JobOffer(
                title=title,
                company=company,
                url=url,
                source=self.name,
                description=_strip_html(summary)[:800],
                salary_text=salary_text,
                salary_min=parse_salary(salary_text),
                location=LOCATION,
            ))
            time.sleep(0.1)
        return offers


def _find_company(html: str) -> str:
    m = re.search(r"<b>(.*?)</b>|company[\"']:\s*[\"'](.*?)[\"']", html, re.IGNORECASE)
    return (m.group(1) or m.group(2) or "").strip() if m else ""


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html).strip()


def _find_salary(text: str) -> str:
    m = re.search(r"(\d[\d\s]*(?:Kč|CZK|tis\.?\s*Kč|k\b)[^<\n]*)", text, re.IGNORECASE)
    return m.group(1).strip() if m else ""

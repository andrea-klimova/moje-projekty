"""Scraper pro Jobs.cz — používá RSS feed."""
import time
import feedparser
import requests
from .base import JobOffer, parse_salary, HEADERS
from config import LOCATION


RSS_URL = (
    "https://www.jobs.cz/rss/pozice/"
    "?q[]=marketing"
    "&locality[radius]=0"
    "&locality[city]=Praha"
)


class JobsCzScraper:
    name = "Jobs.cz"

    def fetch(self) -> list[JobOffer]:
        feed = feedparser.parse(RSS_URL)
        offers = []
        for entry in feed.entries:
            title = entry.get("title", "")
            url = entry.get("link", "")
            summary = entry.get("summary", "")
            company = entry.get("author", "") or _extract_company(summary)
            salary_text = _extract_salary_text(summary)

            offers.append(JobOffer(
                title=title,
                company=company,
                url=url,
                source=self.name,
                description=summary,
                salary_text=salary_text,
                salary_min=parse_salary(salary_text),
                location=LOCATION,
            ))
            time.sleep(0.1)
        return offers


def _extract_company(text: str) -> str:
    """Pokus o extrakci firmy z HTML summary."""
    import re
    m = re.search(r"<strong>(.*?)</strong>", text)
    return m.group(1) if m else ""


def _extract_salary_text(text: str) -> str:
    """Hledá zmínku o platu v textu nabídky."""
    import re
    m = re.search(r"(\d[\d\s]*(?:Kč|CZK|tis\.?\s*Kč|k\b)[^<\n]*)", text, re.IGNORECASE)
    return m.group(1).strip() if m else ""

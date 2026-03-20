from __future__ import annotations
import hashlib
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class JobOffer:
    title: str
    company: str
    url: str
    source: str
    description: str = ""
    salary_text: str = ""
    salary_min: Optional[int] = None
    location: str = "Praha"
    ai_score: int = 0
    ai_comment: str = ""

    @property
    def id(self) -> str:
        """Unique ID based on URL (or title+company fallback)."""
        key = self.url or f"{self.title}|{self.company}"
        return hashlib.md5(key.encode()).hexdigest()


def parse_salary(text: str) -> Optional[int]:
    """Extracts minimum salary (int Kč) from a free-text string."""
    if not text:
        return None
    text = text.lower().replace("\xa0", " ").replace(",", ".")

    # e.g. "45k" or "45 000 kč" or "od 45 000" or "45 000 – 70 000 kč"
    numbers = re.findall(r"\d[\d\s\.]*\d|\d+", text)
    values = []
    for n in numbers:
        clean = re.sub(r"[\s\.]", "", n)
        try:
            v = int(clean)
            # reject obviously wrong values (< 1 000 or > 500 000)
            if 1_000 <= v <= 500_000:
                values.append(v)
        except ValueError:
            pass

    # "45k" shorthand
    k_matches = re.findall(r"(\d+)\s*k\b", text)
    for m in k_matches:
        values.append(int(m) * 1_000)

    return min(values) if values else None


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
}

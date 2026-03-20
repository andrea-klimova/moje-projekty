"""AI hodnocení nabídek pomocí OpenRouter API."""
import os
from openai import OpenAI
from scrapers.base import JobOffer
from config import CV_TEXT, OPENROUTER_MODEL


class AIScorer:

    def __init__(self):
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    def score(self, offer: JobOffer) -> tuple[int, str]:
        """Vrátí (skóre 1–10, komentář) pro danou nabídku."""
        prompt = self._build_prompt(offer)
        response = self.client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3,
        )
        raw = response.choices[0].message.content.strip()
        return _parse_response(raw)

    def _build_prompt(self, offer: JobOffer) -> str:
        return f"""Jsi recruiter hodnotící shodu pracovní nabídky s profilem kandidátky.

## CV KANDIDÁTKY
{CV_TEXT}

## PARAMETRY HLEDÁNÍ
- Hledá: marketingová pozice v Praze, min. 45 000 Kč hrubého
- CHCE: strategie, analytika, B2B, tech/SaaS, SEM, PPC, brand, marketingová automatizace
- NECHCE: správu sociálních sítí, events, community manager, influencer marketing

## NABÍDKA
Pozice: {offer.title}
Firma: {offer.company}
Plat: {offer.salary_text or "neuvedeno"}
Popis: {offer.description[:800]}

## ÚKOL
Ohodnoť shodu nabídky s profilem na škále 1–10.
Odpověz PŘESNĚ v tomto formátu (nic jiného):
SKÓRE: [číslo 1-10]
KOMENTÁŘ: [1–2 věty proč se nabídka hodí nebo nehodí]
"""


def _parse_response(text: str) -> tuple[int, str]:
    score = 5
    comment = text

    for line in text.splitlines():
        line = line.strip()
        if line.upper().startswith("SKÓRE:") or line.upper().startswith("SCORE:"):
            try:
                score = int("".join(filter(str.isdigit, line.split(":", 1)[1])))
                score = max(1, min(10, score))
            except (ValueError, IndexError):
                pass
        elif line.upper().startswith("KOMENTÁŘ:") or line.upper().startswith("COMMENT:"):
            comment = line.split(":", 1)[1].strip()

    return score, comment

"""Filtrování nabídek podle klíčových slov a platu."""
from scrapers.base import JobOffer
from config import DONT_WANT_KEYWORDS, MIN_SALARY

# Stačí slabá vazba na marketing v celém textu
MARKETING_WORDS = [
    "market", "brand", "digital", "growth", "ppc", "sem", "seo",
    "campaign", "kampaň", "reklam", "content", "komunikac",
    "analytik", "analytic", "performance", "advertis", "promo",
]


class JobFilter:

    def filter(self, offers: list[JobOffer]) -> list[JobOffer]:
        results = []
        for offer in offers:
            reason = self._reject_reason(offer)
            if reason is None:
                results.append(offer)
        return results

    def _reject_reason(self, offer: JobOffer) -> str | None:
        # DONT_WANT kontrolujeme jen v NÁZVU pozice
        # (ne v celém popisu — jinak by vypadl každý marketing manager
        #  jehož popis jen zmiňuje sociální sítě jako jednu z mnoha věcí)
        title_lower = offer.title.lower()
        for kw in DONT_WANT_KEYWORDS:
            if kw.lower() in title_lower:
                return f"DONT_WANT v názvu: {kw}"

        # Filtr platu — pouze pokud je explicitně uveden a nižší než minimum
        if offer.salary_min is not None and offer.salary_min < MIN_SALARY:
            return f"PLAT: {offer.salary_min} < {MIN_SALARY}"

        # Musí mít alespoň slabou vazbu na marketing (název nebo popis)
        full_text = f"{offer.title} {offer.description}".lower()
        if not any(w in full_text for w in MARKETING_WORDS):
            return "NERELEVANTNÍ: žádné marketingové slovo"

        return None  # prošlo

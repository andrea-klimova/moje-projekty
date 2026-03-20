"""Filtrování nabídek podle klíčových slov a platu."""
from scrapers.base import JobOffer
from config import WANT_KEYWORDS, DONT_WANT_KEYWORDS, MIN_SALARY


class JobFilter:

    def filter(self, offers: list[JobOffer]) -> list[JobOffer]:
        results = []
        for offer in offers:
            if self._is_relevant(offer):
                results.append(offer)
        return results

    def _is_relevant(self, offer: JobOffer) -> bool:
        text = f"{offer.title} {offer.description} {offer.salary_text}".lower()

        # Vyřadit pokud obsahuje nežádoucí klíčová slova
        for kw in DONT_WANT_KEYWORDS:
            if kw.lower() in text:
                return False

        # Filtr platu — pouze pokud je plat uveden a je nižší než minimum
        if offer.salary_min is not None and offer.salary_min < MIN_SALARY:
            return False

        # Musí obsahovat alespoň 1 žádoucí klíčové slovo nebo "marketing" v názvu
        title_lower = offer.title.lower()
        if "marketing" in title_lower:
            return True

        return any(kw.lower() in text for kw in WANT_KEYWORDS)

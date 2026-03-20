"""Filtrování nabídek podle klíčových slov a platu."""
from scrapers.base import JobOffer
from config import DONT_WANT_KEYWORDS, MIN_SALARY


class JobFilter:

    def filter(self, offers: list[JobOffer]) -> list[JobOffer]:
        results = []
        for offer in offers:
            reason = self._reject_reason(offer)
            if reason is None:
                results.append(offer)
        return results

    def _reject_reason(self, offer: JobOffer) -> str | None:
        title_lower = offer.title.lower()

        # 1. Vyřadit pokud NÁZEV pozice obsahuje nežádoucí klíčová slova
        #    (kontrolujeme jen název — ne popis, aby se nevyhazovaly pozice
        #    které jen zmiňují sociální sítě jako jednu z mnoha věcí)
        for kw in DONT_WANT_KEYWORDS:
            if kw.lower() in title_lower:
                return f"DONT_WANT: {kw}"

        # 2. Filtr platu — jen pokud je explicitně uveden a nižší než minimum
        if offer.salary_min is not None and offer.salary_min < MIN_SALARY:
            return f"PLAT: {offer.salary_min} < {MIN_SALARY}"

        # 3. Přeskočit prázdné nabídky bez názvu
        if not offer.title or len(offer.title) < 4:
            return "PRÁZDNÝ název"

        return None  # prošlo

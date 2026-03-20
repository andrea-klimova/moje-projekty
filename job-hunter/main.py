"""Job Hunter — hlavní skript.

Spouštěj: python main.py
Vyžaduje env proměnné: OPENROUTER_API_KEY, GMAIL_ADDRESS, GMAIL_APP_PASSWORD
"""
import json
import sys
from pathlib import Path

from scrapers.jobscz import JobsCzScraper
from scrapers.pracecz import PraceCzScraper
from scrapers.startupjobs import StartupJobsScraper
from scrapers.jobstack import JobstackScraper
from scrapers.linkedin import LinkedInScraper
from scrapers.agencies import AgenciesScraper
from filter import JobFilter
from ai_scorer import AIScorer
from email_sender import EmailSender

HISTORY_FILE = Path(__file__).parent / "history.json"


def load_history() -> set[str]:
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_history(history: set[str]) -> None:
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(history), f, ensure_ascii=False, indent=2)


def main() -> None:
    print("=" * 50)
    print("  JOB HUNTER — spuštěn")
    print("=" * 50)

    history = load_history()
    print(f"Historie: {len(history)} dříve odeslaných nabídek\n")

    # --- Scraping ---
    scrapers = [
        JobsCzScraper(),
        PraceCzScraper(),
        StartupJobsScraper(),
        JobstackScraper(),
        LinkedInScraper(),
        AgenciesScraper(),
    ]

    all_offers = []
    for scraper in scrapers:
        print(f"[{scraper.name}] Stahuji nabídky…")
        try:
            offers = scraper.fetch()
            print(f"  → {len(offers)} nabídek nalezeno")
            all_offers.extend(offers)
        except Exception as e:
            print(f"  ✗ Chyba: {e}")

    print(f"\nCelkem nalezeno: {len(all_offers)} nabídek")

    # --- Filtrování ---
    job_filter = JobFilter()
    filtered = job_filter.filter(all_offers)
    print(f"Po filtrování:   {len(filtered)} nabídek")

    # --- Odstranění duplicit (již odeslané) ---
    new_offers = [o for o in filtered if o.id not in history]
    print(f"Nové nabídky:    {len(new_offers)}\n")

    if not new_offers:
        print("Žádné nové nabídky. E-mail nebude odeslán.")
        return

    # --- AI hodnocení ---
    print("AI hodnocení nabídek…")
    scorer = AIScorer()
    scored = []
    for offer in new_offers:
        try:
            score, comment = scorer.score(offer)
            offer.ai_score = score
            offer.ai_comment = comment
            scored.append(offer)
            print(f"  [{score:2d}/10] {offer.title[:50]} @ {offer.company}")
        except Exception as e:
            print(f"  ✗ Chyba AI pro '{offer.title}': {e}")
            offer.ai_score = 0
            offer.ai_comment = "Nepodařilo se ohodnotit."
            scored.append(offer)

    # Seřadit podle skóre (nejlepší první)
    scored.sort(key=lambda o: o.ai_score, reverse=True)

    # --- Odeslání e-mailu ---
    print("\nOdesílám e-mail…")
    try:
        sender = EmailSender()
        sender.send(scored)
        print(f"✓ E-mail odeslán ({len(scored)} nabídek)")
    except Exception as e:
        print(f"✗ Chyba při odesílání e-mailu: {e}")
        sys.exit(1)

    # --- Aktualizace historie ---
    for offer in scored:
        history.add(offer.id)
    save_history(history)
    print("✓ Historie aktualizována")
    print("=" * 50)


if __name__ == "__main__":
    main()

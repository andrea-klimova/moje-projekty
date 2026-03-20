"""Job Hunter — hlavní skript.

Spouštěj: python main.py
Vyžaduje env proměnné: OPENROUTER_API_KEY, GMAIL_ADDRESS, GMAIL_APP_PASSWORD
"""
import json
import sys
from datetime import date, datetime
from pathlib import Path

from scrapers.jobscz import JobsCzScraper
from scrapers.pracecz import PraceCzScraper
from scrapers.startupjobs import StartupJobsScraper
from scrapers.jobstack import JobstackScraper
from scrapers.linkedin import LinkedInScraper
from scrapers.agencies import AgenciesScraper
from scrapers.atmoskop import AtmoskopScraper
from filter import JobFilter
from ai_scorer import AIScorer
from email_sender import EmailSender
import config as cfg

ROOT = Path(__file__).parent
HISTORY_FILE = ROOT / "history.json"
WEB_DATA_DIR = ROOT.parent / "docs" / "job-hunter" / "data"
OFFERS_FILE = WEB_DATA_DIR / "offers.json"
CONFIG_JSON = WEB_DATA_DIR / "config.json"


def load_history() -> set[str]:
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_history(history: set[str]) -> None:
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(history), f, ensure_ascii=False, indent=2)


def save_web_data(new_offers: list) -> None:
    """Uloží nabídky do docs/job-hunter/data/offers.json pro webové rozhraní."""
    WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Načti existující nabídky
    existing = []
    if OFFERS_FILE.exists():
        with open(OFFERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            existing = data.get("offers", [])

    # Existující IDs pro deduplikaci
    existing_ids = {o["id"] for o in existing}

    # Přidej nové nabídky na začátek
    today = date.today().isoformat()
    new_records = []
    for o in new_offers:
        if o.id not in existing_ids:
            new_records.append({
                "id": o.id,
                "title": o.title,
                "company": o.company,
                "url": o.url,
                "source": o.source,
                "salary_text": o.salary_text,
                "salary_min": o.salary_min,
                "ai_score": o.ai_score,
                "ai_comment": o.ai_comment,
                "description": o.description[:500],
                "location": o.location,
                "date_found": today,
            })

    all_offers = new_records + existing

    with open(OFFERS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "updated": datetime.now().isoformat(timespec="seconds"),
            "total": len(all_offers),
            "offers": all_offers,
        }, f, ensure_ascii=False, indent=2)

    # Ulož config.json pro webové rozhraní
    with open(CONFIG_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "want_keywords": cfg.WANT_KEYWORDS,
            "dont_want_keywords": cfg.DONT_WANT_KEYWORDS,
            "min_salary": cfg.MIN_SALARY,
            "portals": [s.name for s in [
                JobsCzScraper(), PraceCzScraper(), StartupJobsScraper(),
                JobstackScraper(), AtmoskopScraper(), LinkedInScraper(),
            ]],
            "cv_text": cfg.CV_TEXT,
            "openrouter_model": cfg.OPENROUTER_MODEL,
        }, f, ensure_ascii=False, indent=2)

    print(f"✓ Web data uložena ({len(new_records)} nových, {len(all_offers)} celkem)")


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
        AtmoskopScraper(),
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
        # I tak ulož config.json pro web
        save_web_data([])
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

    scored.sort(key=lambda o: o.ai_score, reverse=True)

    # --- Uložení dat pro webové rozhraní ---
    save_web_data(scored)

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

# MANUAL — Job Hunter

## 1. Co to je

Automatická aplikace, která každý den prohledá české pracovní portály, AI ohodnotí každou nabídku podle tvého CV a preferencí, a pošle přehledný HTML e-mail s nejlepšími pozicemi.

---

## 2. K čemu slouží

- **Šetří čas** — nemusíš každý den ručně procházet 6+ portálů
- **Filtruje irelevantní nabídky** — automaticky vyřazuje obchodní pozice, sociální sítě, nízké mzdy
- **AI hodnocení** — každá nabídka dostane skóre 1–10 podle shody s tvým CV a preferencemi
- **Bez duplicit** — aplikace si pamatuje co už ti poslala, neposílá znovu
- **Webové rozhraní** — na GitHub Pages vidíš historii nabídek a můžeš je označovat stavy

---

## 3. Jak byla vytvořena

| Co | Nástroj |
|---|---|
| Kód | Python 3 |
| Scraping | requests, BeautifulSoup4, feedparser |
| AI hodnocení | OpenRouter API (model: openai/gpt-4o-mini) |
| E-mail | Gmail SMTP (port 465, SSL) |
| Automatizace | GitHub Actions (každý den v 7:00 UTC) |
| Web | GitHub Pages (vanilla JS + CSS) |
| Data | history.json, docs/job-hunter/data/offers.json |

**Scraped portály:**
- Jobs.cz — HTML scraping
- Práce.cz — HTML scraping
- StartupJobs.cz — Next.js `__NEXT_DATA__` extrakce
- Profesia.cz — HTML scraping (4 kategorie)
- Atmoskop.cz — HTML scraping
- Indeed.cz — HTML scraping
- 10 kariérních stránek firem (McCann, Ogilvy, BBDO, Mindshare, PHD, Prazdroj, dm, O2, Alza, Mondelez)

---

## 4. Jak to funguje

```
GitHub Actions (7:00 každý den)
    ↓
main.py spustí scrapers/
    ↓
Každý scraper stáhne nabídky z portálu (requests + BeautifulSoup)
    ↓
filter.py: vyřadí DONT_WANT_KEYWORDS v názvu, mzda < 45 000 Kč
    ↓
ai_scorer.py: pošle nabídky na OpenRouter → skóre 1–10 + komentář
    ↓
email_sender.py: sestaví HTML e-mail (zelené/oranžové/červené badges)
    ↓
Odešle na Gmail
    ↓
Uloží hash URL do history.json (příště přeskočí)
    ↓
Uloží offers.json do docs/ → GitHub Pages web
```

---

## 5. Jak ji používat

### E-mail
- Každé ráno dorazí e-mail s novými nabídkami
- Skóre 8–10 = zelené (výborná shoda)
- Skóre 5–7 = oranžové (průměrná shoda)
- Skóre 1–4 = červené (slabá shoda)
- Každá nabídka má odkaz přímo na portál

### Webové rozhraní
Otevři: `https://andrea-klimova.github.io/moje-projekty/job-hunter/`

**Záložky:**
- **Nabídky** — všechny nabídky z posledního běhu, filtrovatelné
- **Nastavení** — úprava klíčových slov, minimální mzdy, portálů
- **AI Prompt** — editace promptu pro hodnocení nabídek
- **Průvodní dopis** — generátor průvodního dopisu pro konkrétní nabídku

**Označování stavů** (ukládá se v prohlížeči):
- 🟢 Mám zájem
- ❌ Nerelevantní
- 📤 Přihlásila jsem se
- ⏳ Čekám na odpověď

### Ruční spuštění
1. Jdi na `github.com/andrea-klimova/moje-projekty`
2. Záložka **Actions** → **Job Hunter**
3. **Run workflow** → **Run workflow**

---

## 6. Jak upravit nastavení

### Klíčová slova a mzda (doporučeno přes web)
1. Otevři webové rozhraní → záložka **Nastavení**
2. Uprav klíčová slova nebo minimální mzdu
3. Změny se uloží do localStorage prohlížeče

### Klíčová slova a mzda (přes kód)
Soubor: `job-hunter/config.py`

```python
MIN_SALARY = 45_000          # minimální mzda v Kč
DONT_WANT_KEYWORDS = [...]   # co filtrovat z názvů nabídek
WANT_KEYWORDS = [...]        # preferovaná klíčová slova
```

Po změně: uložit a "Nahraj vše na GitHub" v Claude Code.

### Firmy na kariérních stránkách
Soubor: `job-hunter/config.py` → seznam `AGENCIES`
- Přidej/odeber firmy — každá má `name`, `url`, `keyword`

### AI prompt
Soubor: `job-hunter/PROMPT.md`
Nebo přes webové rozhraní → záložka **AI Prompt**

### Frekvence spouštění
Soubor: `.github/workflows/job-hunter.yml`
```yaml
- cron: '0 7 * * *'   # každý den v 7:00 UTC (= 8:00/9:00 CZ)
```

### GitHub Secrets (API klíče)
`github.com/andrea-klimova/moje-projekty` → Settings → Secrets and variables → Actions
- `OPENROUTER_API_KEY` — klíč z openrouter.ai
- `GMAIL_ADDRESS` — tvůj Gmail
- `GMAIL_APP_PASSWORD` — App Password z myaccount.google.com/apppasswords

# MANUAL — Blog Čtečka

## 1. Co to je

Automatická aplikace, která každé pondělí ráno přečte 25 odborných technologických blogů, nechá AI vygenerovat česká shrnutí a náměty na články, a pošle přehledný e-mail.

---

## 2. K čemu slouží

- **Přehled tech novinek** — každý týden shrnutí z 25 blogů v 5 kategoriích
- **Česky** — AI přeloží a shrne i anglické články
- **Náměty na vlastní obsah** — AI navrhuje témata na základě přečtených článků
- **Šetří čas** — místo ručního čtení desítek zdrojů dostaneš jeden e-mail
- **Přizpůsobitelné** — lze vypnout/zapnout jednotlivé blogy, upravit prompt

---

## 3. Jak byla vytvořena

| Co | Nástroj |
|---|---|
| Kód | Python 3 |
| Čtení blogů | feedparser (RSS), requests |
| AI shrnutí | Groq API (model: llama-3.1-8b-instant) |
| E-mail | Gmail SMTP (port 465, SSL) |
| Automatizace | GitHub Actions (každé pondělí v 7:00 UTC) |
| Konfigurace | config.json (seznam blogů), ai-prompt.txt |
| Historie | history.json, last-email.html |

**Sledované kategorie:**
- 🔧 DevOps & CI/CD (Red Hat, GitLab, DZone, DevOps.com, Harness)
- ☁️ Cloud & Kubernetes (Kubernetes, CNCF, The New Stack, HashiCorp, AWS, Google Cloud, Azure)
- 🐧 Linux & Open Source (LWN.net, Linux Foundation, Opensource.com, SUSE, Fedora, It's FOSS)
- 💰 FinOps & Cloud Cost (FinOps Foundation, CloudZero, Infracost, Spot.io)
- 🔒 Security & DevSecOps (Aqua Security, Sysdig, Snyk)

---

## 4. Jak to funguje

```
GitHub Actions (každé pondělí v 7:00 UTC)
    ↓
main.py načte config.json (seznam povolených blogů)
    ↓
feedparser stáhne RSS feedy všech blogů
    ↓
Filtruje články starší než 7 dní
    ↓
Vybere max. 20 nejnovějších článků celkem
    ↓
Pošle do Groq API → česká shrnutí + náměty na články
    ↓
Sestaví HTML e-mail s barevným layoutem
    ↓
Odešle na Gmail
    ↓
Uloží history.json + last-email.html (náhled)
```

---

## 5. Jak ji používat

### E-mail
- Každé pondělí ráno dorazí e-mail s přehledem
- Obsah: shrnutí nejzajímavějších článků + náměty na vlastní blog
- Struktura: sekce podle kategorií (DevOps, Cloud, Linux, FinOps, Security)

### Ruční spuštění
1. Jdi na `github.com/andrea-klimova/moje-projekty`
2. Záložka **Actions** → **Blog Čtečka**
3. **Run workflow** → **Run workflow**

### Náhled posledního e-mailu
Soubor `blog-citecka/last-email.html` v repozitáři — otevři v prohlížeči.

---

## 6. Jak upravit nastavení

### Zapnout/vypnout blogy
Soubor: `blog-citecka/config.json`
```json
{
  "feeds": {
    "🔧 DevOps & CI/CD": [
      { "name": "Red Hat Blog", "url": "...", "enabled": true },
      { "name": "GitLab Blog",  "url": "...", "enabled": false }
    ]
  }
}
```
Změň `"enabled": false` pro blogy, které nechceš.

### Počet zpracovávaných článků
Soubor: `blog-citecka/config.json`
```json
{
  "max_articles": 20,
  "days_back": 7
}
```
- `max_articles` — kolik článků se pošle do AI (více = vyšší náklady)
- `days_back` — jak staré články zahrnout (default: 7 dní)

### AI prompt (co má AI shrnout)
Soubor: `blog-citecka/ai-prompt.txt`
Uprav instrukce pro AI — co má zdůraznit, jak formátovat výstup, kolik námětů navrhnout.

### Frekvence spouštění
Soubor: `.github/workflows/blog-citecka.yml`
```yaml
- cron: '0 7 * * 1'   # každé pondělí v 7:00 UTC
```
Změň `* * 1` na jiný den (1=Po, 2=Út, ... 5=Pá).

### Přidat nový blog
Soubor: `blog-citecka/config.json` — přidej nový objekt do příslušné kategorie:
```json
{ "name": "Nový Blog", "url": "https://novyblog.com/feed/", "enabled": true }
```

### GitHub Secrets (API klíče)
`github.com/andrea-klimova/moje-projekty` → Settings → Secrets and variables → Actions
- `GROQ_API_KEY` — klíč z console.groq.com
- `GMAIL_ADDRESS` — tvůj Gmail
- `GMAIL_APP_PASSWORD` — App Password z myaccount.google.com/apppasswords

# Plán: Automatická čtečka blogů

**Datum vzniku:** březen 2026  
**Stav:** 🟡 Fáze 1 — příprava účtů  

---

## Co to je

Webová aplikace, která každé pondělí ráno automaticky přečte vybrané odborné blogy,
nechá Claude vygenerovat česká shrnutí a náměty na články, a pošle přehledný e-mail.
K tomu jednoduchá webová stránka s historií a nastavením.

---

## Moje požadavky

- **Výstup:** e-mail + webová stránka s historií
- **Jazyk:** česky (shrnutí i náměty přeložené)
- **Kdy:** každé pondělí ráno
- **Počet položek:** vše relevantní (bez limitu)
- **Obsah e-mailu:** shrnutí nejzajímavějších článků + náměty na blog články
- **Editace:** možnost upravit zadání, blogy, prompt přímo ve webovém rozhraní
- **Náhled:** vidět e-mail před odesláním

---

## Sledované kategorie a blogy

### 🔧 DevOps & CI/CD
- Red Hat Blog
- GitLab Blog
- DZone DevOps
- DevOps.com
- Harness Blog

### ☁️ Cloud & Kubernetes
- Kubernetes Blog
- CNCF Blog
- The New Stack
- HashiCorp Blog
- AWS Open Source Blog
- Google Cloud Blog
- Microsoft Azure Blog

### 🐧 Linux & Open Source
- LWN.net
- Linux Foundation Blog
- Opensource.com
- SUSE Blog
- Fedora Magazine
- It's FOSS News

### 💰 FinOps & Cloud Cost
- FinOps Foundation Blog
- CloudZero Blog
- Infracost Blog
- Spot.io Blog

### 🔒 Security & DevSecOps
- Aqua Security Blog
- Sysdig Blog
- Snyk Blog

---

## Technický stack (vše zdarma)

| Co | Nástroj |
|---|---|
| Kód | Python |
| Hosting + automatizace | GitHub Actions (každé pondělí 7:00) |
| Webová stránka | GitHub Pages |
| E-mail | Gmail SMTP |
| AI | Anthropic API (Claude) |
| Data / historie | JSON soubor na GitHubu |

---

## Fáze projektu

### Fáze 1 — Příprava účtů a prostředí ⬅️ JSME TADY
- [ ] Založit GitHub účet
- [ ] Získat Anthropic API klíč z console.anthropic.com
- [ ] Nastavit Gmail App Password pro odesílání e-mailů
- [ ] Nainstalovat Claude Code na Windows

### Fáze 2 — Jádro aplikace
- [ ] RSS čtečka — stahuje články z 25 blogů
- [ ] AI modul — česká shrnutí a náměty přes Claude API
- [ ] E-mail modul — HTML e-mail odeslaný přes Gmail

### Fáze 3 — Automatizace
- [ ] GitHub Actions workflow — spuštění každé pondělí v 7:00
- [ ] Ukládání výsledků do JSON (historie)

### Fáze 4 — Webová stránka
- [ ] Historie odeslaných e-mailů
- [ ] Nastavení: které blogy sledovat, kdy posílat
- [ ] Editace AI promptu přímo ve webovém rozhraní
- [ ] Úprava počtu námětů a formátu
- [ ] Náhled e-mailu před odesláním

---

## Změny a rozhodnutí

| Datum | Co se změnilo | Proč |
|---|---|---|
| březen 2026 | Vznik projektu | — |

---

## Poznámky

- Claude Pro plán nestačí pro API — je potřeba zvlášť API klíč z console.anthropic.com
- API klíč NIKDY nedávat do kódu — uložit jako GitHub Secret
- Gmail App Password ≠ heslo do Gmailu — je to speciální heslo jen pro aplikace

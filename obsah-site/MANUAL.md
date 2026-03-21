# MANUAL — Obsah Site

## 1. Co to je

Složka šablon a plánů pro tvorbu obsahu na různé kanály — blog, Instagram, LinkedIn, Facebook, newsletter a X (Twitter).

---

## 2. K čemu slouží

- **Centrální místo pro content plánování** — vše na jednom místě
- **Šablony pro každý kanál** — každý kanál má vlastní složku s PLAN.md
- **Konzistentní hlas značky** — jednotné zadání pro AI generování obsahu
- **Rychlá tvorba** — místo přemýšlení od nuly máš připravené šablony

---

## 3. Jak byla vytvořena

| Co | Nástroj |
|---|---|
| Struktura | Složky pro každý kanál |
| Formát | Markdown (.md soubory) |
| Verzování | GitHub |

**Kanály:**
- `blog/` — blog články
- `instagram/` — Instagram posty
- `linkedin/` — LinkedIn příspěvky
- `facebook/` — Facebook příspěvky
- `newsletter/` — e-mailový newsletter
- `x-twitter/` — tweety / X příspěvky

---

## 4. Jak to funguje

```
Každá složka = jeden kanál
    ↓
PLAN.md v každé složce = šablona a pokyny pro daný kanál
    ↓
Otevřeš příslušný PLAN.md
    ↓
Zadáš do Claude: "Přečti PLAN.md a vytvoř obsah pro [téma]"
    ↓
Claude vygeneruje obsah podle šablony kanálu
```

---

## 5. Jak ji používat

### Tvorba obsahu pro konkrétní kanál
1. Otevři Claude Code ve složce `moje-projekty Claude`
2. Řekni: *"Přečti obsah-site/blog/PLAN.md a napiš článek o [téma]"*
3. Nebo pro Instagram: *"Přečti obsah-site/instagram/PLAN.md a vytvoř post o [téma]"*

### Hromadná tvorba obsahu
Řekni Claude: *"Přečti všechny PLAN.md v obsah-site a vytvoř měsíční content plán pro [téma/produkt]"*

### Uložení výstupu
Hotový obsah ulož do příslušné složky jako nový soubor, např.:
- `blog/2026-03-clanek-o-marketingu.md`
- `instagram/2026-03-posts.md`

---

## 6. Jak upravit nastavení

### Úprava šablony kanálu
Otevři `obsah-site/[kanál]/PLAN.md` a uprav:
- Tón a styl psaní
- Délku příspěvků
- Strukturu obsahu
- Cílovou skupinu
- Hashtagy (Instagram)
- Frekvenci publikování

### Přidání nového kanálu
1. Vytvoř novou složku: `obsah-site/[novy-kanal]/`
2. Vytvoř `PLAN.md` s popisem kanálu a pokyny
3. Nahraj na GitHub: *"Nahraj vše na GitHub"* v Claude Code

### Propojení s AI automatizací
Pokud chceš obsah generovat automaticky (např. každý týden), řekni Claude Code:
*"Vytvoř GitHub Actions workflow který každý [den] vygeneruje obsah pro [kanál] a pošle mi ho e-mailem"*

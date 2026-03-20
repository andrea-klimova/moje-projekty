## Workflow: Jak vytvořit nový projekt v Claude Code

### Fáze 0 — Než začneš
1. Otevři tento chat (Claude.ai) a promysli projekt
2. Polož si otázky: Co to má dělat? Pro koho? Jak často? Jaký výstup?
3. Nech si Claude položit upřesňující otázky — jedna po jedné
4. Řekni "dost" až máš vše promyšleno
5. Nech napsat PLAN.md — zkontroluj, dej OK

### Fáze 1 — Příprava složky a souborů
1. Otevři Claude Code a vyber složku C:\moje-projekty Claude
2. Řekni Claude Code: "Vytvoř složku [název-projektu] s PLAN.md, PROMPT.md a POZNAMKY.md"
3. Do PLAN.md se automaticky zapíše vše z plánu
4. Nahraj na GitHub: "Nahraj vše na GitHub"

### Fáze 2 — Příprava účtů a secrets
Zkontroluj co potřebuješ a co už máš:
- GitHub účet — github.com
- OpenRouter API klíč — openrouter.ai → GitHub Secrets: OPENROUTER_API_KEY
- Gmail App Password — myaccount.google.com/apppasswords → GitHub Secrets: GMAIL_APP_PASSWORD
- Gmail adresa → GitHub Secrets: GMAIL_ADDRESS
- Anthropic API klíč — console.anthropic.com → GitHub Secrets: příslušný název

Secrets přidáš na: github.com/andrea-klimova/[repozitář] → Settings → Secrets and variables → Actions

### Fáze 3 — Napsání aplikace
Řekni Claude Code v jednom příkazu vše co aplikace má dělat:

"Přečti PLAN.md. Pak vytvoř Python aplikaci která:
1. [co stahuje / čte / zpracovává]
2. [co dělá s daty — AI, filtrování, třídění]
3. [jak posílá výstup — e-mail, web, soubor]
4. [jak často se spouští — každý den / týden]
Použij GitHub Secrets: OPENROUTER_API_KEY, GMAIL_ADDRESS, GMAIL_APP_PASSWORD.
Vytvoř GitHub Actions workflow. Nahraj vše na GitHub."

### Fáze 4 — Testování
1. Jdi na GitHub → Actions
2. Najdi svůj workflow → klikni "Run workflow"
3. Počkej na výsledek — zelené nebo červené
4. Pokud chyba → pošli screenshot chyby do Claude Code: "Aplikace hlásí tuto chybu, oprav ji a nahraj na GitHub"
5. Opakuj dokud není zelené

### Fáze 5 — Webové rozhraní
Řekni Claude Code:

"Přečti PLAN.md. Vytvoř webové rozhraní na GitHub Pages které zobrazuje:
1. [co má zobrazovat — historii, statistiky...]
2. [co lze upravovat — nastavení, prompt...]
3. [co lze dělat — označovat, filtrovat, generovat...]
Stránka má být v češtině, přehledná, moderní. Nahraj na GitHub a nastav GitHub Pages."

### Fáze 6 — Průběžná údržba
- Chceš změnit chování aplikace → Řekni Claude Code co změnit
- Chceš změnit nastavení → Uprav přes webové rozhraní
- Aplikace přestala fungovat → GitHub → Actions → chyba → pošli do Claude Code
- Chceš přidat novou funkci → "Přidej do aplikace funkci XY, přečti nejdřív PLAN.md"
- Chceš aktualizovat PLAN.md → "Aktualizuj PLAN.md — přidej/změň XY"

### Zlatá pravidla
- Nikdy neupravuj kód ručně — vždy přes Claude Code
- Vždy začni příkazem: "Přečti PLAN.md" — Claude Code bude mít kontext
- Secrets nikdy do kódu — vždy do GitHub Secrets
- Po každé změně — Claude Code nahraje na GitHub automaticky
- Když něco nefunguje — pošli screenshot chyby, nehádej

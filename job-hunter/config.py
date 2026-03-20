CV_TEXT = """
Andrea Klímová — Marketing Specialist

Aktuální pozice: Marketing Specialist — ELOS Technologies s.r.o. (10/2022 – nyní, Praha)
- Správa firemního webu (struktura, články, případové studie, reference)
- Copywriting: blogy, odborné články, newslettery
- Grafika: Canva, Figma, Adobe
- Analytika: reporting, návštěvnost, dosah, výkon kampaní (Google Analytics 4)
- Spolupráce s vývojáři a designéry při rozvoji webu
- HubSpot, základní SEO a PPC, plánování kampaní

Předchozí zkušenosti:
- Back Office Manager — ELOS Technologies s.r.o. (12/2017–9/2022) — fakturace, administrativa, cestovní příkazy, smluvní dokumentace
- Event Manager — Globe Bookstore and Cafe (5/2014–7/2017) — vedení týmu, finanční agenda, organizace akcí

Dovednosti:
- Marketing: HubSpot, základní SEO a PPC, Google Analytics 4, copywriting, plánování kampaní, newslettery
- Technické: MS Excel, Canva, Figma, Adobe, Confluence, ChatGPT

Vzdělání: SOŠ Frýdek-Místek, Maturita (Podnikání)
Jazyky: Čeština (rodilá mluvčí), Angličtina B2 (aktivní)
Kurzy: Letní akademie digitálního marketingu, Canva & Figma, LinkedIn pro personal branding, Copywriting & PR
""".strip()

# Klíčová slova která chceme
WANT_KEYWORDS = [
    "strategie", "analytika", "analýza", "b2b", "tech", "saas",
    "sem", "ppc", "google ads", "brand", "automatizace", "automation",
    "hubspot", "marketing automation", "growth", "performance",
    "data", "reporting", "kampaně", "campaigns", "digital marketing",
    "performance marketing", "brand manager", "marketing manager",
    "marketing specialist", "marketing analytik", "growth marketing",
]

# Klíčová slova která nechceme
DONT_WANT_KEYWORDS = [
    "community manager", "community manažer",
    "influencer", "influencer marketing",
    "event manager", "eventový marketing", "events manager",
    "správa sociálních sítí", "social media manager",
    "tiktok", "instagram manažer", "facebook manažer",
]

# Minimální mzda v Kč
MIN_SALARY = 45_000

# Hledané fráze na portálech
SEARCH_QUERIES = ["marketing", "marketing manager", "performance marketing", "PPC"]
LOCATION = "Praha"

# 10 doporučených firem/agentur v Praze — sledujeme jejich kariérní stránky
AGENCIES = [
    # --- Marketingové agentury ---
    {
        "name": "McCann Prague",
        "url": "https://mccann.cz/kariera/",
        "keyword": "marketing",
    },
    {
        "name": "Ogilvy Prague",
        "url": "https://www.ogilvy.cz/prace/",
        "keyword": "marketing",
    },
    {
        "name": "BBDO Prague",
        "url": "https://www.bbdo.cz/kariera/",
        "keyword": "marketing",
    },
    {
        "name": "Mindshare Czech",
        "url": "https://www.groupm.com/office/prague/",
        "keyword": "marketing",
    },
    {
        "name": "PHD Media",
        "url": "https://www.phdmedia.com/czech-republic/",
        "keyword": "marketing",
    },
    # --- Firmy se silným marketingem (ne IT) ---
    {
        "name": "Plzeňský Prazdroj",
        "url": "https://www.prazdroj.cz/kariera",
        "keyword": "marketing",
    },
    {
        "name": "dm drogerie markt CZ",
        "url": "https://www.dm.cz/kariera/",
        "keyword": "marketing",
    },
    {
        "name": "O2 Czech Republic",
        "url": "https://jobs.o2.cz/",
        "keyword": "marketing",
    },
    {
        "name": "Alza.cz",
        "url": "https://www.alza.cz/kariera/",
        "keyword": "marketing",
    },
    {
        "name": "Mondelez Czech Republic",
        "url": "https://www.mondelezinternational.com/careers",
        "keyword": "marketing",
    },
]

# OpenRouter model
OPENROUTER_MODEL = "openai/gpt-4o-mini"

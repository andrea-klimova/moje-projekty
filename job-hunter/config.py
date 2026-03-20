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
    {
        "name": "Productboard",
        "url": "https://www.productboard.com/careers/",
        "keyword": "marketing",
    },
    {
        "name": "Kiwi.com",
        "url": "https://jobs.kiwi.com/",
        "keyword": "marketing",
    },
    {
        "name": "Rohlik Group",
        "url": "https://www.rohlik.group/cs/kariera",
        "keyword": "marketing",
    },
    {
        "name": "Kentico (Xperience)",
        "url": "https://www.kentico.com/company/careers",
        "keyword": "marketing",
    },
    {
        "name": "STRV",
        "url": "https://www.strv.com/careers",
        "keyword": "marketing",
    },
    {
        "name": "Gen Digital (Avast)",
        "url": "https://careers.gendigital.com/",
        "keyword": "marketing",
    },
    {
        "name": "Livesport",
        "url": "https://www.livesport.eu/kariera/",
        "keyword": "marketing",
    },
    {
        "name": "Rossum",
        "url": "https://rossum.ai/careers/",
        "keyword": "marketing",
    },
    {
        "name": "Notino",
        "url": "https://www.notino.cz/kariera/",
        "keyword": "marketing",
    },
    {
        "name": "Mall.cz / Allegro",
        "url": "https://kariera.mall.cz/",
        "keyword": "marketing",
    },
]

# OpenRouter model
OPENROUTER_MODEL = "openai/gpt-4o-mini"

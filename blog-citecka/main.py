#!/usr/bin/env python3
"""
Blog čtečka — automatické české shrnutí blogů přes OpenRouter API + Gmail
Spouští se každé pondělí v 7:00 přes GitHub Actions
"""

import os
import json
import re
import smtplib
import time
import requests
import feedparser
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# ── RSS feedy ────────────────────────────────────────────────────────────────

FEEDS = {
    "🔧 DevOps & CI/CD": [
        ("Red Hat Blog",  "https://www.redhat.com/en/rss/blog"),
        ("GitLab Blog",   "https://about.gitlab.com/blog/feed.xml"),
        ("DZone DevOps",  "https://feeds.dzone.com/devops"),
        ("DevOps.com",    "https://devops.com/feed/"),
        ("Harness Blog",  "https://www.harness.io/blog/rss.xml"),
    ],
    "☁️ Cloud & Kubernetes": [
        ("Kubernetes Blog",      "https://kubernetes.io/feed.xml"),
        ("CNCF Blog",            "https://www.cncf.io/feed/"),
        ("The New Stack",        "https://thenewstack.io/feed/"),
        ("HashiCorp Blog",       "https://www.hashicorp.com/blog/feed.xml"),
        ("AWS Open Source Blog", "https://aws.amazon.com/blogs/opensource/feed/"),
        ("Google Cloud Blog",    "https://cloud.google.com/blog/rss"),
        ("Microsoft Azure Blog", "https://azure.microsoft.com/en-us/blog/feed/"),
    ],
    "🐧 Linux & Open Source": [
        ("LWN.net",               "https://lwn.net/headlines/rss"),
        ("Linux Foundation Blog", "https://www.linuxfoundation.org/blog/feed/"),
        ("Opensource.com",        "https://opensource.com/feed"),
        ("SUSE Blog",             "https://www.suse.com/c/feed/"),
        ("Fedora Magazine",       "https://fedoramagazine.org/feed/"),
        ("It's FOSS News",        "https://news.itsfoss.com/feed/"),
    ],
    "💰 FinOps & Cloud Cost": [
        ("FinOps Foundation Blog", "https://www.finops.org/blog/feed/"),
        ("CloudZero Blog",         "https://www.cloudzero.com/blog/rss.xml"),
        ("Infracost Blog",         "https://www.infracost.io/blog/rss.xml"),
        ("Spot.io Blog",           "https://spot.io/blog/feed/"),
    ],
    "🔒 Security & DevSecOps": [
        ("Aqua Security Blog", "https://blog.aquasec.com/rss.xml"),
        ("Sysdig Blog",        "https://sysdig.com/blog/feed/"),
        ("Snyk Blog",          "https://snyk.io/blog/feed/"),
    ],
}

DAYS_BACK = 7  # stahuj články z posledních N dní


# ── RSS čtečka ───────────────────────────────────────────────────────────────

def fetch_articles(days_back: int = DAYS_BACK) -> dict:
    """Stáhne RSS feedy a vrátí články za posledních N dní."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    result = {}

    for category, feeds in FEEDS.items():
        articles = []
        for name, url in feeds:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    published = entry.get("published_parsed") or entry.get("updated_parsed")
                    if published:
                        pub_dt = datetime(*published[:6], tzinfo=timezone.utc)
                        if pub_dt < cutoff:
                            continue
                    title   = entry.get("title", "Bez názvu").strip()
                    link    = entry.get("link", "")
                    summary = entry.get("summary", entry.get("description", ""))
                    # Odstraň HTML tagy ze summary
                    summary = re.sub(r"<[^>]+>", "", summary)[:400].strip()
                    articles.append({
                        "source":  name,
                        "title":   title,
                        "link":    link,
                        "summary": summary,
                    })
            except Exception as e:
                print(f"  ⚠️  Chyba při načítání {name}: {e}")

        if articles:
            result[category] = articles
        print(f"  {category}: {len(articles)} článků")

    return result


# ── OpenRouter API ───────────────────────────────────────────────────────────

MAX_ARTICLES = 20  # maximální počet článků odeslaných do AI

OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL    = "meta-llama/llama-3.1-8b-instruct:free"


def summarize_with_openrouter(articles_by_category: dict) -> str:
    """Pošle články do OpenRouter API a vrátí česká shrnutí + náměty."""

    # Vyber maximálně MAX_ARTICLES nejnovějších článků celkem (RSS feedy jsou seřazeny od nejnovějších)
    all_articles = [
        (category, article)
        for category, articles in articles_by_category.items()
        for article in articles
    ]
    all_articles = all_articles[:MAX_ARTICLES]

    # Znovu seskup do kategorií pro přehledný prompt
    limited_by_category: dict = {}
    for category, article in all_articles:
        limited_by_category.setdefault(category, []).append(article)

    print(f"   Odesílám do OpenRouter: {len(all_articles)} článků (limit {MAX_ARTICLES})")

    articles_text = ""
    for category, articles in limited_by_category.items():
        articles_text += f"\n\n### {category}\n"
        for a in articles:
            articles_text += f"- [{a['source']}] {a['title']}\n  {a['summary'][:300]}\n"

    prompt = f"""Jsi expert na DevOps, cloud, Linux, FinOps a bezpečnost. \
Analyzuj tyto články z odborných blogů z tohoto týdne a odpověz VÝHRADNĚ ČESKY.

ČLÁNKY:
{articles_text}

Tvůj výstup musí mít přesně tuto strukturu:

## 📰 Nejzajímavější články tohoto týdne

Pro každou kategorii vyber 2–4 nejzajímavější články. U každého uveď:
- **Název článku** — zdroj v závorce
- 2–3 věty shrnutí česky: co je hlavní poselství a proč je to důležité
- Jedna věta: co z toho může prakticky využít DevOps inženýr nebo tech blogger

## 💡 Náměty na blog články (10 námětů)

Na základě trendů z těchto článků navrhni 10 námětů na vlastní blog články v češtině.
Formát každého námětu:
**[číslo]. [Konkrétní název článku]**
Proč je to aktuální: [jedna věta]
Klíčové body: [3 stručné body]

Piš srozumitelně a prakticky. Vyhni se obecnostem.
"""

    time.sleep(3)  # pauza před požadavkem — ochrana před překročením API limitu

    response = requests.post(
        OPENROUTER_ENDPOINT,
        headers={
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
            "Content-Type":  "application/json",
        },
        json={
            "model":    OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    response.raise_for_status()

    time.sleep(2)  # pauza po požadavku — ochrana před překročením API limitu

    return response.json()["choices"][0]["message"]["content"]


# ── HTML e-mail ──────────────────────────────────────────────────────────────

def markdown_to_html(text: str) -> str:
    """Jednoduchý převod markdown → HTML pro e-mail."""
    # Nadpisy
    text = re.sub(r"^## (.+)$",  r"<h2>\1</h2>", text, flags=re.MULTILINE)
    text = re.sub(r"^### (.+)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)
    # Tučné
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Odrážky
    lines = text.split("\n")
    html_lines = []
    in_ul = False
    for line in lines:
        if line.startswith("- "):
            if not in_ul:
                html_lines.append("<ul>")
                in_ul = True
            html_lines.append(f"  <li>{line[2:]}</li>")
        else:
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            html_lines.append(line)
    if in_ul:
        html_lines.append("</ul>")
    text = "\n".join(html_lines)
    # Odstavce (prázdné řádky)
    text = re.sub(r"\n{2,}", "</p><p>", text)
    return f"<p>{text}</p>"


def build_html_email(ai_content: str, article_count: int, week: str) -> str:
    """Sestaví HTML e-mail."""
    body = markdown_to_html(ai_content)

    return f"""<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 700px; margin: 0 auto; background: #f4f6f9; color: #1a1a1a;
  }}
  .header {{
    background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
    color: white; padding: 32px 40px; border-radius: 12px 12px 0 0;
  }}
  .header h1 {{ margin: 0 0 6px; font-size: 22px; font-weight: 700; }}
  .header p  {{ margin: 0; opacity: 0.8; font-size: 13px; }}
  .stats {{
    background: white; padding: 14px 40px; border-bottom: 1px solid #e8edf2;
    display: flex; gap: 40px;
  }}
  .stat strong {{ display: block; font-size: 22px; color: #1e3a5f; }}
  .stat span   {{ font-size: 12px; color: #888; }}
  .content {{ background: white; padding: 32px 40px; }}
  h2 {{
    color: #1e3a5f; font-size: 18px;
    border-bottom: 2px solid #e8f0fb; padding-bottom: 8px; margin-top: 36px;
  }}
  h3 {{ color: #2d6a9f; font-size: 15px; margin-top: 24px; }}
  ul {{ padding-left: 20px; }}
  li {{ margin-bottom: 10px; line-height: 1.65; }}
  strong {{ color: #111; }}
  a  {{ color: #2d6a9f; }}
  p  {{ line-height: 1.7; margin: 8px 0; }}
  .footer {{
    background: #eef1f6; padding: 18px 40px; border-radius: 0 0 12px 12px;
    font-size: 12px; color: #999; text-align: center;
  }}
  .footer a {{ color: #2d6a9f; text-decoration: none; }}
</style>
</head>
<body>
  <div class="header">
    <h1>📰 Týdenní přehled technologických blogů</h1>
    <p>Automaticky vygenerováno · {week}</p>
  </div>
  <div class="stats">
    <div class="stat"><strong>{article_count}</strong><span>článků zpracováno</span></div>
    <div class="stat"><strong>5</strong><span>kategorií</span></div>
    <div class="stat"><strong>25</strong><span>blogů sledováno</span></div>
  </div>
  <div class="content">
    {body}
  </div>
  <div class="footer">
    Generováno přes OpenRouter AI (Llama 3.1) &amp; GitHub Actions ·
    <a href="https://github.com/andrea-klimova/moje-projekty">andrea-klimova/moje-projekty</a>
  </div>
</body>
</html>"""


# ── Gmail odesílač ───────────────────────────────────────────────────────────

def send_email(html_body: str, week: str) -> None:
    """Odešle HTML e-mail přes Gmail SMTP."""
    address  = os.environ["GMAIL_ADDRESS"]
    password = os.environ["GMAIL_APP_PASSWORD"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📰 Týdenní přehled blogů — {week}"
    msg["From"]    = address
    msg["To"]      = address
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(address, password)
        server.sendmail(address, address, msg.as_string())

    print("✅ E-mail odeslán!")


# ── Historie ─────────────────────────────────────────────────────────────────

def save_history(articles_by_category: dict, week: str) -> None:
    """Uloží výsledky do history.json."""
    path = os.path.join(os.path.dirname(__file__), "history.json")
    try:
        with open(path, encoding="utf-8") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []

    total = sum(len(a) for a in articles_by_category.values())
    history.append({
        "week":       week,
        "generated":  datetime.now(timezone.utc).isoformat(),
        "articles":   total,
        "categories": {cat: len(arts) for cat, arts in articles_by_category.items()},
    })

    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print("💾 Historie uložena.")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    now  = datetime.now()
    week = now.strftime("%d. %m. %Y").lstrip("0")

    print(f"🗓️  Spuštění: {week}")
    print("🔍 Stahuji RSS feedy...")
    articles = fetch_articles()
    total = sum(len(a) for a in articles.values())
    print(f"   Celkem: {total} článků")

    if not articles:
        print("⚠️  Žádné nové články — e-mail se neodesílá.")
        return

    print("🤖 Volám OpenRouter API...")
    ai_content = summarize_with_openrouter(articles)

    print("📧 Sestavuji e-mail...")
    html = build_html_email(ai_content, total, week)

    print("📤 Odesílám e-mail...")
    send_email(html, week)

    save_history(articles, week)


if __name__ == "__main__":
    main()

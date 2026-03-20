"""Odesílání HTML e-mailu přes Gmail SMTP."""
import os
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from scrapers.base import JobOffer


class EmailSender:

    def __init__(self):
        self.address = os.environ["GMAIL_ADDRESS"]
        self.password = os.environ["GMAIL_APP_PASSWORD"]

    def send(self, offers: list[JobOffer]) -> None:
        if not offers:
            return

        subject = f"Job Hunter: {len(offers)} nových nabídek — {date.today().strftime('%d. %m. %Y')}"
        html = _build_html(offers)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.address
        msg["To"] = self.address
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(self.address, self.password)
            server.sendmail(self.address, self.address, msg.as_bytes())


def _score_color(score: int) -> str:
    if score >= 8:
        return "#2ecc71"   # zelená
    if score >= 5:
        return "#f39c12"   # oranžová
    return "#e74c3c"       # červená


def _build_html(offers: list[JobOffer]) -> str:
    today = date.today().strftime("%d. %m. %Y")
    cards = ""

    for o in offers:
        color = _score_color(o.ai_score)
        salary_row = f"<p style='margin:4px 0;color:#555;'>💰 {o.salary_text}</p>" if o.salary_text else ""
        desc = o.description[:300].replace("<", "&lt;").replace(">", "&gt;")

        cards += f"""
        <div style="
            background:#fff;
            border:1px solid #e0e0e0;
            border-left:5px solid {color};
            border-radius:8px;
            padding:20px;
            margin-bottom:20px;
            font-family:Arial,sans-serif;
        ">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <h2 style="margin:0 0 4px;font-size:18px;color:#1a1a1a;">
                        <a href="{o.url}" style="color:#2c3e50;text-decoration:none;">{o.title}</a>
                    </h2>
                    <p style="margin:0 0 8px;color:#666;font-size:14px;">🏢 {o.company} &nbsp;|&nbsp; 📍 {o.location} &nbsp;|&nbsp; 📌 {o.source}</p>
                </div>
                <div style="
                    background:{color};
                    color:#fff;
                    font-weight:bold;
                    font-size:22px;
                    border-radius:50%;
                    width:48px;
                    height:48px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    flex-shrink:0;
                    margin-left:16px;
                ">{o.ai_score}</div>
            </div>
            {salary_row}
            <p style="margin:10px 0 4px;color:#444;font-size:13px;">{desc}…</p>
            <p style="margin:8px 0 0;font-size:13px;color:#555;font-style:italic;">🤖 {o.ai_comment}</p>
            <a href="{o.url}" style="
                display:inline-block;
                margin-top:14px;
                padding:8px 18px;
                background:#2c3e50;
                color:#fff;
                border-radius:5px;
                text-decoration:none;
                font-size:13px;
            ">Zobrazit nabídku →</a>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="cs">
<head><meta charset="utf-8"><title>Job Hunter</title></head>
<body style="background:#f5f5f5;padding:24px;font-family:Arial,sans-serif;">
    <div style="max-width:700px;margin:0 auto;">
        <div style="background:#2c3e50;color:#fff;padding:24px;border-radius:8px 8px 0 0;">
            <h1 style="margin:0;font-size:22px;">🎯 Job Hunter</h1>
            <p style="margin:6px 0 0;opacity:0.8;">{today} &nbsp;·&nbsp; {len(offers)} nových marketingových nabídek v Praze</p>
        </div>
        <div style="padding:24px 0;">
            {cards}
        </div>
        <p style="text-align:center;color:#aaa;font-size:12px;">
            Generováno automaticky · Skóre AI: 🟢 8–10 výborné · 🟡 5–7 průměrné · 🔴 1–4 slabé
        </p>
    </div>
</body>
</html>"""

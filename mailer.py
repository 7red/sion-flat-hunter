import smtplib
import logging
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SENDER_NAME, SENDER_EMAIL, SENDER_PASSWORD, SENDER_PHONE, SMTP_HOST, SMTP_PORT
from scrapers import get_soup

logger = logging.getLogger(__name__)

def extract_agent_email(url):
    """Visite la fiche et extrait l'email de l'agent via le lien mailto:"""
    soup = get_soup(url)
    if not soup:
        return None
    mailto = soup.select_one("a[href^='mailto:']")
    if mailto:
        email = mailto["href"].replace("mailto:", "").strip()
        return email
    return None

def send_contact_email(agent_email, annonce):
    adresse = annonce.get("adresse") or annonce.get("url") or "votre annonce"
    subject = f"Demande de visite — {adresse}"
    body = f"""Madame, Monsieur,

Je suis intéressé par votre annonce ({adresse}).
Comment se passent les visites ? Veuillez également me faire savoir quels documents vous sont nécessaires.

N'hésitez pas à me contacter :

{SENDER_NAME}
{SENDER_PHONE}
{SENDER_EMAIL}

Meilleures salutations
{SENDER_NAME}
"""
    msg = MIMEMultipart()
    msg["From"]    = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg["To"]      = agent_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.sendmail(SENDER_EMAIL, agent_email, msg.as_string())
        logger.info(f"Email envoyé à {agent_email} pour {adresse}")
        return True
    except Exception as e:
        logger.error(f"Email ERREUR → {agent_email} : {e}")
        return False

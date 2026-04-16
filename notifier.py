import requests
import logging
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def send_telegram(annonce):
    prix_str    = f"CHF {annonce['prix']}.-/mois" if annonce.get("prix") else "Prix non indiqué"
    pieces_str  = f"{annonce['pieces']} pièce(s)" if annonce.get("pieces") else ""
    surface_str = f" · {annonce['surface']} m²" if annonce.get("surface") else ""
    adresse_str = f"\n📍 {annonce['adresse']}" if annonce.get("adresse") else ""
    centre_tag  = " · 🏙️ Centre-ville" if annonce.get("centre_ville") else ""
    message = (f"🏠 *Nouveau studio à Sion !*\n{adresse_str}\n💰 {prix_str}\n"
               f"🛋 {pieces_str}{surface_str}{centre_tag}\n"
               f"🔗 [Voir l'annonce]({annonce['url']})\n📡 Source : {annonce.get('source','?')}")
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown", "disable_web_page_preview": False}
    try:
        r = requests.post(TELEGRAM_API, json=payload, timeout=10)
        r.raise_for_status()
        logger.info(f"Telegram OK : {annonce['url']}")
        return True
    except Exception as e:
        logger.error(f"Telegram ERREUR : {e}")
        return False

def send_summary(nb_nouvelles, nb_total):
    message = f"📊 *Résumé de veille*\nNouvelles annonces : {nb_nouvelles}\nTotal en base : {nb_total}"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(TELEGRAM_API, json=payload, timeout=10)
    except Exception as e:
        logger.error(f"Summary Telegram ERREUR : {e}")

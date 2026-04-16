import requests
import logging
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def _post(message):
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        r = requests.post(TELEGRAM_API, json=payload, timeout=10)
        r.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Telegram ERREUR : {e}")
        return False

def send_batch(annonces):
    if not annonces:
        return
    n = len(annonces)
    lines = [f"🏠 <b>{n} appartement{'s' if n > 1 else ''} — Sion centre ≤ CHF 1000</b>\n"]
    for a in annonces:
        prix_str    = f"CHF {a['prix']}.-/mois" if a.get("prix") else "prix non indiqué"
        pieces_str  = f"{a['pieces']} pièce(s) · " if a.get("pieces") else ""
        surface_str = f"{a['surface']} m² · " if a.get("surface") else ""
        adresse_str = a.get("adresse") or "Sion"
        lines.append(
            f"📍 {adresse_str}\n"
            f"💰 {prix_str}  |  {pieces_str}{surface_str}{a.get('source','')}\n"
            f'🔗 <a href="{a["url"]}">Voir l\'annonce</a>'
        )
    message = "\n\n".join(lines)
    ok = _post(message)
    if ok:
        logger.info(f"Telegram : {n} annonce(s) envoyées en un message")

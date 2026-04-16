#!/usr/bin/env python3
import sys, time, logging, os
from datetime import datetime
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from config import SCRAPE_INTERVAL_MINUTES, DELAY_BETWEEN_SITES, LOG_PATH
from database import init_db, save_annonce, is_new, count_annonces
from utils import normalize, passes_filters
from notifier import send_batch
from mailer import extract_agent_email, send_contact_email
from scrapers import ALL_SCRAPERS

os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("agent")

def run_once():
    nouvelles = []
    for name, fn in ALL_SCRAPERS:
        logger.info(f"─── Scraping {name} …")
        try: items = fn()
        except Exception as e: logger.error(f"{name} crash : {e}"); items = []
        for raw in items:
            a = normalize(raw)
            if not passes_filters(a): continue
            if not a.get("url"): continue
            if not is_new(a["url"]): continue
            if save_annonce(a):
                logger.info(f"NOUVELLE ▶ [{a['source']}] {a['titre'][:60]} | {a.get('prix','?')} CHF")
                nouvelles.append(a)
                agent_email = extract_agent_email(a["url"])
                if agent_email:
                    send_contact_email(agent_email, a)
                else:
                    logger.info(f"Pas d'email trouvé pour {a['url']}")
        time.sleep(DELAY_BETWEEN_SITES)
    if nouvelles:
        send_batch(nouvelles)
    return len(nouvelles)

def main():
    logger.info("🏠 Agent veille immobilière — Sion 1 pièce ≤ CHF 1000")
    init_db()
    passage = 0
    while True:
        passage += 1
        logger.info(f"▶ Passage #{passage} — {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        try: nb = run_once()
        except Exception as e: logger.error(f"Erreur : {e}"); nb = 0
        total = count_annonces()
        logger.info(f"✓ {nb} nouvelles | {total} total")
        time.sleep(SCRAPE_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        logger.info("MODE TEST")
        init_db()
        nb = run_once()
        logger.info(f"Test terminé : {nb} nouvelles annonces")
    else:
        main()

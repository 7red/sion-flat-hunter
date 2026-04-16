import sqlite3
import hashlib
import logging
from datetime import datetime
from config import DB_PATH

logger = logging.getLogger(__name__)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS annonces (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                hash        TEXT UNIQUE NOT NULL,
                source      TEXT NOT NULL,
                titre       TEXT,
                prix        INTEGER,
                pieces      REAL,
                surface     INTEGER,
                adresse     TEXT,
                url         TEXT,
                centre_ville INTEGER DEFAULT 0,
                date_vue    TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_hash ON annonces(hash)")
        conn.commit()
    logger.info("Base de données initialisée.")

def make_hash(url):
    return hashlib.sha256(url.strip().encode()).hexdigest()[:16]

def is_new(url):
    h = make_hash(url)
    with get_connection() as conn:
        row = conn.execute("SELECT id FROM annonces WHERE hash = ?", (h,)).fetchone()
    return row is None

def save_annonce(annonce):
    h = make_hash(annonce["url"])
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO annonces
                    (hash, source, titre, prix, pieces, surface, adresse, url, centre_ville, date_vue)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (h, annonce.get("source","?"), annonce.get("titre",""), annonce.get("prix"),
                  annonce.get("pieces"), annonce.get("surface"), annonce.get("adresse",""),
                  annonce["url"], 1 if annonce.get("centre_ville") else 0, datetime.now().isoformat()))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def count_annonces():
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM annonces").fetchone()[0]

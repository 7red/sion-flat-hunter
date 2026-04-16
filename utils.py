import re
import logging
from config import CENTER_KEYWORDS, MAX_PRICE, MAX_ROOMS

logger = logging.getLogger(__name__)

def parse_price(text):
    if not text: return None
    text = text.replace("'","").replace("\u2019","")
    m = re.search(r"(\d{3,5})", text)
    return int(m.group(1)) if m else None

def parse_rooms(text):
    if not text: return None
    m = re.search(r"(\d+(?:[.,]\d)?)\s*(?:pièce|piece|p\.|zimmer|room)", text, re.IGNORECASE)
    if m: return float(m.group(1).replace(",","."))
    m = re.search(r"\b(\d+[.,]?\d?)\b", text)
    return float(m.group(1).replace(",",".")) if m else None

def parse_surface(text):
    if not text: return None
    m = re.search(r"(\d+)\s*m", text, re.IGNORECASE)
    return int(m.group(1)) if m else None

def is_center(titre, adresse):
    combined = f"{titre} {adresse}".lower()
    return any(kw in combined for kw in CENTER_KEYWORDS)

def passes_filters(annonce):
    prix   = annonce.get("prix")
    pieces = annonce.get("pieces")
    if prix and prix > MAX_PRICE:
        return False
    if pieces and pieces > MAX_ROOMS:
        return False
    return True

def normalize(raw):
    titre   = (raw.get("titre") or "").strip()
    adresse = (raw.get("adresse") or "").strip()
    return {
        "source":       raw.get("source","?"),
        "titre":        titre,
        "prix":         parse_price(raw.get("prix_raw") or str(raw.get("prix") or "")),
        "pieces":       raw.get("pieces") or parse_rooms(raw.get("pieces_raw") or titre),
        "surface":      raw.get("surface") or parse_surface(raw.get("surface_raw") or titre),
        "adresse":      adresse,
        "url":          (raw.get("url") or "").strip(),
        "centre_ville": is_center(titre, adresse),
    }

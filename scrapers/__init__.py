import re, time, logging, requests
from bs4 import BeautifulSoup
from config import HEADERS, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

def get_soup(url, params=None):
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        logger.warning(f"GET {url} → {e}")
        return None

def get_json(url, params=None):
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.warning(f"GET JSON {url} → {e}")
        return None

def scrape_homegate():
    url = "https://api.homegate.ch/search/listings"
    params = {"offerType":"rent","listingType":"APARTMENT","locationIds":"CH-VS-6951","numberOfRooms[to]":"1.5","monthlyRent[to]":"1000","sortBy":"dateCreated","sortDirection":"desc","pageSize":"30"}
    data = get_json(url, params)
    if not data: return []
    results = []
    for item in data.get("listings",[]):
        attr = item.get("listing",{}).get("attributes",{})
        loc  = item.get("listing",{}).get("address",{})
        lid  = item.get("listing",{}).get("id","")
        results.append({"source":"Homegate","titre":str(attr.get("numberOfRooms",""))+" pièces","prix":attr.get("monthlyRent"),"pieces":attr.get("numberOfRooms"),"surface":attr.get("livingArea"),"adresse":f"{loc.get('street','')} {loc.get('houseNumber','')}, {loc.get('zip','')} {loc.get('locality','')}".strip(),"url":f"https://www.homegate.ch/louer/{lid}"})
    logger.info(f"Homegate : {len(results)} annonces")
    return results

def _generic_scrape(url, source, base_url, params=None):
    soup = get_soup(url, params)
    if not soup: return []
    results = []
    selectors = ["article","[class*='listing-item']","[class*='property']","[class*='result-item']","li.item",".object"]
    cards = []
    for sel in selectors:
        cards = soup.select(sel)
        if cards: break
    for card in cards:
        link = card.select_one("a[href]")
        if not link: continue
        href = link["href"]
        if not href.startswith("http"):
            href = base_url.rstrip("/") + "/" + href.lstrip("/")
        if href.rstrip("/") == base_url.rstrip("/") or href.endswith("#") or href == "#":
            continue
        titre_el = card.select_one("h2,h3,[class*='title']")
        prix_el  = card.select_one("[class*='price'],[class*='prix'],[class*='loyer']")
        adr_el   = card.select_one("[class*='address'],[class*='location'],[class*='adresse'],[class*='lieu']")
        results.append({"source":source,"titre":titre_el.get_text(strip=True)[:120] if titre_el else "","prix_raw":prix_el.get_text(strip=True) if prix_el else "","adresse":adr_el.get_text(strip=True) if adr_el else "Sion","url":href})
    logger.info(f"{source} : {len(results)} annonces")
    return results

def scrape_immoscout24():
    return _generic_scrape("https://www.immoscout24.ch/fr/appartement/louer/lieu-sion","ImmoScout24","https://www.immoscout24.ch",{"pn":1,"nrf":1.5,"pr":1000})

def scrape_immobilier_ch():
    return _generic_scrape("https://www.immobilier.ch/fr/louer/appartement/valais/sion/page-1","immobilier.ch","https://www.immobilier.ch")

def scrape_home_ch():
    return _generic_scrape("https://www.home.ch/fr/louer/appartement/a-sion","Home.ch","https://www.home.ch",{"rooms_max":"1.5","price_max":"1000"})

def scrape_acheter_louer():
    return _generic_scrape("https://www.acheter-louer.ch/location/appartement/valais/sion.html","Acheter-Louer","https://www.acheter-louer.ch")

def scrape_comparis():
    return _generic_scrape("https://fr.comparis.ch/immobilien/result/list","Comparis","https://fr.comparis.ch")

def scrape_netimmo():
    return _generic_scrape("https://www.netimmo.ch/recherche/location/appartement/valais/sion","Netimmo","https://www.netimmo.ch")

def scrape_anibis():
    return _generic_scrape("https://www.anibis.ch/fr/c/appartements-a-louer","Anibis","https://www.anibis.ch",{"q":"studio appartement sion","r":"1950"})

def scrape_allegro():
    soup = get_soup("https://www.agence-allegro.ch/allegro-locations")
    if not soup: return []
    results = []
    for card in soup.select("div.listing-item"):
        link = card.select_one("a.listing-img-container[href]")
        if not link: continue
        href = link["href"].strip()
        if not href or "fiche-location" not in href: continue
        url = "https://www.agence-allegro.ch/" + href.lstrip("/")

        # Adresse : le <a> avec l'icône fa-map-marker
        adr_el = card.select_one("a i.fa-map-marker")
        adresse = adr_el.parent.get_text(strip=True) if adr_el else ""

        # Pièces et loyer dans la liste de détails
        pieces, prix = None, None
        for li in card.select("ul.listing-details li"):
            txt = li.get_text(" ", strip=True)
            b = li.select_one("b")
            if not b: continue
            if "pièce" in txt.lower() or "piece" in txt.lower():
                try: pieces = float(b.get_text(strip=True).replace(",","."))
                except: pass
            if "loyer" in txt.lower():
                raw = b.get_text(strip=True).replace("\u00a0","").replace("'","").replace(" ","")
                m = re.search(r"(\d{3,5})", raw)
                if m: prix = int(m.group(1))

        results.append({"source":"Allégro Sion","titre":"","prix":prix,"pieces":pieces,"adresse":adresse,"url":url})
    logger.info(f"Allégro Sion : {len(results)} annonces")
    return results

def scrape_gerofinance():
    return _generic_scrape("https://www.gerofinance.ch/locations/appartements/valais/sion","Gerofinance","https://www.gerofinance.ch")

def scrape_comptoir_immo():
    return _generic_scrape("https://comptoir-immo.ch/location/appartement/Valais/Sion/","Comptoir Immobilier","https://comptoir-immo.ch")

def scrape_immostreet():
    return _generic_scrape("https://www.immostreet.ch/fr/location/1-piece/sion-1950/","ImmoStreet","https://www.immostreet.ch")

ALL_SCRAPERS = [
    ("Homegate",         scrape_homegate),
    ("ImmoScout24",      scrape_immoscout24),
    ("immobilier.ch",    scrape_immobilier_ch),
    ("Home.ch",          scrape_home_ch),
    ("Acheter-Louer",    scrape_acheter_louer),
    ("Comparis",         scrape_comparis),
    ("Netimmo",          scrape_netimmo),
    ("Anibis",           scrape_anibis),
    ("Allégro Sion",     scrape_allegro),
    ("Gerofinance",      scrape_gerofinance),
    ("Comptoir Immo",    scrape_comptoir_immo),
    ("ImmoStreet",       scrape_immostreet),
]

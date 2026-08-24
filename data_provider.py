import requests
import random
from datetime import datetime

TCGDEX_BASE = "https://api.tcgdex.net/v2/en"

def _get(url, timeout=15):
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        return None
    return None

def _normalize_tcgdex(card):
    if not card:
        return None

    pricing = card.get("pricing") or {}
    cm = pricing.get("cardmarket") or {}
    tcg = pricing.get("tcgplayer") or {}

    image = card.get("image")
    set_info = card.get("set") or {}

    # TCGdex sometimes expresses Cardmarket unit as cents; normalize defensively.
    unit = cm.get("unit", 1) or 1
    def n(v):
        if v is None:
            return None
        try:
            v = float(v)
            if unit == 100 and v > 500:
                return v / 100
            return v
        except Exception:
            return None

    normalized = {
        "id": card.get("id"),
        "name": card.get("name"),
        "rarity": card.get("rarity") or "",
        "set": {"name": set_info.get("name") or set_info.get("id") or ""},
        "image": image,
        "cardmarket": {
            "prices": {
                "trendPrice": n(cm.get("trend") or cm.get("trend-holo")),
                "averageSellPrice": n(cm.get("avg")),
                "avg1": n(cm.get("avg1") or cm.get("avg1-holo")),
                "avg7": n(cm.get("avg7") or cm.get("avg7-holo")),
                "avg30": n(cm.get("avg30") or cm.get("avg30-holo")),
                "lowPrice": n(cm.get("low") or cm.get("low-holo")),
            },
            "updated": cm.get("updated"),
        },
        "tcgplayer": tcg,
    }
    return normalized

def search_cards(query, limit=50):
    # TCGdex list endpoint supports broad retrieval; client-side filter keeps MVP simple and resilient.
    cards = _get(f"{TCGDEX_BASE}/cards")
    if not cards:
        return []
    q = query.lower().strip()
    matches = [c for c in cards if q in (c.get("name") or "").lower()][:limit]
    out = []
    for stub in matches:
        full = _get(f"{TCGDEX_BASE}/cards/{stub.get('id')}")
        norm = _normalize_tcgdex(full)
        if norm:
            out.append(norm)
    return out

def get_market_universe(limit=500):
    cards = _get(f"{TCGDEX_BASE}/cards", timeout=20)
    if not cards:
        return []

    # Newer / richer cards first is more useful for an MVP screener.
    stubs = cards[-limit:]
    out = []
    for stub in reversed(stubs):
        full = _get(f"{TCGDEX_BASE}/cards/{stub.get('id')}", timeout=8)
        norm = _normalize_tcgdex(full)
        if norm and get_cardmarket_snapshot(norm).get("trend") is not None:
            out.append(norm)
        if len(out) >= min(160, limit):
            break
    return out

def get_cardmarket_snapshot(card):
    p = ((card.get("cardmarket") or {}).get("prices") or {})
    return {
        "trend": p.get("trendPrice"),
        "low": p.get("lowPrice"),
        "avg": p.get("averageSellPrice"),
        "avg1": p.get("avg1"),
        "avg7": p.get("avg7"),
        "avg30": p.get("avg30"),
    }

def demo_universe():
    names = [
        ("Charizard ex","Scarlet & Violet—151","Special Illustration Rare",165),
        ("Gengar VMAX","Fusion Strike","Secret Rare",195),
        ("Umbreon V","Evolving Skies","Ultra Rare",145),
        ("Pikachu ex","Surging Sparks","Special Illustration Rare",125),
        ("Mew ex","Paldean Fates","Special Illustration Rare",82),
        ("Giratina V","Lost Origin","Ultra Rare",210),
        ("Magikarp","Paldea Evolved","Illustration Rare",95),
        ("Dragonite V","Evolving Skies","Ultra Rare",108),
        ("Greninja ex","Twilight Masquerade","Special Illustration Rare",235),
        ("Eevee","Twilight Masquerade","Illustration Rare",55),
        ("Latias ex","Surging Sparks","Special Illustration Rare",188),
        ("Snorlax","Pokémon 151","Illustration Rare",42),
        ("Mimikyu","Paldean Fates","Illustration Rare",18),
        ("Gardevoir ex","Scarlet & Violet","Special Illustration Rare",34),
        ("Lugia V","Silver Tempest","Ultra Rare",175),
    ]
    out = []
    for i,(name,setn,rarity,price) in enumerate(names):
        out.append({
            "id": f"demo-{i}",
            "name": name,
            "set":{"name":setn},
            "rarity":rarity,
            "image":None,
            "cardmarket":{"prices":{
                "trendPrice":price,
                "lowPrice":price*0.92,
                "averageSellPrice":price*0.99,
                "avg1":price*1.01,
                "avg7":price*0.98,
                "avg30":price*0.92,
            }}
        })
    # expand across cheap bands
    for i in range(35):
        price = [3.5,7.5,12.5,17.5,24,39,62,88,125,190][i%10]
        out.append({
            "id": f"demo-x-{i}",
            "name": ["Pikachu","Gengar","Umbreon","Mew","Eevee","Rayquaza","Lucario"][i%7] + f" #{i}",
            "set":{"name":"Demo Market"},
            "rarity":"Illustration Rare" if i%2 else "Rare",
            "image":None,
            "cardmarket":{"prices":{
                "trendPrice":price,
                "lowPrice":price*0.90,
                "averageSellPrice":price*0.98,
                "avg1":price*1.02,
                "avg7":price*0.97,
                "avg30":price*0.91,
            }}
        })
    return out

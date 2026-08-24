import requests
import time

BASE = "https://api.tcgdex.net/v2/en"
POPULAR = [
    "Charizard","Pikachu","Gengar","Umbreon","Rayquaza","Lugia","Mew","Mewtwo",
    "Giratina","Eevee","Sylveon","Greninja","Latias","Dragonite","Magikarp",
    "Gardevoir","Snorlax","Lucario","Espeon","Leafeon","Glaceon","Vaporeon",
    "Jolteon","Flareon","Blastoise","Venusaur","Arceus","Mimikyu"
]

def _get(url, timeout=15):
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        return None
    return None

def _eur(value, unit):
    if value is None:
        return None
    value = float(value)
    return value / 100.0 if unit == 100 else value

def normalize(full):
    if not full:
        return None
    cm = ((full.get("pricing") or {}).get("cardmarket") or {})
    if not cm:
        return None
    unit = cm.get("unit") or 1
    prices = {
        "trend": _eur(cm.get("trend") or cm.get("trend-holo"), unit),
        "low": _eur(cm.get("low") or cm.get("low-holo"), unit),
        "avg": _eur(cm.get("avg") or cm.get("avg-holo"), unit),
        "avg1": _eur(cm.get("avg1") or cm.get("avg1-holo"), unit),
        "avg7": _eur(cm.get("avg7") or cm.get("avg7-holo"), unit),
        "avg30": _eur(cm.get("avg30") or cm.get("avg30-holo"), unit),
    }
    if prices["trend"] is None:
        return None
    set_info = full.get("set") or {}
    return {
        "id": full.get("id"),
        "name": full.get("name"),
        "set_name": set_info.get("name") or set_info.get("id") or "",
        "rarity": full.get("rarity") or "",
        "image_url": (
    f"{full.get('image')}/high.webp"
    if full.get("image")
    else None
),
        "prices": prices,
    }

def fetch_eu_sample(max_cards=300):

    stubs = _get(
        f"{BASE}/cards",
        timeout=25
    )

    if not stubs:
        return [], "Could not retrieve TCGdex card index."

    wanted = []

    # Prefer newer cards first
    for stub in reversed(stubs):

        wanted.append(stub)

        if len(wanted) >= max_cards * 4:
            break

    out = []

    for stub in wanted:

        full = _get(
            f"{BASE}/cards/{stub.get('id')}",
            timeout=10
        )

        card = normalize(full)

        if card:
            out.append(card)

        if len(out) >= max_cards:
            break

        time.sleep(0.02)

    if not out:
        return [], "No cards with European Cardmarket pricing were returned."

    return out, None

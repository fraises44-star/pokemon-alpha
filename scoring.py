POPULARITY = {
    "Charizard": 100, "Pikachu": 98, "Gengar": 96, "Umbreon": 95,
    "Rayquaza": 94, "Lugia": 93, "Mew": 92, "Mewtwo": 91,
    "Giratina": 91, "Eevee": 90, "Sylveon": 90, "Arceus": 90,
    "Espeon": 89, "Greninja": 89, "Latias": 88, "Dragonite": 88,
    "Vaporeon": 88, "Latios": 87, "Leafeon": 87, "Glaceon": 87,
    "Jolteon": 87, "Flareon": 87, "Blastoise": 87, "Venusaur": 85,
    "Lucario": 84, "Snorlax": 84, "Mimikyu": 83, "Magikarp": 83,
    "Gardevoir": 82,
}

def _clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))

def _prices(card):
    return ((card.get("cardmarket") or {}).get("prices") or {})

def _rarity_score(rarity):
    r = (rarity or "").lower()
    if "special illustration" in r: return 100
    if "illustration rare" in r: return 92
    if "hyper rare" in r: return 94
    if "secret" in r: return 90
    if "ultra rare" in r or "rare ultra" in r: return 86
    if "holo" in r: return 68
    if "rare" in r: return 58
    return 45

def _popularity(name):
    best = 50
    n = (name or "").lower()
    for pokemon, s in POPULARITY.items():
        if pokemon.lower() in n:
            best = max(best, s)
    # popularity is useful but deliberately compressed so Charizard cannot win on name alone
    return round(50 + (best - 50) * 0.72)

def score_card(card):
    p = _prices(card)
    trend = p.get("trendPrice")
    avg1 = p.get("avg1")
    avg7 = p.get("avg7")
    avg30 = p.get("avg30")
    low = p.get("lowPrice")
    avg = p.get("averageSellPrice")

    present = sum(x is not None for x in [trend,avg1,avg7,avg30,low,avg])
    confidence = round(35 + present/6*65)

    momentum30 = 0.0
    if trend and avg30:
        momentum30 = (trend/avg30 - 1) * 100
    elif avg7 and avg30:
        momentum30 = (avg7/avg30 - 1) * 100

    # Reward positive momentum but cap hype spikes.
    momentum = _clamp(50 + momentum30 * 2.1)

    # Value rewards a modest discount to recent averages; deep collapses do not automatically score 100.
    reference = avg7 or avg30 or avg
    value = 50
    if trend and reference:
        discount = (reference/trend - 1) * 100
        value = _clamp(58 + discount * 2)
    if low and trend and low < trend:
        value = _clamp(value + min(12, (trend-low)/trend*40))

    rarity = _rarity_score(card.get("rarity"))
    popularity = _popularity(card.get("name"))

    # Liquidity proxy until actual transaction counts are licensed.
    liquidity = 40 + present * 8
    if trend and avg and abs(trend-avg)/max(trend,1) < .12:
        liquidity += 10
    liquidity = _clamp(liquidity)

    # Penalize large short-vs-long jumps as volatility/hype risk.
    volatility = abs(momentum30)
    risk_quality = _clamp(88 - max(0, volatility - 12) * 1.6)

    pii = round(
        momentum * .25 +
        value * .20 +
        rarity * .15 +
        popularity * .15 +
        liquidity * .10 +
        risk_quality * .10 +
        confidence * .05
    )

    return {
        "pii": _clamp(pii),
        "momentum": round(momentum),
        "momentum_30d": round(momentum30,1),
        "value": round(value),
        "rarity": round(rarity),
        "popularity": round(popularity),
        "liquidity": round(liquidity),
        "risk_quality": round(risk_quality),
        "confidence": round(confidence),
    }

def recommendation_label(score):
    if score >= 88: return "🔥 High-conviction watch"
    if score >= 80: return "🟢 Strong"
    if score >= 70: return "👀 Interesting"
    if score >= 60: return "🟡 Speculative"
    return "⚪ Neutral / weak"

def build_thesis(card, s):
    out = []
    if s["momentum_30d"] > 12:
        out.append(f"Strong 30-day price momentum (+{s['momentum_30d']}%), but watch for hype/mean reversion.")
    elif s["momentum_30d"] > 3:
        out.append(f"Constructive 30-day momentum (+{s['momentum_30d']}%).")
    elif s["momentum_30d"] < -8:
        out.append(f"Price is below its 30-day reference ({s['momentum_30d']}%); potential value or deteriorating demand.")
    else:
        out.append("Price action is relatively stable versus the 30-day reference.")

    if s["rarity"] >= 90:
        out.append("Premium rarity profile supports collector demand.")
    if s["popularity"] >= 80:
        out.append("Character demand is structurally strong relative to the average Pokémon.")
    if s["confidence"] < 70:
        out.append("Data coverage is incomplete, so the signal should be treated cautiously.")
    if s["risk_quality"] < 65:
        out.append("Recent price movement is volatile; position sizing matters.")
    return out

def price_band(price):
    if price is None: return "Unknown"
    bands=[(0,5),(5,10),(10,15),(15,20),(20,30),(30,50),(50,75),(75,100),(100,150),(150,250)]
    for lo,hi in bands:
        if lo <= price < hi: return f"€{lo}–€{hi}"
    return "€250+"

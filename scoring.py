POPULARITY = {
    "Charizard":100,"Pikachu":98,"Gengar":96,"Umbreon":95,"Rayquaza":94,"Lugia":93,
    "Mew":92,"Mewtwo":91,"Giratina":91,"Eevee":90,"Sylveon":90,"Arceus":90,
    "Espeon":89,"Greninja":89,"Latias":88,"Dragonite":88,"Vaporeon":88,
    "Leafeon":87,"Glaceon":87,"Jolteon":87,"Flareon":87,"Blastoise":87,
    "Venusaur":85,"Lucario":84,"Snorlax":84,"Mimikyu":83,"Magikarp":83,"Gardevoir":82
}
def clamp(v): return max(0,min(100,v))
def rarity_score(text):
    r=(text or "").lower()
    if "special illustration" in r:return 100
    if "illustration rare" in r:return 92
    if "hyper rare" in r:return 94
    if "secret" in r:return 90
    if "ultra rare" in r or "rare ultra" in r:return 86
    if "holo" in r:return 68
    if "rare" in r:return 58
    return 45
def popularity_score(name):
    base=50;n=(name or "").lower()
    for p,s in POPULARITY.items():
        if p.lower() in n: base=max(base,s)
    return round(50+(base-50)*.72)
def score(row):
    trend,low,avg,avg1,avg7,avg30=[row.get(k) for k in ["trend","low","avg","avg1","avg7","avg30"]]
    present=sum(v is not None for v in [trend,low,avg,avg1,avg7,avg30])
    confidence=round(35+present/6*65)
    momentum30=0.0
    if trend and avg30: momentum30=(trend/avg30-1)*100
    elif avg7 and avg30: momentum30=(avg7/avg30-1)*100
    momentum=clamp(50+momentum30*2)
    value=50
    ref=avg7 or avg30 or avg
    if trend and ref: value=clamp(58+(ref/trend-1)*100*2)
    if low and trend and low<trend: value=clamp(value+min(12,(trend-low)/trend*40))
    rarity=rarity_score(row.get("rarity"));pop=popularity_score(row.get("name"))
    liquidity=clamp(40+present*8+(10 if trend and avg and abs(trend-avg)/max(trend,1)<.12 else 0))
    risk=clamp(88-max(0,abs(momentum30)-12)*1.6)
    pii=round(momentum*.25+value*.20+rarity*.15+pop*.15+liquidity*.10+risk*.10+confidence*.05)
    return {"pii":pii,"momentum30":round(momentum30,1),"value":round(value),"rarity_score":rarity,
            "popularity":pop,"liquidity":round(liquidity),"risk_quality":round(risk),"confidence":confidence}
def signal(pii):
    if pii>=88:return "🔥 High-conviction watch"
    if pii>=80:return "🟢 Strong"
    if pii>=70:return "👀 Interesting"
    if pii>=60:return "🟡 Speculative"
    return "⚪ Neutral / weak"
def thesis(row,s):
    items=[]
    m=s["momentum30"]
    if m>12:items.append(f"Strong European 30-day momentum (+{m}%), with elevated hype risk.")
    elif m>3:items.append(f"Constructive European 30-day momentum (+{m}%).")
    elif m<-8:items.append(f"Trading below its 30-day European reference ({m}%).")
    else:items.append("European price action is relatively stable versus its recent reference.")
    if s["rarity_score"]>=90:items.append("Premium rarity profile supports collector demand.")
    if s["popularity"]>=80:items.append("Character demand is structurally strong.")
    if s["confidence"]<70:items.append("Market data coverage is incomplete, lowering confidence.")
    if s["risk_quality"]<65:items.append("Recent price movement is volatile.")
    return items

import streamlit as st
from supabase import create_client

@st.cache_resource
def get_supabase():
    url = st.secrets.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_ANON_KEY")
    if not url or not key:
        return None
    return create_client(url, key)

def connection_check():
    sb = get_supabase()
    if sb is None:
        return False, "Supabase secrets are missing."
    try:
        sb.table("cards").select("id").limit(1).execute()
        return True, "Connected"
    except Exception as e:
        return False, str(e)

def upsert_cards(cards):
    sb = get_supabase()
    payload = [{
        "id": c["id"],
        "name": c["name"],
        "set_name": c.get("set_name"),
        "rarity": c.get("rarity"),
        "image_url": c.get("image_url"),
    } for c in cards]
    if payload:
        sb.table("cards").upsert(payload).execute()
    return len(payload)

def insert_price_snapshots(cards):
    sb = get_supabase()
    payload = []
    for c in cards:
        p = c.get("prices", {})
        payload.append({
            "card_id": c["id"],
            "trend_price_eur": p.get("trend"),
            "low_price_eur": p.get("low"),
            "avg_sell_eur": p.get("avg"),
            "avg_1d_eur": p.get("avg1"),
            "avg_7d_eur": p.get("avg7"),
            "avg_30d_eur": p.get("avg30"),
            "source": "cardmarket_via_tcgdex",
        })
    if payload:
        sb.table("price_history").insert(payload).execute()
    return len(payload)

def load_market(limit=1000):
    sb = get_supabase()
    if sb is None:
        return []
    cards = (sb.table("cards").select("*").limit(limit).execute().data or [])
    if not cards:
        return []
    prices = (
        sb.table("price_history").select("*")
        .order("recorded_at", desc=True).limit(limit).execute().data or []
    )
    latest = {}
    for p in prices:
        cid = p.get("card_id")
        if cid and cid not in latest:
            latest[cid] = p
    out = []
    for c in cards:
        p = latest.get(c["id"], {})
        out.append({
            **c,
            "trend": p.get("trend_price_eur"),
            "low": p.get("low_price_eur"),
            "avg": p.get("avg_sell_eur"),
            "avg1": p.get("avg_1d_eur"),
            "avg7": p.get("avg_7d_eur"),
            "avg30": p.get("avg_30d_eur"),
            "recorded_at": p.get("recorded_at"),
        })
    return out

def load_price_history(card_id, limit=180):
    sb = get_supabase()
    if sb is None:
        return []
    return (
        sb.table("price_history").select("*")
        .eq("card_id", card_id)
        .order("recorded_at", desc=False).limit(limit).execute().data or []
    )

def load_population(card_id):
    sb = get_supabase()
    if sb is None:
        return []
    return (
        sb.table("population_history").select("*")
        .eq("card_id", card_id)
        .order("recorded_at", desc=True).limit(500).execute().data or []
    )

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

    cards = (
        sb.table("cards")
        .select("*")
        .limit(limit)
        .execute()
        .data
        or []
    )

    if not cards:
        return []

    out = []

    for c in cards:
        price_result = (
            sb.table("price_history")
            .select("*")
            .eq("card_id", c["id"])
            .order("recorded_at", desc=True)
            .limit(1)
            .execute()
        )

        prices = price_result.data or []

        p = prices[0] if prices else {}

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
def load_graded_sales(card_id, limit=200):
    sb = get_supabase()

    if sb is None:
        return []

    result = (
        sb.table("graded_sales")
        .select("*")
        .eq("card_id", card_id)
        .order("sold_at", desc=True)
        .limit(limit)
        .execute()
    )

    return result.data or []


def load_market_signals(card_id=None, limit=500):
    sb = get_supabase()

    if sb is None:
        return []

    query = (
        sb.table("market_signals")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
    )

    if card_id:
        query = query.eq("card_id", card_id)

    result = query.execute()

    return result.data or []


def save_market_signal(
    card_id,
    liquidity_score=None,
    momentum_score=None,
    volatility_score=None,
    graded_premium_score=None,
    population_score=None,
    reprint_risk_score=None,
    opportunity_score=None,
):
    sb = get_supabase()

    if sb is None:
        raise RuntimeError("Supabase is not connected.")

    payload = {
        "card_id": card_id,
        "liquidity_score": liquidity_score,
        "momentum_score": momentum_score,
        "volatility_score": volatility_score,
        "graded_premium_score": graded_premium_score,
        "population_score": population_score,
        "reprint_risk_score": reprint_risk_score,
        "opportunity_score": opportunity_score,
    }

    sb.table("market_signals").insert(payload).execute()

    return payload

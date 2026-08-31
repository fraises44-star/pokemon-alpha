import os

from supabase import create_client
from cardmarket_prices import fetch_cardmarket_prices


SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_ANON_KEY,
)


result = (
    supabase.table("cards")
    .select("id,name,cardmarket_id")
    .not_.is_("cardmarket_id", "null")
    .limit(10)
    .execute()
)

cards = result.data or []

print("MAPPED CARDS:", len(cards))

card_by_market_id = {
    str(card["cardmarket_id"]): card
    for card in cards
}

cardmarket_ids = list(card_by_market_id.keys())

prices = fetch_cardmarket_prices(
    cardmarket_ids
)

price_rows = []

for item in prices:
    external_id = str(item.get("externalId") or "")
    card = card_by_market_id.get(external_id)

    if not card:
        print(
            "SKIPPED UNKNOWN RETURNED ID:",
            external_id,
        )
        continue

    price = item.get("price") or {}

    price_rows.append({
        "card_id": card["id"],
        "trend_price_eur": price.get("trend"),
        "low_price_eur": price.get("low"),
        "avg_sell_eur": price.get("sell"),
        "avg_1d_eur": price.get("avg1"),
        "avg_7d_eur": price.get("avg7"),
        "avg_30d_eur": price.get("avg30"),
        "source": "cardmarket_via_tcg_cardmarket_api",
    })

print("PRICE ROWS TO INSERT:", len(price_rows))

if price_rows:
    supabase.table("price_history").insert(
        price_rows
    ).execute()

print(
    "SUCCESS: inserted",
    len(price_rows),
    "Cardmarket price rows",
)

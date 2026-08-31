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

cardmarket_ids = [
    card["cardmarket_id"]
    for card in cards
]

print("REQUESTED CARDMARKET IDS:")
print(cardmarket_ids)
prices = fetch_cardmarket_prices(
    cardmarket_ids
    
)

print("PRICE RESULTS:")
print(prices)

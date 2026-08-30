import os
import requests
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
API_KEY = os.environ["TCG_CARDMARKET_API_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_ANON_KEY,
)

card_id = "smp-SM158"

result = (
    supabase.table("cards")
    .select("id,name,set_name,cardmarket_id")
    .eq("id", card_id)
    .single()
    .execute()
)

card = result.data

print("DATABASE CARD:", card)

cardmarket_id = card.get("cardmarket_id")

if not cardmarket_id:
    raise RuntimeError("Card has no Cardmarket ID")

url = (
    "https://tcg-api-production-5148.up.railway.app"
    f"/cards/pokemon/{cardmarket_id}"
)

response = requests.get(
    url,
    headers={"X-API-Key": API_KEY},
    timeout=20,
)

print("STATUS:", response.status_code)

response.raise_for_status()

market_card = response.json()
price = market_card.get("price") or {}

print("CARDMARKET ID:", cardmarket_id)
print("NAME:", market_card.get("name"))
print("TREND:", price.get("trend"))
print("LOW:", price.get("low"))
print("AVG1:", price.get("avg1"))
print("AVG7:", price.get("avg7"))
print("AVG30:", price.get("avg30"))

import os
import requests

API_KEY = os.environ["TCG_CARDMARKET_API_KEY"]

url = "https://tcg-api-production-5148.up.railway.app/cards/search"

params = {
    "game": "pokemon",
    "name": "Charizard",
    "limit": 100,
}

headers = {
    "X-API-Key": API_KEY,
}

response = requests.get(
    url,
    params=params,
    headers=headers,
    timeout=20,
)

print("STATUS:", response.status_code)
data = response.json()

for card in data.get("data", []):
    name = card.get("name", "")
    external_id = card.get("externalId")
    expansion_id = card.get("expansionId")
    price = card.get("price") or {}

    if "SM158" in str(external_id).upper() or "SM158" in name.upper():
        print("FOUND SM158")
        print("NAME:", name)
        print("EXTERNAL ID:", external_id)
        print("EXPANSION ID:", expansion_id)
        print("SELL:", price.get("sell"))
        print("LOW:", price.get("low"))
        print("TREND:", price.get("trend"))
        print("AVG1:", price.get("avg1"))
        print("AVG7:", price.get("avg7"))
        print("AVG30:", price.get("avg30"))

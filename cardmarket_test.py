import os
import requests

API_KEY = os.environ["TCG_CARDMARKET_API_KEY"]

url = "https://tcg-api-production-5148.up.railway.app/cards/search"

params = {
    "game": "pokemon",
    "name": "Charizard",
    "limit": 100,
    "page": 2,
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

cards = data.get("data", [])

target_ids = {
    "558291",
    "412909",
    "851285",
    "886369",
}

for card in cards:
    if str(card.get("externalId")) in target_ids:
        price = card.get("price") or {}

        print("-----")
        print("NAME:", card.get("name"))
        print("CARDMARKET ID:", card.get("externalId"))
        print("EXPANSION:", card.get("expansionId"))
        print("SELL:", price.get("sell"))
        print("LOW:", price.get("low"))
        print("TREND:", price.get("trend"))
        print("AVG1:", price.get("avg1"))
        print("AVG7:", price.get("avg7"))
        print("AVG30:", price.get("avg30"))

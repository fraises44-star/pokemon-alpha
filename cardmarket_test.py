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

print("RESULTS:", len(cards))

for number, card in enumerate(cards, start=1):
    print(
        number,
        "| NAME:", card.get("name"),
        "| CARDMARKET ID:", card.get("externalId"),
        "| EXPANSION:", card.get("expansionId")
    )

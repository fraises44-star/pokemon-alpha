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

print("TYPE:", type(data))
print("TOP LEVEL:", data.keys() if isinstance(data, dict) else "NOT A DICT")
print("DATA TYPE:", type(data.get("data")) if isinstance(data, dict) else "N/A")
print("DATA LENGTH:", len(data.get("data", [])) if isinstance(data, dict) else "N/A")
print("FIRST ITEM:", data.get("data", [None])[0] if isinstance(data, dict) and data.get("data") else "NO ITEMS")

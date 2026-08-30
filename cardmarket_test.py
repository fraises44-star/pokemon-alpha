import os
import requests

API_KEY = os.environ["TCG_CARDMARKET_API_KEY"]

url = "https://tcg-api-production-5148.up.railway.app/cards/pokemon/368851"

headers = {
    "X-API-Key": API_KEY,
}

response = requests.get(
    url,
    headers=headers,
    timeout=20,
)

print("STATUS:", response.status_code)
print("RESPONSE:")
print(response.text)

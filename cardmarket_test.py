import os
import requests

API_KEY = os.environ["CARDMARKETAPI_KEY"]

url = "https://cardmarketapi.com/api/v1/search"

headers = {
    "X-API-Key": API_KEY,
}

params = {
    "q": "SM158",
    "game": "pokemon",
}

response = requests.get(
    url,
    headers=headers,
    params=params,
    timeout=20,
)

print("STATUS:", response.status_code)
print("RESPONSE:")
print(response.text)

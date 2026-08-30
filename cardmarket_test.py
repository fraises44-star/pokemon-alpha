import os
import requests

API_KEY = os.environ["CARDMARKETAPI_KEY"]

url = "https://api.cardmarketapi.com/v1/search"

headers = {
    "Authorization": f"Bearer {API_KEY}",
}

params = {
    "query": "SM158",
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

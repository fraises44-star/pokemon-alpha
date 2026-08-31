import os
import requests


BASE_URL = "https://tcg-api-production-5148.up.railway.app"
API_KEY = os.environ["TCG_CARDMARKET_API_KEY"]


def fetch_cardmarket_prices(cardmarket_ids):

    if not cardmarket_ids:
        return []

    response = requests.post(
        f"{BASE_URL}/cards/batch",
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "game": "pokemon",
            "cardIds": [
                str(card_id)
                for card_id in cardmarket_ids
            ],
        },
        timeout=30,
    )

    print(
        "CARDMARKET PRICE API STATUS:",
        response.status_code,
    )

    if not response.ok:
    raise RuntimeError(
        "Cardmarket pricing request failed: "
        + response.text
    )

    return response.json()

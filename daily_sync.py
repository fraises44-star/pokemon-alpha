import os

from supabase import create_client
from eu_market import fetch_eu_sample


SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_ANON_KEY
)


def main():

    print("Starting Pokémon Alpha EU daily market sync...")

    cards, error = fetch_eu_sample(300)

    if error:
        raise RuntimeError(error)

    print(f"Retrieved {len(cards)} European cards.")

    card_rows = []

    price_rows = []

    for card in cards:

        card_rows.append({
            "id": card["id"],
            "name": card["name"],
            "set_name": card.get("set_name"),
            "rarity": card.get("rarity"),
            "image_url": card.get("image_url"),
        })

        prices = card.get("prices", {})

        price_rows.append({
            "card_id": card["id"],
            "trend_price_eur": prices.get("trend"),
            "low_price_eur": prices.get("low"),
            "avg_sell_eur": prices.get("avg"),
            "avg_1d_eur": prices.get("avg1"),
            "avg_7d_eur": prices.get("avg7"),
            "avg_30d_eur": prices.get("avg30"),
            "source": "cardmarket_via_tcgdex",
        })

    print("Updating card database...")

    supabase.table("cards").upsert(
        card_rows
    ).execute()

    print("Saving today's European price snapshots...")

    supabase.table("price_history").insert(
        price_rows
    ).execute()

    print(
        f"SUCCESS: stored {len(price_rows)} "
        "European price snapshots."
    )


if __name__ == "__main__":
    main()

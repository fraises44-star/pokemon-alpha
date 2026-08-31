import os

from supabase import create_client
from cardmarket_prices import fetch_cardmarket_prices


SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_ANON_KEY,
)


BATCH_SIZE = 10


def main():
    print("Starting InvestDex Cardmarket daily sync...")

    result = (
        supabase.table("cards")
        .select("id,name,cardmarket_id")
        .not_.is_("cardmarket_id", "null")
        .limit(1000)
        .execute()
    )

    cards = result.data or []

    print("MAPPED CARDS:", len(cards))

    if not cards:
        print("No mapped cards found.")
        return

    card_by_market_id = {
        str(card["cardmarket_id"]): card
        for card in cards
    }

    cardmarket_ids = list(
        card_by_market_id.keys()
    )

    price_rows = []

    for start in range(
        0,
        len(cardmarket_ids),
        BATCH_SIZE,
    ):
        batch_ids = cardmarket_ids[
            start:start + BATCH_SIZE
        ]

        print(
            "FETCHING BATCH:",
            start // BATCH_SIZE + 1,
            "| CARDS:",
            len(batch_ids),
        )

        prices = fetch_cardmarket_prices(
            batch_ids
        )

        for item in prices:
            external_id = str(
                item.get("externalId") or ""
            )

            card = card_by_market_id.get(
                external_id
            )

            if not card:
                print(
                    "SKIPPED UNKNOWN RETURNED ID:",
                    external_id,
                )
                continue

            price = item.get("price") or {}

            price_rows.append({
                "card_id": card["id"],
                "trend_price_eur": price.get("trend"),
                "low_price_eur": price.get("low"),
                "avg_sell_eur": price.get("sell"),
                "avg_1d_eur": price.get("avg1"),
                "avg_7d_eur": price.get("avg7"),
                "avg_30d_eur": price.get("avg30"),
                "source": (
                    "cardmarket_via_"
                    "tcg_cardmarket_api"
                ),
            })

    print(
        "PRICE ROWS TO INSERT:",
        len(price_rows),
    )

    if price_rows:
        supabase.table("price_history").insert(
            price_rows
        ).execute()

    print(
        "SUCCESS: stored",
        len(price_rows),
        "Cardmarket price snapshots.",
    )


if __name__ == "__main__":
    main()

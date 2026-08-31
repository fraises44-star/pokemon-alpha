import os
import re
import requests
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
MAPPING_API_KEY = os.environ["CARDMARKETAPI_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_ANON_KEY,
)

result = (
    supabase.table("cards")
    .select("id,name,set_name,cardmarket_id")
    .is_("cardmarket_id", "null")
    .limit(10)
    .execute()
)

cards = result.data or []

print("UNMAPPED CARDS:", len(cards))

for card in cards:
    card_id = card.get("id") or ""
    name = card.get("name") or ""
    set_name = card.get("set_name") or ""

    collector_part = card_id.split("-")[-1]

    match = re.match(
        r"([A-Za-z]+)(\d+)$",
        collector_part,
    )

    if match:
        search_code = (
            f"{match.group(1)} "
            f"{match.group(2)}"
        )
    else:
        search_code = collector_part

    if len(search_code.strip()) < 2:
        print("-----")
        print("SKIPPED:", card_id)
        print("REASON: Search code is too short")
        continue

    print("-----")
    print("DATABASE ID:", card_id)
    print("NAME:", name)
    print("SET:", set_name)
    print("SEARCH CODE:", search_code)

    response = requests.get(
        "https://cardmarketapi.com/api/v1/search",
        headers={
            "X-API-Key": MAPPING_API_KEY,
        },
        params={
            "q": search_code,
            "game": "pokemon",
        },
        timeout=20,
    )

    print("STATUS:", response.status_code)

   if response.status_code == 429:
    print("DAILY API LIMIT REACHED — STOPPING")
    break

   if response.status_code != 200:
    print("ERROR:", response.text)
    continue

    payload = response.json()
    candidates = payload.get("results") or []

    print("CANDIDATES:", len(candidates))

    verified = []

    for candidate in candidates:
        candidate_name = (
            candidate.get("name") or ""
        ).lower()

        candidate_set = (
            candidate.get("expansion") or ""
        ).lower()

        if (
            name.lower() in candidate_name
            and set_name.lower() == candidate_set
        ):
            verified.append(candidate)

    print("VERIFIED MATCHES:", len(verified))

    if len(verified) == 1:
        candidate = verified[0]

        cardmarket_id = str(candidate.get("id"))

        print(
            "VERIFIED:",
            cardmarket_id,
            "|",
            candidate.get("name"),
            "|",
            candidate.get("code"),
            "|",
            candidate.get("expansion"),
        )

        supabase.table("cards").update({
            "cardmarket_id": cardmarket_id
        }).eq(
            "id",
            card_id
        ).execute()

        print(
            "SAVED:",
            card_id,
            "->",
            cardmarket_id,
        )

    else:
        print(
            "SKIPPED:",
            card_id,
            "because verified match count is",
            len(verified),
        )

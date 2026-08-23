import streamlit as st
import requests
import pandas as pd

# ---------------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------------

st.set_page_config(
    page_title="Pokemon Alpha",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Pokemon Alpha")
st.subheader("Should I buy this Pokémon card today?")
st.caption("Early MVP — rankings are based on a simple PII scoring model.")


# ---------------------------------------------------------
# API SETUP
# ---------------------------------------------------------

API_URL = "https://api.pokemontcg.io/v2/cards"

try:
    API_KEY = st.secrets["POKEMONTCG_API_KEY"]
except Exception:
    API_KEY = None

HEADERS = {}

if API_KEY:
    HEADERS["X-Api-Key"] = API_KEY


# ---------------------------------------------------------
# POPULARITY MODEL
# ---------------------------------------------------------

popular_pokemon = {
    "Charizard": 100,
    "Pikachu": 98,
    "Gengar": 96,
    "Umbreon": 95,
    "Rayquaza": 94,
    "Lugia": 93,
    "Mew": 92,
    "Mewtwo": 91,
    "Giratina": 91,
    "Eevee": 90,
    "Sylveon": 90,
    "Arceus": 90,
    "Espeon": 89,
    "Greninja": 89,
    "Latias": 88,
    "Dragonite": 88,
    "Vaporeon": 88,
    "Latios": 87,
    "Leafeon": 87,
    "Glaceon": 87,
    "Jolteon": 87,
    "Flareon": 87,
    "Blastoise": 87,
    "Venusaur": 85,
    "Lucario": 84,
    "Snorlax": 84,
    "Mimikyu": 83,
    "Magikarp": 83,
    "Gardevoir": 82,
}


# ---------------------------------------------------------
# PII SCORING MODEL
# ---------------------------------------------------------

def score_card(card):

    name = card.get("name", "")
    rarity = card.get("rarity", "") or ""

    prices = card.get("cardmarket", {}).get("prices", {})

    trend_price = prices.get("trendPrice") or 0
    low_price = prices.get("lowPrice") or 0
    average_sell = prices.get("averageSellPrice") or 0

    # POPULARITY
    popularity_score = 50

    for pokemon, score in popular_pokemon.items():
        if pokemon.lower() in name.lower():
            popularity_score = score
            break

    # RARITY
    rarity_score = 45
    rarity_lower = rarity.lower()

    if "special illustration" in rarity_lower:
        rarity_score = 100
    elif "illustration rare" in rarity_lower:
        rarity_score = 92
    elif "hyper rare" in rarity_lower:
        rarity_score = 95
    elif "rare ultra" in rarity_lower:
        rarity_score = 90
    elif "secret" in rarity_lower:
        rarity_score = 88
    elif "rare holo" in rarity_lower:
        rarity_score = 72
    elif "rare" in rarity_lower:
        rarity_score = 60

    # PRICE STRENGTH
    if trend_price >= 150:
        price_score = 95
    elif trend_price >= 75:
        price_score = 88
    elif trend_price >= 30:
        price_score = 80
    elif trend_price >= 15:
        price_score = 72
    elif trend_price >= 5:
        price_score = 65
    elif trend_price > 0:
        price_score = 55
    else:
        price_score = 30

    # VALUE SCORE
    value_score = 50

    if low_price and trend_price:

        discount = (
            (trend_price - low_price)
            / trend_price
        ) * 100

        if discount >= 30:
            value_score = 100
        elif discount >= 20:
            value_score = 90
        elif discount >= 15:
            value_score = 82
        elif discount >= 10:
            value_score = 75
        elif discount >= 5:
            value_score = 65
        else:
            value_score = 50

    # MARKET STRENGTH
    market_strength = 50

    if average_sell and trend_price:

        difference = abs(
            average_sell - trend_price
        ) / trend_price

        if difference <= 0.05:
            market_strength = 90
        elif difference <= 0.10:
            market_strength = 80
        elif difference <= 0.20:
            market_strength = 65
        else:
            market_strength = 45

    # FINAL PII
    investment_score = round(
        popularity_score * 0.30
        + rarity_score * 0.25
        + price_score * 0.15
        + value_score * 0.20
        + market_strength * 0.10
    )

    investment_score = min(
        max(investment_score, 0),
        100
    )

    return {
        "PII": investment_score,
        "Popularity": popularity_score,
        "RarityScore": rarity_score,
        "PriceScore": price_score,
        "ValueScore": value_score,
        "MarketStrength": market_strength
    }


# ---------------------------------------------------------
# RECOMMENDATION
# ---------------------------------------------------------

def recommendation(score):

    if score >= 90:
        return "🔥 Strong Buy Candidate"
    elif score >= 82:
        return "🟢 Strong Watch"
    elif score >= 74:
        return "👀 Interesting"
    elif score >= 65:
        return "🟡 Speculative"
    else:
        return "⚠️ Weak Signal"


# ---------------------------------------------------------
# PRICE TIERS
# ---------------------------------------------------------

price_tiers = [
    (0, 5),
    (5, 10),
    (10, 15),
    (15, 20),
    (20, 30),
    (30, 50),
    (50, 75),
    (75, 100),
    (100, 150),
    (150, 250),
]


# ---------------------------------------------------------
# DOWNLOAD CARD POOL
# ---------------------------------------------------------

@st.cache_data(ttl=3600)
def get_card_pool():

    params = {
        "pageSize": 100
    }

    for attempt in range(3):

        try:

            response = requests.get(
                API_URL,
                headers=HEADERS,
                params=params,
                timeout=60
            )

            if response.status_code == 200:

                return {
                    "success": True,
                    "status": 200,
                    "error": None,
                    "cards": response.json().get("data", [])
                }

            return {
                "success": False,
                "status": response.status_code,
                "error": response.text[:500],
                "cards": []
            }

        except requests.exceptions.Timeout:

            if attempt < 2:
                continue

            return {
                "success": False,
                "status": None,
                "error": "Pokémon TCG API timed out after 3 attempts.",
                "cards": []
            }

        except requests.RequestException as e:

            return {
                "success": False,
                "status": None,
                "error": str(e),
                "cards": []
            }


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

with st.spinner("Loading Pokémon market data..."):

    pool_result = get_card_pool()


if not pool_result["success"]:

    st.error(
        f"API error: {pool_result['status']} — {pool_result['error']}"
    )

    st.stop()


# THIS IS THE LINE THAT WAS MISSING
cards = pool_result["cards"]


# ---------------------------------------------------------
# PRICE TIER DASHBOARD
# ---------------------------------------------------------

st.divider()

st.markdown("## 🏆 Best Investment Candidate by Price Tier")

st.caption(
    "Each bracket is separate, so the same cheap card cannot win every tier."
)

tier_results = []


for min_price, max_price in price_tiers:

    candidates = []

    for card in cards:

        prices = card.get(
            "cardmarket",
            {}
        ).get(
            "prices",
            {}
        )

        trend_price = prices.get("trendPrice")
        low_price = prices.get("lowPrice")
        average_sell = prices.get("averageSellPrice")

        if trend_price is None:
            continue

        if min_price == 0:
            inside_range = 0 < trend_price < max_price
        else:
            inside_range = min_price <= trend_price < max_price

        if not inside_range:
            continue

        scores = score_card(card)

        candidates.append({
            "Card": card.get("name"),
            "Set": card.get("set", {}).get("name"),
            "Rarity": card.get("rarity"),
            "Price": trend_price,
            "Low": low_price,
            "Average": average_sell,
            "PII": scores["PII"],
            "Popularity": scores["Popularity"],
            "Rarity Score": scores["RarityScore"],
            "Value Score": scores["ValueScore"],
            "Market Strength": scores["MarketStrength"],
            "Image": card.get("images", {}).get("small"),
            "Min Price": min_price,
            "Max Price": max_price
        })

    if candidates:

        candidate_df = pd.DataFrame(candidates)

        candidate_df = candidate_df.sort_values(
            [
                "PII",
                "Popularity",
                "Value Score"
            ],
            ascending=[
                False,
                False,
                False
            ]
        )

        best_card = candidate_df.iloc[0]

        tier_results.append(best_card)


# ---------------------------------------------------------
# SHOW FIRST 5 TIERS
# ---------------------------------------------------------

if tier_results:

    first_row = st.columns(5)

    for column, card in zip(
        first_row,
        tier_results[:5]
    ):

        with column:

            st.markdown(
                f"### €{int(card['Min Price'])}–€{int(card['Max Price'])}"
            )

            if card["Image"]:
                st.image(
                    card["Image"],
                    use_container_width=True
                )

            st.markdown(
                f"**{card['Card']}**"
            )

            st.caption(
                card["Set"]
            )

            st.metric(
                "PII Score",
                f"{int(card['PII'])}/100"
            )

            st.write(
                recommendation(card["PII"])
            )

            st.write(
                f"Market: **€{card['Price']:.2f}**"
            )

            if pd.notna(card["Low"]):

                st.write(
                    f"Low: €{card['Low']:.2f}"
                )


    st.divider()


    # -----------------------------------------------------
    # SHOW NEXT 5 TIERS
    # -----------------------------------------------------

    second_row = st.columns(5)

    for column, card in zip(
        second_row,
        tier_results[5:]
    ):

        with column:

            st.markdown(
                f"### €{int(card['Min Price'])}–€{int(card['Max Price'])}"
            )

            if card["Image"]:
                st.image(
                    card["Image"],
                    use_container_width=True
                )

            st.markdown(
                f"**{card['Card']}**"
            )

            st.caption(
                card["Set"]
            )

            st.metric(
                "PII Score",
                f"{int(card['PII'])}/100"
            )

            st.write(
                recommendation(card["PII"])
            )

            st.write(
                f"Market: **€{card['Price']:.2f}**"
            )

            if pd.notna(card["Low"]):

                st.write(
                    f"Low: €{card['Low']:.2f}"
                )


else:

    st.warning(
        "No cards in the current API pool matched the price tiers."
    )


# ---------------------------------------------------------
# TIER TABLE
# ---------------------------------------------------------

if tier_results:

    st.divider()

    st.markdown("## 📊 Today's Tier Rankings")

    tier_table = pd.DataFrame(tier_results)

    tier_table["Price Tier"] = (
        "€"
        + tier_table["Min Price"].astype(int).astype(str)
        + "–€"
        + tier_table["Max Price"].astype(int).astype(str)
    )

    display_columns = [
        "Price Tier",
        "Card",
        "Set",
        "Rarity",
        "Price",
        "Low",
        "PII",
        "Popularity",
        "Rarity Score",
        "Value Score",
        "Market Strength"
    ]

    st.dataframe(
        tier_table[display_columns],
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------------------------
# SEARCH
# ---------------------------------------------------------

st.divider()

st.markdown("## 🔎 Search Any Pokémon Card")

search = st.text_input(
    "Search by Pokémon name",
    value="Gengar"
)


if search:

    params = {
        "q": f'name:"{search}*"',
        "pageSize": 100
    }

    try:

        response = requests.get(
            API_URL,
            headers=HEADERS,
            params=params,
            timeout=60
        )

        if response.status_code != 200:

            st.error(
                f"Search API error: "
                f"{response.status_code} — "
                f"{response.text[:500]}"
            )

        else:

            search_cards = response.json().get(
                "data",
                []
            )

            results = []

            for card in search_cards:

                prices = card.get(
                    "cardmarket",
                    {}
                ).get(
                    "prices",
                    {}
                )

                trend_price = prices.get(
                    "trendPrice"
                )

                if trend_price is None:
                    continue

                scores = score_card(card)

                results.append({
                    "Card": card.get("name"),
                    "Set": card.get("set", {}).get("name"),
                    "Rarity": card.get("rarity"),
                    "Trend Price €": trend_price,
                    "Low Price €": prices.get("lowPrice"),
                    "Average Sell €": prices.get("averageSellPrice"),
                    "PII": scores["PII"],
                    "Popularity": scores["Popularity"],
                    "Rarity Score": scores["RarityScore"],
                    "Value Score": scores["ValueScore"],
                    "Market Strength": scores["MarketStrength"],
                    "Image": card.get("images", {}).get("small")
                })

            if not results:

                st.warning(
                    "No cards with Cardmarket pricing were found."
                )

            else:

                df = pd.DataFrame(results)

                df = df.sort_values(
                    "PII",
                    ascending=False
                ).reset_index(drop=True)

                top = df.iloc[0]

                st.markdown(
                    "### 🥇 Best Search Result"
                )

                image_col, info_col = st.columns(
                    [1, 3]
                )

                with image_col:

                    if top["Image"]:

                        st.image(
                            top["Image"],
                            use_container_width=True
                        )

                with info_col:

                    st.markdown(
                        f"## {top['Card']}"
                    )

                    st.write(
                        f"**Set:** {top['Set']}"
                    )

                    st.write(
                        f"**Rarity:** {top['Rarity']}"
                    )

                    st.metric(
                        "PII Score",
                        f"{int(top['PII'])}/100"
                    )

                    st.write(
                        recommendation(top["PII"])
                    )

                    metric1, metric2, metric3 = st.columns(3)

                    metric1.metric(
                        "Trend Price",
                        f"€{top['Trend Price €']:.2f}"
                    )

                    if pd.notna(top["Low Price €"]):

                        metric2.metric(
                            "Low Price",
                            f"€{top['Low Price €']:.2f}"
                        )

                    if pd.notna(top["Average Sell €"]):

                        metric3.metric(
                            "Average Sell",
                            f"€{top['Average Sell €']:.2f}"
                        )

                st.markdown(
                    "### 📊 All Matching Cards"
                )

                st.dataframe(
                    df.drop(columns=["Image"]),
                    use_container_width=True,
                    hide_index=True
                )

    except requests.exceptions.Timeout:

        st.error(
            "Search timed out. Please try again."
        )

    except requests.RequestException as e:

        st.error(
            f"Could not connect to the Pokémon API: {e}"
        )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "Pokemon Alpha MVP • PII scores are experimental and are not financial advice."
)

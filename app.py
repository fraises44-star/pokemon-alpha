import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Pokemon Alpha", layout="wide")

st.title("📈 Pokemon Alpha")
st.subheader("Should I buy this Pokémon card today?")

API_URL = "https://api.pokemontcg.io/v2/cards"

popular_pokemon = {
    "Charizard": 100,
    "Pikachu": 98,
    "Gengar": 96,
    "Umbreon": 95,
    "Rayquaza": 94,
    "Lugia": 93,
    "Mew": 92,
    "Mewtwo": 91,
    "Eevee": 90,
    "Latias": 88,
    "Latios": 87,
}

def score_card(card):
    name = card.get("name", "")
    rarity = card.get("rarity", "")
    prices = card.get("cardmarket", {}).get("prices", {})

    trend = prices.get("trendPrice") or 0
    low = prices.get("lowPrice") or 0

    popularity = 50

    for pokemon, score in popular_pokemon.items():
        if pokemon.lower() in name.lower():
            popularity = score

    rarity_score = 50

    if rarity:
        if "Secret" in rarity or "Rare Ultra" in rarity:
            rarity_score = 90
        elif "Rare Holo" in rarity:
            rarity_score = 75
        elif "Rare" in rarity:
            rarity_score = 60

    price_score = min(trend * 2, 100) if trend else 40

    upside_score = 50

    if low and trend and low < trend:
        upside_score = min(
            ((trend - low) / trend) * 100 + 50,
            100
        )

    investment_score = round(
        popularity * 0.35 +
        rarity_score * 0.25 +
        price_score * 0.20 +
        upside_score * 0.20
    )

    return investment_score


@st.cache_data(ttl=3600)
def get_cards_under_20():

    params = {
        "q": "cardmarket.prices.trendPrice:[2 TO 20]",
        "pageSize": 250
    }

    response = requests.get(API_URL, params=params)

    if response.status_code != 200:
        return []

    return response.json().get("data", [])


st.markdown("## 🔥 Top 5 Cards Under €20")

cards = get_cards_under_20()

results = []

for card in cards:

    score = score_card(card)

    prices = card.get("cardmarket", {}).get("prices", {})

    results.append({
        "Card": card.get("name"),
        "Set": card.get("set", {}).get("name"),
        "Price": prices.get("trendPrice"),
        "Low": prices.get("lowPrice"),
        "PII": score,
        "Image": card.get("images", {}).get("small")
    })


if results:

    df_top = pd.DataFrame(results)

    df_top = df_top.sort_values(
        "PII",
        ascending=False
    ).head(5)

    columns = st.columns(5)

    for column, (_, card) in zip(columns, df_top.iterrows()):

        with column:

            st.image(card["Image"])

            st.markdown(
                f"### {card['Card']}"
            )

            st.write(card["Set"])

            st.metric(
                "PII Score",
                card["PII"]
            )

            st.write(
                f"€{card['Price']}"
            )

else:

    st.warning(
        "Could not retrieve cards."
    )


st.divider()


st.markdown("## 🔎 Search Cards")

search = st.text_input(
    "Search card",
    value="Gengar"
)

if search:

    params = {
        "q": f'name:"{search}*"',
        "pageSize": 20
    }

    response = requests.get(
        API_URL,
        params=params
    )

    if response.status_code != 200:

        st.error(
            "API error. Try again later."
        )

    else:

        cards = response.json().get(
            "data",
            []
        )

        results = []

        for card in cards:

            score = score_card(card)

            prices = card.get(
                "cardmarket",
                {}
            ).get(
                "prices",
                {}
            )

            results.append({

                "Card":
                card.get("name"),

                "Set":
                card.get("set", {}).get("name"),

                "Rarity":
                card.get("rarity"),

                "Trend Price €":
                prices.get("trendPrice"),

                "Low Price €":
                prices.get("lowPrice"),

                "PII Score":
                score,

                "Image":
                card.get("images", {}).get("small")

            })


        df = pd.DataFrame(results)

        if df.empty:

            st.warning(
                "No cards found."
            )

        else:

            df = df.sort_values(
                "PII Score",
                ascending=False
            )

            top = df.iloc[0]

            col1, col2 = st.columns(
                [1,3]
            )

            with col1:

                st.image(
                    top["Image"]
                )

            with col2:

                st.metric(
                    "PII Score",
                    f'{top["PII Score"]}/100'
                )

                st.write(
                    f'**Card:** {top["Card"]}'
                )

                st.write(
                    f'**Set:** {top["Set"]}'
                )

                st.write(
                    f'**Trend Price:** €{top["Trend Price €"]}'
                )

                st.write(
                    f'**Low Price:** €{top["Low Price €"]}'
                )


            st.dataframe(
                df.drop(
                    columns=["Image"]
                ),

                use_container_width=True
            )

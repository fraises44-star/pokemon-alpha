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
    cardmarket = card.get("cardmarket", {})
    prices = cardmarket.get("prices", {})

    avg_sell = prices.get("averageSellPrice") or 0
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
        upside_score = min(((trend - low) / trend) * 100 + 50, 100)

    investment_score = round(
        popularity * 0.35 +
        rarity_score * 0.25 +
        price_score * 0.20 +
        upside_score * 0.20
    )

    return investment_score, popularity, rarity_score, price_score, upside_score

search = st.text_input("Search card", value="Gengar")

if search:
    params = {
        "q": f'name:"{search}*"',
        "pageSize": 20,
        "orderBy": "-cardmarket.prices.trendPrice"
    }

    response = requests.get(API_URL, params=params)

    if response.status_code != 200:
        st.error("API error. Try again later.")
    else:
        cards = response.json().get("data", [])

        results = []

        for card in cards:
            score, popularity, rarity_score, price_score, upside_score = score_card(card)

            prices = card.get("cardmarket", {}).get("prices", {})
            set_data = card.get("set", {})

            results.append({
                "Card": card.get("name"),
                "Set": set_data.get("name"),
                "Rarity": card.get("rarity"),
                "Trend Price €": prices.get("trendPrice"),
                "Avg Sell €": prices.get("averageSellPrice"),
                "Low Price €": prices.get("lowPrice"),
                "PII Score": score,
                "Popularity": popularity,
                "Rarity Score": rarity_score,
                "Image": card.get("images", {}).get("small")
            })

        df = pd.DataFrame(results)

        if df.empty:
            st.warning("No cards found.")
        else:
            df = df.sort_values("PII Score", ascending=False)

            top = df.iloc[0]

            st.markdown("## 🔥 Best card found")
            col1, col2 = st.columns([1, 3])

            with col1:
                st.image(top["Image"])

            with col2:
                st.metric("PII Score", f'{top["PII Score"]}/100')
                st.write(f'**Card:** {top["Card"]}')
                st.write(f'**Set:** {top["Set"]}')
                st.write(f'**Rarity:** {top["Rarity"]}')
                st.write(f'**Trend Price:** €{top["Trend Price €"]}')
                st.write(f'**Low Price:** €{top["Low Price €"]}')

                if top["PII Score"] >= 85:
                    st.success("Signal: Strong watch / possible buy")
                elif top["PII Score"] >= 70:
                    st.info("Signal: Interesting")
                else:
                    st.warning("Signal: Weak / risky")

            st.markdown("## 📊 Search results")
            st.dataframe(
                df.drop(columns=["Image"]),
                use_container_width=True
            )

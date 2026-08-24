import streamlit as st
import pandas as pd
from datetime import datetime

from data_provider import (
    search_cards,
    get_market_universe,
    demo_universe,
    get_cardmarket_snapshot,
)
from scoring import score_card, recommendation_label, build_thesis, price_band
from storage import init_store, add_watchlist, get_watchlist, remove_watchlist, add_portfolio, get_portfolio
from ui import inject_css, render_score_gauge, render_metric_card

st.set_page_config(
    page_title="Pokémon Alpha",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
init_store()

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("# 📈 Pokémon Alpha")
    st.caption("Investment intelligence for Pokémon cards")
    page = st.radio(
        "Navigate",
        ["Dashboard", "Screener", "Card Analyzer", "Portfolio", "Watchlist", "Methodology"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Prototype data sources")
    st.markdown("**Raw market:** Cardmarket / TCGdex")
    st.markdown("**US market:** TCGplayer / TCGdex")
    st.markdown("**Graded:** connector-ready")
    st.markdown("**Population:** connector-ready")
    st.divider()
    st.caption("PII scores are experimental research signals, not financial advice.")

# ---------------- Helpers ----------------
@st.cache_data(ttl=3600, show_spinner=False)
def load_universe():
    live = get_market_universe(limit=500)
    if live:
        return live, "Live"
    return demo_universe(), "Demo fallback"

def dataframe_from_cards(cards):
    rows = []
    for card in cards:
        score = score_card(card)
        cm = get_cardmarket_snapshot(card)
        rows.append({
            "ID": card.get("id"),
            "Card": card.get("name"),
            "Set": (card.get("set") or {}).get("name", ""),
            "Rarity": card.get("rarity", ""),
            "Price €": cm.get("trend"),
            "Avg 1d €": cm.get("avg1"),
            "Avg 7d €": cm.get("avg7"),
            "Avg 30d €": cm.get("avg30"),
            "30d Momentum %": score["momentum_30d"],
            "PII": score["pii"],
            "Signal": recommendation_label(score["pii"]),
            "Confidence": score["confidence"],
            "Popularity": score["popularity"],
            "Value": score["value"],
            "Rarity Score": score["rarity"],
            "Liquidity Proxy": score["liquidity"],
            "Image": card.get("image") or (card.get("images") or {}).get("small"),
            "_card": card,
        })
    return pd.DataFrame(rows)

cards, source_mode = load_universe()
df = dataframe_from_cards(cards)

# ---------------- Dashboard ----------------
if page == "Dashboard":
    st.title("Pokémon Alpha")
    st.markdown("### Find the cards with the strongest **risk-adjusted investment signals**.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Cards evaluated", f"{len(df):,}", source_mode)
    with c2:
        strong = int((df["PII"] >= 82).sum()) if not df.empty else 0
        render_metric_card("Strong signals", strong, "PII ≥ 82")
    with c3:
        median = int(df["PII"].median()) if not df.empty else 0
        render_metric_card("Median PII", median, "Current universe")
    with c4:
        updated = datetime.now().strftime("%H:%M")
        render_metric_card("Last refresh", updated, "Cache: 60 min")

    st.markdown("## 🏆 Best candidate by price band")
    bands = [(0,5),(5,10),(10,15),(15,20),(20,30),(30,50),(50,75),(75,100),(100,150),(150,250)]
    winners = []
    for lo, hi in bands:
        band_df = df[(df["Price €"].notna()) & (df["Price €"] >= lo) & (df["Price €"] < hi)].copy()
        if not band_df.empty:
            winners.append((lo, hi, band_df.sort_values(["PII","Confidence"], ascending=False).iloc[0]))

    for start in (0,5):
        cols = st.columns(5)
        for col, item in zip(cols, winners[start:start+5]):
            lo, hi, row = item
            with col:
                st.markdown(f"#### €{lo}–€{hi}")
                if row["Image"]:
                    st.image(row["Image"], use_container_width=True)
                st.markdown(f"**{row['Card']}**")
                st.caption(row["Set"])
                st.metric("PII", f"{int(row['PII'])}/100")
                if pd.notna(row["Price €"]):
                    st.markdown(f"**€{row['Price €']:.2f}**")
                st.caption(recommendation_label(row["PII"]))

    st.markdown("## 🚀 Opportunity leaderboard")
    leaderboard = df[df["Price €"].notna()].sort_values(["PII","30d Momentum %","Confidence"], ascending=False).head(15)
    st.dataframe(
        leaderboard[["Card","Set","Price €","PII","Signal","30d Momentum %","Confidence"]],
        use_container_width=True, hide_index=True
    )

    st.markdown("## 📉 Potential value entries")
    value = df[df["Price €"].notna()].sort_values(["Value","PII"], ascending=False).head(10)
    st.dataframe(
        value[["Card","Set","Price €","Value","PII","30d Momentum %"]],
        use_container_width=True, hide_index=True
    )

# ---------------- Screener ----------------
elif page == "Screener":
    st.title("Investment Screener")
    st.caption("Filter the market rather than browsing one Pokémon at a time.")

    fc1, fc2, fc3, fc4 = st.columns(4)
    min_price = fc1.number_input("Min €", min_value=0.0, value=0.0, step=5.0)
    max_price = fc2.number_input("Max €", min_value=1.0, value=250.0, step=10.0)
    min_pii = fc3.slider("Minimum PII", 0, 100, 60)
    min_momentum = fc4.slider("Min 30d momentum %", -50, 100, -10)

    filtered = df[
        (df["Price €"].notna()) &
        (df["Price €"] >= min_price) &
        (df["Price €"] <= max_price) &
        (df["PII"] >= min_pii) &
        (df["30d Momentum %"] >= min_momentum)
    ].copy()

    sort_by = st.selectbox("Sort by", ["PII", "30d Momentum %", "Value", "Confidence", "Price €"])
    ascending = sort_by == "Price €"
    filtered = filtered.sort_values(sort_by, ascending=ascending)

    st.metric("Matches", len(filtered))
    st.dataframe(
        filtered[["Card","Set","Rarity","Price €","Avg 7d €","Avg 30d €","30d Momentum %","PII","Signal","Confidence"]],
        use_container_width=True, hide_index=True
    )

# ---------------- Analyzer ----------------
elif page == "Card Analyzer":
    st.title("Card Analyzer")
    query = st.text_input("Search card or Pokémon", placeholder="e.g. Gengar, Umbreon, Charizard")

    if query:
        with st.spinner("Searching market data..."):
            results = search_cards(query, limit=50)

        if not results:
            st.warning("No live results returned. Try a broader search.")
        else:
            labels = [
                f"{c.get('name')} — {(c.get('set') or {}).get('name','')} — {c.get('id','')}"
                for c in results
            ]
            idx = st.selectbox("Select card", range(len(results)), format_func=lambda i: labels[i])
            card = results[idx]
            score = score_card(card)
            cm = get_cardmarket_snapshot(card)

            left, right = st.columns([1, 2.4])
            with left:
                img = card.get("image") or (card.get("images") or {}).get("large") or (card.get("images") or {}).get("small")
                if img:
                    st.image(img, use_container_width=True)
                if st.button("⭐ Add to watchlist", use_container_width=True):
                    add_watchlist(card)
                    st.success("Added.")
                if st.button("➕ Add to portfolio", use_container_width=True):
                    add_portfolio(card, quantity=1, cost=cm.get("trend") or 0)
                    st.success("Added with quantity 1.")

            with right:
                st.markdown(f"# {card.get('name')}")
                st.caption(f"{(card.get('set') or {}).get('name','')} • {card.get('rarity','')} • {card.get('id','')}")
                render_score_gauge(score["pii"], recommendation_label(score["pii"]))

                m1,m2,m3,m4 = st.columns(4)
                m1.metric("Trend", f"€{cm['trend']:.2f}" if cm.get("trend") is not None else "—")
                m2.metric("1-day avg", f"€{cm['avg1']:.2f}" if cm.get("avg1") is not None else "—")
                m3.metric("7-day avg", f"€{cm['avg7']:.2f}" if cm.get("avg7") is not None else "—")
                m4.metric("30-day avg", f"€{cm['avg30']:.2f}" if cm.get("avg30") is not None else "—")

                st.markdown("### Investment thesis")
                for line in build_thesis(card, score):
                    st.markdown(f"- {line}")

                st.markdown("### PII breakdown")
                breakdown = pd.DataFrame({
                    "Factor": ["Momentum","Value","Rarity","Popularity","Liquidity proxy","Risk quality","Data confidence"],
                    "Score": [
                        score["momentum"], score["value"], score["rarity"], score["popularity"],
                        score["liquidity"], score["risk_quality"], score["confidence"]
                    ]
                })
                st.bar_chart(breakdown.set_index("Factor"))

            st.markdown("## Graded market")
            st.info(
                "The UI is ready for PSA, BGS/Beckett, CGC, TAG, SGC and ACE sold comps. "
                "For a commercial launch, this should only be switched on when we have a licensed/approved data feed."
            )
            graded = pd.read_csv("data/graded_market.csv")
            graded = graded[graded["card_id"] == card.get("id")]
            if graded.empty:
                st.caption("No graded records loaded for this card yet.")
            else:
                st.dataframe(graded, use_container_width=True, hide_index=True)

            st.markdown("## Population & supply")
            pops = pd.read_csv("data/populations.csv")
            pops = pops[pops["card_id"] == card.get("id")]
            if pops.empty:
                st.caption("No population records loaded for this card yet.")
            else:
                st.dataframe(pops, use_container_width=True, hide_index=True)

# ---------------- Portfolio ----------------
elif page == "Portfolio":
    st.title("Portfolio")
    portfolio = get_portfolio()
    if not portfolio:
        st.info("Add cards from Card Analyzer to start your portfolio.")
    else:
        pdf = pd.DataFrame(portfolio)
        invested = (pdf["quantity"] * pdf["cost_basis"]).sum()
        st.metric("Cost basis", f"€{invested:,.2f}")
        st.dataframe(pdf, use_container_width=True, hide_index=True)
        st.caption("Prototype storage is local to the running app. Supabase authentication/storage is the next production step.")

# ---------------- Watchlist ----------------
elif page == "Watchlist":
    st.title("Watchlist")
    wl = get_watchlist()
    if not wl:
        st.info("Add cards from Card Analyzer.")
    else:
        for item in wl:
            c1,c2,c3 = st.columns([1,5,1])
            with c1:
                if item.get("image"):
                    st.image(item["image"], width=90)
            with c2:
                st.markdown(f"**{item['name']}**")
                st.caption(f"{item.get('set_name','')} • {item['card_id']}")
            with c3:
                if st.button("Remove", key=f"rm-{item['card_id']}"):
                    remove_watchlist(item["card_id"])
                    st.rerun()

# ---------------- Methodology ----------------
else:
    st.title("PII Methodology")
    st.markdown("""
The **Pokémon Investment Index (PII)** is intentionally explainable. It does not predict guaranteed returns.

Current prototype weighting:

- **25% Momentum** — compares current/short-term price signals with the 30-day average.
- **20% Value** — rewards cards trading below recent averages without blindly rewarding collapsing prices.
- **15% Rarity / collectability** — illustration rares, special illustration rares, secrets and premium variants.
- **15% Character demand** — a deliberately capped demand prior; it helps Charizard, Pikachu, Gengar, Eeveelutions etc., but cannot determine the result by itself.
- **10% Liquidity proxy** — availability of multiple market observations and consistency between them.
- **10% Risk quality** — volatility and data-quality penalties.
- **5% Data confidence** — how complete the market record is.

The production model should add **actual sold-volume/liquidity, graded sold comps, population growth, set-print/reprint risk, and longer proprietary price history**.
""")
    st.warning(
        "Important commercial point: eBay Marketplace Insights/sold-data access is restricted, so a consumer subscription product "
        "should use an approved eBay relationship or a licensed third-party graded-data provider rather than unauthorized scraping."
    )

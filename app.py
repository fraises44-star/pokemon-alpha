import streamlit as st
import pandas as pd

from supabase_db import (
    connection_check, load_market, load_price_history, load_population,
    upsert_cards, insert_price_snapshots
)
from eu_market import fetch_eu_sample
from scoring import score, signal, thesis
from ui import css, card_metric, score_box

st.set_page_config(
    page_title="Pokémon Alpha Europe",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
css()

with st.sidebar:
    st.markdown("# 📈 Pokémon Alpha")
    st.caption("European Pokémon investment intelligence")
    page = st.radio(
        "Navigation",
        ["Dashboard", "Screener", "Card Analyzer", "Market Sync", "Methodology"],
        label_visibility="collapsed"
    )
    st.divider()
    ok, status = connection_check()
    if ok:
        st.success("Supabase connected")
    else:
        st.error("Supabase not connected")
    st.markdown("**Market:** 🇪🇺 Europe")
    st.markdown("**Raw pricing:** Cardmarket")
    st.markdown("**Currency:** EUR")
    st.markdown("**US market:** Not enabled")
    st.markdown("**Graded:** Coming via licensed feed")
    st.markdown("**Population:** Database ready")
    st.divider()
    st.caption("Experimental research signals, not financial advice.")

market = load_market()
df = pd.DataFrame()

if market:
    rows = []
    for r in market:
        s = score(r)
        rows.append({
            **r,
            "PII": s["pii"],
            "30d Momentum %": s["momentum30"],
            "Value": s["value"],
            "Popularity": s["popularity"],
            "Rarity Score": s["rarity_score"],
            "Liquidity Proxy": s["liquidity"],
            "Risk Quality": s["risk_quality"],
            "Confidence": s["confidence"],
            "Signal": signal(s["pii"]),
        })
    df = pd.DataFrame(rows)

if page == "Dashboard":
    st.title("Pokémon Alpha 🇪🇺")
    st.markdown("### European Pokémon card investment intelligence")
    st.caption("This dashboard reads from your Supabase database, so it does not depend on a live API request every time somebody visits.")

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        card_metric("Cards in database", f"{len(df):,}", "European universe")
    with c2:
        strong = int((df["PII"] >= 80).sum()) if not df.empty else 0
        card_metric("Strong signals", strong, "PII ≥ 80")
    with c3:
        median = int(df["PII"].median()) if not df.empty else 0
        card_metric("Median PII", median, "Current database")
    with c4:
        card_metric("Market", "EUR", "Cardmarket")

    if df.empty:
        st.info("Your database is connected but currently empty.")
        st.markdown("""
### First data import

Open **Market Sync** in the left menu and press **Sync EU market now**.

That will:
1. retrieve a starter universe of European cards;
2. store card metadata in Supabase;
3. store today's Cardmarket snapshot;
4. make Dashboard, Screener and Card Analyzer work from your own database.
""")
    else:
        st.markdown("## 🏆 Best candidate by European price band")
        bands=[(0,5),(5,10),(10,15),(15,20),(20,30),(30,50),(50,75),(75,100),(100,150),(150,250)]
        winners=[]
        for lo,hi in bands:
            b=df[(df["trend"].notna()) & (df["trend"]>=lo) & (df["trend"]<hi)]
            if not b.empty:
                winners.append((lo,hi,b.sort_values(["PII","Confidence"],ascending=False).iloc[0]))

        for start in (0,5):
            cols=st.columns(5)
            for col,item in zip(cols,winners[start:start+5]):
                lo,hi,row=item
                with col:
                    st.markdown(f"#### €{lo}–€{hi}")
                    if row.get("image_url"):
                        st.markdown(
    f'<img src="{row["image_url"]}" style="width:100%;border-radius:14px;">',
    unsafe_allow_html=True
)
                    st.markdown(f"**{row['name']}**")
                    st.caption(row.get("set_name",""))
                    st.metric("PII",f"{int(row['PII'])}/100")
                    st.markdown(f"**€{row['trend']:.2f}**")
                    st.caption(row["Signal"])

        st.markdown("## 🚀 European opportunity leaderboard")
        lead=df[df["trend"].notna()].sort_values(["PII","Confidence"],ascending=False).head(20)
        st.dataframe(
            lead[["name","set_name","rarity","trend","avg7","avg30","30d Momentum %","PII","Signal","Confidence"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "trend": st.column_config.NumberColumn("Trend €", format="€%.2f"),
                "avg7": st.column_config.NumberColumn("7d avg €", format="€%.2f"),
                "avg30": st.column_config.NumberColumn("30d avg €", format="€%.2f"),
            }
        )

elif page == "Screener":
    st.title("EU Investment Screener")
    if df.empty:
        st.info("Run Market Sync first.")
    else:
        a,b,c,d=st.columns(4)
        min_price=a.number_input("Minimum €",0.0,10000.0,0.0,5.0)
        max_price=b.number_input("Maximum €",0.0,10000.0,250.0,10.0)
        min_pii=c.slider("Minimum PII",0,100,60)
        min_mom=d.slider("Minimum 30d momentum %",-75,150,-10)

        f=df[
            (df["trend"].notna()) &
            (df["trend"]>=min_price) &
            (df["trend"]<=max_price) &
            (df["PII"]>=min_pii) &
            (df["30d Momentum %"]>=min_mom)
        ].copy()

        sort=st.selectbox("Sort by",["PII","30d Momentum %","Value","Confidence","trend"])
        f=f.sort_values(sort,ascending=(sort=="trend"))
        st.metric("Matching European cards",len(f))
        st.dataframe(
            f[["name","set_name","rarity","trend","avg7","avg30","30d Momentum %","Value","PII","Signal","Confidence"]],
            use_container_width=True,hide_index=True
        )

elif page == "Card Analyzer":
    st.title("Card Analyzer 🇪🇺")
    if df.empty:
        st.info("Run Market Sync first.")
    else:
        q=st.text_input("Search your European card database",placeholder="Gengar")
        filtered=df
        if q:
            filtered=df[df["name"].str.contains(q,case=False,na=False)]

        if filtered.empty:
            st.warning("No matching card in the current synced universe.")
        else:
            options=filtered.index.tolist()
            idx=st.selectbox(
                "Select card",
                options,
                format_func=lambda i:f"{df.loc[i,'name']} — {df.loc[i,'set_name']} — {df.loc[i,'id']}"
            )
            row=df.loc[idx].to_dict()
            s=score(row)

            left,right=st.columns([1,2.5])
            with left:
                if row.get("image_url"):
                    st.markdown(
    f'<img src="{row["image_url"]}" style="width:100%;border-radius:14px;">',
    unsafe_allow_html=True
)
            with right:
                st.markdown(f"# {row['name']}")
                st.caption(f"{row.get('set_name','')} • {row.get('rarity','')}")
                score_box(s["pii"],signal(s["pii"]))

                m1,m2,m3,m4=st.columns(4)
                m1.metric("Trend",f"€{row['trend']:.2f}" if row.get("trend") is not None else "—")
                m2.metric("1d avg",f"€{row['avg1']:.2f}" if row.get("avg1") is not None else "—")
                m3.metric("7d avg",f"€{row['avg7']:.2f}" if row.get("avg7") is not None else "—")
                m4.metric("30d avg",f"€{row['avg30']:.2f}" if row.get("avg30") is not None else "—")

                st.markdown("### Investment thesis")
                for item in thesis(row,s):
                    st.markdown(f"- {item}")

            st.markdown("## Proprietary price history")
            hist=load_price_history(row["id"])
            if len(hist)<2:
                st.caption("History will build each time the market sync runs. Repeated daily snapshots become your proprietary dataset.")
            else:
                h=pd.DataFrame(hist)
                h["recorded_at"]=pd.to_datetime(h["recorded_at"])
                chart=h.set_index("recorded_at")[["trend_price_eur","avg_7d_eur","avg_30d_eur"]]
                chart.columns=["Trend","7d average","30d average"]
                st.line_chart(chart)

            st.markdown("## Graded market")
            st.info("PSA, BGS/Beckett, CGC, TAG, SGC and ACE sold comps will plug in here once we select a feed that permits commercial use.")

            st.markdown("## Population")
            pop=load_population(row["id"])
            if not pop:
                st.caption("No population snapshots loaded yet.")
            else:
                st.dataframe(pd.DataFrame(pop),use_container_width=True,hide_index=True)

elif page == "Market Sync":
    st.title("EU Market Sync")
    st.markdown("""
This is your **data collection step**.

The public dashboard does not contact external market APIs every time somebody visits. Instead, this page imports a European starter universe into **your Supabase database**.

For the prototype you run it manually. Later we automate it once per day.
""")

    ok,status=connection_check()
    if not ok:
        st.error(f"Supabase connection failed: {status}")
    else:
        st.success("Supabase is connected.")
        size=st.slider("Cards to sync",20,120,60,10)

        if st.button("🇪🇺 Sync EU market now",type="primary",use_container_width=True):
            progress=st.progress(5,text="Retrieving European market data...")
            cards,error=fetch_eu_sample(size)

            if error:
                progress.empty()
                st.error(error)
            else:
                progress.progress(65,text="Writing card metadata to Supabase...")
                try:
                    n1=upsert_cards(cards)
                    progress.progress(82,text="Saving today's Cardmarket snapshots...")
                    n2=insert_price_snapshots(cards)
                    progress.progress(100,text="Done")
                    st.success(f"Synced {n1} cards and stored {n2} European price snapshots.")
                    st.info("Return to Dashboard and refresh once.")
                except Exception as e:
                    progress.empty()
                    st.error(f"Supabase write failed: {e}")
                    st.warning(
                        "If the error mentions permissions or RLS, send me the exact error. "
                        "I will give you the one SQL command needed for this prototype."
                    )

else:
    st.title("Pokémon Investment Index — Europe")
    st.markdown("""
The PII is an explainable **European-market research signal**.

Current prototype weights:

- **25% price momentum**
- **20% value / entry level**
- **15% rarity / collectability**
- **15% character demand**
- **10% liquidity proxy**
- **10% volatility / risk quality**
- **5% data confidence**

Current market inputs are **Cardmarket EUR prices**: trend, low, average selling price, and 1/7/30-day averages where available.

### Planned production additions

- actual transaction liquidity / sales velocity;
- PSA, BGS/Beckett, CGC, TAG, SGC and ACE graded sold comps;
- population and population-growth history;
- set age, print supply and reprint risk;
- longer proprietary daily price history;
- portfolios and alerts;
- user accounts and subscription billing.

**US pricing and TCGplayer are intentionally not part of this version.**
""")

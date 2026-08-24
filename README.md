# Pokémon Alpha — Commercial Prototype

A Streamlit MVP for Pokémon card investment research.

## What is included
- Executive dashboard
- 10 non-overlapping price-band winners
- Market screener
- Card analyzer
- Explainable Pokémon Investment Index (PII)
- Cardmarket trend / 1-day / 7-day / 30-day signals via TCGdex
- TCGplayer-ready normalized payload
- Watchlist
- Portfolio foundation
- Graded-sales table connector
- Population table connector
- Demo fallback if a public API is unavailable
- Commercial-data warnings rather than silent scraping

## Deploy
1. Upload all files to the root of your GitHub repository.
2. Keep the `data` folder.
3. Streamlit Community Cloud should use `app.py`.
4. No API key is required for the TCGdex prototype.
5. Reboot the Streamlit app after replacing the files.

## Important production limitations
The prototype is designed to validate UX and the scoring concept. Before charging users:

1. Move watchlists/portfolios to Supabase/Postgres with user authentication.
2. Run market ingestion as scheduled jobs and save proprietary daily snapshots.
3. Add a licensed/approved graded-sales feed.
4. Add PSA/CGC/BGS/TAG population data only under terms that allow your use.
5. Add billing (Stripe) only after the data rights and product-market fit are clear.
6. Replace public API-on-page-load architecture with your own database/cache.

## Graded data CSV schema
`data/graded_market.csv`

- card_id
- grader
- grade
- last_sold
- currency
- sold_date
- avg_30d
- sales_30d
- source

## Population CSV schema
`data/populations.csv`

- card_id
- grader
- grade
- population
- population_30d_ago
- population_90d_ago
- updated_at
- source

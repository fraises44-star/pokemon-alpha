# Pokémon Alpha V0.3 — EU + Supabase

This build is intentionally Europe-first.

## Architecture

European Cardmarket data (prototype ingestion via TCGdex)
→ explicit Market Sync
→ Supabase
→ Pokémon Alpha dashboard

The dashboard reads from Supabase and therefore does not sit blank while dozens of external API requests execute.

## Streamlit secrets

```toml
SUPABASE_URL = "..."
SUPABASE_ANON_KEY = "..."
```

Your older POKEMONTCG_API_KEY can remain; V0.3 does not use it.

## First run

1. Deploy all files to GitHub.
2. Reboot Streamlit.
3. Open **Market Sync**.
4. Choose 40–60 cards.
5. Click **Sync EU market now**.
6. Return to Dashboard.

## Next production steps

- scheduled daily ingestion;
- proper authentication and RLS;
- permanent watchlists / portfolios;
- licensed graded-sales feed;
- population-data feed with commercial rights;
- Stripe subscriptions;
- monitoring and backups.

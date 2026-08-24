import streamlit as st

def init_store():
    st.session_state.setdefault("watchlist", {})
    st.session_state.setdefault("portfolio", {})

def _img(card):
    return card.get("image") or (card.get("images") or {}).get("small")

def add_watchlist(card):
    st.session_state["watchlist"][card.get("id")] = {
        "card_id": card.get("id"),
        "name": card.get("name"),
        "set_name": (card.get("set") or {}).get("name",""),
        "image": _img(card),
    }

def get_watchlist():
    return list(st.session_state.get("watchlist", {}).values())

def remove_watchlist(card_id):
    st.session_state.get("watchlist", {}).pop(card_id, None)

def add_portfolio(card, quantity=1, cost=0):
    key = card.get("id")
    st.session_state["portfolio"][key] = {
        "card_id": key,
        "name": card.get("name"),
        "set_name": (card.get("set") or {}).get("name",""),
        "quantity": quantity,
        "cost_basis": float(cost or 0),
    }

def get_portfolio():
    return list(st.session_state.get("portfolio", {}).values())

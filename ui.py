import streamlit as st

def inject_css():
    st.markdown("""
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 4rem; max-width: 1450px;}
    [data-testid="stMetric"] {
        background: rgba(127,127,127,.06);
        border: 1px solid rgba(127,127,127,.16);
        padding: 14px 16px;
        border-radius: 14px;
    }
    div[data-testid="stImage"] img {border-radius: 14px;}
    .alpha-card {
        border: 1px solid rgba(127,127,127,.15);
        border-radius: 16px;
        padding: 16px;
        background: rgba(127,127,127,.035);
    }
    .smallmuted {opacity:.68;font-size:.86rem;}
    </style>
    """, unsafe_allow_html=True)

def render_score_gauge(score, label):
    st.markdown(f"""
    <div class="alpha-card">
      <div class="smallmuted">POKÉMON INVESTMENT INDEX</div>
      <div style="font-size:52px;font-weight:800;line-height:1.05">{int(score)}<span style="font-size:20px;opacity:.55">/100</span></div>
      <div style="margin-top:6px;font-weight:600">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(title, value, sub):
    st.markdown(f"""
    <div class="alpha-card">
      <div class="smallmuted">{title.upper()}</div>
      <div style="font-size:30px;font-weight:800">{value}</div>
      <div class="smallmuted">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

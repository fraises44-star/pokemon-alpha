import streamlit as st
def css():
    st.markdown("""<style>
    .block-container{max-width:1450px;padding-top:1.8rem;padding-bottom:4rem}
    .alpha{border:1px solid rgba(127,127,127,.16);border-radius:16px;padding:16px;background:rgba(127,127,127,.035)}
    .muted{opacity:.62;font-size:.84rem}
    div[data-testid="stImage"] img{border-radius:14px}
    [data-testid="stMetric"]{border:1px solid rgba(127,127,127,.13);border-radius:14px;padding:12px}
    </style>""",unsafe_allow_html=True)
def card_metric(title,value,subtitle=""):
    st.markdown(f'<div class="alpha"><div class="muted">{title.upper()}</div><div style="font-size:30px;font-weight:800">{value}</div><div class="muted">{subtitle}</div></div>',unsafe_allow_html=True)
def score_box(score,label):
    st.markdown(f'<div class="alpha"><div class="muted">POKÉMON INVESTMENT INDEX — EUROPE</div><div style="font-size:52px;font-weight:850">{int(score)}<span style="font-size:19px;opacity:.5">/100</span></div><div style="font-weight:650">{label}</div></div>',unsafe_allow_html=True)

import streamlit as st

def inject_css():
    st.markdown("""<style>
html, body, [class*="css"] { background-color: #0a0f0a !important; color: #e2e8f0 !important; }
.main .block-container { padding: 1.5rem 2rem 3rem; max-width: 1400px; }
[data-testid="stSidebar"] { background: #0d150e !important; border-right: 1px solid rgba(74,222,128,0.2) !important; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stButton"] > button[kind="primary"] { background: linear-gradient(135deg,#22c55e,#16a34a) !important; color:#000 !important; font-weight:700 !important; border:none !important; border-radius:10px !important; box-shadow:0 0 20px rgba(74,222,128,0.3) !important; }
[data-testid="stButton"] > button { border-radius:8px !important; }
.kpi-card { background:#111a12; border:1px solid rgba(74,222,128,0.15); border-radius:14px; padding:1.2rem; text-align:center; position:relative; overflow:hidden; margin-bottom:8px; }
.kpi-card::before { content:''; position:absolute; top:0;left:0;right:0;height:3px; }
.k1::before{background:#4ade80}.k2::before{background:#06b6d4}.k3::before{background:#f59e0b}.k4u::before{background:#4ade80}.k4d::before{background:#ef4444}
.kv{font-size:1.8rem;font-weight:800;color:#e2e8f0;line-height:1;margin-bottom:0.2rem}
.kl{font-size:0.7rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.1em}
.ks{font-size:0.72rem;color:#64748b;margin-top:0.2rem}
.weather-card{background:#0d1f1a;border:1px solid rgba(74,222,128,0.25);border-radius:14px;padding:1.2rem;margin-bottom:1rem}
.weather-title{color:#4ade80;font-size:0.8rem;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.8rem;font-weight:600}
.weather-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem}
.weather-item{background:rgba(74,222,128,0.06);border-radius:8px;padding:0.6rem;text-align:center}
.weather-val{font-size:1.3rem;font-weight:700;color:#e2e8f0}
.weather-lbl{font-size:0.68rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.08em}
[data-testid="stMetric"]{background:#111a12;border:1px solid rgba(74,222,128,0.15);border-radius:14px;padding:1rem}
[data-testid="stMetricValue"]{color:#4ade80 !important}
.login-box{background:#111a12;border:1px solid rgba(74,222,128,0.25);border-radius:16px;padding:2.5rem;max-width:420px;margin:4rem auto}
.login-title{text-align:center;font-size:1.8rem;font-weight:800;color:#e2e8f0;margin-bottom:0.3rem}
.login-sub{text-align:center;color:#94a3b8;font-size:0.9rem;margin-bottom:1.5rem}
</style>""", unsafe_allow_html=True)

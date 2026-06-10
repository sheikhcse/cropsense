"""
app.py — CropSense AI
=====================
Entry point. Run with:  streamlit run app.py
"""

import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="CropSense AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Local imports ─────────────────────────────────────────────────────────────
from database           import init_db, save_prediction
from utils.model        import build_model, run_prediction
from utils.constants    import T
from components         import inject_css, render_auth_page, render_sidebar, render_kpis, render_tabs

# ── Initialise ────────────────────────────────────────────────────────────────
init_db()   # Create SQLite tables if they don't exist
inject_css()

# ── Session defaults ──────────────────────────────────────────────────────────
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("lang", "bn")

# ── Auth gate ─────────────────────────────────────────────────────────────────
if not st.session_state["logged_in"]:
    render_auth_page()
    st.stop()

# ── Build / load ML model ─────────────────────────────────────────────────────
model_bundle = build_model()
model, scaler, le_crop, le_soil, le_season, le_irr, FN, df, met = model_bundle

L = T[st.session_state["lang"]]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:1.8rem 1rem 1.2rem">
  <h1 style="font-size:2.8rem;font-weight:800;color:#e2e8f0;margin:0 0 0.3rem">
    CropSense <span style="color:#4ade80">AI</span>
  </h1>
  <p style="color:#94a3b8;font-size:0.95rem;margin:0">{L['subtitle']}</p>
</div>""", unsafe_allow_html=True)

# ── Sidebar (returns all inputs) ──────────────────────────────────────────────
inputs = render_sidebar(le_crop, le_soil, le_season, le_irr)
lang   = inputs["lang"]
L      = T[lang]

# ── Weather card (main area) ──────────────────────────────────────────────────
wd     = inputs["wd"]
source = inputs["source"]
if wd and wd.get("success"):
    st.markdown(f"""<div class="weather-card">
      <div class="weather-title">{L['current_weather']} - {inputs['district']} ({wd['city']}) [{source}]</div>
      <div class="weather-grid">
        <div class="weather-item"><div class="weather-val">{wd['temp']} C</div><div class="weather-lbl">{L['temperature'].split('(')[0]}</div></div>
        <div class="weather-item"><div class="weather-val">{wd['humidity']}%</div><div class="weather-lbl">{L['humidity'].split('(')[0]}</div></div>
        <div class="weather-item"><div class="weather-val">{wd['wind']} km/h</div><div class="weather-lbl">Wind</div></div>
        <div class="weather-item"><div class="weather-val">{wd['feels_like']} C</div><div class="weather-lbl">Feels Like</div></div>
      </div>
      <p style="margin:0.6rem 0 0;font-size:0.82rem;color:#94a3b8;text-align:center">
        {wd['description']} - {wd['pressure']} hPa
      </p>
    </div>""", unsafe_allow_html=True)
else:
    st.info(L["weather_info"])

# ── Prediction ────────────────────────────────────────────────────────────────
if inputs["predict_btn"] or "lp" not in st.session_state:
    result = run_prediction(
        model, scaler, le_crop, le_soil, le_season, le_irr, FN,
        inputs["ct"], inputs["so"], inputs["se"], inputs["ir"],
        inputs["temp"], inputs["rain"], inputs["hum"], inputs["sun"],
        inputs["ph"], inputs["nit"], inputs["phos"], inputs["pot"],
        inputs["pest"], inputs["area"],
    )
    st.session_state["lp"] = dict(
        ph=result[0], tot=result[1], std=result[2],
        lo=result[3], hi=result[4], ar=inputs["area"],
        ct=inputs["ct"],
    )
    # Save to DB when predict button clicked
    if inputs["predict_btn"]:
        save_prediction(
            username   = st.session_state.get("username", ""),
            crop_type  = inputs["ct"],
            district   = inputs["district"],
            yield_pred = result[0],
            total_yield= result[1],
            field_area = inputs["area"],
        )

p    = st.session_state["lp"]
cavg = df[df["crop_type"] == inputs["ct"]]["yield_per_ha"].mean()

render_kpis(p, cavg, lang)
render_tabs(inputs, model_bundle, df, lang)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;margin-top:2rem;padding:1rem;
  border-top:1px solid rgba(74,222,128,0.1);color:#334155;font-size:0.75rem">
  {L['footer']}
</div>""", unsafe_allow_html=True)

"""
components/sidebar.py
Renders the full sidebar: language, logout, district, crop, weather, soil inputs.
Returns all user inputs as a dict.
"""
import streamlit as st
from utils.constants import T, DISTRICTS, RAIN_MAP, SOILS, SEASONS, IRRS
from utils.weather import get_weather
def render_sidebar(le_crop, le_soil, le_season, le_irr) -> dict:
    lang = st.session_state.get("lang", "bn")
    with st.sidebar:
        # Language + Logout
        col_lang, col_out = st.columns(2)
        with col_lang:
            lc = st.selectbox(T[lang]["language"], ["বাংলা", "English"],
                              index=0 if lang == "bn" else 1, key="lang_sidebar")
            st.session_state["lang"] = "bn" if lc == "বাংলা" else "en"
            lang = st.session_state["lang"]
        with col_out:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(T[lang]["logout_btn"], use_container_width=True):
                st.session_state["logged_in"] = False
                st.rerun()

        L = T[lang]
        st.caption(f"{L['logged_in_as']}: **{st.session_state.get('username','')}**")
        st.markdown("---")

        # District & Weather
        st.markdown(f"### {L['district']}")
        district = st.selectbox(L["select_district"], list(DISTRICTS.keys()))
        lat, lon = DISTRICTS[district]
        weather_btn = st.button(L["get_weather"], use_container_width=True)

        wd = None; source = None
        if weather_btn:
            with st.spinner(L["fetching"]):
                wd, source = get_weather(district, lat, lon, L)
                st.session_state["wd_result"]   = wd
                st.session_state["wd_source"]   = source
                st.session_state["wd_district"] = district
        elif "wd_result" in st.session_state and st.session_state.get("wd_district") == district:
            wd     = st.session_state["wd_result"]
            source = st.session_state.get("wd_source", "")

        default_temp = float(wd["temp"])     if (wd and wd.get("success")) else 28.0
        default_hum  = float(wd["humidity"]) if (wd and wd.get("success")) else 75.0

        if wd and wd.get("success"):
            st.success(f"{L['weather_ok']} - {source} - {wd['city']}")
        elif wd and not wd.get("success"):
            st.error(f"{L['weather_err']}: {wd.get('error','')}")

        st.markdown("---")
        st.markdown(f"### {L['crop_field']}")
        ct   = st.selectbox(L["crop_name"],  sorted(le_crop.classes_))
        so   = st.selectbox(L["soil_type"],  le_soil.classes_)
        se   = st.selectbox(L["season"],     le_season.classes_)
        ir   = st.selectbox(L["irrigation"], le_irr.classes_)
        area = st.slider(L["field_area"], 0.1, 50.0, 1.0, 0.1)

        st.markdown("---")
        weather_note = L["auto"] if (wd and wd.get("success")) else ""
        st.markdown(f"### {L['weather_section']} {weather_note}")
        temp = st.slider(L["temperature"],  10.0, 45.0,  default_temp, 0.5)
        rain = st.slider(L["rainfall"],    200.0, 3000.0, float(RAIN_MAP.get(district, 1500)), 10.0)
        hum  = st.slider(L["humidity"],     20.0, 100.0,  default_hum, 1.0)
        sun  = st.slider(L["sunshine"],      3.0,  12.0,  6.5, 0.1)

        st.markdown("---")
        st.markdown(f"### {L['soil_inputs']}")
        ph   = st.slider(L["soil_ph"],      4.5,  8.5,   6.3, 0.1)
        nit  = st.slider(L["nitrogen"],     0.0, 200.0, 85.0, 1.0)
        phos = st.slider(L["phosphorus"],   0.0, 120.0, 35.0, 1.0)
        pot  = st.slider(L["potassium"],    0.0, 180.0, 45.0, 1.0)
        pest = st.slider(L["pesticide"],    0.0,  15.0,  1.5, 0.1)

        predict_btn = st.button(L["predict_btn"], use_container_width=True, type="primary")

    return dict(
        lang=lang, district=district, wd=wd, source=source,
        ct=ct, so=so, se=se, ir=ir, area=area,
        temp=temp, rain=rain, hum=hum, sun=sun,
        ph=ph, nit=nit, phos=phos, pot=pot, pest=pest,
        predict_btn=predict_btn,
    )

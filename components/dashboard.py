"""
components/dashboard.py
Renders the 5 analytics tabs after prediction.
"""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from database import save_prediction, get_user_predictions
from utils.model import run_prediction
from utils.constants import T
LY = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="#e2e8f0",
    title_font_size=14,
)
def render_kpis(p: dict, cavg: float, lang: str):
    L  = T[lang]
    dl = (p["ph"] - cavg) / cavg * 100 if cavg > 0 else 0
    c1, c2, c3, c4 = st.columns(4)
    for col, cls, val, lbl, sub in [
        (c1, "k1",  f"{p['ph']:.2f}", L["ton_ha"],    L["predicted"]),
        (c2, "k2",  f"{p['tot']:.2f}", L["total_ton"], L["for_ha"].format(a=p["ar"])),
        (c3, "k3",  f"+/-{p['std']:.2f}", L["uncertainty"], L["ci"].format(lo=f"{p['lo']:.1f}", hi=f"{p['hi']:.1f}")),
        (c4, "k4u" if dl >= 0 else "k4d", f"{dl:+.1f}%", L["vs_avg"], L["avg"].format(avg=f"{cavg:.2f}")),
    ]:
        col.markdown(
            f'<div class="kpi-card {cls}"><div class="kv">{val}</div>'
            f'<div class="kl">{lbl}</div><div class="ks">{sub}</div></div>',
            unsafe_allow_html=True
        )
    st.markdown("<br>", unsafe_allow_html=True)
    if p["ph"] >= cavg * 1.1:
        st.success(L["great"].format(dl=dl))
    elif p["ph"] >= cavg * 0.9:
        st.info(L["good"].format(ct=p["ct"]))
    else:
        st.warning(L["warn"])
def render_tabs(inputs, model_bundle, df, lang):
    L                   = T[lang]
    model, scaler, le_crop, le_soil, le_season, le_irr, FN, _, met = model_bundle
    ct   = inputs["ct"]; so   = inputs["so"]; se   = inputs["se"]
    ir   = inputs["ir"]; area = inputs["area"]
    temp = inputs["temp"]; rain = inputs["rain"]; hum  = inputs["hum"]
    sun  = inputs["sun"]; ph   = inputs["ph"];   nit  = inputs["nit"]
    phos = inputs["phos"]; pot  = inputs["pot"]; pest = inputs["pest"]
    p    = st.session_state["lp"]

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [L["tab1"], L["tab2"], L["tab3"], L["tab4"], L["tab5"]]
    )

    # Tab 1: Analytics 
    with tab1:
        ca, cb = st.columns([3, 2])
        with ca:
            cdf = df[df["crop_type"] == ct]
            f = go.Figure()
            f.add_trace(go.Histogram(x=cdf["yield_per_ha"], nbinsx=25,
                                     marker_color="#4ade80", opacity=0.7))
            f.add_vline(x=p["ph"], line_dash="dash", line_color="#f97316",
                        annotation_text=f"{L['your']}: {p['ph']:.2f} t/ha",
                        annotation_font_color="#f97316")
            f.add_vrect(x0=p["lo"], x1=p["hi"],
                        fillcolor="rgba(249,115,22,0.08)", line_width=0)
            f.update_layout(title=f"{L['dist_chart']} - {ct}",
                            xaxis_title="t/ha", yaxis_title="n", **LY)
            st.plotly_chart(f, use_container_width=True)
        with cb:
            cats = [L["temperature"].split("(")[0], L["rainfall"].split("(")[0],
                    L["humidity"].split("(")[0], "N", "P", "K"]
            maxv = [45, 3000, 100, 200, 120, 180]
            vals = [temp, rain, hum, nit, phos, pot]
            norm = [min(100, v/m*100) for v, m in zip(vals, maxv)]
            f2 = go.Figure(go.Scatterpolar(
                r=norm+[norm[0]], theta=cats+[cats[0]],
                fill="toself",
                fillcolor="rgba(74,222,128,0.18)",
                line=dict(color="#4ade80", width=2)
            ))
            f2.update_layout(
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(range=[0,100], tickfont_color="#94a3b8",
                                   gridcolor="rgba(148,163,184,0.15)"),
                    angularaxis=dict(tickfont_color="#e2e8f0",
                                    gridcolor="rgba(148,163,184,0.15)"),
                ),
                title=L["field_profile"],
                paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0",
                showlegend=False, title_font_size=14
            )
            st.plotly_chart(f2, use_container_width=True)

        cc, cd = st.columns(2)
        with cc:
            sa = df.groupby("season")["yield_per_ha"].mean().reset_index()
            f3 = px.bar(sa, x="season", y="yield_per_ha", color="yield_per_ha",
                        color_continuous_scale="Greens", title=L["season_chart"])
            f3.update_layout(coloraxis_showscale=False, xaxis_title="",
                             yaxis_title=L["avg_yield"], **LY)
            st.plotly_chart(f3, use_container_width=True)
        with cd:
            top  = df.groupby("crop_type")["yield_per_ha"].mean().nlargest(10).reset_index()
            clrs = ["#f97316" if x == ct else "#4ade80" for x in top["crop_type"]]
            f4   = go.Figure(go.Bar(x=top["yield_per_ha"], y=top["crop_type"],
                                    orientation="h", marker_color=clrs))
            f4.update_layout(title=L["top10"], xaxis_title=L["avg_yield"], **LY)
            st.plotly_chart(f4, use_container_width=True)

    #  Tab 2: Feature Impact 
    with tab2:
        st.markdown(f"### {L['feature_title']}")
        imp = model.feature_importances_
        lb  = (["ফসল","মাটি","মৌসুম","সেচ","তাপমাত্রা","বৃষ্টিপাত","আর্দ্রতা","সূর্যালোক","pH","নাইট্রোজেন","ফসফরাস","পটাশিয়াম","কীটনাশক","জমির আয়তন"]
               if lang == "bn" else
               ["Crop","Soil","Season","Irrigation","Temperature","Rainfall","Humidity","Sunshine","pH","Nitrogen","Phosphorus","Potassium","Pesticide","Field Area"])
        fi = pd.DataFrame({"Feature": lb, "Importance": imp}).sort_values("Importance")
        f5 = go.Figure(go.Bar(
            x=fi["Importance"], y=fi["Feature"], orientation="h",
            marker=dict(color=fi["Importance"],
                        colorscale=[[0,"#1e3a2f"],[0.5,"#4ade80"],[1,"#f97316"]],
                        showscale=True)
        ))
        f5.update_layout(title=L["feature_rank"], height=450, xaxis_title="", **LY)
        st.plotly_chart(f5, use_container_width=True)

        st.markdown(f"### {L['sensitivity']}")
        if lang == "bn":
            fm   = {"তাপমাত্রা":4,"বৃষ্টিপাত":5,"আর্দ্রতা":6,"সূর্যালোক":7,"pH":8,"নাইট্রোজেন":9,"ফসফরাস":10,"পটাশিয়াম":11}
            cv_d = {"তাপমাত্রা":temp,"বৃষ্টিপাত":rain,"আর্দ্রতা":hum,"সূর্যালোক":sun,"pH":ph,"নাইট্রোজেন":nit,"ফসফরাস":phos,"পটাশিয়াম":pot}
            fr   = {"তাপমাত্রা":(10,42),"বৃষ্টিপাত":(200,3000),"আর্দ্রতা":(20,100),"সূর্যালোক":(3,12),"pH":(4.5,8.5),"নাইট্রোজেন":(0,200),"ফসফরাস":(0,120),"পটাশিয়াম":(0,180)}
        else:
            fm   = {"Temperature":4,"Rainfall":5,"Humidity":6,"Sunshine":7,"pH":8,"Nitrogen":9,"Phosphorus":10,"Potassium":11}
            cv_d = {"Temperature":temp,"Rainfall":rain,"Humidity":hum,"Sunshine":sun,"pH":ph,"Nitrogen":nit,"Phosphorus":phos,"Potassium":pot}
            fr   = {"Temperature":(10,42),"Rainfall":(200,3000),"Humidity":(20,100),"Sunshine":(3,12),"pH":(4.5,8.5),"Nitrogen":(0,200),"Phosphorus":(0,120),"Potassium":(0,180)}
        sel  = st.selectbox(L["select_feature"], list(fm.keys()))
        xs   = np.linspace(*fr[sel], 60)
        base = [le_crop.transform([ct])[0], le_soil.transform([so])[0],
                le_season.transform([se])[0], le_irr.transform([ir])[0],
                temp, rain, hum, sun, ph, nit, phos, pot, pest, area]
        ys = []
        for xv in xs:
            rb = base.copy(); rb[fm[sel]] = xv
            ys.append(np.expm1(model.predict(
                scaler.transform(pd.DataFrame([rb], columns=FN))
            )[0]))
        f6 = go.Figure()
        f6.add_trace(go.Scatter(x=xs, y=ys, mode="lines",
                                line=dict(color="#4ade80", width=3),
                                fill="tozeroy", fillcolor="rgba(74,222,128,0.06)"))
        f6.add_vline(x=cv_d[sel], line_dash="dash", line_color="#f97316",
                     annotation_text=f"{L['current']}: {cv_d[sel]}",
                     annotation_font_color="#f97316")
        f6.update_layout(title=f"{L['yield_vs']} {sel}",
                         xaxis_title=sel, yaxis_title="t/ha", **LY)
        st.plotly_chart(f6, use_container_width=True)

    #  Tab 3: Data 
    with tab3:
        st.markdown(f"### {L['data_title']}")
        m1, m2, m3 = st.columns(3)
        m1.metric(L["total_records"], f"{len(df):,}")
        m2.metric(L["crop_types"],    df["crop_type"].nunique())
        m3.metric(L["avg_yield_lbl"], f"{df['yield_per_ha'].mean():.2f} t/ha")
        xax = st.selectbox(L["x_axis"],
                           ["rainfall","temperature","nitrogen","humidity","soil_ph","potassium"])
        f7 = px.scatter(df, x=xax, y="yield_per_ha", color="crop_type", opacity=0.5,
                        title=f"{L['yield_vs']} {xax}", labels={"yield_per_ha":"t/ha"})
        f7.update_layout(**LY)
        st.plotly_chart(f7, use_container_width=True)
        with st.expander(L["raw_data"]):
            st.dataframe(df.head(200), use_container_width=True)

    #  Tab 4: Model Report 
    with tab4:
        st.markdown(f"### {L['model_title']}")
        a, b, c, d = st.columns(4)
        a.metric(L["test_r2"],   f"{met['r2']:.4f}")
        b.metric(L["test_mae"],  f"{met['mae']:.2f} t/ha")
        c.metric(L["test_rmse"], f"{met['rmse']:.2f} t/ha")
        d.metric(L["cv_r2"],     f"{met['cv_mean']:.3f} +/-{met['cv_std']:.3f}")
        st.markdown("---")
        gap = met["overfit_gap"]
        if gap < 0.05:  st.success(L["no_overfit"].format(gap=gap))
        elif gap < 0.10: st.warning(L["slight_overfit"].format(gap=gap))
        else:            st.error(L["overfit"].format(gap=gap))
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""**{L['improvements']}:**
- Log Transform
- Outlier Removal (5-95%)
- max_depth=10
- min_samples_leaf=10
- 5-Fold Cross Validation
- Removed: {met['outliers_removed']}""")
        with col2:
            st.markdown(f"""**{L['train_vs_test']}:**
| | Train | Test |
|---|---|---|
| R2  | {met['train_r2']:.4f} | {met['r2']:.4f} |
| MAE | {met['train_mae']:.2f} | {met['mae']:.2f} |
| CV R2 | - | {met['cv_mean']:.3f} |""")
        st.markdown(f"#### {L['actual_vs_pred']}")
        f8 = go.Figure()
        f8.add_trace(go.Scatter(x=met["y_test"], y=met["y_pred"], mode="markers",
                                marker=dict(color="#4ade80", opacity=0.4, size=4),
                                name=L["predictions"]))
        mn = min(min(met["y_test"]), min(met["y_pred"]))
        mx = max(max(met["y_test"]), max(met["y_pred"]))
        f8.add_trace(go.Scatter(x=[mn, mx], y=[mn, mx], mode="lines",
                                line=dict(color="#f97316", dash="dash", width=2),
                                name=L["perfect_fit"]))
        f8.update_layout(xaxis_title="Actual (t/ha)", yaxis_title="Predicted (t/ha)", **LY)
        st.plotly_chart(f8, use_container_width=True)

    #  Tab 5: My Prediction History 
    with tab5:
        st.markdown(f"### {L['history_title']}")
        username = st.session_state.get("username", "")
        history  = get_user_predictions(username)
        if not history:
            st.info(L["no_history"])
        else:
            hist_df = pd.DataFrame(history)
            hist_df.columns = [L["hist_crop"], L["hist_district"],
                               L["hist_yield"], L["hist_total"],
                               L["hist_area"],  L["hist_date"]]
            st.dataframe(hist_df, use_container_width=True)

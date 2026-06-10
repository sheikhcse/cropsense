"""
utils/model.py
--------------
Random Forest model: training (cached) + prediction helper.
"""

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .constants import CROPS, SOILS, SEASONS, IRRS, SM, IM


@st.cache_resource(show_spinner="AI Model building (~20s)...")
def build_model():
    rng = np.random.default_rng(42)
    rows = []
    for _ in range(8000):
        cr  = rng.choice(list(CROPS.keys())); c = CROPS[cr]
        so  = rng.choice(SOILS)
        se  = rng.choice(SEASONS)
        ir  = rng.choice(IRRS)
        t   = float(np.clip(rng.normal(c["to"],  5),            10,   42))
        r   = float(np.clip(rng.normal(c["ro"],  c["ro"]*0.3), 200, 3000))
        h   = float(np.clip(rng.normal(72,  15),  30,  100))
        su  = float(np.clip(rng.normal(6.5,  1.8),  3,   12))
        ph  = float(np.clip(rng.normal(6.3,  0.8),  4.5,  8))
        n   = float(np.clip(rng.normal(85,  35),    0,  200))
        p   = float(np.clip(rng.normal(35,  20),    0,  120))
        k   = float(np.clip(rng.normal(45,  25),    0,  180))
        pe  = float(np.clip(rng.exponential(1.5),   0,   15))
        ar  = float(np.clip(rng.exponential(2),     0.1, 50))
        y = (
            c["base"]
            * max(0.1, 1 - 0.003 * (t - c["to"])**2)
            * max(0.1, 1 - 0.0000002 * (r - c["ro"])**2)
            * max(0.1, 1 - 0.06 * abs(ph - 6.3))
            * (1 + c["ns"] * n)
            * (1 + 0.003 * p)
            * (1 + 0.002 * k)
            * (1 + 0.015 * pe)
            * (0.88 + 0.018 * su)
            * SM[so] * IM[ir]
            * (0.93 + 0.001 * h)
        )
        y = max(0.05, y * float(rng.normal(1, 0.05)))
        rows.append([cr, so, se, ir, t, r, h, su, ph, n, p, k, pe, ar, y])

    df = pd.DataFrame(rows, columns=[
        "crop_type", "soil_type", "season", "irrigation_type",
        "temperature", "rainfall", "humidity", "sunshine_hours",
        "soil_ph", "nitrogen", "phosphorus", "potassium",
        "pesticide_use", "field_area", "yield_per_ha"
    ])

    # Remove per-crop outliers (5–95 percentile)
    clean = []
    for crop in df["crop_type"].unique():
        sub = df[df["crop_type"] == crop]
        Q1  = sub["yield_per_ha"].quantile(0.05)
        Q3  = sub["yield_per_ha"].quantile(0.95)
        clean.append(sub[(sub["yield_per_ha"] >= Q1) & (sub["yield_per_ha"] <= Q3)])
    df = pd.concat(clean, ignore_index=True)

    lc  = LabelEncoder().fit(df["crop_type"])
    ls  = LabelEncoder().fit(df["soil_type"])
    lse = LabelEncoder().fit(df["season"])
    li  = LabelEncoder().fit(df["irrigation_type"])

    FN = ["crop_enc", "soil_enc", "sea_enc", "irr_enc",
          "temperature", "rainfall", "humidity", "sunshine_hours",
          "soil_ph", "nitrogen", "phosphorus", "potassium",
          "pesticide_use", "field_area"]

    df["crop_enc"] = lc.transform(df["crop_type"])
    df["soil_enc"] = ls.transform(df["soil_type"])
    df["sea_enc"]  = lse.transform(df["season"])
    df["irr_enc"]  = li.transform(df["irrigation_type"])

    X = df[FN]; y = df["yield_per_ha"]; y_log = np.log1p(y)
    Xt, Xe, yt, ye = train_test_split(
        X, y_log, test_size=0.2, random_state=42,
        stratify=pd.cut(y_log, bins=5, labels=False)
    )
    sc = StandardScaler()
    rf = RandomForestRegressor(
        n_estimators=200, max_depth=10, min_samples_leaf=10,
        min_samples_split=20, max_features=0.7, n_jobs=-1, random_state=42
    )
    rf.fit(sc.fit_transform(Xt), yt)

    yp     = np.expm1(rf.predict(sc.transform(Xe)));  ye_o = np.expm1(ye)
    yp_tr  = np.expm1(rf.predict(sc.fit_transform(Xt))); yt_o = np.expm1(yt)
    kf     = KFold(n_splits=5, shuffle=True, random_state=42)
    cv     = cross_val_score(rf, sc.transform(X), np.log1p(y), cv=kf, scoring="r2")

    met = {
        "r2":         r2_score(ye_o, yp),
        "mae":        mean_absolute_error(ye_o, yp),
        "rmse":       float(np.sqrt(mean_squared_error(ye_o, yp))),
        "train_r2":   r2_score(yt_o, yp_tr),
        "train_mae":  mean_absolute_error(yt_o, yp_tr),
        "cv_mean":    float(cv.mean()),
        "cv_std":     float(cv.std()),
        "overfit_gap": r2_score(yt_o, yp_tr) - r2_score(ye_o, yp),
        "y_test":     ye_o.tolist(),
        "y_pred":     yp.tolist(),
        "outliers_removed": 8000 - len(df),
    }
    return rf, sc, lc, ls, lse, li, FN, df, met


def run_prediction(model, scaler, le_crop, le_soil, le_season, le_irr, FN,
                   ct, so, se, ir, temp, rain, hum, sun, ph, nit, phos, pot, pest, area):
    """Return (yield_per_ha, total_yield, std, ci_lo, ci_hi)."""
    row = pd.DataFrame(
        [[le_crop.transform([ct])[0], le_soil.transform([so])[0],
          le_season.transform([se])[0], le_irr.transform([ir])[0],
          temp, rain, hum, sun, ph, nit, phos, pot, pest, area]],
        columns=FN
    )
    s  = scaler.transform(row)
    pr = np.expm1(model.predict(s)[0])

    rng2 = np.random.default_rng(42)
    ps   = [np.expm1(model.predict(s + rng2.normal(0, 0.03, s.shape))[0])
            for _ in range(40)]
    std  = float(np.std(ps))
    return pr, pr * area, std, max(0, pr - 1.96 * std), pr + 1.96 * std

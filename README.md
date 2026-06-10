#  CropSense AI

Real-time weather-based crop yield prediction for Bangladesh agriculture.

## Project Structure

```
cropsense/
│
├── app.py                    ← Main entry point (run this)
├── style.css                 ← All CSS styles (dark theme)
├── requirements.txt
│
├── database/
│   ├── __init__.py
│   ├── db.py                 ← SQLite setup, user auth, prediction history
│   └── cropsense.db          ← Auto-created on first run (git-ignore this)
│
├── utils/
│   ├── __init__.py
│   ├── constants.py          ← Districts, crops, soils, translations (EN/BN)
│   ├── weather.py            ← OpenWeatherMap API + session cache
│   └── model.py              ← RandomForest training (cached) + prediction
│
└── components/
    ├── __init__.py
    ├── style_loader.py       ← Injects style.css into Streamlit
    ├── auth_page.py          ← Login / Register UI
    ├── sidebar.py            ← Full sidebar with all inputs
    └── dashboard.py          ← KPI cards + 5 analytics tabs
```

## Setup & Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Features
-  SQLite user authentication (register/login/logout)
-  Prediction history saved per user in database
-  Real-time weather from OpenWeatherMap (1hr cache)
-  Random Forest ML model with 5-fold cross validation
-  5 analytics tabs: charts, feature impact, data explorer, model report, history
- 🇧🇩 Bilingual: বাংলা / English

## Database Tables
- `users` — username, hashed password, created_at, last_login
- `predictions` — username, crop, district, yield, area, timestamp

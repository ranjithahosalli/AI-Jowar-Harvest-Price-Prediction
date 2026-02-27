import requests
from datetime import datetime, timedelta
import joblib
import pandas as pd

API_KEY = "YOUR_API_KEY"
RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"

price_model = joblib.load("price_model.pkl")

def fetch_price_from_api(state, market, date_str):
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 1000,
        "filters[state]": state,
        "filters[market]": market,
        "filters[commodity]": "Jowar",
        "filters[date]": date_str
    }

    url = f"https://api.data.gov.in/resource/{RESOURCE_ID}"
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None

    data = response.json().get("records", [])
    if len(data) == 0:
        return None

    try:
        return float(data[0].get("modal_price"))
    except:
        return None


def ml_predict_price(date_str, last_price):
    dt = datetime.strptime(date_str, "%Y-%m-%d")

    features = {
        "Year": dt.year,
        "Month": dt.month,
        "Day": dt.day,
        "Week": dt.isocalendar().week,
        "Lag_3": last_price,
        "Lag_7": last_price
    }

    X = pd.DataFrame([features])
    predicted_price = price_model.predict(X)[0]
    return round(predicted_price, 2)


def get_lag_prices(state, market, harvest_date):
    harvest_dt = datetime.strptime(harvest_date, "%Y-%m-%d")

    lag3_date = (harvest_dt - timedelta(days=3)).strftime("%Y-%m-%d")
    lag7_date = (harvest_dt - timedelta(days=7)).strftime("%Y-%m-%d")

    # Try API first
    lag3 = fetch_price_from_api(state, market, lag3_date)
    lag7 = fetch_price_from_api(state, market, lag7_date)

    # If API missing → use ML instead
    if lag3 is None:
        # Use latest available price or fallback
        lag3 = ml_predict_price(lag3_date, last_price=3000)

    if lag7 is None:
        lag7 = ml_predict_price(lag7_date, last_price=3000)

    return lag3, lag7

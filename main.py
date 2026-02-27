# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import joblib
import pandas as pd

from weather_api import get_weather_forecast
from gdd_model import predict_harvest_date
from price_api import get_lag_prices   # updated hybrid implementation

# load price model (used only for direct /predict-price if needed)
price_model = joblib.load("price_model.pkl")

app = FastAPI()

class PredictRequest(BaseModel):
    sowing_date: str
    lat: float
    lon: float

class CombinedRequest(BaseModel):
    sowing_date: str
    lat: float
    lon: float
    state: str
    market: str

@app.post("/predict-harvest")
def predict_harvest(req: PredictRequest):
    sow_date = datetime.strptime(req.sowing_date, "%Y-%m-%d")
    weather_data = get_weather_forecast(req.lat, req.lon)
    predicted_date = predict_harvest_date(sow_date, weather_data)
    return {
        "sowing_date": req.sowing_date,
        "predicted_harvest_date": predicted_date.strftime("%Y-%m-%d"),
        "message": "Harvest date predicted using GDD model"
    }

@app.post("/predict-all")
def predict_all(req: CombinedRequest):
    # 1. harvest
    sow_date = datetime.strptime(req.sowing_date, "%Y-%m-%d")
    weather_data = get_weather_forecast(req.lat, req.lon)
    harvest_date = predict_harvest_date(sow_date, weather_data)

    # 2. get lag prices (this will use API if available or forecast otherwise)
    lag_3, lag_7 = get_lag_prices(req.state, req.market, harvest_date.strftime("%Y-%m-%d"))

    if lag_3 is None or lag_7 is None:
        return {
            "error": "Unable to fetch or forecast lag prices for this region/date.",
            "details": "Check market/state names or API key configuration."
        }

    # 3. predict final price using loaded price_model
    date_obj = harvest_date
    features = {
        "Year": date_obj.year,
        "Month": date_obj.month,
        "Day": date_obj.day,
        "Week": date_obj.isocalendar().week,
        "Lag_3": lag_3,
        "Lag_7": lag_7
    }

    X_input = pd.DataFrame([features])
    predicted_price = price_model.predict(X_input)[0]

    return {
        "sowing_date": req.sowing_date,
        "harvest_date": harvest_date.strftime("%Y-%m-%d"),
        "lag_3_price": lag_3,
        "lag_7_price": lag_7,
        "predicted_price": round(predicted_price, 2),
        "state": req.state,
        "market": req.market
    }

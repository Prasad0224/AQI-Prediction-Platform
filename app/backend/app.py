from flask import Flask, jsonify
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np
import joblib
from database.db import init_db, insert_record, fetch_history

app = Flask(__name__)
CORS(app)

# =====================
# Load Models
# =====================
model = joblib.load("../../models/aqi_model.pkl")
forecast_model = joblib.load("../../models/aqi_forecast_model.pkl")

# Load medians for missing pollutant filling
train_df = pd.read_csv("../../data/processed/aqi_clean.csv")
median_values = train_df[["PM2.5","PM10","NO2","SO2","CO","O3","NH3"]].median()

# Initialize database
init_db()

# =====================
# API Config
# =====================
API_KEY = "579b464db66ec23bdd000001ba7c83c075784fde7ead526137a405e4"
AQI_URL = "https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"

# =====================
# Helper for forecast
# =====================
def get_last_aqi_sequence(city, length=5):
    data = fetch_history(city, limit=length)
    aqi_values = [row[0] for row in data]
    if len(aqi_values) < length:
        return None
    return aqi_values[::-1]

# =====================
# Routes
# =====================

@app.route("/predict/<city>")
def predict(city):

    params = {
        "api-key": API_KEY,
        "format": "json",
        "filters[city]": city,
        "limit": 100
    }

    r = requests.get(AQI_URL, params=params)
    try:
        records = r.json().get("records", [])
    except:
        return jsonify({"error": "API response error"})

    if not records:
        return jsonify({"error": "No live data for this city"})

    df = pd.DataFrame(records)[["pollutant_id","avg_value"]]
    df["avg_value"] = pd.to_numeric(df["avg_value"], errors="coerce")

    pivot = df.pivot_table(values="avg_value", columns="pollutant_id", aggfunc="first")

    pivot.columns = [c.lower().replace('.', '') for c in pivot.columns]
    pivot = pivot.rename(columns={
        "pm25":"PM2.5",
        "pm10":"PM10",
        "no2":"NO2",
        "so2":"SO2",
        "co":"CO",
        "ozone":"O3",
        "nh3":"NH3"
    })

    if "CO" in pivot.columns:
        pivot["CO"] = pivot["CO"] / 1000

    required_cols = ["PM2.5","PM10","NO2","SO2","CO","O3","NH3"]
    for col in required_cols:
        if col not in pivot.columns:
            pivot[col] = median_values[col]

    pivot = pivot[required_cols]

    prediction = model.predict(pivot)[0]

    insert_record(city, prediction)

    return jsonify({
        "city": city,
        "predicted_AQI": round(float(prediction), 2)
    })


@app.route("/history/<city>")
def history(city):
    data = fetch_history(city, limit=5)
    aqi_values = [row[0] for row in data][::-1]
    timestamps = [row[1] for row in data][::-1]

    return jsonify({
        "aqi_values": aqi_values,
        "timestamps": timestamps
    })


@app.route("/forecast/<city>")
def forecast(city):
    seq = get_last_aqi_sequence(city)

    if seq is None:
        return jsonify({"error": "Not enough history yet"})

    seq_array = np.array(seq).reshape(1, -1)
    next_aqi = forecast_model.predict(seq_array)[0]

    return jsonify({
        "next_hour_AQI": round(float(next_aqi), 2)
    })


@app.route("/states")
def states():
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 1000
    }

    r = requests.get(AQI_URL, params=params)
    records = r.json().get("records", [])

    state_list = sorted(list(set(rec["state"] for rec in records)))
    return jsonify(state_list)


@app.route("/cities/<state>")
def cities_by_state(state):
    params = {
        "api-key": API_KEY,
        "format": "json",
        "filters[state]": state,
        "limit": 1000
    }

    r = requests.get(AQI_URL, params=params)
    records = r.json().get("records", [])

    city_list = sorted(list(set(rec["city"] for rec in records)))
    return jsonify(city_list)


if __name__ == "__main__":
    app.run(debug=True)

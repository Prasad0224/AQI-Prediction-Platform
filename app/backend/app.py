from flask import Flask, jsonify
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np
import joblib
from database.db import init_db, insert_record, fetch_history
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

app = Flask(__name__)
CORS(app)

model = joblib.load("../../models/aqi_model.pkl")
lstm_scaler = joblib.load("../../models/aqi_lstm_scaler.pkl")

lstm_model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(8, 4)),
    LSTM(32),
    Dense(1)
])

lstm_model.load_weights("../../models/aqi_lstm_forecast.h5")

# Median Pollutant Values
train_df = pd.read_csv("../../data/processed/aqi_clean.csv")
median_values = train_df[["PM2.5","PM10","NO2","SO2","CO","O3","NH3"]].median()

# Initialize Database
init_db()

# CPCB API Config
API_KEY = "579b464db66ec23bdd000001ba7c83c075784fde7ead526137a405e4"
AQI_URL = "https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"

# Build LSTM Sequence
def get_last_lstm_sequence(city, seq_length=8):
    data = fetch_history(city, limit=seq_length)

    if len(data) < seq_length:
        return None

    seq = []
    for row in data[::-1]:
        # row = (aqi, temperature, humidity, wind_speed, timestamp)
        seq.append([row[0], row[1], row[2], row[3]])

    seq = np.array(seq)
    seq_scaled = lstm_scaler.transform(seq)
    return seq_scaled.reshape(1, seq_scaled.shape[0], seq_scaled.shape[1])

# Route: Current AQI Prediction
@app.route("/predict/<city>")
def predict(city):

    params = {
        "api-key": API_KEY,
        "format": "json",
        "filters[city]": city,
        "limit": 100
    }

    try:
        response = requests.get(AQI_URL, params=params, timeout=8)
        records = response.json().get("records", [])
    except:
        return jsonify({"error": "CPCB API error"})

    if not records:
        return jsonify({"error": "No data for this city"})

    # Pollutant Processing
    df = pd.DataFrame(records)[["pollutant_id","avg_value"]]
    df["avg_value"] = pd.to_numeric(df["avg_value"], errors="coerce")

    pivot = df.pivot_table(
        values="avg_value",
        columns="pollutant_id",
        aggfunc="mean"
    )

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

    # CO scaling
    if "CO" in pivot.columns:
        pivot["CO"] = pivot["CO"] / 1000

    required_cols = ["PM2.5","PM10","NO2","SO2","CO","O3","NH3"]

    for col in required_cols:
        if col not in pivot.columns:
            pivot[col] = median_values[col]

    pivot = pivot[required_cols]

    # Predict Current AQI
    prediction = model.predict(pivot)[0]
    
    # Fetch Real Weather
    lat = float(records[0]["latitude"])
    lon = float(records[0]["longitude"])

    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current="
        f"temperature_2m,relative_humidity_2m,wind_speed_10m"
    )

    try:
        weather = requests.get(weather_url, timeout=5).json()["current"]
        temperature = weather["temperature_2m"]
        humidity = weather["relative_humidity_2m"]
        wind_speed = weather["wind_speed_10m"]
    except:
        temperature = 25.0
        humidity = 50.0
        wind_speed = 5.0

    # Store in Database
    insert_record(city, prediction, temperature, humidity, wind_speed)

    return jsonify({
        "city": city,
        "predicted_AQI": round(float(prediction), 2),
        "weather": {
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed
        }
    })

# Route: AQI History
@app.route("/history/<city>")
def history(city):
    data = fetch_history(city, limit=8)

    aqi_values = [row[0] for row in data][::-1]
    timestamps = [row[4] for row in data][::-1]

    return jsonify({
        "aqi_values": aqi_values,
        "timestamps": timestamps
    })

# Route: LSTM Forecast
@app.route("/forecast/<city>")
def forecast(city):
    seq = get_last_lstm_sequence(city)

    if seq is None:
        return jsonify({"error": "Not enough history for forecast"})

    pred_scaled = lstm_model.predict(seq)[0][0]

    dummy = np.zeros((1,4))
    dummy[0][0] = pred_scaled
    aqi_unscaled = lstm_scaler.inverse_transform(dummy)[0][0]

    return jsonify({
        "next_hour_AQI": round(float(aqi_unscaled), 2)
    })

# Routes: State & City Lists
@app.route("/states")
def states():
    params = {"api-key": API_KEY, "format": "json", "limit": 1000}
    r = requests.get(AQI_URL, params=params)
    records = r.json().get("records", [])
    states = sorted(list(set(x["state"] for x in records)))
    return jsonify(states)

@app.route("/cities/<state>")
def cities(state):
    params = {
        "api-key": API_KEY,
        "format": "json",
        "filters[state]": state,
        "limit": 1000
    }
    r = requests.get(AQI_URL, params=params)
    records = r.json().get("records", [])
    cities = sorted(list(set(x["city"] for x in records)))
    return jsonify(cities)

# Run Server
if __name__ == "__main__":
    app.run(debug=True)
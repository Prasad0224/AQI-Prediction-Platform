import requests
import pandas as pd
import time

from database.db import init_db, insert_record
from app import model, median_values, AQI_URL, API_KEY, CITY_COORDS

# Initialize DB (creates table if not exists)
init_db()

# -----------------------------
# Get all cities from CPCB API
# -----------------------------
params = {
    "api-key": API_KEY,
    "format": "json",
    "limit": 1000
}

try:
    resp = requests.get(AQI_URL, params=params, timeout=8)
    records = resp.json().get("records", [])
except:
    print("Failed to fetch city list from CPCB API")
    exit()

cities = sorted(list(set(r["city"] for r in records)))

print(f"Found {len(cities)} cities. Starting seeding...\n")

# -----------------------------
# Seed data for each city
# -----------------------------
for city in cities:
    print(f"\nCollecting: {city}")

    # Collect 3 records per city
    for i in range(3):
        print(f"  Record {i+1}/3")

        params_city = {
            "api-key": API_KEY,
            "format": "json",
            "filters[city]": city,
            "limit": 100
        }

        # ---- Fetch CPCB live data safely ----
        try:
            response = requests.get(AQI_URL, params=params_city, timeout=8)

            if response.status_code != 200:
                print("   CPCB API error, skipped")
                continue

            r = response.json()
            rec = r.get("records", [])

        except:
            print("   CPCB API timeout / invalid response, skipped")
            continue

        if not rec:
            print("   No pollutant data, skipped")
            continue

        # ---- Process pollutant data ----
        df = pd.DataFrame(rec)[["pollutant_id", "avg_value"]]
        df["avg_value"] = pd.to_numeric(df["avg_value"], errors="coerce")

        pivot = df.pivot_table(
            values="avg_value",
            columns="pollutant_id",
            aggfunc="mean"
        )

        pivot.columns = [c.lower().replace('.', '') for c in pivot.columns]
        pivot = pivot.rename(columns={
            "pm25": "PM2.5",
            "pm10": "PM10",
            "no2": "NO2",
            "so2": "SO2",
            "co": "CO",
            "ozone": "O3",
            "nh3": "NH3"
        })

        # Convert CO µg/m³ → mg/m³
        if "CO" in pivot.columns:
            pivot["CO"] = pivot["CO"] / 1000

        # Ensure all required columns exist
        required_cols = ["PM2.5","PM10","NO2","SO2","CO","O3","NH3"]

        for col in required_cols:
            if col not in pivot.columns:
                pivot[col] = median_values[col]

        pivot = pivot[required_cols]

        # ---- Predict AQI using ML model ----
        try:
            prediction = model.predict(pivot)[0]
        except:
            print("   ML prediction error, skipped")
            continue

        # ---- Fetch Weather Data safely ----
        lat, lon = CITY_COORDS.get(city, (28.61, 77.20))

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
            # Safe fallback defaults
            temperature = 25.0
            humidity = 50.0
            wind_speed = 5.0

        # ---- Store into Database ----
        insert_record(city, prediction, temperature, humidity, wind_speed)

        print("   Saved")

        # Gentle delay to avoid rate limits
        time.sleep(1)

print("\n🎉 Database seeding completed safely!")
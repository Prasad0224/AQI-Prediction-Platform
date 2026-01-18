import requests
import pandas as pd
import time
from database.db import insert_record
from app import AQI_URL, API_KEY, median_values, model

params = {
    "api-key": API_KEY,
    "format": "json",
    "limit": 1000
}

resp = requests.get(AQI_URL, params=params)
data = resp.json()
records = data.get("records", [])

cities = sorted(list(set(r["city"] for r in records)))
print(f"Found {len(cities)} cities. Starting seeding...\n")

for city in cities:
    print("Seeding:", city)
    count = 0
    attempts = 0

    while count < 5 and attempts < 10:
        attempts += 1

        params_city = {
            "api-key": API_KEY,
            "format": "json",
            "filters[city]": city,
            "limit": 100
        }

        r = requests.get(AQI_URL, params=params_city)
        if r.status_code != 200:
            time.sleep(1)
            continue

        try:
            rec_data = r.json()
        except:
            time.sleep(1)
            continue

        rec = rec_data.get("records", [])
        if not rec:
            time.sleep(1)
            continue

        df = pd.DataFrame(rec)[["pollutant_id","avg_value"]]
        df["avg_value"] = pd.to_numeric(df["avg_value"], errors="coerce")

        pivot = df.pivot_table(values="avg_value", columns="pollutant_id", aggfunc="first")
        pivot.columns = [c.lower().replace('.', '') for c in pivot.columns]
        pivot = pivot.rename(columns={
            "pm25":"PM2.5","pm10":"PM10","no2":"NO2",
            "so2":"SO2","co":"CO","ozone":"O3","nh3":"NH3"
        })

        if "CO" in pivot.columns:
            pivot["CO"] = pivot["CO"] / 1000

        required_cols = ["PM2.5","PM10","NO2","SO2","CO","O3","NH3"]
        for col in required_cols:
            if col not in pivot.columns:
                pivot[col] = median_values[col]

        pivot = pivot[required_cols]

        pred = model.predict(pivot)[0]
        insert_record(city, pred)
        count += 1
        time.sleep(0.3)

    if count < 5:
        print(f" ⚠ Only {count}/5 records seeded")
    else:
        print(" ✅ Done")

print("\n🎉 Database seeding completed safely!")
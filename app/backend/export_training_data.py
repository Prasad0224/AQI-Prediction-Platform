import sqlite3
import pandas as pd

conn = sqlite3.connect("database/aqi_data.db")

df = pd.read_sql("""
SELECT city, predicted_aqi, temperature, humidity, wind_speed, timestamp
FROM aqi_history
ORDER BY timestamp
""", conn)

conn.close()

df.to_csv("../../data/processed/aqi_weather_timeseries.csv", index=False)

print("Export completed:", df.shape)
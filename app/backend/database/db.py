import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "aqi_data.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS aqi_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            predicted_aqi REAL,
            temperature REAL,
            humidity REAL,
            wind_speed REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_record(city, aqi, temp, humidity, wind):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO aqi_history 
        (city, predicted_aqi, temperature, humidity, wind_speed, timestamp) 
        VALUES (?,?,?,?,?,?)
    """, (
        city,
        float(aqi),
        float(temp),
        float(humidity),
        float(wind),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def fetch_history(city, limit=5):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT predicted_aqi, temperature, humidity, wind_speed, timestamp
        FROM aqi_history 
        WHERE city=? 
        ORDER BY id DESC 
        LIMIT ?
    """, (city, limit))
    data = c.fetchall()
    conn.close()
    return data
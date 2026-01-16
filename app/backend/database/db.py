import sqlite3

def init_db():
    conn = sqlite3.connect("aqi_data.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aqi_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            predicted_aqi REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def insert_record(city, predicted_aqi):
    conn = sqlite3.connect("aqi_data.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO aqi_history (city, predicted_aqi)
        VALUES (?, ?)
    """, (city, predicted_aqi))

    conn.commit()
    conn.close()


def fetch_history(city):
    conn = sqlite3.connect("aqi_data.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT predicted_aqi, timestamp 
        FROM aqi_history 
        WHERE city = ?
        ORDER BY timestamp DESC
        LIMIT 15
    """, (city,))

    data = cursor.fetchall()
    conn.close()
    return data
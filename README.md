# 🇮🇳 Air Quality Monitoring & Forecasting Platform

A **real-time Air Quality Index (AQI) Monitoring and Forecasting Web Application** built using **Government of India CPCB live AQI data**, **Machine Learning**, and a **Flask-based web dashboard**.

This project demonstrates a complete **end-to-end ML pipeline** — from live data collection and preprocessing to prediction, database storage, visualization, and short-term forecasting.

---

## 🚀 Features
✔ Live AQI data from **Government of India CPCB API**  
✔ Machine Learning model for **current AQI prediction**  
✔ Time-series model for **next-hour AQI forecasting**  
✔ SQLite database for storing AQI history  
✔ Interactive AQI trend chart (last 5 readings)  
✔ Dynamic **State → City** selection  
✔ Flask REST API backend  
✔ Clean responsive web dashboard  

## ⚙️ Tech Stack
- Python  
- Pandas, NumPy  
- Scikit-learn  
- Flask + Flask-CORS  
- SQLite  
- Chart.js  
- Government of India CPCB AQI API  

## 🖥️ How to Run Locally

### 1️⃣ Install dependencies
pip install -r requirements.txt

### 2️⃣ Start Flask backend
cd app/backend
python app.py

Backend runs at:
http://127.0.0.1:5000

### 3️⃣ Open frontend
Open in browser:
app/frontend/index.html

### 4️⃣Seed database once
To ensure every city has initial AQI history:
cd app/backend
python seed_history.py

## 📊 Model Performance
Current AQI Prediction Model-
R² Score: 0.93
MAE: ~17 AQI units
RMSE: ~27 AQI units

Next-Hour Forecast Model-
MAE: ~5 AQI units

## 🌍 Dashboard Capabilities
Dynamic State → City selection
Real-time AQI prediction
Last 5 AQI trend visualization
Next-hour AQI forecast

## 🎯 Project Highlights
Uses official Government AQI data
End-to-end ML deployment
Real-time data processing
Database-backed time-series forecasting
Fully scalable architecture
# 🌍 Air Quality Prediction & Forecasting Platform

A **real-time Air Quality Monitoring and Forecasting Web Application** that uses **Government of India live AQI data**, **Machine Learning**, and **Time-Series Forecasting** to predict current and next-hour Air Quality Index (AQI).

This project demonstrates an **end-to-end ML pipeline** — from data cleaning and model training to real-time API integration, database storage, and an interactive web dashboard.

---

## 🚀 Features

- 📡 Live AQI data from **Government of India CPCB API**
- 🧠 Machine Learning model for **current AQI prediction**
- 🕒 Time-series forecasting for **next-hour AQI prediction**
- 🗄️ SQLite database for AQI history storage
- 📈 Interactive AQI history chart (Chart.js)
- 🌐 Flask backend REST API
- 💻 Responsive Web Dashboard frontend

---

## 🏗️ Project Architecture
Frontend (HTML + CSS + JS + Chart.js)
↓
Flask Backend API
↓
Live Government AQI API + Weather API
↓
ML Model (Current AQI Prediction)
↓
SQLite Database (AQI History)
↓
Forecast Model (Next-Hour AQI)
↓
Dashboard Visualization


---

## 📁 Project Structure



AQI-Prediction-Platform/
│
├── app/
│ ├── backend/
│ │ ├── app.py # Flask backend
│ │ └── database/
│ │ └── db.py # SQLite operations
│ └── frontend/
│ └── index.html # Web dashboard UI
│
├── data/
│ ├── raw/ # Original Kaggle dataset
│ └── processed/ # Cleaned dataset
│
├── notebooks/
│ ├── 01_data_cleaning.ipynb
│ ├── 02_live_api_testing.ipynb
│ ├── 03_model_training.ipynb
│ └── 04_aqi_forecasting.ipynb
│
├── models/
│ ├── aqi_model.pkl # Current AQI ML model
│ └── aqi_forecast_model.pkl # Next-hour Forecast model
│
├── requirements.txt
└── README.md


---

## ⚙️ Tech Stack

- Python  
- Pandas, NumPy  
- Scikit-learn  
- Flask + Flask-CORS  
- SQLite  
- Chart.js  
- Government of India AQI API  
- Open-Meteo Weather API  

---

## 🖥️ How to Run Locally

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt

2️⃣ Start Flask Backend
cd app/backend
python app.py


Backend runs at:

http://127.0.0.1:5000/

3️⃣ Open Frontend

Open this file in your browser:

app/frontend/index.html

📊 Dashboard Features

Current AQI prediction

Next-hour AQI forecast

AQI history trend chart

Multi-city live monitoring

🎯 Model Performance

Current AQI Model

R² Score: 0.93

MAE: 16.97

RMSE: 27.33

Forecast Model

MAE: ≈ 5 AQI units

🌟 Project Highlights

Real-time integration with government sensor data

Robust handling of missing live sensor values

Feature scaling and unit normalization

End-to-end ML deployment pipeline

Time-series forecasting implementation
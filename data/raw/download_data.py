import requests

API_KEY = "579b464db66ec23bdd000001ba7c83c075784fde7ead526137a405e4"
URL = "https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"

params = {
    "api-key": API_KEY,
    "format": "json",
    "limit": 1000
}

response = requests.get(URL, params=params).json()
records = response["records"]

dates = [r["last_update"] for r in records]

# Convert to sortable format
from datetime import datetime
dates = [datetime.strptime(d, "%d-%m-%Y %H:%M:%S") for d in dates]

print("Earliest available date in API:", min(dates))
print("Latest available date in API:", max(dates))
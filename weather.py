import requests
import json
import time
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("WEATHER_API_KEY")


api_url = "https://api.weatherapi.com/v1/forecast.json"

params = {
    "key": api_key,
    "q": "90045"
}

response = requests.get(api_url, params=params)


# print(response.status_code)

data = response.json()

# print(json.dumps(data, indent=2))

print(data["location"]["name"])
print(data["location"]["region"])
print(data["current"]["temp_f"])
print(data["current"]["condition"]["text"])


zip_codes = [
    "90045", "10001", "60601", "98101", "33101",
    "77001", "85001", "19101", "30301", "55401",
    "80201", "94102", "78201", "02101", "48201",
    "97201", "70112", "89101", "84101", "46201",
    "28201", "37201", "73101", "87101", "50301",
    "66101", "68101", "72201", "53201", "61601",
    "64101", "23219", "37501", "40201", "45201",
    "54601", "57101", "59101", "63101", "65101",
    "83701", "92101", "93401", "95814", "96801",
    "99501", "32801"
]

results = []

for zip_code in zip_codes:
    params = {
        "key": api_key,
        "q": zip_code,
        "days": 7
    }
    response = requests.get(api_url, params=params)
    data = response.json()

    city = data["location"]["name"]

    for day in data["forecast"]["forecastday"]:
        date = day["date"]
        max_temp = day["day"]["maxtemp_f"]
        min_temp = day["day"]["mintemp_f"]
        condition = day["day"]["condition"]["text"]

        results.append({
            "zip_code": zip_code,
            "city": city,
            "date": date,
            "max_temp_f": max_temp,
            "min_temp_f": min_temp,
            "condition": condition
        })

        print(f"{city} {date}: {max_temp}°F / {min_temp}°F, {condition}")
    time.sleep(1)

df = pd.DataFrame(results)
print(df)
print(f"\nRows: {df.shape[0]}, Columns: {df.shape[1]}")

df.to_csv("weather_data.csv", index=False)

import requests
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

# ======================
# 1. Fetch Data from NASA POWER API
# ======================
def fetch_data(lat, lon):
    params = "T2M,PRECTOTCORR,WS10M,RH2M"
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters={params}&start=20000101&end=20241231&latitude={lat}&longitude={lon}&community=AG&format=JSON"
    r = requests.get(url).json()
    
    # convert JSON → DataFrame (each variable separately)
    data = {}
    for var in ["T2M", "PRECTOTCORR", "WS10M", "RH2M"]:
        df = pd.DataFrame(r['properties']['parameter'][var].items(), columns=["Date", var])
        df["Date"] = pd.to_datetime(df["Date"], format="%Y%m%d")
        df[var] = df[var].astype(float)
        df = df.set_index("Date").resample("M").mean().reset_index()
        data[var] = df
    return data

# ======================
# 2. Train SARIMAX + Forecast for One Variable
# ======================
def forecast_variable(df, steps=12):
    series = df.set_index("Date")[df.columns[1]]
    model = SARIMAX(series, order=(1,1,1), seasonal_order=(1,1,1,12))
    result = model.fit(disp=False)

    forecast = result.get_forecast(steps=steps)
    forecast_mean = forecast.predicted_mean
    forecast_ci = forecast.conf_int()

    forecast_dates = pd.date_range(series.index[-1] + pd.DateOffset(months=1), periods=steps, freq="M")
    forecast_df = pd.DataFrame({
        "Date": forecast_dates,
        "Forecast": forecast_mean.values,
        "Lower": forecast_ci.iloc[:,0].values,
        "Upper": forecast_ci.iloc[:,1].values
    })
    return forecast_df

# ======================
# 3. Classification Rules
# ======================
def classify_weather(temp, rain, wind, humidity):
    conditions = []
    if temp > 35:
        conditions.append("Very Hot")
    elif temp < 5:
        conditions.append("Very Cold")
    else:
        conditions.append("Comfortable Temp")

    if rain > 20:  # mm/month تقريبًا
        conditions.append("Very Wet")

    if wind > 20:  # m/s
        conditions.append("Very Windy")

    if humidity > 70:  # %
        conditions.append("Very Uncomfortable (Humidity)")

    return " & ".join(conditions)

# ======================
# 4. Main Function
# ======================
def predict_weather(lat, lon, target_month):
    # 1. Fetch data
    data = fetch_data(lat, lon)

    # 2. Forecast each variable
    forecasts = {}
    for var, df in data.items():
        forecasts[var] = forecast_variable(df, steps=12)

    # 3. Extract requested month
    results = {}
    for var, fdf in forecasts.items():
        user_forecast = fdf[fdf["Date"].dt.month == target_month].iloc[0]
        results[var] = {
            "value": round(user_forecast["Forecast"], 2),
            "lower": round(user_forecast["Lower"], 2),
            "upper": round(user_forecast["Upper"], 2)
        }

    # 4. Classification
    label = classify_weather(
        temp=results["T2M"]["value"],
        rain=results["PRECTOTCORR"]["value"],
        wind=results["WS10M"]["value"],
        humidity=results["RH2M"]["value"]
    )

    # 5. Return JSON-like dict
    return {
        "date": forecasts["T2M"].iloc[0]["Date"].strftime("%Y-%m"),
        "temperature": results["T2M"],
        "rainfall": results["PRECTOTCORR"],
        "windspeed": results["WS10M"],
        "humidity": results["RH2M"],
        "condition": label
    }

# ======================
# 5. Example Run
# ======================
result = predict_weather(24.1, 32.9, target_month=6)
print(result)
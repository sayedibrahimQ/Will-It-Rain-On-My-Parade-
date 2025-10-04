import requests
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import datetime
# ======================
# 1. Fetch Data from NASA POWER API
# ======================
def fetch_data(lat, lon):
    params = "T2M,PRECTOTCORR,WS10M,RH2M"
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters={params}&start=20200101&end=2025930&latitude={lat}&longitude={lon}&community=AG&format=JSON"
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
def classify_variable(var, value):
    if var == "T2M":  # Temperature °C
        if value > 35: return "Very Hot"
        elif value > 30: return "Hot"
        elif value >= 15: return "Comfortable"
        elif value >= 5: return "Cold"
        else: return "Very Cold"

    elif var == "PRECTOTCORR":  # Rainfall mm/month
        if value > 200: return "Very Wet (Heavy Rain)"
        elif value > 100: return "Wet"
        elif value >= 30: return "Light Rain"
        else: return "Dry"

    elif var == "WS10M":  # Windspeed m/s
        if value > 25: return "Stormy (Very Windy)"
        elif value > 15: return "Windy"
        elif value > 5: return "Breezy"
        else: return "Calm"

    elif var == "RH2M":  # Humidity %
        if value > 80: return "Very Uncomfortable (Extremely Humid)"
        elif value > 60: return "Humid"
        elif value >= 30: return "Comfortable Humidity"
        else: return "Dry Air"

    return "Unknown"

# ======================
# 4. Main Function
# ======================
# ======================
# 4. Main Function (UPDATED)
# ======================
def predict_weather(lat, lon, target_date_str):
    target_date = pd.to_datetime(target_date_str)  # YYYY-MM format

    # 1. Fetch data
    data = fetch_data(lat, lon)

    # 2. Forecast each variable
    forecasts = {}
    results = {}
    
    # We need to find the maximum number of months to forecast
    last_data_date = data["T2M"]["Date"].max()
    months_ahead = (target_date.year - last_data_date.year) * 12 + (target_date.month - last_data_date.month)
    if months_ahead <= 0:
        raise ValueError(f"Target date {target_date.strftime('%Y-%m')} must be after last available data {last_data_date.strftime('%Y-%m')}")

    for var, df in data.items():
        forecasts[var] = forecast_variable(df, steps=months_ahead)
        
        user_forecast = forecasts[var][forecasts[var]["Date"].dt.strftime("%Y-%m") == target_date.strftime("%Y-%m")]
        if user_forecast.empty:
            raise ValueError(f"Date {target_date.strftime('%Y-%m')} not in forecast range")

        row = user_forecast.iloc[0]
        val = round(row["Forecast"], 2)

        results[var] = {
            "value": val,
            "lower": round(row["Lower"], 2),
            "upper": round(row["Upper"], 2),
            "condition": classify_variable(var, val)
        }

    # 3. Overall Classification (summary)
    label = " & ".join([results[v]["condition"] for v in results])

    # 4. NEW: Prepare the trend data for the chart
    # We'll take the last 12 months of the forecast
    trend_data_start_index = max(0, months_ahead - 12)
    
    trend_df_temp = forecasts["T2M"].iloc[trend_data_start_index:].copy()
    trend_df_rain = forecasts["PRECTOTCORR"].iloc[trend_data_start_index:].copy()
    
    forecast_trend = []
    c = 0
    for i in range(len(trend_df_temp)):
        if trend_df_temp.iloc[i]["Date"].strftime("%Y-%m") > target_date.strftime("%Y-%m"):
            c += 1
            forecast_trend.append({
                "date": trend_df_temp.iloc[i]["Date"].strftime("%Y-%m"),
                "temperature_forecast": round(trend_df_temp.iloc[i]["Forecast"], 1),
                "temperature_lower": round(trend_df_temp.iloc[i]["Lower"], 1),
                "temperature_upper": round(trend_df_temp.iloc[i]["Upper"], 1),
                "rainfall_forecast": round(trend_df_rain.iloc[i]["Forecast"], 1),
            })
            if c == 5:
                break

    # 5. Return JSON-like dict with the new trend data included
    return {
        "date": target_date.strftime("%Y-%m"),
        "temperature": results["T2M"],
        "rainfall": results["PRECTOTCORR"],
        "windspeed": results["WS10M"],
        "humidity": results["RH2M"],
        "condition": label,
        "forecast_trend": forecast_trend # This is the new key we'll use
    }
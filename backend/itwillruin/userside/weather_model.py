"""
Redesigned weather prediction model for the "Parade Weather" dashboard.

This script fetches daily and hourly data from the NASA POWER API,
trains a SARIMAX time-series model to forecast daily weather conditions,
and simulates an hourly forecast to provide a complete data package for the UI.
"""
import requests
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import datetime, timedelta
import numpy as np
import asyncio

# --- 1. NASA POWER API Data Fetching ---

async def fetch_historical_daily_data(lat, lon, start_date="20200101"):
    """
    Fetches historical daily weather data from NASA POWER API.
    This data is used to train the time-series forecasting models.
    """
    # Added T2M_MAX, T2M_MIN, and ALLSKY_SFC_UVA for high/low temps and UV Index
    params = "T2M_MAX,T2M_MIN,T2M,PRECTOTCORR,WS10M,RH2M,ALLSKY_SFC_UVA"
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters={params}&start={start_date}&end={end_date}&latitude={lat}&longitude={lon}&community=AG&format=JSON"
    
    # In a real async Django app, use an async HTTP client like httpx or aiohttp
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, requests.get, url)
    if response.status_code != 200:
        raise Exception("Failed to fetch data from NASA POWER API.")
    r = response.json()

    # Process the JSON response into a single pandas DataFrame
    df_data = r['properties']['parameter']
    df = pd.DataFrame(df_data)
    df.index = pd.to_datetime(df.index, format='%Y%m%d')
    # NASA POWER uses -999 for missing values; replace with NaN and forward-fill
    df.replace(-999, np.nan, inplace=True)
    df.ffill(inplace=True)
    
    return df

# --- 2. Helper Functions & Data Simulation ---

def calculate_feels_like(temp, humidity):
    """
    Calculates the "feels like" temperature using the Steadman formula (Heat Index).
    Simplified and only effective for temps > 26°C.
    """
    if temp < 26.7: # Heat index is not typically calculated for lower temps
        return temp

    heat_index = -8.7847 + 1.6114 * temp + 2.3385 * humidity - 0.1461 * temp * humidity - 0.0123 * temp**2 - 0.0164 * humidity**2 + 0.0022 * temp**2 * humidity + 0.0007 * temp * humidity**2 - 0.0000036 * temp**2 * humidity**2
    return round(heat_index, 1)

def get_historical_averages(daily_df, target_date):
    """
    Calculates the historical average high and low temperature for a specific day of the year.
    """
    day_of_year = target_date.dayofyear
    historical_day_data = daily_df[daily_df.index.dayofyear == day_of_year]
    
    if historical_day_data.empty:
        return {'avg_high': None, 'avg_low': None}
        
    avg_high = historical_day_data['T2M_MAX'].mean()
    avg_low = historical_day_data['T2M_MIN'].mean()
    
    return {'avg_high': round(avg_high, 1), 'avg_low': round(avg_low, 1)}

def simulate_hourly_forecast(daily_forecast):
    """
    Simulates an hourly forecast for a future date based on predicted daily values.
    This creates the data needed for the hourly chart on the dashboard.
    """
    low_temp = daily_forecast['T2M_MIN']
    high_temp = daily_forecast['T2M_MAX']
    
    temp_range = high_temp - low_temp
    hours = np.arange(24)
    # Simulate a sine wave for temperature, peaking around 3 PM (hour 15)
    hourly_temps = low_temp + (temp_range / 2) * (1 - np.cos((hours - 3) * np.pi / 12))
    
    rain_chance_percent = daily_forecast.get('rain_chance_percent', 15)
    # Distribute rain chance, peaking in the afternoon
    rain_distribution = np.sin(hours * np.pi / 24)**2
    hourly_rain_chance = (rain_distribution / rain_distribution.max()) * rain_chance_percent * 1.5
    hourly_rain_chance = np.clip(hourly_rain_chance, 0, 95)

    # Format for Chart.js
    chart_labels = ['8am', '10am', '12pm', '2pm', '4pm', '6pm', '8pm', '10pm']
    chart_temps = [round(hourly_temps[i], 1) for i in [8, 10, 12, 14, 16, 18, 20, 22]]
    chart_rain_chances = [int(hourly_rain_chance[i]) for i in [8, 10, 12, 14, 16, 18, 20, 22]]
        
    return {
        'labels': chart_labels,
        'temperatures': chart_temps,
        'rain_chances': chart_rain_chances
    }

# --- 3. Time-Series Forecasting ---

def forecast_daily_variable(series, steps=1):
    """
    Trains a SARIMAX model and forecasts a single variable for a number of days ahead.
    """
    # Using a weekly seasonality (m=7) for daily data
    model = SARIMAX(series, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7),
                    enforce_stationarity=False, enforce_invertibility=False)
    result = model.fit(disp=False)
    
    forecast = result.get_forecast(steps=steps)
    return forecast.predicted_mean.iloc[-1] # Return the last day's forecast

# --- 4. Main Prediction Orchestrator ---

async def get_weather_prediction_for_day(lat, lon, target_date_str):
    """
    Main function to generate a complete weather forecast package for the dashboard.
    """
    target_date = pd.to_datetime(target_date_str)
    
    # 1. Fetch historical data for model training
    historical_df = await fetch_historical_daily_data(lat, lon)
    
    # 2. Forecast each required variable for the target date
    last_known_date = historical_df.index.max()
    days_to_forecast = (target_date.date() - last_known_date.date()).days
    
    daily_forecast = {}
    if days_to_forecast < 1:
        print(f"Target date {target_date_str} is in the past or today. Using historical data.")
        day_data = historical_df.loc[historical_df.index.date == target_date.date()].iloc[0]
        daily_forecast = day_data.to_dict()
    else:
        variables_to_forecast = ['T2M_MAX', 'T2M_MIN', 'T2M', 'PRECTOTCORR', 'RH2M', 'WS10M', 'ALLSKY_SFC_UVA']
        for var in variables_to_forecast:
            daily_forecast[var] = forecast_daily_variable(historical_df[var], steps=days_to_forecast)

    # 3. Calculate derived metrics
    historical_averages = get_historical_averages(historical_df, target_date)
    feels_like_temp = calculate_feels_like(daily_forecast['T2M'], daily_forecast['RH2M'])
    # Estimate rain chance from precipitation amount (heuristic)
    rain_chance_percent = min(int(daily_forecast['PRECTOTCORR'] * 20), 100)
    daily_forecast['rain_chance_percent'] = rain_chance_percent
    
    # 4. Simulate hourly forecast for the chart
    hourly_forecast_data = simulate_hourly_forecast(daily_forecast)

    # 5. Assemble the final data package for the dashboard
    dashboard_data = {
        'main_overview': {
            'temp': round(daily_forecast['T2M'], 1),
            'condition': "Partly Cloudy", # Placeholder, can be replaced by an AI model
            'high_temp': round(daily_forecast['T2M_MAX'], 1),
            'low_temp': round(daily_forecast['T2M_MIN'], 1),
            'feels_like': feels_like_temp,
            'rain_chance': rain_chance_percent
        },
        'detailed_metrics': {
            'precipitation_mm': max(0, round(daily_forecast['PRECTOTCORR'], 1)),
            'humidity_percent': int(daily_forecast['RH2M']),
            'wind_speed_kmh': int(daily_forecast['WS10M'] * 3.6), # m/s to km/h
            'uv_index': int(daily_forecast['ALLSKY_SFC_UVA'] / 25) if daily_forecast['ALLSKY_SFC_UVA'] > 0 else 0, # Simple UVA to Index conversion
            'visibility_km': 10 # Placeholder, as this is not available from POWER API
        },
        'hourly_forecast_chart': {
            'labels': hourly_forecast_data['labels'],
            'datasets': [
                {'label': 'Temperature (°C)', 'data': hourly_forecast_data['temperatures']},
                {'label': 'Rain Chance (%)', 'data': hourly_forecast_data['rain_chances']}
            ]
        },
        'historical_comparison_chart': {
            'labels': ['Forecasted', 'Historical Average'],
            'datasets': [
                {'label': 'High Temp (°C)', 'data': [round(daily_forecast['T2M_MAX'], 1), historical_averages['avg_high']]},
                {'label': 'Low Temp (°C)', 'data': [round(daily_forecast['T2M_MIN'], 1), historical_averages['avg_low']]}
            ]
        }
    }
    
    return dashboard_data

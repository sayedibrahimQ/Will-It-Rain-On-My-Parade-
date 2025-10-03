from django.shortcuts import render
from django.http import HttpResponse
from .utils import get_city_from_latlon , get_weather_analysis_json 
import logging # Using logging is better for production
from dotenv import load_dotenv
from datetime import datetime

# It's good practice to set up a logger
logger = logging.getLogger(__name__)


# Load environment variables from .env file
load_dotenv()

def home(request):
    
    return render(request, 'index.html')

def map(request):
    return render(request, 'map.html')

def dashboard(request):
    
    if request.method == "POST":
        location = request.POST.get("location")  # text input (if user typed)
        # hidden input (from map click)
        date = request.POST.get("date")

        lat = request.POST.get("latitude")  
        lon = request.POST.get("longitude")  
        location = get_city_from_latlon(lat, lon)
        
        historical_data = {
            "location": location, # Use the determined location name
            "time_period": 'auhost', # You would calculate this from the 'date' variable
            "avg_temp_c": 30,
            "chance_of_rain_percent": 45,
            "avg_wind_speed_kph": 10,
            "dominant_condition": "Humid with afternoon thunderstorms",
            "heat_index_advisory_chance_percent": 70,
            "uv_index_avg": 10
        }
        ai_insights = get_weather_analysis_json(historical_data)
        return render(request, 'dashboard.html', {"location": location, "lat": lat, "lon": lon, "date": date, 'ai_insights': ai_insights})

    return render(request, 'dashboard.html')




def weather_planner_view(request):
    context = {}
    if request.method == 'POST':
        # --- Cleaned up user input handling ---
        latlon = request.POST.get("latlon")      # e.g., "29.7604,-95.3698"
        date = request.POST.get('date')          # e.g., '2025-08-15'
        lat = latlon.split(",")[0]
        lon = latlon.split(",")[1]
        # Determine the location name
        location = get_city_from_latlon(lat, lon)
        
        # --- Fetch and process historical data from NASA APIs ---
        # This is where your core logic to get data from NASA for the lat, lon, and date goes.
        # For now, we'll use dummy data as before.
        
        # You should replace the hardcoded values with your actual fetched data
        historical_data = {
            "location": location, # Use the determined location name
            "time_period": date.strftime("%Y-%m-%d"), # You would calculate this from the 'date' variable
            "avg_temp_c": 30,
            "chance_of_rain_percent": 45,
            "avg_wind_speed_kph": 10,
            "dominant_condition": "Humid with afternoon thunderstorms",
            "heat_index_advisory_chance_percent": 70,
            "uv_index_avg": 10
        }

        # --- Call the Gemini utility function to get insights ---
        ai_insights = get_weather_analysis_json(historical_data)

        # --- Add data to the context for rendering ---
        context['historical_data'] = historical_data
        context['ai_insights'] = ai_insights
        context['submitted'] = True

    return render(request, 'planner.html', context)
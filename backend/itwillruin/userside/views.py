"""
Django views for the Parade Weather application.

This file implements modern, asynchronous views to provide a responsive user experience.
- Standard views render the page templates.
- An async API endpoint handles data-intensive requests for weather predictions,
  allowing the frontend to load immediately and display data as it becomes available.
"""
import json
import asyncio
import logging
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from asgiref.sync import sync_to_async
from datetime import datetime

# It's good practice to import from your app's modules.
# We assume the new weather model is in 'weather_model.py'.
from .weather_model import get_weather_prediction_for_day
from .utils import get_city_from_latlon, get_weather_analysis_json

# A single logger for the views module is a good practice.
logger = logging.getLogger(__name__)

# --- Static Page Views ---

def home_view(request):
    """Renders the home page."""
    return render(request, 'index.html')

def map_view(request):
    """Renders the prediction page with the map."""
    return render(request, 'map.html')

def insights_view(request):
    """Renders the AI insights page."""
    return render(request, 'insights.html')

def about_view(request):
    """Renders the about page."""
    return render(request, 'about.html')


async def dashboard_view(request):
    """
    Renders the main dashboard.
    On GET, it shows the prediction page to start a forecast.
    On POST, it fetches data asynchronously and renders the dashboard with results.
    """
    if request.method != 'POST':
        # A GET request to the dashboard should redirect to the prediction page
        # as there's no data to display yet.
        return render(request, 'map.html')

    try:
        lat = request.POST.get('lat')
        lon = request.POST.get('lon')
        date_str = request.POST.get('date')

        if not all([lat, lon, date_str]):
            # Handle missing data gracefully
            return render(request, 'nodata.html', {'error': 'Latitude, longitude, and date are required.'})

        # The view is now async, so we can correctly 'await' the coroutine.
        # This resolves the RuntimeWarning.
        data = await get_weather_prediction_for_day(lat, lon, date_str)
        
        # Use sync_to_async for synchronous functions to avoid blocking the event loop.
        city = await sync_to_async(get_city_from_latlon)(lat, lon)
        
        # Format date for display
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%B %d, %Y")

        context = {
            'date': formatted_date,
            "city": city,
            "data": data,
            # Pass chart data to the template for use with the json_script tag
            "hourly_chart_data": data.get('hourly_forecast_chart', {}),
            "historical_chart_data": data.get('historical_comparison_chart', {})
        }
        return render(request, 'dashboard.html', context)

    except Exception as e:
        logger.error(f"Error in dashboard_view: {e}", exc_info=True)
        # It's good practice to show an error to the user.
        return render(request, 'error.html', {'error': 'Could not generate forecast. Please try again.'})


# --- Asynchronous API View ---

async def weather_forecast_api(request):
    """
    An asynchronous API endpoint to fetch and process weather forecast data.
    This is called by the JavaScript on the prediction and dashboard pages.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        # Best practice for APIs is to receive JSON data in the request body.
        data = json.loads(request.body)
        lat_str = data.get('latitude')
        lon_str = data.get('longitude')
        date_str = data.get('date')

        # Validate input parameters
        if not all([lat_str, lon_str, date_str]):
            return HttpResponseBadRequest('Missing required parameters: latitude, longitude, date.')
        
        lat = float(lat_str)
        lon = float(lon_str)
        # Check date format
        datetime.strptime(date_str, '%Y-%m-%d')

    except (json.JSONDecodeError, TypeError, ValueError) as e:
        logger.warning(f"Invalid input for weather_forecast_api: {e}")
        return HttpResponseBadRequest('Invalid input format. Latitude/Longitude must be numbers and date must be YYYY-MM-DD.')

    try:
        # 1. Await the primary weather data forecast from the model.
        logger.info(f"Fetching weather prediction for {lat}, {lon} on {date_str}")
        weather_data = await get_weather_prediction_for_day(lat, lon, date_str)

        # 2. Prepare a richer dataset for the AI analysis call.
        location_name = await sync_to_async(get_city_from_latlon)(lat, lon)
        
        main_overview = weather_data.get('main_overview', {})
        detailed_metrics = weather_data.get('detailed_metrics', {})
        ai_prompt_data = {
            "location": location_name,
            "date": date_str,
            "condition": main_overview.get('condition'),
            "high_temp_c": main_overview.get('high_temp'),
            "low_temp_c": main_overview.get('low_temp'),
            "feels_like_c": main_overview.get('feels_like'),
            "chance_of_rain_percent": main_overview.get('rain_chance'),
            "precipitation_mm": detailed_metrics.get('precipitation_mm'),
            "humidity_percent": detailed_metrics.get('humidity_percent'),
            "wind_speed_kmh": detailed_metrics.get('wind_speed_kmh'),
            "uv_index": detailed_metrics.get('uv_index'),
        }
        
        # 3. Await the AI insights using the richer data.
        logger.info("Fetching AI analysis.")
        ai_insights = await sync_to_async(get_weather_analysis_json)(ai_prompt_data)

        # 4. Combine all results into the final JSON response.
        full_response = {
            'weather_data': weather_data,
            'ai_insights': ai_insights,
            'location_name': location_name,
            'request_date': date_str,
        }
        return JsonResponse(full_response)

    except Exception as e:
        logger.error(f"Error in weather_forecast_api: {e}", exc_info=True)
        return JsonResponse({'error': 'An error occurred while processing your request.'}, status=500)


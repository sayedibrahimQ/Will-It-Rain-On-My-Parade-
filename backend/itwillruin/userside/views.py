import json
from django.shortcuts import render
from django.http import HttpResponse
from .utils import get_city_from_latlon , get_weather_analysis_json 
import logging # Using logging is better for production
from dotenv import load_dotenv
from datetime import datetime
from .Forecasting_pipline import predict_weather
# It's good practice to set up a logger
logger = logging.getLogger(__name__)


# Load environment variables from .env file
load_dotenv()

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def team(request):
    return render(request, 'team.html')

def map(request):
    return render(request, 'map.html')

def dashboard(request):
    
    if request.method == "POST":
        location = request.POST.get("location")  # text input (if user typed)
        # hidden input (from map click)
        date = request.POST.get("date")
        # convert string -> datetime object
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()

        # format year-month only
        year_month = date_obj.strftime("%Y-%m")
        lat = request.POST.get("latitude")  
        lon = request.POST.get("longitude")  
        location = get_city_from_latlon(lat, lon)
        
        result_data = predict_weather(lat, lon, year_month)
        forecast_trend_data = result_data.get("forecast_trend", [])
        forecast_trend_json = json.dumps(forecast_trend_data)
        historical_data = {
            "location": location, 
            "time_period": {date_obj.strftime('%b')}, 
            "avg_temp_c": (result_data['temperature']['upper'] + result_data['temperature']['lower']) / 2,
            "chance_of_rain_percent": (result_data['rainfall']['upper'] + result_data['rainfall']['lower']) / 2,
            "avg_wind_speed_kph": (result_data['windspeed']['upper'] + result_data['windspeed']['lower']) / 2,
            "dominant_condition": result_data['condition'],
            "heat_index_advisory_chance_percent": result_data['humidity']['value'] * result_data['temperature']['value'] * 0.35,
        }
        ai_insights = get_weather_analysis_json(historical_data)
        # ai_insights = None
        return render(request, 'dashboard.html', {"location": location, "lat": lat, "lon": lon, "date": date, 'ai_insights': ai_insights, 'day_data': result_data, 'forecast_trend_json': forecast_trend_json })

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






from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO

def download_report(request):
    # 1. Get query parameters from the URL
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")
    date_str = request.GET.get("date")
    # ai_insights = request.GET.get("ainsights")

    # 2. Basic validation
    if not all([lat, lon, date_str]):
        return HttpResponse("Error: Missing required parameters (lat, lon, date).", status=400)

    try:
        # 3. Re-run the data generation logic (same as in dashboard view)
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        year_month = date_obj.strftime("%Y-%m")
        
        location = get_city_from_latlon(lat, lon)
        result_data = predict_weather(lat, lon, year_month)

        # Create historical_data dict for the AI
        historical_data = {
            "location": location, 
            "time_period": date_obj.strftime('%B %Y'), 
            "avg_temp_c": (result_data['temperature']['upper'] + result_data['temperature']['lower']) / 2,
            "chance_of_rain_percent": (result_data['rainfall']['upper'] + result_data['rainfall']['lower']) / 2,
            "avg_wind_speed_kph": (result_data['windspeed']['upper'] + result_data['windspeed']['lower']) / 2,
            "dominant_condition": result_data['condition'],
            "heat_index_advisory_chance_percent": result_data['humidity']['value'] * result_data['temperature']['value'] * 0.35,
        }
        ai_insights = get_weather_analysis_json(historical_data)

        # 4. Prepare context for the PDF template
        context = {
            "location": location,
            "date": date_str,
            "day_data": result_data,
            "ai_insights": ai_insights,
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 5. Render the HTML template to a string
        template = get_template('report_template.html')
        html = template.render(context)

        # 6. Generate the PDF
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

        if not pdf.err:
            # 7. Create the HTTP response with PDF content
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            # This header tells the browser to download the file
            filename = f"Weather_Report_{location.replace(' ', '_')}_{date_str}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        return HttpResponse(f"An error occurred while generating the report: {e}", status=500)

    return HttpResponse("Error generating PDF.", status=500)
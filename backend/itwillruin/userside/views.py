from django.shortcuts import render
from django.http import HttpResponse
from .utils import get_city_from_latlon

def home(request):
    
    return render(request, 'index.html')

def dashboard(request):
    
    if request.method == "POST":
        location = request.POST.get("location")  # text input (if user typed)
        latlon = request.POST.get("latlon")      # hidden input (from map click)
        date = request.POST.get("date")
        # If user picked from map
        if latlon:
            lat, lon = latlon.split(",")
        else:
            lat, lon = None, None
        lat = latlon.split(",")[0]
        lon = latlon.split(",")[1]
        location = get_city_from_latlon(lat, lon)
        
        return render(request, 'dashboard.html', {"location": location, "lat": lat, "lon": lon, "date": date})

    return render(request, 'dashboard.html')


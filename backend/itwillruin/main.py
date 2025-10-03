import requests
import pandas as pd
url = "https://power.larc.nasa.gov/api/temporal/daily/point"
params = {
    "parameters": "T2M,T2M_MAX,T2M_MIN,PRECTOT",
    "community": "AG",
    "longitude": 31.2357,
    "latitude": 30.0444,
    "start": "19910101",
    "end": "20250930",
    "format": "JSON"
}

r = requests.get(url, params=params)
data = r.json()

# Convert to pandas DataFrame
df = pd.DataFrame(data['properties']['parameter'])

# Set date index
df.index.name = "Date"

# Save to Excel
df.to_excel("cairo_weather.xlsx")
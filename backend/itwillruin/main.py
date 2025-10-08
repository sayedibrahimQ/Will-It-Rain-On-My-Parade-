# import requests
# import pandas as pd
# url = "https://power.larc.nasa.gov/api/temporal/daily/point"
# params = {
#     "parameters": "T2M,T2M_MAX,T2M_MIN,PRECTOT,WS2M,ALLSKY_KT",
#     "community": "AG",
#     "longitude": 31.2357,
#     "latitude": 30.0444,
#     "start": "19910101",
#     "end": "20250930",
#     "format": "JSON"
# }

# r = requests.get(url, params=params)
# data = r.json()

# # Convert to pandas DataFrame
# df = pd.DataFrame(data['properties']['parameter'])

# df.index = pd.to_datetime(df.index, format="%Y%m%d")

# # Reset index if you want a Date column instead of index
# df = df.reset_index().rename(columns={"index": "Date"})


# df.to_excel("cairo_weather.xlsx", index=False)


import xarray as xr

url = "https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDF.07/1998/01/3B-DAY.MS.MRG.3IMERG.19980101-S000000-E235959.V07B.nc4"
ds = xr.open_dataset(url, engine="netcdf4")

print(ds)
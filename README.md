# Weather Predictor — Project Spec

**Purpose:** A Django web app that predicts the weather for a user-specified date and location using a replaceable ML model (trained externally). The app accepts a date and location and returns a predicted weather label (e.g., Sunny, Rain), numeric values (temperature, precipitation probability, wind speed, humidity), and a confidence score. The model artifact will be stored in `predictor/models/` and can be replaced either by file-replace or via an admin upload UI.

**Inputs**
- date (YYYY-MM-DD) — required
- location — City name OR latitude & longitude (decide one)

**Outputs**
- Predicted label(s) (e.g., Sunny / Rain / Cloudy)
- Numeric weather values: temperature (°C), precipitation probability (%), wind speed (m/s), humidity (%)
- Confidence/probability and model metadata (name/version, trained date range)
- Optional: 7-day historical mini-chart and satellite thumbnail with "Open in Worldview" link

**Model**
- Expected file path: `predictor/models/weather_model.joblib` (changeable)
- Accepted formats: joblib/pickle (.joblib/.pkl) or .h5 (Keras)
- There will be a loader utility that loads model + scaler and exposes `predict(date, location)`.

**Data sources**
- Primary: NASA (MERRA-2, GPM IMERG) via Earthdata / GES DISC OPeNDAP
- Optional: MODIS (imagery), GLDAS (hydrology)

**Frontend**
- TailwindCSS + Lottie for icons recommended
- Result page shows an icon, main numbers, confidence, and a small chart

**Notes**
- Admin method to replace model must be documented in README.

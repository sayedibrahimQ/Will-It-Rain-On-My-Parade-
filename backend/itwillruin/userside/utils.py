
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import requests
import logging # Using logging is better for production
from google import genai
from google.genai import types
# It's good practice to set up a logger
logger = logging.getLogger(__name__)


def get_city_from_latlon(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    response = requests.get(url, headers={"User-Agent": "django-app"})
    data = response.json()

    # Example structure: data["address"]["city"] or ["town"] or ["village"]
    address = data.get("address", {})
    city = address.get("city") or address.get("town") or address.get("village") or "Unknown"
    return city



# Load environment variables from .env file
load_dotenv()



def get_weather_analysis_json(weather_data: dict) -> dict:
    """
    Generates a weather analysis JSON by calling the Gemini API.

    Args:
        weather_data: A dictionary containing weather information.

    Returns:
        A dictionary with the structured weather analysis,
        or an error dictionary if something goes wrong.
    """
    try:
        # Initialize the client inside the function if you prefer,
        # or you can initialize it once outside if you're calling this frequently.
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        model_name = "gemini-2.5-pro" # Using 1.5 Pro as it's generally recommended

        # The user's prompt, now correctly formatted inside the function
        prompt_text = f"""
        **Input Data:**
        - Location: {weather_data.get('location', 'N/A')}
        - Time of Year: {weather_data.get('time_period', 'N/A')}
        - Average Temperature: {weather_data.get('avg_temp_c', 'N/A')}°C
        - Chance of Precipitation: {weather_data.get('chance_of_rain_percent', 'N/A')}%
        - Average Wind Speed: {weather_data.get('avg_wind_speed_kph', 'N/A')} km/h
        - Typical Dominant Condition: {weather_data.get('dominant_condition', 'N/A')}
        - Chance of 'Very Hot' (Heat Index Advisory): {weather_data.get('heat_index_advisory_chance_percent', 'N/A')}%
        - Average UV Index: {weather_data.get('uv_index_avg', 'N/A')}
        """

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt_text)],
            ),
        ]

        # Your configuration for forcing JSON output
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=genai.types.Schema(
                type=genai.types.Type.OBJECT,
                required=["summary", "parade_planner", "nasa_fun_fact"],
                properties={
                    "summary": genai.types.Schema(type=genai.types.Type.STRING),
                    "parade_planner": genai.types.Schema(
                        type=genai.types.Type.OBJECT,
                        required=["overall_outlook", "clothing_recommendation", "contingency_plan"],
                        properties={
                            "overall_outlook": genai.types.Schema(type=genai.types.Type.STRING),
                            "clothing_recommendation": genai.types.Schema(type=genai.types.Type.STRING),
                            "contingency_plan": genai.types.Schema(type=genai.types.Type.STRING),
                        },
                    ),
                    "nasa_fun_fact": genai.types.Schema(type=genai.types.Type.STRING),
                },
            ),
            # This system instruction is crucial for guiding the model
            system_instruction=[
                types.Part.from_text(text="""
                You are an expert meteorologist and AI assistant for a NASA Space Apps project called \"Will It Rain On My Parade?\".
                Your task is to analyze the following historical weather data for a specific location and time of year.
                Provide a user-friendly summary and actionable recommendations for someone planning an outdoor event like a parade, hike, or vacation.
                1.  Start with a friendly, conversational summary of what the weather is typically like.
                2.  Provide a "Parade Planner" section with clear, actionable recommendations.
                3.  Generate a "NASA Fun Fact" related to weather, climate, or Earth observation.
                4.  Your entire response **MUST** be in a valid JSON format. Do not include any text before or after the JSON object.

                **Required JSON Format:**
                {{
                "summary": "A concise, conversational summary of the typical weather conditions.",
                "parade_planner": {{
                    "overall_outlook": "A rating like 'Good', 'Fair with caution', or 'Challenging'.",
                    "clothing_recommendation": "Specific advice on what to wear (e.g., light layers, sunscreen, hat).",
                    "contingency_plan": "Advice on what to prepare for (e.g., have a backup indoor location, bring umbrellas)."
                }},
                "nasa_fun_fact": "An interesting fact related to NASA's Earth observation or weather satellites."
                }}
                """)
            ],
        )

        # Use the regular generate_content for non-streaming, as it's simpler
        # The API handles assembling the JSON for you.
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=generate_content_config,
        )

        # The response.text will contain the complete JSON string
        json_string = response.text
        
        # Parse the JSON string into a Python dictionary
        return json.loads(json_string)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from API: {e}")
        return {"error": "Failed to parse JSON response from the model.", "raw_response": json_string}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": "An unexpected error occurred while generating the content."}
























def generate_weather_insights(weather_data: dict):
    """
    Analyzes historical weather data using Gemini AI to generate a summary and recommendations.

    Args:
        weather_data (dict): A dictionary containing structured historical weather data.
                             Example:
                             {
                                 "location": "New York City, USA",
                                 "time_period": "Third week of July",
                                 "avg_temp_c": 24,
                                 "chance_of_rain_percent": 35,
                                 "avg_wind_speed_kph": 12,
                                 "dominant_condition": "Partly Cloudy",
                                 "heat_index_advisory_chance_percent": 20,
                                 "uv_index_avg": 8
                             }

    Returns:
        dict: A dictionary containing the generated summary and recommendations,
              or a fallback dictionary if an error occurs.
    """
    # This check for the API key is now moved to the top-level of the module.
    # If the configure() call fails, the generate_content() call will fail,
    # and the except block below will catch it. This is more robust.
    # The line `if not genai.conf.api_key:` has been REMOVED as it caused the error.

    # This prompt engineering is key to getting a good, structured response.
    prompt = f"""
    You are an expert meteorologist and AI assistant for a NASA Space Apps project called "Will It Rain On My Parade?".
    Your task is to analyze the following historical weather data for a specific location and time of year.
    Provide a user-friendly summary and actionable recommendations for someone planning an outdoor event like a parade, hike, or vacation.

    **Input Data:**
    - Location: {weather_data.get('location', 'N/A')}
    - Time of Year: {weather_data.get('time_period', 'N/A')}
    - Average Temperature: {weather_data.get('avg_temp_c', 'N/A')}°C
    - Chance of Precipitation: {weather_data.get('chance_of_rain_percent', 'N/A')}%
    - Average Wind Speed: {weather_data.get('avg_wind_speed_kph', 'N/A')} km/h
    - Typical Dominant Condition: {weather_data.get('dominant_condition', 'N/A')}
    - Chance of 'Very Hot' (Heat Index Advisory): {weather_data.get('heat_index_advisory_chance_percent', 'N/A')}%
    - Average UV Index: {weather_data.get('uv_index_avg', 'N/A')}

    **Instructions:**
    1.  Start with a friendly, conversational summary of what the weather is typically like.
    2.  Provide a "Parade Planner" section with clear, actionable recommendations.
    3.  Generate a "NASA Fun Fact" related to weather, climate, or Earth observation.
    4.  Your entire response **MUST** be in a valid JSON format. Do not include any text before or after the JSON object.

    **Required JSON Format:**
    {{
      "summary": "A concise, conversational summary of the typical weather conditions.",
      "parade_planner": {{
        "overall_outlook": "A rating like 'Good', 'Fair with caution', or 'Challenging'.",
        "clothing_recommendation": "Specific advice on what to wear (e.g., light layers, sunscreen, hat).",
        "contingency_plan": "Advice on what to prepare for (e.g., have a backup indoor location, bring umbrellas)."
      }},
      "nasa_fun_fact": "An interesting fact related to NASA's Earth observation or weather satellites."
    }}
    """

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # Clean up the response to ensure it's valid JSON
        # Models sometimes wrap JSON in markdown backticks
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        
        # Parse the JSON string into a Python dictionary
        insights = json.loads(cleaned_response_text)
        return insights

    except Exception as e:
        # Handle potential errors from API key issues, API calls, or JSON parsing
        logger.error(f"An error occurred while generating AI insights: {e}")
        # Return a fallback response so your app doesn't crash
        return {
            "summary": "We couldn't generate AI-powered insights at this moment. Please check the historical data manually.",
            "parade_planner": {
                "overall_outlook": "N/A",
                "clothing_recommendation": "N/A",
                "contingency_plan": "N/A"
            },
            "nasa_fun_fact": "NASA's Earth-observing satellites, like the GOES series, help us monitor our planet's weather and climate patterns from space, providing critical data for forecasting."
        }
        
        
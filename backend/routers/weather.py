import requests
from fastapi import APIRouter, HTTPException, Query
from starlette.concurrency import run_in_threadpool
from datetime import datetime
from zoneinfo import ZoneInfo

from .. import schemas
from ..config import settings

router = APIRouter(
    tags=["Weather"]
)

def get_daily_weather(lat: float, lon: float, days: int = 7):
    """
    Fetches weather data from the OpenWeatherMap API.
    This is a synchronous function and should be run in a thread pool.
    """
    if settings.GOOGLE_MAPS_API_KEY == "YOUR_GOOGLE_MAPS_API_KEY_HERE":
        raise HTTPException(
            status_code=500,
            detail="Google Maps API key is not configured on the server."
        )

    api_url = f"https://weather.googleapis.com/v1/forecast/days:lookup?key={settings.GOOGLE_MAPS_API_KEY}&location.latitude={lat}&location.longitude={lon}&days={days}&pageSize={days+1}&unitsSystem=METRIC"
    
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        if "forecastDays" not in response.json():
            return {}
        return response.json()
    except requests.exceptions.RequestException as e:
        try:
            error_data = e.response.json()
            error_message = error_data.get("error", {}).get("message", str(e))
            raise HTTPException(status_code=e.response.status_code, detail=f"Error from Google Weather API: {error_message}")
        except (ValueError, AttributeError):
            raise HTTPException(status_code=503, detail=f"Could not connect to weather service: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching weather data: {e}")

def get_hourly_weather(lat: float, lon: float, hours: int = 24):
    """
    Fetches weather data from the OpenWeatherMap API.
    This is a synchronous function and should be run in a thread pool.
    """
    if settings.GOOGLE_MAPS_API_KEY == "YOUR_GOOGLE_MAPS_API_KEY_HERE":
        raise HTTPException(
            status_code=500,
            detail="Google Maps API key is not configured on the server."
        )

    api_url = f"https://weather.googleapis.com/v1/forecast/hours:lookup?key={settings.GOOGLE_MAPS_API_KEY}&location.latitude={lat}&location.longitude={lon}&hours={hours}&pageSize={hours+1}&unitsSystem=METRIC"
    
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        if "forecastHours" not in response.json():
            return {}
        return response.json()
    except requests.exceptions.RequestException as e:
        try:
            error_data = e.response.json()
            error_message = error_data.get("error", {}).get("message", str(e))
            raise HTTPException(status_code=e.response.status_code, detail=f"Error from Google Weather API: {error_message}")
        except (ValueError, AttributeError):
            raise HTTPException(status_code=503, detail=f"Could not connect to weather service: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching weather data: {e}")

@router.get("/weather", response_model=schemas.WeatherResponse)
async def get_weather_forecast(
    lat: float = Query(..., description="Latitude for the weather forecast", example=28.6139),
    lon: float = Query(..., description="Longitude for the weather forecast", example=77.2090)
):
    """
    Provides a 7-day weather forecast for a given latitude and longitude using Google Weather API.
    """
    raw_weather_data = await run_in_threadpool(get_daily_weather, lat, lon, days=7)

    try:
        return schemas.WeatherResponse.model_validate(raw_weather_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse weather data from external API: {e}")

@router.get("/spraying-conditions", response_model=schemas.SprayingConditionsResponse)
async def get_spraying_conditions(
    lat: float = Query(..., description="Latitude for the location", example=28.6139),
    lon: float = Query(..., description="Longitude for the location", example=77.2090)
):
    """
    Provides an hourly breakdown of ideal spraying conditions for the next 24 hours.
    Conditions are rated as 'Good', 'Moderate', or 'Bad' based on temperature,
    wind speed, precipitation chance, and humidity.
    """
    raw_hourly_data = await run_in_threadpool(get_hourly_weather, lat, lon, hours=24)

    if "forecastHours" not in raw_hourly_data:
        raise HTTPException(status_code=404, detail="Hourly weather data not available for this location.")

    spraying_conditions = []
    for hour_data in raw_hourly_data.get("forecastHours", []):
        temp = hour_data.get("temperature", {}).get("degrees", 0.0)
        wind_kph = hour_data.get("wind", {}).get("speed", {}).get("value", 0.0)
        gust_kph = hour_data.get("wind", {}).get("gust", {}).get("value", 0.0)
        precip_chance = hour_data.get("precipitation", {}).get("probability", {}).get("percent", 0)
        humidity = hour_data.get("relativeHumidity", 0)
        wet_bulb_temp = hour_data.get("wetBulbTemperature", {}).get("degrees", 0)
        dew_point = hour_data.get("dewPoint", {}).get("degrees", 0)
        utc_time_str = hour_data.get("interval", {}).get("endTime")

        if utc_time_str:
            try:
                utc_dt = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
                ist_dt = utc_dt.astimezone(ZoneInfo("Asia/Kolkata"))
                time = ist_dt.isoformat()
            except (ValueError, TypeError):
                time = utc_time_str
        else:
            time = "Time not available"
            

        delta_t = temp - wet_bulb_temp
        dew_gap = temp - dew_point
        
        reasons = []
        condition = "Good"

        if temp < 4 or temp > 30:
            reasons.append(f"Temp ({temp:.1f}°C) out of safe range (4-30°C)")
            condition = "Bad"
            
        if wind_kph > 14 or gust_kph > 18:
            reasons.append(f"Wind ({wind_kph:.1f} kph, gust {gust_kph:.1f} kph) too strong (>14 kph or gust >18 kph)")
            condition = "Bad"
            
        if precip_chance > 25:
            reasons.append(f"Rain chance ({precip_chance}%) is too high (>25%)")
            condition = "Bad"
        
        if delta_t > 10:
            reasons.append(f"Delta T ({delta_t:.1f}°C) is too high (>10), high evaporation risk")
            condition = "Bad"
            
        if humidity < 20 or humidity > 90:
            reasons.append(f"Humidity ({humidity}%) is extreme (<20% or >90%)")
            condition = "Bad"

        if dew_gap < 2:
            reasons.append(f"Leaves likely wet (dew gap {dew_gap:.1f}°C < 2°C)")
            condition = "Bad"

        if condition == "Good":
            if 8 < wind_kph <= 14:
                reasons.append(f"Wind ({wind_kph:.1f} kph) is high (8-14 kph)")
                condition = "Moderate"
                
            if 13 < gust_kph <= 18:
                reasons.append(f"Gusts ({gust_kph:.1f} kph) are strong (13-18 kph)")
                condition = "Moderate"
                
            if wind_kph < 3:
                reasons.append(f"Wind ({wind_kph:.1f} kph) is too low (<3 kph), risk of inversion")
                condition = "Moderate"
                
            if 25 < temp <= 30:
                reasons.append(f"Temp ({temp:.1f}°C) is high (25-30°C), risk of volatility")
                condition = "Moderate"
                
            if 4 <= temp < 15:
                reasons.append(f"Temp ({temp:.1f}°C) is cool (4-15°C), may slow uptake")
                condition = "Moderate"
                
            if humidity < 40 or humidity > 80:
                reasons.append(f"Humidity ({humidity}%) out of ideal range (40-80%)")
                condition = "Moderate"
                
            if 0 < precip_chance <= 25:
                reasons.append(f"Low rain chance ({precip_chance}%)")
                condition = "Moderate"
                
            if 8 < delta_t <= 10:
                reasons.append(f"Delta T ({delta_t:.1f}°C) is high (8-10), caution for evaporation")
                condition = "Moderate"
                
            if 2 <= dew_gap < 4:
                reasons.append(f"Dew gap small ({dew_gap:.1f}°C), possible leaf moisture")
                condition = "Moderate"

        if not reasons:
            reason_text = "Ideal conditions for spraying."
        else:
            reason_text = ", ".join(reasons) + "."

        spraying_conditions.append(schemas.SprayingCondition(
            time=time,
            condition=condition,
            wind_kph=wind_kph,
            temperature_c=temp,
            precipitation_chance=precip_chance,
            humidity=humidity,
            reason=reason_text
        ))

    return schemas.SprayingConditionsResponse(conditions=spraying_conditions)

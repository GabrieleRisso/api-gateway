
import requests
from fastapi import HTTPException
from datetime import datetime
from ..config import settings

class WeatherService:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        
    async def get_cuneo_weather(self):
        """
        Recupera i dati meteorologici per Cuneo usando requests invece di openmeteo_requests
        """
        try:
            params = {
                "latitude": 44.384,  # Cuneo coordinates
                "longitude": 7.543,
                "hourly": ["temperature_2m", "relative_humidity_2m"],
                "timezone": "Europe/Rome",
                "current_weather": True
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            
            data = response.json()
            
            # Extract current weather data
            current_weather = data.get('current_weather', {})
            temperature = current_weather.get('temperature')
            
            # Get first hour's humidity from hourly data
            hourly_data = data.get('hourly', {})
            humidity = hourly_data.get('relative_humidity_2m', [None])[0]
            
            return {
                "city": "Cuneo",
                "temperature": float(temperature) if temperature is not None else None,
                "humidity": float(humidity) if humidity is not None else None,
                "timestamp": datetime.now()
            }
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Errore nel recupero dei dati meteo: {str(e)}"
            )
        except (KeyError, IndexError, TypeError) as e:
            raise HTTPException(
                status_code=500,
                detail=f"Errore nel processamento dei dati meteo: {str(e)}"
            )

weather_service = WeatherService()
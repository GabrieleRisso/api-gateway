# Implementazione Pratica: FastAPI Weather, Time e OpenAI

## Struttura del Progetto
```
weather_service/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── weather_service.py
│   │   ├── time_service.py
│   │   └── openai_service.py
│   ├── models/
│   │   └── schemas.py
│   └── utils/
│       └── error_handlers.py
└── requirements.txt
```

## 1. Setup Iniziale

### requirements.txt
```txt
fastapi==0.100.0
uvicorn==0.22.0
python-dotenv==1.0.0
openmeteo-requests==1.0.0
requests-cache==1.1.0
retry-requests==1.0.0
numpy==1.24.3
pandas==2.0.3
openai==0.28.0
python-decouple==3.8
```

### config.py
```python
from pydantic_settings import BaseSettings
from decouple import config

class Settings(BaseSettings):
    OPENAI_API_KEY: str = config('OPENAI_API_KEY', default='')
    CUNEO_LAT: float = 44.384
    CUNEO_LON: float = 7.543
    ENVIRONMENT: str = config('ENVIRONMENT', default='development')

    class Config:
        env_file = ".env"

settings = Settings()
```

## 2. Definizione degli Schemas

### models/schemas.py
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class WeatherResponse(BaseModel):
    city: str
    temperature: float
    timestamp: datetime
    humidity: Optional[float] = None

class TimeResponse(BaseModel):
    current_time: datetime
    timezone: str = "Europe/Rome"

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    timestamp: datetime
```

## 3. Implementazione dei Servizi

### services/weather_service.py
```python
import openmeteo_requests
import requests_cache
from retry_requests import retry
from fastapi import HTTPException
from datetime import datetime
from ..config import settings

class WeatherService:
    def __init__(self):
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.client = openmeteo_requests.Client(session=retry_session)

    async def get_cuneo_weather(self):
        """
        Recupera i dati meteorologici per Cuneo
        """
        try:
            params = {
                "latitude": settings.CUNEO_LAT,
                "longitude": settings.CUNEO_LON,
                "hourly": ["temperature_2m", "relative_humidity_2m"]
            }
            
            response = self.client.weather_api(
                "https://api.open-meteo.com/v1/forecast",
                params=params
            )[0]
            
            hourly = response.Hourly()
            current_temp = hourly.Variables(0).ValuesAsNumpy()[0]
            current_humidity = hourly.Variables(1).ValuesAsNumpy()[0]
            
            return {
                "city": "Cuneo",
                "temperature": float(current_temp),
                "humidity": float(current_humidity),
                "timestamp": datetime.now()
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Errore nel recupero dei dati meteo: {str(e)}"
            )

weather_service = WeatherService()
```

### services/time_service.py
```python
from datetime import datetime
import pytz

class TimeService:
    def __init__(self):
        self.timezone = pytz.timezone('Europe/Rome')

    async def get_current_time(self):
        """
        Restituisce l'ora corrente nel fuso orario italiano
        """
        current_time = datetime.now(self.timezone)
        return {
            "current_time": current_time,
            "timezone": str(self.timezone)
        }

time_service = TimeService()
```

### services/openai_service.py
```python
from openai import AsyncOpenAI
from ..config import settings
from fastapi import HTTPException
from datetime import datetime

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def get_chat_response(self, message: str):
        """
        Ottiene una risposta da OpenAI GPT-3.5
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": message}
                ],
                max_tokens=150
            )
            
            return {
                "response": response.choices[0].message.content,
                "timestamp": datetime.now()
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Errore nella comunicazione con OpenAI: {str(e)}"
            )

openai_service = OpenAIService()
```

## 4. Implementazione Main FastAPI App

### main.py
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .services.weather_service import weather_service
from .services.time_service import time_service
from .services.openai_service import openai_service
from .models.schemas import WeatherResponse, TimeResponse, ChatRequest, ChatResponse

app = FastAPI(
    title="Multi-Service API",
    description="API che fornisce dati meteo, ora corrente e risposte AI",
    version="1.0.0"
)

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/weather/cuneo", response_model=WeatherResponse)
async def get_cuneo_weather():
    """
    Recupera i dati meteo correnti per Cuneo
    """
    return await weather_service.get_cuneo_weather()

@app.get("/time", response_model=TimeResponse)
async def get_current_time():
    """
    Recupera l'ora corrente nel fuso orario italiano
    """
    return await time_service.get_current_time()

@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Invia un messaggio a GPT-3.5 e ottiene una risposta
    """
    return await openai_service.get_chat_response(request.message)

@app.get("/health")
async def health_check():
    """
    Endpoint per il controllo dello stato dell'API
    """
    return {"status": "healthy"}
```

## 6. File .env
```env
OPENAI_API_KEY=your-api-key-here
ENVIRONMENT=development
```

## 7. Istruzioni per l'Utilizzo

### Avvio Locale
1. Creare un ambiente virtuale:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Installare le dipendenze:
```bash
pip install -r requirements.txt
```

3. Creare il file .env con le variabili necessarie

4. Avviare l'applicazione:
```bash
uvicorn app.main:app --reload
```

## 8. Test degli Endpoint

### Esempio di richieste curl:

```bash
# Test Weather Endpoint
curl http://localhost:8000/weather/cuneo

# Test Time Endpoint
curl http://localhost:8000/time

# Test Chat Endpoint
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Cosa posso visitare a Cuneo?"}'
```

## 9. Documentazione API
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
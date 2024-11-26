from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .services.weather_service import weather_service
from .services.time_service import time_service
from .services.openai_service import openai_service
from .models.schemas import WeatherResponse, TimeResponse, ChatRequest, ChatResponse

app = FastAPI(
    title="Weather API Service",
    description="API che fornisce dati meteo, ora corrente e risposte AI",
    version="1.0.0",
    # Remove the /api prefix from here as Nginx will handle it
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/weather/cuneo", 
         response_model=WeatherResponse,
         tags=["Weather"],
         summary="Get Cuneo Weather",
         description="Recupera i dati meteo correnti per Cuneo")
async def get_cuneo_weather():
    """
    Recupera i dati meteo correnti per Cuneo
    
    Returns:
        WeatherResponse: I dati meteo correnti includendo temperatura e umidità
    """
    return await weather_service.get_cuneo_weather()

@app.get("/time", 
         response_model=TimeResponse,
         tags=["Time"],
         summary="Get Current Time",
         description="Recupera l'ora corrente nel fuso orario italiano")
async def get_current_time():
    """
    Recupera l'ora corrente
    
    Returns:
        TimeResponse: L'ora corrente nel fuso orario italiano
    """
    return await time_service.get_current_time()

@app.post("/chat", 
          response_model=ChatResponse,
          tags=["Chat"],
          summary="Chat with AI",
          description="Invia un messaggio all'AI e ricevi una risposta")
async def chat_with_ai(request: ChatRequest):
    """
    Invia un messaggio all'AI
    
    Args:
        request (ChatRequest): Il messaggio da inviare

    Returns:
        ChatResponse: La risposta dell'AI
    """
    return await openai_service.get_chat_response(request.message)

@app.get("/health",
         tags=["Health"],
         summary="Health Check",
         description="Verifica lo stato del servizio")
async def health_check():
    """
    Endpoint per il controllo dello stato dell'API
    
    Returns:
        dict: Lo stato del servizio
    """
    return {"status": "healthy"}
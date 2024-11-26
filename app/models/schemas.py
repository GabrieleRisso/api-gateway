from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class WeatherResponse(BaseModel):
    city: str
    temperature: Optional[float]
    humidity: Optional[float]
    timestamp: datetime

# ... altri schemas ...
class TimeResponse(BaseModel):
    current_time: datetime
    timezone: str = "Europe/Rome"

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    timestamp: datetime
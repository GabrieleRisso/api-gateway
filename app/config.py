from pydantic import BaseModel
from decouple import config

class Settings(BaseModel):
    OPENAI_API_KEY: str = config('OPENAI_API_KEY', default='')
    CUNEO_LAT: float = 44.384
    CUNEO_LON: float = 7.543
    ENVIRONMENT: str = config('ENVIRONMENT', default='development')

    class Config:
        frozen = True

settings = Settings()
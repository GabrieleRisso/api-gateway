
from openai import OpenAI
from ..config import settings
from fastapi import HTTPException
from datetime import datetime

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def get_chat_response(self, message: str):
        """
        Ottiene una risposta da OpenAI GPT-3.5
        """
        try:
            response = self.client.chat.completions.create(
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
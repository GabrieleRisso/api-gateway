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
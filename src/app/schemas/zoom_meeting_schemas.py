# schemas/meeting_schemas.py

from pydantic import BaseModel
from datetime import datetime

class ZoomMeetingCreate(BaseModel):
    topic: str
    start_time: datetime
    duration: int
    timezone: str
    agenda: str

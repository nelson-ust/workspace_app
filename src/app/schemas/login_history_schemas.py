# schemas/login_history_schemas.py

from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class LoginHistoryRead(BaseModel):
    id: int
    user_id: int
    username:str
    email:str
    full_name:str
    login_time: datetime
    logout_time: Optional[datetime]
    ip_address: str
    user_agent: str

    class Config:
        orm_mode = True

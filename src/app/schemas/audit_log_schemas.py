from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any

class AuditLogRead(BaseModel):
    id: int
    user_id: int
    username: str
    email: str
    full_name: str
    phone_number: str
    action: str
    model: str
    model_id: int
    changes: Optional[str]
    date_created: datetime

    class Config:
        orm_mode = True

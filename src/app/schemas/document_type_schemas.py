from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class DocumentTypeCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DocumentTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class DocumentTypeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    date_created: Optional[datetime]
    date_updated: Optional[datetime]

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

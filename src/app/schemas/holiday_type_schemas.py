from pydantic import BaseModel
from typing import Optional

class HolidayTypeBase(BaseModel):
    name: str
    description: Optional[str] = None

class HolidayTypeCreate(HolidayTypeBase):
    pass

class HolidayTypeUpdate(HolidayTypeBase):
    pass

class HolidayTypeResponse(HolidayTypeBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

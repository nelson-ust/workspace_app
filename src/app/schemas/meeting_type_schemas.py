from pydantic import BaseModel
from typing import Optional

class MeetingTypeBase(BaseModel):
    name: str

class MeetingTypeCreate(MeetingTypeBase):
    pass

class MeetingTypeUpdate(MeetingTypeBase):
    pass

class MeetingTypeResponse(MeetingTypeBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True

from pydantic import BaseModel
from typing import Optional

class LeaveTypeBase(BaseModel):
    name: str
    description: Optional[str] = None

class LeaveTypeCreate(LeaveTypeBase):
    pass

class LeaveTypeUpdate(LeaveTypeBase):
    name: Optional[str] = None
    description: Optional[str] = None

class LeaveTypeResponse(LeaveTypeBase):
    id: int

    class Config:
        from_attributes = True  # Use from_attributes instead of orm_mode for Pydantic v2

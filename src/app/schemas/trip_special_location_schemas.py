# from pydantic import BaseModel
# from typing import Optional

# class TripStartLocationBase(BaseModel):
#     name: str
#     description: Optional[str] = None
#     latitude: Optional[float] = None
#     longitude: Optional[float] = None

# class TripStartLocationCreate(TripStartLocationBase):
#     tenancy_id: Optional[int] = None

# class TripStartLocationUpdate(TripStartLocationBase):
#     tenancy_id: Optional[int] = None

# class TripStartLocation(TripStartLocationBase):
#     id: int
#     tenancy_id: Optional[int]

#     class Config:
#         orm_mode = True




from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TripStartLocationBase(BaseModel):
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    tenancy_id: int

class TripStartLocationCreate(BaseModel):
    name: str
    description: str
    latitude: float
    longitude: float
    tenancy_id: int  # Ensure this is an integer

class TenancyIDsRequest(BaseModel):
    tenancy_ids: List[int]

class TenancyIDRequest(BaseModel):
    tenancy_ids: List[int]


class TripStartLocationUpdate(TripStartLocationBase):
    pass

class TripStartLocationResponse(TripStartLocationBase):
    id: int
    is_active: bool
    date_created: datetime
    date_updated: Optional[datetime] = None
    date_deleted: Optional[datetime] = None

    class Config:
        orm_mode = True

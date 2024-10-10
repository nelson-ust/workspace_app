# schemas/vehicle_movement_schemas.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VehicleMovementBase(BaseModel):
    vehicle_id: int
    description: str
    start_date: datetime
    end_date: Optional[datetime]
    location: Optional[str]

class VehicleMovementCreate(VehicleMovementBase):
    pass

class VehicleMovementUpdate(VehicleMovementBase):
    pass

class VehicleMovementResponse(VehicleMovementBase):
    id: int
    driver_id: Optional[int]

    class Config:
        orm_mode = True

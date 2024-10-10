
from pydantic import BaseModel, Field
from typing import Optional

# Base schema for common attributes
class VehicleBase(BaseModel):
    name: str
    licence_plate: str
    alternate_plate: Optional[str]
    make: str
    year: int = Field(..., example="2008")
    fuel_type: str
    current_mileage: float
    seat_capacity: int
    tenancy_id: int


# Schema for requests to create a Vehicle
class VehicleCreate(VehicleBase):
    fuel_economy: float



# Schema for requests to update a Vehicle
class VehicleUpdate(BaseModel):
    current_mileage: float
    is_available: bool
    tenancy_id: int



# Schema for reading an Vehicle, including its ID
class VehicleRead(VehicleBase):
    id: int
    is_available:bool
    class Config:
        from_attributes = True
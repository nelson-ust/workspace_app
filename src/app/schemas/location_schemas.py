#schemas/location_schemas.py
from pydantic import BaseModel, Field
from typing import Optional

# Base schema for common attributes
class LocationBase(BaseModel):
    name: str

# Schema for requests to create a Location
class LocationCreate(LocationBase):
    tenancy_id: int = Field(..., description="The ID of the tenancy that the location belongs to")

# Schema for requests to update a Location
class LocationUpdate(BaseModel):
    name: Optional[str] = Field(None, description="The new name of the location")
    tenancy_id: Optional[int] = Field(None, description="The new tenancy ID for the location")

# Schema for reading a Location, including its ID and tenancy relation
class LocationRead(LocationBase):
    id: int
    tenancy_id: int

    class Config:
        from_attributes = True

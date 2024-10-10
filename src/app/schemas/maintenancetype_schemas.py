#schemas/maintenance.py
from pydantic import BaseModel, Field

# Base schema for common attributes
class MaintenanceTypeBase(BaseModel):
    name: str = Field(..., description="The name of maintenance type")

# Schema for requests to create a Maintenance
class MaintenanceCreate(MaintenanceTypeBase):
    pass

# Schema for requests to update a Maintenance
class MaintenanceUpdate(MaintenanceTypeBase):
    pass

# Schema for reading a Maintenance, including its ID
class MaintenanceRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

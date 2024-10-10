#schemas/srt_schemas.py
from pydantic import BaseModel, Field
from typing import Optional

# Base schema for common attributes
class SRTBase(BaseModel):
    name: str
    description: Optional[str] = Field(None, description="A brief description of the SRT")

# Schema for requests to create an SRT
class SRTCreate(SRTBase):
    tenancy_id: int = Field(..., description="The ID of the tenancy that the SRT belongs to")

# Schema for requests to update an SRT
class SRTUpdate(BaseModel):
    name: Optional[str] = Field(None, description="The new name of the SRT")
    description: Optional[str] = Field(None, description="The new description of the SRT")
    tenancy_id: Optional[int] = Field(None, description="The new tenancy ID for the SRT")

# Schema for reading an SRT, including its ID and tenancy relation
class SRTRead(SRTBase):
    id: int
    name:str
    description: Optional[str]
    tenancy_id: int

    class Config:
        from_attributes = True

class EmployeeBase(BaseModel):
    firstname: str
    lastname: str

    class config:
        from_attributes = True
class EmployeeInSRT():
    pass

class EmployeeInSRTRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone_number: str
    department_id: int  # Assuming you want to include the department ID
    unit_id: int  # Assuming you want to include the unit ID if applicable
    # Include other relevant fields here

    class Config:
        from_attributes = True
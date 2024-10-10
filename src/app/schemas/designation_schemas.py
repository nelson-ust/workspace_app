# schemas/designation_schemas.py
from pydantic import BaseModel, Field
from typing import Optional

# Base schema for Designation
class DesignationBase(BaseModel):
    name: str = Field(..., example="Senior Developer")

# Schema for creating a Designation
class DesignationCreate(DesignationBase):
    pass

# Schema for updating a Designation
class DesignationUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Lead Developer")

# Schema for reading Designation data
class DesignationRead(DesignationBase):
    id: int

    class Config:
        from_attributes = True


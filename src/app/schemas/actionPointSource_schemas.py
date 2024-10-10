#schemas/actionpointsource.py
from pydantic import BaseModel, Field

# Base schema for common attributes
class ActionPointSourceBase(BaseModel):
    name: str = Field(..., description="The name of actionpoint source")

# Schema for requests to create a ActionPointSource
class ActionPointSourceCreate(ActionPointSourceBase):
    pass

# Schema for requests to update a ActionPointSource
class ActionPointSourceUpdate(ActionPointSourceBase):
    pass

# Schema for reading an ActionPointSource, including its ID
class ActionPointSourceRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

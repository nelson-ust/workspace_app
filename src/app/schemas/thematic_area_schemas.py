from pydantic import BaseModel
from typing import Optional

# Base model for common attributes
class ThematicAreaBase(BaseModel):
    name: str

# Input model for creating a new Thematic Area
class ThematicAreaCreate(ThematicAreaBase):
    pass

# Input model for updating an existing Thematic Area
class ThematicAreaUpdate(BaseModel):
    name: Optional[str] = None

# Model for DB representation including ID and timestamps
class ThematicAreaRead(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

# Output model for reading request status data
class ThematicArea(ThematicAreaRead):
    pass


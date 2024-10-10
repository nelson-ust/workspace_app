from pydantic import BaseModel
from typing import Optional

# Schema for Site responses
class SiteBase(BaseModel):
    name: str

# Schema for requests to create a Site
class SiteCreate(SiteBase):
    site_type: str
    location_id: int
    tenancy_id: int

# Schema for requests to update a Site
class SiteUpdate(BaseModel):
    name: Optional[str] = None
    site_type: Optional[str] = None

# Schema for reading a Site, including its ID and 
class SiteRead(SiteBase):
    id: int
    name:str
    location_id: int
    tenancy_id: int

    class Config:
        from_attributes = True

class EmployeeList(BaseModel):
    id: int
    first_name: str
    last_name: str
    
    class Config:
        from_attributes = True
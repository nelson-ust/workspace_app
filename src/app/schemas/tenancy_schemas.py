from pydantic import BaseModel, Field
from typing import List, Optional

# Base schema for common attributes
class TenancyBase(BaseModel):
    name: str

# Schema for requests to create a Tenancy
class TenancyCreate(TenancyBase):
    pass

# Schema for requests to update a Tenancy
class TenancyUpdate(BaseModel):
    name: Optional[str] = Field(None, description="The new name of the tenancy")

# For the relationships, assuming you have or will create LocationRead and SRTRead schemas
# These should be defined in their respective schema files (e.g., location_schemas.py, srt_schemas.py)

# Schema for reading a Tenancy, including its related locations and SRTs
class TenancyRead(TenancyBase):
    id: int
    locations: List[Optional['LocationRead']] = []
    srts: List[Optional['SRTRead']] = []

    class Config:
        from_attributes = True

# After defining LocationRead and SRTRead, update forward references
# This is necessary due to Pydantic's handling of forward references
from schemas.location_schemas import LocationRead  # Adjust import path as necessary
from schemas.srt_schemas import SRTRead  # Adjust import path as necessary
TenancyRead.update_forward_refs()

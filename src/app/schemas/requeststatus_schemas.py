from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base model for common attributes
class RequestStatusBase(BaseModel):
    name: str

# Input model for creating a new request status
class RequestStatusCreate(RequestStatusBase):
    pass

# Input model for updating an existing request status
class RequestStatusUpdate(BaseModel):
    name: Optional[str] = None

# Model for DB representation including ID and timestamps
class RequestStatusInDBBase(RequestStatusBase):
    id: int
    date_created: Optional[datetime] = None
    date_updated: Optional[datetime] = None

    class Config:
        from_attributes = True

# Output model for reading request status data
class RequestStatus(RequestStatusInDBBase):
    pass

# Optional: If there's a need to include related entities like WorkPlanRequests in the response
class WorkPlanRequestBase(BaseModel):
    # Assuming a simplified model for demonstration
    plan_id: int
    status_id: int

    class Config:
        from_attributes = True

class RequestStatusWithRequests(RequestStatusInDBBase):
    requests: List[WorkPlanRequestBase] = []

    class Config:
        from_attributes = True

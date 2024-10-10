#schemas/issue_status.py
from pydantic import BaseModel, Field

# Base schema for common attributes
class IssueStatusBase(BaseModel):
    status: str = Field(..., description="The name of issuelog source")

# Schema for requests to create a IssueStatus
class IssueStatusCreate(IssueStatusBase):
    pass

# Schema for requests to update a IssueStatus
class IssueStatusUpdate(IssueStatusBase):
    pass

# Schema for reading an IssueStatus, including its ID
class IssueStatusRead(BaseModel):
    id: int
    status: str

    class Config:
        from_attributes = True

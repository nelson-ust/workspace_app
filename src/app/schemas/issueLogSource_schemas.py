#schemas/issuelogsource.py
from pydantic import BaseModel, Field

# Base schema for common attributes
class IssueLogSourceBase(BaseModel):
    name: str = Field(..., description="The name of issuelog source")

# Schema for requests to create a IssueLogSource
class IssueLogSourceCreate(IssueLogSourceBase):
    pass

# Schema for requests to update a issuelogsource
class IssueLogSourceUpdate(IssueLogSourceBase):
    pass

# Schema for reading an IssueLogSource, including its ID
class IssueLogSourceRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

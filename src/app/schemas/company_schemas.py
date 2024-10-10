from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class CompanyCreate(BaseModel):
    name: str
    tenancy_id: int  # Add tenancy_id

class CompanyUpdate(BaseModel):
    name: Optional[str]
    tenancy_id: Optional[int]  # Add tenancy_id here


class CompanyResponse(BaseModel):
    id: int
    name: str
    tenancy_id: int  # Add tenancy_id 
    date_created: str  # Ensure this is a string
    date_updated: Optional[str]

    class Config:
        orm_mode = True

    @staticmethod
    def from_orm(obj):
        return CompanyResponse(
            id=obj.id,
            name=obj.name,
            tenancy_id=obj.tenancy_id,  # Add tenancy_id 
            date_created=obj.date_created.isoformat() if obj.date_created else None,
            date_updated=obj.date_updated.isoformat() if obj.date_updated else None,
        )


class ThirdPartyParticipantCreate(BaseModel):
    name: str
    email: str
    phone_number: Optional[str]
    company_id: Optional[int]
    site_id: Optional[int]
    meeting_id: Optional[int]

    class Config:
        from_attributes = True

class ThirdPartyParticipantUpdate(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    company_id: Optional[int]
    site_id: Optional[int]
    meeting_id: Optional[int]

    class Config:
        from_attributes = True

class ThirdPartyParticipantResponse(BaseModel):
    id: int
    name: str
    email: str
    phone_number: Optional[str]
    company_id: Optional[int]
    site_id: Optional[int]
    meeting_id: Optional[int]

    class Config:
        from_attributes = True
# from pydantic import BaseModel, Field
# from datetime import date, datetime
# from typing import Optional

# class HolidayBase(BaseModel):
#     """
#     Base schema for holiday-related data.
#     """
#     name: str = Field(..., title="Holiday Name", max_length=100, description="Name of the holiday")
#     description: Optional[str] = Field(None, title="Holiday Description", description="Description of the holiday")
#     date: datetime = Field(..., title="Holiday Date", description="Date of the holiday")


# class HolidayCreate(HolidayBase):
#     """
#     Schema for creating a new holiday.
#     """
#     pass  # Inherits all fields from HolidayBase


# class HolidayUpdate(HolidayBase):
#     """
#     Schema for updating an existing holiday.
#     """
#     name: Optional[str] = Field(None, title="Holiday Name", max_length=100, description="Name of the holiday")
#     description: Optional[str] = Field(None, title="Holiday Description", description="Description of the holiday")
#     date: Optional[datetime] = Field(None, title="Holiday Date", description="Date of the holiday")


# class HolidayResponse(HolidayBase):
#     """
#     Schema for returning holiday data in responses.
#     """
#     id: int = Field(..., title="Holiday ID", description="Unique identifier of the holiday")

#     class Config:
#         orm_mode = True  # Enable ORM mode to work with SQLAlchemy models




from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class HolidayBase(BaseModel):
    """
    Base schema for holiday-related data.
    """
    name: str = Field(..., title="Holiday Name", max_length=100, description="Name of the holiday")
    description: Optional[str] = Field(None, title="Holiday Description", description="Description of the holiday")
    date: datetime = Field(..., title="Holiday Date", description="Date of the holiday")
    holiday_type_id: Optional[int] = Field(None, title="Holiday Type ID", description="ID of the holiday type")

class HolidayCreate(HolidayBase):
    """
    Schema for creating a new holiday.
    """
    holiday_type_id: int = Field(..., title="Holiday Type ID", description="ID of the holiday type")

class HolidayUpdate(BaseModel):
    """
    Schema for updating an existing holiday.
    """
    name: Optional[str] = Field(None, title="Holiday Name", max_length=100, description="Name of the holiday")
    description: Optional[str] = Field(None, title="Holiday Description", description="Description of the holiday")
    date: Optional[datetime] = Field(None, title="Holiday Date", description="Date of the holiday")
    holiday_type_id: Optional[int] = Field(None, title="Holiday Type ID", description="ID of the holiday type")

class HolidayResponse(HolidayBase):
    """
    Schema for returning holiday data in responses.
    """
    id: int = Field(..., title="Holiday ID", description="Unique identifier of the holiday")
    holiday_type: Optional[str] = Field(None, title="Holiday Type", description="Name of the holiday type")

    class Config:
        orm_mode = True  # Enable ORM mode to work with SQLAlchemy models

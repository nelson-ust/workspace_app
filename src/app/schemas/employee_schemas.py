# #schemas/Employee_schemas.py
# from pydantic import BaseModel, Field, validator
# from typing import Optional, List
# from schemas.srt_schemas import SRTRead  # Assuming you have an SRTRead schema


# class SrtRead(BaseModel):
#     id: int
#     name: str
#     tenancy_id:int

#     class Config:
#         from_attribute = True


# # Base schema for common attributes
# class EmployeeBase(BaseModel):
#     first_name: str = Field(..., example="John")
#     last_name: str = Field(..., example="Doe")
#     phone_number: str = Field(..., example="123-456-7890")
#     department_id: int = Field(..., example=1)
#     unit_id: Optional[int] = Field(None, example=1)
#     #srt_id: Optional[int] = Field(None, example=1)

# # Schema for updating Employee data
# class EmployeeUpdate(BaseModel):
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#     phone_number: Optional[str] = None
#     department_id: Optional[int] = None
#     unit_id: Optional[int] = None
#     #srt_ids: Optional[int] = None

# class EmployeeCreate(BaseModel):
#     first_name: str = Field(..., example="John")
#     last_name: str = Field(..., example="Doe")
#     phone_number: str = Field(..., example="123-456-7890")
#     staff_code: str = Field(..., example="CCFN/2021/A664")
#     employee_email : str = Field(..., example="nattah@ccfng.org")
#     address: Optional[str] = Field(..., example="No, 15 Azikiwe Street")
#     state_origin: str =  Field(..., example="Abia")
#     lga_origin: str = Field(..., example="Umuahia North")
#     designation_id: Optional[int] = None
#     department_id: Optional[int] = None  # Made optional
#     unit_id: Optional[int] = None  # Made optional
#     # srt_ids: Optional[List[int]] = None  # Assuming an employee can be assigned to multiple SRTs
#     tenancy_id: int  # Not optional

# # Schema for reading Employee data, possibly including the related SRT data
# class EmployeeRead(EmployeeBase):
#     id: int
#     first_name:str
#     last_name: str
#     phone_number: str
#     is_active: bool
#     staff_code: str
#     employee_email:str
#     address: str
#     state_origin: str
#     lga_origin: str
#     designation_id: int
#     department_id: int
#     unit_id: int
#     # Assuming SRTRead is a Pydantic model for SRT data
#     srts: Optional[List[SRTRead]] = []
#     tenancy_id: int = None

#     class Config:
#         from_attributes = True  # Enable ORM mode for compatibility with ORM objects

# class SRTAssignment(BaseModel):
#     employee_id: int
#     srt_ids: List[int]

# class DepartmentUpdate(BaseModel):
#     department_id: int

# class EmployeeList(BaseModel):
#     id: int
#     first_name: str
#     last_name: str

#     class Config:
#         from_attributes = True


# schemas/designation_schemas.py
from datetime import date
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List
from schemas.srt_schemas import SRTRead  # Assuming you have an SRTRead schema


class SrtRead(BaseModel):
    id: int
    name: str
    tenancy_id: int

    class Config:
        from_attribute = True


# Base schema for common attributes
class EmployeeBase(BaseModel):
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Doe")
    phone_number: str = Field(..., example="123-456-7890")
    department_id: int = Field(..., example=1)
    unit_id: Optional[int] = Field(None, example=1)
    # srt_id: Optional[int] = Field(None, example=1)


# Schema for updating Employee data
class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    department_id: Optional[int] = None
    unit_id: Optional[int] = None
    # srt_ids: Optional[int] = None


class EmployeeCreate(BaseModel):
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Doe")
    phone_number: str = Field(..., example="123-456-7890")
    staff_code: str = Field(..., example="CCFN/2021/A664")
    employee_email: EmailStr = Field(..., example="johndoe@example.com")
    address: Optional[str] = Field(..., example="No, 15 Azikiwe Street")
    state_origin: str = Field(..., example="Abia")
    lga_origin: str = Field(..., example="Umuahia North")
    designation_id: Optional[int] = None
    department_id: Optional[int] = None  # Made optional
    unit_id: Optional[int] = None  # Made optional
    # srt_ids: Optional[List[int]] = None  # Assuming an employee can be assigned to multiple SRTs
    tenancy_id: int  # Not optional
    date_of_birth: date = Field(..., example="1990-05-23")
    gender: Optional[str] =Field(..., example="Female")

# # Schema for reading Employee data, possibly including the related SRT data
# class EmployeeRead(EmployeeBase):
#     id: int
#     first_name: str
#     last_name: str
#     phone_number: str
#     is_active: bool
#     staff_code: str
#     employee_email: EmailStr
#     address: str
#     state_origin: str
#     lga_origin: str
#     designation_id: int
#     department_id: int
#     unit_id: int
#     user_id: Optional[int] = None  # Include user_id if associated
#     # Assuming SRTRead is a Pydantic model for SRT data
#     srts: Optional[List[SRTRead]] = []
#     tenancy_id: Optional[int] = None
#     #user_id:Optional[int]
#     class Config:
#         from_attributes = True  # Enable ORM mode for compatibility with ORM objects

class EmployeeRead(BaseModel):
    id: int # = Field(..., alias='employee_id')  # Ensure this aligns with the database field name or query alias
    first_name: str
    last_name: str
    phone_number: str
    gender: Optional[str]
    is_active: bool
    staff_code: str
    employee_email: EmailStr #= Field(..., alias='email')  # Ensure this aligns with the database field name or query alias
    address: str
    state_origin: str
    lga_origin: str
    designation_id: int
    department_id: int
    unit_id: Optional[int]
    user_id: Optional[int] = None
    srts: Optional[List[SRTRead]] = []
    tenancy_id: Optional[int]

    class Config:
        from_attributes = True


class EmployeeReadWithUserID(BaseModel):
    id: int  = Field(..., alias='employee_id')  # Ensure this aligns with the database field name or query alias
    first_name: str
    last_name: str
    phone_number: str
    is_active: bool
    staff_code: str
    employee_email: EmailStr #= Field(..., alias='email')  # Ensure this aligns with the database field name or query alias
    address: str
    state_origin: str
    lga_origin: str
    designation_id: int
    department_id: int
    unit_id: Optional[int]
    user_id: Optional[int] 
    srts: Optional[List[SRTRead]] = []
    tenancy_id: Optional[int]

    class Config:
        from_attributes = True
        populate_by_name = True


class SRTAssignment(BaseModel):
    # employee_id: int
    srt_ids: List[int]


class Department_and_Unit_Update(BaseModel):
    department_id: int
    unit_id: int


class EmployeeList(BaseModel):
    id: int
    first_name: str
    last_name: str
    

    class Config:
        from_attributes = True

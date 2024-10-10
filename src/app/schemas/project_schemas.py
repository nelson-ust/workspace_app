from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# Project Schemas
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str]
    start_date: date
    end_date: Optional[date]
    project_sum: float

class ProjectUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    project_sum: Optional[float]

class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: date
    end_date: Optional[date]
    project_sum: float
    is_active: bool

    class Config:
        orm_mode: True

# Funder Schemas
class FunderOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool

    class Config:
        orm_mode: True

# Project Component Schemas
class ProjectComponentCreate(BaseModel):
    name: str
    description: Optional[str]

class ProjectComponentUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]

class ProjectComponentOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool

    class Config:
        orm_mode: True

# Employee Schemas
class EmployeeOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    is_active: bool

    class Config:
        orm_mode: True


# class EmployeeDetail(BaseModel):
#     employee_id: int
#     full_name: str
#     email: str
#     phone_number: str

# class EmployeeProjectDetail(BaseModel):
#     project_id: int
#     project_name: str
#     employees: List[EmployeeDetail]


class TenancyDetail(BaseModel):
    tenancy_id: int
    tenancy_name: str

class EmployeeDetail(BaseModel):
    employee_id: int
    full_name: str
    email: str
    phone_number: str
    state: Optional[TenancyDetail]

class EmployeeProjectDetail(BaseModel):
    project_id: int
    project_name: str
    employees: List[EmployeeDetail]
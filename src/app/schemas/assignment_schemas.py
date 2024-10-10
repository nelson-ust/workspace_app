from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

class EmployeeInfo(BaseModel):
    id: int
    fullname: str
    phone_number: Optional[str]

    class Config:
        from_attributes = True

class AssignmentBase(BaseModel):
    name: str = Field(..., example="Project Alpha")
    description: Optional[str] = Field(None, example="Description of the assignment")
    start_date: date = Field(..., example="2024-06-01")
    end_date: Optional[date] = Field(None, example="2024-07-01")
    status: str = Field(..., example="Active")

class AssignmentCreate(AssignmentBase):
    assignment_lead_id: Optional[int] = Field(None, example=1)
    assigned_employee_ids: Optional[List[int]] = Field(None, example=[1, 2, 3])
    tenancy_ids: Optional[List[int]] = Field(None, example=[1, 2])

class AssignmentUpdate(AssignmentBase):
    assignment_lead_id: Optional[int] = Field(None, example=1)
    assigned_employee_ids: Optional[List[int]] = Field(None, example=[1, 2, 3])
    tenancy_ids: Optional[List[int]] = Field(None, example=[1, 2])

class AssignmentResponse(AssignmentBase):
    id: int
    assignment_lead_id: Optional[int]
    initiating_user_fullname: str
    is_active: bool
    date_created: Optional[date]
    date_updated: Optional[date]
    date_deleted: Optional[date]
    tenancies: List[int]
    responsible_employees: List[int]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        data = {
            'id': obj.id,
            'name': obj.name,
            'description': obj.description,
            'start_date': obj.start_date,
            'end_date': obj.end_date,
            'status': obj.status,
            'assignment_lead_id': obj.assignment_lead_id,
            'initiating_user_fullname': obj.initiating_user_fullname,
            'is_active': obj.is_active,
            'date_created': obj.date_created.date() if obj.date_created else None,
            'date_updated': obj.date_updated.date() if obj.date_updated else None,
            'date_deleted': obj.date_deleted.date() if obj.date_deleted else None,
            'tenancies': [tenancy.id for tenancy in obj.tenancies],
            'responsible_employees': [employee.id for employee in obj.responsible_employees]
        }
        return cls(**data)

class AssignmentWithEmployees(BaseModel):
    assignment: AssignmentResponse
    employees: List[EmployeeInfo]

    class Config:
        from_attributes = True







# from pydantic import BaseModel, Field
# from typing import List, Optional
# from datetime import date

# class EmployeeInfo(BaseModel):
#     id: int
#     fullname: str
#     phone_number: Optional[str]

#     class Config:
#         from_attributes = True

# class AssignmentBase(BaseModel):
#     name: str = Field(..., example="Project Alpha")
#     description: Optional[str] = Field(None, example="Description of the assignment")
#     start_date: date = Field(..., example="2024-06-01")
#     end_date: Optional[date] = Field(None, example="2024-07-01")
#     status: str = Field(..., example="Active")

# class AssignmentCreate(AssignmentBase):
#     assignment_lead_id: Optional[int] = Field(None, example=1)
#     assigned_employee_ids: Optional[List[int]] = Field(None, example=[1, 2, 3])
#     tenancy_ids: Optional[List[int]] = Field(None, example=[1, 2])

# class AssignmentUpdate(AssignmentBase):
#     assignment_lead_id: Optional[int] = Field(None, example=1)
#     assigned_employee_ids: Optional[List[int]] = Field(None, example=[1, 2, 3])
#     tenancy_ids: Optional[List[int]] = Field(None, example=[1, 2])

# class AssignmentResponse(AssignmentBase):
#     id: int
#     assignment_lead_id: Optional[int]
#     initiating_user_fullname: str
#     is_active: bool
#     date_created: Optional[date]
#     date_updated: Optional[date]
#     date_deleted: Optional[date]
#     tenancies: List[int]
#     responsible_employees: List[int]

#     class Config:
#         from_attributes = True

# class AssignmentWithEmployees(BaseModel):
#     assignment: AssignmentResponse
#     employees: List[EmployeeInfo]

#     class Config:
#         from_attributes = True




from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date

class MilestoneBase(BaseModel):
    name: str
    description: Optional[str] = None
    due_date: date
    completion_date: Optional[date] = None
    #status: str
    comment: Optional[str] = None
    assignment_id: int
    responsible_employee_id: int

class MilestoneCreate(MilestoneBase):
    pass

class MilestoneUpdate(MilestoneBase):
    name: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = None

class MilestoneResponse(MilestoneBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class EmployeeInfo(BaseModel):
    id: int
    full_name: str

class MilestoneDetailResponse(BaseModel):
    milestone: MilestoneResponse
    assignment_employees: List[EmployeeInfo]
    responsible_employee: EmployeeInfo

    model_config = ConfigDict(from_attributes=True)

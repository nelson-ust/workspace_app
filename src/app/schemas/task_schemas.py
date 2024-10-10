# from pydantic import BaseModel, Field, ConfigDict, validator
# from typing import Optional, List
# from datetime import date, datetime

# class EmployeeInfo(BaseModel):
#     id: int
#     full_name: str

#     class Config:
#         orm_mode = True
#         from_attributes = True

# class MilestoneInfo(BaseModel):
#     id: int
#     name: str
#     description: Optional[str]
#     due_date: date
#     completion_date: Optional[date]
#     status: str
#     comment: Optional[str]

#     class Config:
#         orm_mode = True
#         from_attributes = True

# class AssignmentInfo(BaseModel):
#     id: int
#     name: str
#     description: Optional[str]
#     start_date: date
#     end_date: Optional[date]
#     status: str
#     comment: Optional[str]

#     class Config:
#         orm_mode = True
#         from_attributes = True

# class TaskBase(BaseModel):
#     description: str
#     due_date: Optional[date] = None
#     status_id: int
#     comment: Optional[str] = None
#     assignment_id: Optional[int]

#     @validator('description')
#     def description_must_not_be_empty(cls, v):
#         if not v or not v.strip():
#             raise ValueError('Description must not be empty')
#         return v

#     class Config:
#         orm_mode = True
#         from_attributes = True

# class TaskCreate(TaskBase):
#     milestone_id: int
#     employee_ids: List[int]

# class TaskUpdate(TaskBase):
#     milestone_id: Optional[int] = None
#     employee_ids: Optional[List[int]] = None

# class TaskResponse(TaskBase):
#     id: int
#     milestone_id: int
#     employee_ids: List[int]
#     date_created: date
#     date_updated: Optional[date]

#     @validator('date_created', pre=True)
#     def date_created_to_date(cls, v):
#         if isinstance(v, datetime):
#             return v.date()
#         return v

#     @validator('date_updated', pre=True, always=True)
#     def date_updated_to_date(cls, v):
#         if v is None:
#             return None
#         if isinstance(v, datetime):
#             return v.date()
#         return v

#     class Config:
#         orm_mode = True
#         from_attributes = True

# class TaskDetailResponse(BaseModel):
#     task: TaskResponse
#     milestone: MilestoneInfo
#     assignment: AssignmentInfo
#     task_employees: List[EmployeeInfo]
#     assignment_employees: List[EmployeeInfo]

#     class Config:
#         orm_mode = True
#         from_attributes = True


# schemas/task_schemas.py

from pydantic import BaseModel, ConfigDict, Field, validator
from typing import Optional, List
from datetime import date, datetime

class EmployeeInfo(BaseModel):
    id: int
    full_name: str

    class Config:
        orm_mode = True
        from_attributes = True

class MilestoneInfo(BaseModel):
    id: int
    name: str
    description: Optional[str]
    due_date: date
    completion_date: Optional[date]
    status: str
    comment: Optional[str]

    class Config:
        orm_mode = True
        from_attributes = True

class AssignmentInfo(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: date
    end_date: Optional[date]
    status: str
    comment: Optional[str]

    class Config:
        orm_mode = True
        from_attributes = True

class TaskBase(BaseModel):
    description: str
    due_date: Optional[date] = None
    status_id: int
    comment: Optional[str] = None
    assignment_id: Optional[int]

    @validator('description')
    def description_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Description must not be empty')
        return v

    class Config:
        orm_mode = True
        from_attributes = True

class TaskCreate(TaskBase):
    milestone_id: int
    employee_ids: List[int]

class TaskUpdate(TaskBase):
    milestone_id: Optional[int] = None
    employee_ids: Optional[List[int]] = None

class TaskResponse(TaskBase):
    id: int
    milestone_id: int
    employee_ids: List[int]
    date_created: date
    date_updated: Optional[date]

    class Config:
        from_attributes = True

class TaskDetailResponse(BaseModel):
    task: TaskResponse
    milestone: MilestoneInfo
    assignment: AssignmentInfo
    task_employees: List[EmployeeInfo]
    assignment_employees: List[EmployeeInfo]

    class Config:
        from_attributes = True

class ReopenTaskRequest(BaseModel):
    comment: str
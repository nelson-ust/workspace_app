#schemas/workplan_schemas.py
# schemas/workplan_schemas.py
from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime, time
from typing import Optional, List

# Basic WorkPlan schema for common properties
class WorkPlanBase(BaseModel):
    activity_title: str
    specific_task: str
    logistics_required: Optional[str] = None
    activity_date: date
    activity_start_time: Optional[time] = None

class LineItem(BaseModel):
    description: str
    employee_ids: List[int] = Field(default_factory=list, description="List of employee IDs associated with the line item")

class ScopeOfWork(BaseModel):
    description: str
    line_items: List[LineItem]

# Schema for WorkPlan creation
class WorkPlanCreate(WorkPlanBase):
    initiating_user_id: int
    initiating_unit_id: Optional[int] = None
    initiating_srt_id: Optional[int] = None
    initiating_department_id: Optional[int] = None
    initiating_thematic_area_id: Optional[int] = None
    activity_lead_id: Optional[int] = None
    workplan_source_id: Optional[int] = None
    site_ids: List[int] = Field(default_factory=list, description="List of site IDs associated with the work plan")
    employee_ids: List[int] = Field(default_factory=list, description="List of employee IDs participating in the work plan")
    location_ids: List[int] = Field(default_factory=list, description="List of location IDs involved in the work plan")
    tenancy_id: int
    project_id: int
    need_vehicle: bool
    #vehicle_assigned: bool
    scope_of_work: ScopeOfWork


class WorkPlanUpdate(BaseModel):
    activity_title: Optional[str] = None
    specific_task: Optional[str] = None
    logistics_required: Optional[str] = None
    activity_date: Optional[date] = None
    activity_start_time: Optional[time] = None
    # initiating_user_id: Optional[int] = None
    activity_lead_id: Optional[int] = None
    initiating_unit_id: Optional[int] = None
    initiating_department_id: Optional[int] = None
    initiating_srt_id: Optional[int] = None
    initiating_thematic_area_id: Optional[int] = None
    workplan_source_id: Optional[int] = None
    employee_ids: Optional[List[int]] = None
    site_ids: Optional[List[int]] = None
    location_ids: Optional[List[int]] = None

    class Config:
        from_attributes = True


class WorkPlanRead(BaseModel):
    id: int
    activity_title: str
    specific_task: str
    logistics_required: str
    activity_date: datetime
    initiating_user_id: int
    status: str = Field(..., example="Pending, Approved, Denied")

    class Config:
        from_attributes = True

# Additional schemas might include statistics or summaries
class WorkPlanStatistics(BaseModel):
    total_count: int
    approved_count: int
    denied_count: int
    rescheduled_count: int

# Advanced search result schema
class WorkPlanSearchResults(BaseModel):
    results: List[WorkPlanRead]

# Schema to handle patch updates for specific fields
class WorkPlanPatch(BaseModel):
    is_approved: Optional[bool] = None
    is_denied: Optional[bool] = None
    is_rescheduled: Optional[bool] = None


class WorkPlanReschedule(BaseModel):
    reason: str
    new_date: datetime


class EmployeeModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    employee_email: str
    phone_number: str

    class Config:
        from_attributes = True


class WorkPlanForApprovalSchema(BaseModel):
    activity_title: str
    activity_date: date
    location_name: str
    workplan_source_name: str
    implementing_team: str

    class Config:
        from_attributes = True


class ApprovedWorkPlan(BaseModel):
    id: int
    workplan_code: str
    workplan_source_name: str
    activity_title: str
    specific_task: str
    logistics_required: str
    activity_date: date
    activity_time: time
    initiating_user_id: int
    status: str
    employee_names: List[str]
    employee_count: int
    locations: List[str]
    implementing_team: str

    class Config:
        from_attributes = True


class ApprovedWorkPlanRead(BaseModel):
    id: int
    workplan_code: str
    activity_title: str
    specific_task: str
    logistics_required: str
    activity_date: datetime
    initiating_user_id: int
    status: str
    employee_names: List[str] = []
    employee_count: int
    class Config:
        from_attributes = True


class WorkPlanStatusSummary(BaseModel):
    status: str
    employee_count: int
    employees: List[str]

class MonthlyWorkPlanSummary(BaseModel):
    month: int
    year: int
    details: List[WorkPlanStatusSummary]

class WorkPlanReadByDateRange(BaseModel):
    work_plan_id: int
    workplan_code: Optional[str]    
    activity_title: str
    specific_task: str
    logistics_required: Optional[str]
    activity_date: date
    initiating_user_name: str
    workplan_source_name: str
    status: str
    employee_names: List[str]
    employee_count: int

    class Config:
        from_attributes = True
        

# class EmployeeModel(BaseModel):
#     id: int
#     name: str

class EmployeeModel(BaseModel):
    # Define your fields here, matching the SQLAlchemy model's attributes
    id: int
    first_name: str
    last_name: str
    employee_email: Optional[EmailStr] 
    phone_number:str
    staff_code:str
    # More fields as needed

    class Config:
        orm_mode = True
        from_attributes = True

class LocationModel(BaseModel):
    id: int
    name: str

class SiteModel(BaseModel):
    id: int
    name: str

class WorkPlanSourceModel(BaseModel):
    name: str

class WorkPlanDetails(BaseModel):
    id: int
    activity_title: str
    logistics_required: str
    workplan_source: Optional[WorkPlanSourceModel]
    employees: List[EmployeeModel]
    locations: List[LocationModel]
    sites: List[SiteModel]

    class Config:
        from_attributes = True


class EmployeeWithoutWorkPlan(BaseModel):
    employee_id: int
    staff_code: str
    last_name: str
    first_name: str
    phone_number: str

    class Config:
        from_attributes = True  # If you're fetching data directly from ORM models
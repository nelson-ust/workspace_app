from pydantic import BaseModel, Extra
from typing import Optional, List, Text
from datetime import date, datetime
from schemas.site_schemas import SiteRead

class IssueBase(BaseModel):
    source_id:Optional[int]
    issue_description:Text
    key_recommendation:Optional[Text]=None
    time_line_date:Optional[date]=None
    reported_by_id:int
    focal_persons:List[int]
    thematic_area_id:Optional[int]=None
    site_id:Optional[int]=None
    meeting_id:Optional[int]=None
    srt_id:Optional[int]=None
    unit_id:Optional[int]=None
    department_id:Optional[int]=None
    tenancy_id:int


class IssueCreate(IssueBase):
    pass


class IssueUpdate(BaseModel):
    source_id:Optional[int]
    issue_description:Optional[Text]=None
    key_recommendation:Optional[Text]=None
    date_reported:Optional[date]
    time_line_date:Optional[date]
    # focal_persons:Optional[List[int]]

    # class Config:
    #     extra='allow'
    


class IssueRead(IssueUpdate):
    id:int

    class Config:
        from_attributes = True


class EmployeeList(BaseModel):
    id: int
    first_name: str
    last_name: str
    employee_email:str

    class Config:
        from_attributes = True


class IssueLogClosure(BaseModel):
    notes_on_closure:Optional[str]=None
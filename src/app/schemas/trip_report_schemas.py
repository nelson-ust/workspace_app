from datetime import datetime
from typing import List, Optional
from fastapi import Query
from pydantic import BaseModel

class TripReportSchema(BaseModel):
    id: int
    file_path: str
    trip_id: int
    workplan_id: int
    tenancy_id: int
    is_submitted: bool
    trip_outcome: Optional[str]
    observations: Optional[str]
    summary: Optional[str]
    issue_identified: Optional[bool]

    class Config:
        orm_mode = True

class IssueDetail(BaseModel):
    issue_description: str
    status_id: int
    time_line_date: datetime
    key_recommendation: str
    focal_persons: List[int]

class TripReportSubmission(BaseModel):
    trip_id: int
    workplan_id: int
    summary: Optional[str]
    trip_outcome: Optional[str]
    observations: Optional[str]
    issue_identified: Optional[bool]
    trip_completed: Optional[bool]
    reason: Optional[str]
    site_ids: Optional[List[int]]
    issues: Optional[List[IssueDetail]]


# from datetime import datetime
# from typing import List, Optional
# from pydantic import BaseModel

# class IssueDetail(BaseModel):
#     issue_description: str
#     status_id: int
#     time_line_date: datetime
#     key_recommendation: str
#     focal_persons: List[int]

# class TripReportSubmission(BaseModel):
#     trip_id: int
#     workplan_id: int
#     summary: Optional[str]
#     trip_outcome: Optional[str]
#     observations: Optional[str]
#     issue_identified: Optional[bool]
#     trip_completed: Optional[bool]
#     reason: Optional[str]
#     site_ids: Optional[List[int]]
#     issues: Optional[List[IssueDetail]]

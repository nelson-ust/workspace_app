
# #schemas/personal_development_performance_review_schemas.py


# from pydantic import BaseModel, Field
# from datetime import date, datetime
# from typing import List, Optional
# from schemas.approval_flow_schemas import ApprovalFlowDisplaySchema

# # Define the schema for creating a new performance review
# # class PersonalDevelopmentPerformanceReviewCreateSchema(BaseModel):
# #     employee_id: int = Field(..., description="ID of the employee being reviewed")
# #     review_period_start: date = Field(..., description="Start date of the review period")
# #     review_period_end: date = Field(..., description="End date of the review period")
# #     goals: List[str] = Field(..., description="List of goals set for the employee")
# #     strengths: Optional[str] = Field(None, description="Employee's strengths as noted by the supervisor")
# #     areas_for_improvement: Optional[str] = Field(None, description="Areas where the employee can improve")
# #     supervisor_comments: Optional[str] = Field(None, description="Comments from the supervisor")
# #     next_steps: Optional[str] = Field(None, description="Recommended next steps for employee development")
# #     approval_flow_id: Optional[int] = Field(None, description="ID of the associated approval flow for the review process")
# #     created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Timestamp when the review was created")

# #     class Config:
# #         from_attributes = True  # For ORM mappings with Pydantic V2+

# class PersonalDevelopmentPerformanceReviewCreateSchema(BaseModel):
#     employee_id: int = Field(..., description="ID of the employee being reviewed")
#     review_period_start: date = Field(..., description="Start date of the review period")
#     review_period_end: date = Field(..., description="End date of the review period")
#     goals: List[str] = Field(..., description="List of goals set for the employee")
#     strengths: Optional[str] = Field(None, description="Employee's strengths as noted by the initiator")
#     areas_for_improvement: Optional[str] = Field(None, description="Areas where the employee can improve")
#     next_steps: Optional[str] = Field(None, description="Recommended next steps for employee development")
#     approval_flow_id: int = Field(..., description="ID of the associated approval flow for the review process")
#     created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Timestamp of when the review was created")
#     class Config:
#         from_attributes = True  # For ORM mappings with Pydantic V2+

# # Define the schema for updating an existing performance review
# class PersonalDevelopmentPerformanceReviewUpdateSchema(BaseModel):
#     review_period_start: Optional[date] = Field(None, description="Start date of the review period")
#     review_period_end: Optional[date] = Field(None, description="End date of the review period")
#     goals: Optional[List[str]] = Field(None, description="List of updated goals set for the employee")
#     strengths: Optional[str] = Field(None, description="Updated strengths of the employee")
#     areas_for_improvement: Optional[str] = Field(None, description="Updated areas for improvement")
#     supervisor_comments: Optional[str] = Field(None, description="Updated comments from the supervisor")
#     next_steps: Optional[str] = Field(None, description="Updated next steps for employee development")
#     approval_flow_id: Optional[int] = Field(None, description="ID of the associated approval flow for the review process")
#     updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="Timestamp of the last update")

#     class Config:
#         from_attributes = True


# # Define the schema for displaying a performance review (e.g., in API responses)
# class PersonalDevelopmentPerformanceReviewDisplaySchema(BaseModel):
#     id: int = Field(..., description="ID of the performance review")
#     employee_id: int = Field(..., description="ID of the employee being reviewed")
#     review_period_start: date = Field(..., description="Start date of the review period")
#     review_period_end: date = Field(..., description="End date of the review period")
#     goals: List[str] = Field(..., description="List of goals set for the employee")
#     strengths: Optional[str] = Field(None, description="Employee's strengths as noted by the supervisor")
#     areas_for_improvement: Optional[str] = Field(None, description="Areas where the employee can improve")
#     supervisor_comments: Optional[str] = Field(None, description="Comments from the supervisor")
#     next_steps: Optional[str] = Field(None, description="Recommended next steps for employee development")
#     approval_flow: Optional[ApprovalFlowDisplaySchema] = Field(None, description="Associated approval flow with the review")
#     created_at: datetime = Field(..., description="Timestamp when the review was created")
#     updated_at: Optional[datetime] = Field(None, description="Timestamp of the last update to the review")

#     class Config:
#         from_attributes = True


# # Define the schema for querying performance reviews (optional but useful for filtering)
# class PersonalDevelopmentPerformanceReviewQuerySchema(BaseModel):
#     employee_id: Optional[int] = Field(None, description="ID of the employee being reviewed")
#     review_period_start: Optional[date] = Field(None, description="Filter by the start date of the review period")
#     review_period_end: Optional[date] = Field(None, description="Filter by the end date of the review period")
#     approval_flow_id: Optional[int] = Field(None, description="ID of the associated approval flow for filtering")

from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field
from schemas.approval_flow_schemas import ApprovalFlowDisplaySchema

# Define schema for Result-Based Objective
class ResultBasedObjectiveSchema(BaseModel):
    objective_name: str = Field(..., description="Name of the result-based objective")
    description: Optional[str] = Field(None, description="Description of the result-based objective")
    result: Optional[str] = Field(None, description="The achieved result for this objective")

    class Config:
        orm_mode = True

# Define schema for Broad-Based Objective
class BroadBasedObjectiveSchema(BaseModel):
    objective_name: str = Field(..., description="Name of the broad-based objective")
    description: Optional[str] = Field(None, description="Description of the broad-based objective")
    result_based_objectives: List[ResultBasedObjectiveSchema] = Field(
        [], description="List of result-based objectives associated with this broad-based objective"
    )

    class Config:
        orm_mode = True

# Schema for creating a new performance review
class PersonalDevelopmentPerformanceReviewCreateSchema(BaseModel):
    employee_id: int = Field(..., description="ID of the employee being reviewed")
    review_period_start: date = Field(..., description="Start date of the review period")
    review_period_end: date = Field(..., description="End date of the review period")
    broad_based_objectives: List[BroadBasedObjectiveSchema] = Field(
        ..., description="List of broad-based objectives with nested result-based objectives"
    )
    strengths: Optional[str] = Field(None, description="Employee's strengths as noted by the initiator")
    areas_for_improvement: Optional[str] = Field(None, description="Areas where the employee can improve")
    next_steps: Optional[str] = Field(None, description="Recommended next steps for employee development")
    approval_flow_id: int = Field(..., description="ID of the associated approval flow for the review process")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Timestamp of when the review was created")
    
    class Config:
        from_attributes = True  # For ORM mappings with Pydantic V2+

# Schema for updating an existing performance review
class PersonalDevelopmentPerformanceReviewUpdateSchema(BaseModel):
    review_period_start: Optional[date] = Field(None, description="Start date of the review period")
    review_period_end: Optional[date] = Field(None, description="End date of the review period")
    broad_based_objectives: Optional[List[BroadBasedObjectiveSchema]] = Field(
        None, description="Updated list of broad-based objectives with nested result-based objectives"
    )
    strengths: Optional[str] = Field(None, description="Updated strengths of the employee")
    areas_for_improvement: Optional[str] = Field(None, description="Updated areas for improvement")
    supervisor_comments: Optional[str] = Field(None, description="Updated comments from the supervisor")
    next_steps: Optional[str] = Field(None, description="Updated next steps for employee development")
    approval_flow_id: Optional[int] = Field(None, description="ID of the associated approval flow for the review process")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="Timestamp of the last update")
    
    class Config:
        from_attributes = True

# Schema for displaying a performance review (e.g., in API responses)
class PersonalDevelopmentPerformanceReviewDisplaySchema(BaseModel):
    id: int = Field(..., description="ID of the performance review")
    employee_id: int = Field(..., description="ID of the employee being reviewed")
    review_period_start: date = Field(..., description="Start date of the review period")
    review_period_end: date = Field(..., description="End date of the review period")
    broad_based_objectives: List[BroadBasedObjectiveSchema] = Field(
        ..., description="List of broad-based objectives with nested result-based objectives"
    )
    strengths: Optional[str] = Field(None, description="Employee's strengths as noted by the supervisor")
    areas_for_improvement: Optional[str] = Field(None, description="Areas where the employee can improve")
    supervisor_comments: Optional[str] = Field(None, description="Comments from the supervisor")
    next_steps: Optional[str] = Field(None, description="Recommended next steps for employee development")
    approval_flow: Optional[ApprovalFlowDisplaySchema] = Field(None, description="Associated approval flow with the review")
    created_at: datetime = Field(..., description="Timestamp when the review was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of the last update to the review")
    
    class Config:
        from_attributes = True

# Schema for querying performance reviews (optional but useful for filtering)
class PersonalDevelopmentPerformanceReviewQuerySchema(BaseModel):
    employee_id: Optional[int] = Field(None, description="ID of the employee being reviewed")
    review_period_start: Optional[date] = Field(None, description="Filter by the start date of the review period")
    review_period_end: Optional[date] = Field(None, description="Filter by the end date of the review period")
    approval_flow_id: Optional[int] = Field(None, description="ID of the associated approval flow for filtering")

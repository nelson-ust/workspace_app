from pydantic import BaseModel, Field
from typing import List, Optional
from schemas.approval_step_schemas import ApprovalStepReadSchema

# Define the schema for individual approval steps
class ApprovalStepSchema(BaseModel):
    step_order: int = Field(..., description="Order of the approval step")
    role_id: int = Field(..., description="ID of the user role responsible for this step")
    description: Optional[str] = Field(None, description="Description of the approval step")

# Schema to use when creating a new Approval Flow
class ApprovalFlowCreateSchema(BaseModel):
    name: str = Field(..., description="Name of the approval flow")
    description: Optional[str] = Field(None, description="Description of the approval flow")
    module_id: int = Field(..., description="ID of the module this approval flow is associated with")
    steps: List[ApprovalStepSchema] = Field(..., description="List of approval steps for the flow")

# Schema to use for updating an existing Approval Flow
class ApprovalFlowUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, description="Name of the approval flow")
    description: Optional[str] = Field(None, description="Description of the approval flow")
    module_id: Optional[int] = Field(None, description="ID of the module this approval flow is associated with")
    steps: List[ApprovalStepSchema] = Field(..., description="Updated list of approval steps for the flow")

# Schema to represent the Approval Flow data that will be sent back to clients
class ApprovalFlowResponseSchema(ApprovalFlowCreateSchema):
    id: int = Field(..., description="Identifier of the approval flow")

# Schema for querying an approval flow (if needed, can be expanded with search filters)
class ApprovalFlowQuerySchema(BaseModel):
    name: Optional[str] = Field(None, description="Name to search for approval flows")

# Display schema for Approval Flow, including the detailed list of steps for clients
class ApprovalFlowDisplaySchema(BaseModel):
    id: int = Field(..., description="Identifier of the approval flow")
    name: str = Field(..., description="Name of the approval flow")
    description: Optional[str] = Field(None, description="Description of the approval flow")
    module_id: int = Field(..., description="ID of the module associated with this approval flow")
    steps: List[ApprovalStepReadSchema] = Field(..., description="Detailed list of approval steps in the flow")

    class Config:
        from_attributes = True  # To use with Pydantic V2, replaces orm_mode

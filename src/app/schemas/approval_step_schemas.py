# from pydantic import BaseModel
# from typing import Optional

# class ApprovalStepCreateSchema(BaseModel):
#     step_order: int
#     role_id: int
#     description: Optional[str]

# class ApprovalStepUpdateSchema(BaseModel):
#     step_order: Optional[int]
#     role_id: Optional[int]
#     description: Optional[str]

# class ApprovalStepReadSchema(BaseModel):
#     id: int
#     step_order: int
#     role_id: int
#     description: Optional[str]

#     class Config:
#         from_attributes = True  # This is for Pydantic v2 to replace 'orm_mode'



from pydantic import BaseModel, Field
from typing import Optional

# class ApprovalStepCreateSchema(BaseModel):
#     step_order: int = Field(..., description="Order of the approval step")
#     role_id: int = Field(..., description="ID of the role responsible for this step")
#     description: Optional[str] = Field(None, description="Description of the approval step")
#     module_id: int = Field(..., description="ID of the module associated with this approval step")
#     # approval_flow_id: int = Field(..., description="ID of the approval flow this step belongs to")

# class ApprovalStepUpdateSchema(BaseModel):
#     step_order: Optional[int] = Field(None, description="Updated order of the approval step")
#     role_id: Optional[int] = Field(None, description="Updated role ID for the approval step")
#     description: Optional[str] = Field(None, description="Updated description of the approval step")
#     module_id: Optional[int] = Field(None, description="Updated ID of the module associated with this step")
#     # approval_flow_id: Optional[int] = Field(None, description="Updated ID of the approval flow this step belongs to")

class ApprovalStepCreateSchema(BaseModel):
    step_order: int
    role_id: int
    action: str
    description: Optional[str]
    module_id: int
    flow_id: int  # Ensure this field is present and required

class ApprovalStepUpdateSchema(BaseModel):
    step_order: Optional[int]
    role_id: Optional[int]
    action: Optional[str]
    description: Optional[str]
    module_id: Optional[int]
    flow_id: Optional[int]

class ApprovalStepReadSchema(BaseModel):
    id: int = Field(..., description="ID of the approval step")
    step_order: int = Field(..., description="Order of the approval step")
    role_id: int = Field(..., description="ID of the role responsible for this step")
    description: Optional[str] = Field(None, description="Description of the approval step")
    module_id: int = Field(..., description="ID of the module associated with this approval step")
    # approval_flow_id: int = Field(..., description="ID of the approval flow this step belongs to")

    class Config:
        from_attributes = True  # This is for Pydantic v2 to replace 'orm_mode'

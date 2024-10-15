# from pydantic import BaseModel
# from typing import List, Optional
# from schemas.approval_flow_schemas import ApprovalFlowReadSchema

# # Base schema for Module - shared properties
# class ModuleBaseSchema(BaseModel):
#     name: str
#     description: Optional[str] = None

# # Schema for creating a new Module
# class ModuleCreateSchema(ModuleBaseSchema):
#     pass

# # Schema for updating an existing Module
# class ModuleUpdateSchema(BaseModel):
#     name: Optional[str] = None
#     description: Optional[str] = None

# # Schema for reading Module information with nested ApprovalFlows
# class ModuleReadSchema(ModuleBaseSchema):
#     id: int
#     approval_flows: List[ApprovalFlowReadSchema] = []

#     class Config:
#         orm_mode = True  # Enables compatibility with ORM objects


from pydantic import BaseModel, Field
from typing import Optional
from schemas.approval_flow_schemas import ApprovalFlowDisplaySchema  # Updated import

class ModuleCreateSchema(BaseModel):
    name: str = Field(..., description="Name of the module")
    description: Optional[str] = Field(None, description="Description of the module")

class ModuleUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, description="Name of the module")
    description: Optional[str] = Field(None, description="Description of the module")

class ModuleReadSchema(ModuleCreateSchema):
    id: int = Field(..., description="ID of the module")
    approval_flow: Optional[ApprovalFlowDisplaySchema] = Field(None, description="Associated approval flow")

    class Config:
        from_attributes = True

class ModuleSchema(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True
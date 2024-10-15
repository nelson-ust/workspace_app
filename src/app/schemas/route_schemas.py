# # schemas/route_schemas.py
# from pydantic import BaseModel
# from typing import List, Optional

# class ModuleSchema(BaseModel):
#     id: int
#     name: str

#     class Config:
#         orm_mode = True

# class RouteCreateSchema(BaseModel):
#     path: str
#     method: str
#     description: Optional[str] = None
#     module_id: Optional[int] = None
#     permitted_roles: List[str]

# class RouteUpdateSchema(BaseModel):
#     description: Optional[str] = None
#     module_id: Optional[int] = None
#     permitted_roles: Optional[List[str]] = None

# class RouteDisplaySchema(BaseModel):
#     id: int
#     path: str
#     method: str
#     description: str
#     module: Optional[ModuleSchema]  # Include Module details

#     class Config:
#         from_attributes = True
#         orm_mode = True

# schemas/route_schemas.py
from pydantic import BaseModel
from typing import List, Optional
from .module_schemas import ModuleSchema  # Import the module schema

class RouteCreateSchema(BaseModel):
    path: str
    method: str
    description: Optional[str] = None
    permitted_roles: List[str]
    module_id: int

class RouteUpdateSchema(BaseModel):
    description: Optional[str] = None
    permitted_roles: Optional[List[str]]
    module_id: Optional[int]

class RouteDisplaySchema(BaseModel):
    id: int
    path: str
    method: str
    description: str
    module: ModuleSchema  # Update to use ModuleSchema

    class Config:
        orm_mode = True  # Ensure it works with SQLAlchemy objects
        from_attributes = True

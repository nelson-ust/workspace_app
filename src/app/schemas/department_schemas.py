#department_schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

# Base schema for common attributes
class DepartmentBase(BaseModel):
    name: str

# Schema for department creation requests
class DepartmentCreate(DepartmentBase):
    pass

# Schema for department update requests
class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, description="New name of the department")

# Schema for reading department data, includes employees
class DepartmentRead(DepartmentBase):
    id: int
    # Assuming you have an EmployeeRead schema defined somewhere that you want to include
    employees: List[Optional['EmployeeRead']] = []

    class Config:
        from_attributes = True

# Necessary due to Pydantic's need to prevent circular imports.
# Define EmployeeRead schema after DepartmentRead or in a separate module to avoid circular import issues.
from schemas.employee_schemas import EmployeeRead  # Adjust import path as necessary
DepartmentRead.update_forward_refs()

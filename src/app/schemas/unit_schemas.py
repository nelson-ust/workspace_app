# from pydantic import BaseModel, Field
# from typing import Optional

# # Schema for unit responses
# class UnitBase(BaseModel):
#     name: str

# # Schema for requests to create a Unit
# class UnitCreate(UnitBase):
#     department_id: int = Field(..., description="The ID of the department the unit belongs to")

# # Schema for requests to update a Unit
# class UnitUpdate(BaseModel):
#     name: Optional[str] = None
#     department_id: Optional[int] = None

# # Schema for reading a Unit, including its ID and department_id
# class UnitRead(UnitBase):
#     id: int
#     name:str
#     department_id: int
#     department_name:Optional[str] = None

#     class Config:
#         from_attributes = True


# # class UnitRead(BaseModel):
# #     id: int
# #     name: str
# #     department_id: int
# #     # If you want to include department_name in the response, ensure it's defined here.
#     department_name: Optional[str] = None


from pydantic import BaseModel, Field
from typing import Optional, List

# Schema for unit responses
class UnitBase(BaseModel):
    name: str

# Schema for requests to create a Unit
class UnitCreate(UnitBase):
    department_id: int = Field(..., description="The ID of the department the unit belongs to")

# Schema for requests to update a Unit
class UnitUpdate(BaseModel):
    name: Optional[str] = None
    department_id: Optional[int] = None

# Schema for reading a Unit, including its ID and department_id
class UnitRead(UnitBase):
    id: int
    name:str
    department_id: int
    department_name:Optional[str] = None
    employees: List[Optional['EmployeeRead']] = []

    class Config:
        from_attributes = True


# class UnitRead(BaseModel):
#     id: int
#     name: str
#     department_id: int
#     # If you want to include department_name in the response, ensure it's defined here.
#     department_name: Optional[str] = None
from schemas.employee_schemas import EmployeeRead  # Adjust import path as necessary
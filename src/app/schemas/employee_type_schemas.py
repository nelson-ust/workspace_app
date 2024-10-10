from pydantic import BaseModel
from typing import Optional

class EmployeeTypeBase(BaseModel):
    name: str
    description: Optional[str] = None

class EmployeeTypeCreate(EmployeeTypeBase):
    pass

class EmployeeTypeUpdate(EmployeeTypeBase):
    pass

class EmployeeTypeResponse(EmployeeTypeBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

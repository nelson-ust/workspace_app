from typing import List, Optional
from pydantic import BaseModel

class UserRoleBase(BaseModel):
    name: str

class UserRoleCreate(UserRoleBase):
    pass

class UserRoleUpdate(UserRoleBase):
    pass

class UserBase(BaseModel):
    username: str
    email: str

    class Config:
        from_attributes = True

class UserInUserRole(UserBase):
    id: int
    employee_id: Optional[int] = None

class UserRole(UserRoleBase):
    id: int
    users: List[UserInUserRole] = []

    class Config:
        from_attributes = True

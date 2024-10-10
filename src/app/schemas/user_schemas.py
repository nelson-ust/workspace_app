# #schemas/user_schemas.py
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

# Base models for roles
class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    pass

class RoleRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# Base models for users
class UserBase(BaseModel):
    username: str = Field(..., example="johndoe")
    email: EmailStr = Field(..., example="johndoe@example.com")

class UserCreate(UserBase):
    password: str = Field(..., min_length=7, example="verysecretpassword")
    employee_id: Optional[int] = None
    tenancy_id: int

class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=7, example="newsecretpassword")
    employee_id: Optional[int] = None
    tenancy_id: Optional[int] = None


class ProjectRead(BaseModel):
    project_id: int
    project_name: str
    project_description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    roles: List[RoleRead] = []
    employee_id: Optional[int] = None
    tenancy_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    tenancy_name: Optional[str] = None
    unit_id: Optional[int] = None
    department_id: Optional[int] = None
    projects: List[ProjectRead] = []  # Include projects data

    class Config:
        from_attributes = True


# Models for handling password reset
class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    reset_token: str
    new_password: str

# Token models for JWT handling
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str]

# Model for user with extended details, possibly for use in more detailed user profile endpoints
class UserReadWithTeancy(UserRead):
    tenancy_name: Optional[str]  # Add tenancy name for extended details

class UserReadWithEmployee(UserRead):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]  # New field, assuming this is part of the user details now

class RoleAssignment(BaseModel):
    user_id: int
    roles: List[int]

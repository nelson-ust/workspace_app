from pydantic import BaseModel
from typing import Optional

class ProjectComponentBase(BaseModel):
    name: str
    description: Optional[str]

class ProjectComponentCreate(ProjectComponentBase):
    project_id: int

class ProjectComponentUpdate(ProjectComponentBase):
    pass

class ProjectComponentOut(ProjectComponentBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TaskStatusBase(BaseModel):
    name: str = Field(..., example="Pending")

class TaskStatusCreate(TaskStatusBase):
    pass

class TaskStatusUpdate(TaskStatusBase):
    name: Optional[str] = Field(None, example="In Progress")

class TaskStatusInDBBase(TaskStatusBase):
    id: int
    is_active: bool
    date_created: Optional[datetime]
    date_updated: Optional[datetime] = None
    date_deleted: Optional[datetime] = None

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
        }

class TaskStatus(TaskStatusInDBBase):
    pass

class TaskStatusInDB(TaskStatusInDBBase):
    pass

class TaskStatusList(BaseModel):
    tasks: List[TaskStatus]

    class Config:
        orm_mode = True

class TaskStatusResponse(TaskStatusInDBBase):
    class Config:
        orm_mode = True

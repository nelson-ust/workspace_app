from pydantic import BaseModel
from typing import Optional

class FunderBase(BaseModel):
    name: str
    description: Optional[str] = None

class FunderCreate(FunderBase):
    pass

class FunderUpdate(FunderBase):
    pass

class FunderOut(FunderBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

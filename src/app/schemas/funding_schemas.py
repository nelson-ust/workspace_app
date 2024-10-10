from pydantic import BaseModel
from typing import Optional

class FundingBase(BaseModel):
    project_id: int
    funder_id: int
    component_id: int
    amount_funded: float

class FundingCreate(FundingBase):
    pass

class FundingUpdate(FundingBase):
    pass

class FundingOut(FundingBase):
    is_active: bool

    class Config:
        orm_mode = True

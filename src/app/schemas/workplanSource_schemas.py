from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WorkPlanSourceBase(BaseModel):
    name: str

class WorkPlanSourceCreate(WorkPlanSourceBase):
    pass

class WorkPlanSourceUpdate(WorkPlanSourceBase):
    pass

class WorkPlanSourceInDBBase(WorkPlanSourceBase):
    id: int
    date_created: Optional[datetime] = None
    date_updated: Optional[datetime] = None

    class Config:
        from_attributes = True

class WorkPlanSource(WorkPlanSourceInDBBase):
    pass

# If you have a WorkPlan model that needs to be included in the response
# for a WorkPlanType, define it here and add it to the WorkPlanType model.

class WorkPlanBase(BaseModel):
    title: str
    description: Optional[str] = None

    # Assuming there's a need for a simplified WorkPlan schema here
    class Config:
        from_attributes = True

class WorkPlanTypeWithWorkPlans(WorkPlanSource):
    workplans: List[WorkPlanBase] = []
    #

# # schemas/meal_combination_schemas.py

# from pydantic import BaseModel
# from typing import Optional

# class MealCombinationBase(BaseModel):
#     name: str
#     description: Optional[str] = None

# class MealCombinationCreate(MealCombinationBase):
#     pass

# class MealCombinationUpdate(MealCombinationBase):
#     pass

# class MealCombinationResponse(MealCombinationBase):
#     id: int
#     is_active: bool

#     class Config:
#         orm_mode = True
#         from_attributes=True


# schemas/meal_combination_schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MealCombinationBase(BaseModel):
    name: str
    description: Optional[str] = None

class MealCombinationCreate(MealCombinationBase):
    pass

class MealCombinationUpdate(MealCombinationBase):
    pass

class MealCombinationResponse(MealCombinationBase):
    id: int
    is_active: bool
    date_created: datetime
    date_updated: Optional[datetime] = None
    date_deleted: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes=True

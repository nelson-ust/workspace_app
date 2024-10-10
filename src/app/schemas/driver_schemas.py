# from typing import Optional
# from pydantic import BaseModel
# from datetime import date

# # Schema for Driver responses
# class DriverBase(BaseModel):
#     user_id: int
#     licence_number: str
#     licence_exp_date: date
#     tenancy_id: int
#     is_available:bool

# # Schema for requests to create a Driver
# class DriverCreate(DriverBase):
#     pass

# # Schema for requests to update a Driver
# class DriverUpdate(BaseModel):
#     licence_number: str
#     licence_exp_date: date
#     is_available: Optional[bool]
#     # tenancy_id: int

# # Schema for reading a Driver
# class DriverRead(DriverBase):
#     id:int
#     full_name: str
#     class Config:
#         from_attributes = True



from typing import Optional
from pydantic import BaseModel
from datetime import date

# Schema for Driver responses
class DriverBase(BaseModel):
    user_id: int
    licence_number: str
    licence_exp_date: date
    tenancy_id: int
    is_available: bool

# Schema for requests to create a Driver
class DriverCreate(DriverBase):
    pass

# Schema for requests to update a Driver
class DriverUpdate(BaseModel):
    licence_number: str
    licence_exp_date: date
    is_available: Optional[bool]

# Schema for reading a Driver
class DriverRead(DriverBase):
    id: int
    full_name: str

    class Config:
        from_attributes = True

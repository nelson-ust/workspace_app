# # # schemas/leave_request_schemas.py
# # from pydantic import BaseModel
# # from datetime import date

# # class LeaveRequestBase(BaseModel):
# #     employee_id: int
# #     start_date: date
# #     end_date: date
# #     reason: str

# # class LeaveRequestCreate(LeaveRequestBase):
# #     hr_staff_id: int
# #     reliever_id: int

# # class LeaveRequestUpdate(BaseModel):
# #     status: str

# # class LeaveRequestResponse(LeaveRequestBase):
# #     id: int
# #     status: str

# #     class Config:
# #         orm_mode = True



# from pydantic import BaseModel
# from datetime import date

# class LeaveRequestBase(BaseModel):
#     start_date: date
#     end_date: date
#     reason: str

# class LeaveRequestCreate(LeaveRequestBase):
#     hr_staff_id: int
#     reliever_id: int

# class LeaveRequestUpdate(BaseModel):
#     status: str

# class LeaveRequestResponse(LeaveRequestBase):
#     id: int
#     employee_id: int
#     status: str

#     class Config:
#         orm_mode = True



# In your Pydantic schemas (schemas/leave_request_schemas.py)
from pydantic import BaseModel
from datetime import date

class LeaveRequestBase(BaseModel):
    start_date: date
    end_date: date
    reason: str
    leave_type_id: int  # Add this line

class LeaveRequestCreate(LeaveRequestBase):
    hr_staff_id: int
    reliever_id: int

class LeaveRequestUpdate(BaseModel):
    status: str

class LeaveRequestResponse(LeaveRequestBase):
    id: int
    status: str

    class Config:
        orm_mode = True

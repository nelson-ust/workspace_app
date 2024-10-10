from pydantic import BaseModel, Field
from typing import List, Optional

# Base schema for BankDetail
class BankDetailBase(BaseModel):
    bank_name: str = Field(..., description="Name of the bank")
    account_number: str = Field(..., description="Bank account number")
    ifsc_code: Optional[str] = Field(None, description="IFSC code of the bank")

    class Config:
        orm_mode = True

# Schema for creating a new BankDetail
class BankDetailCreate(BankDetailBase):
    employee_id: int = Field(..., description="ID of the employee associated with the bank detail")

# Schema for updating an existing BankDetail
class BankDetailUpdate(BaseModel):
    bank_name: Optional[str] = Field(None, description="Name of the bank")
    account_number: Optional[str] = Field(None, description="Bank account number")
    ifsc_code: Optional[str] = Field(None, description="IFSC code of the bank")

    class Config:
        orm_mode = True

# Schema for reading a BankDetail (includes the ID and employee ID)
class BankDetail(BankDetailBase):
    id: int = Field(..., description="ID of the bank detail")
    employee_id: int = Field(..., description="ID of the employee associated with the bank detail")

# Schema for reading a list of BankDetails
class BankDetailList(BaseModel):
    bank_details: list[BankDetail] = Field(..., description="List of bank details")

    class Config:
        orm_mode = True

class BankDetailsFilter(BaseModel):
    project_ids: Optional[List[int]]
    tenancy_ids: Optional[List[int]]
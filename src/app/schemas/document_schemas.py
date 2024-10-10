from pydantic import BaseModel
from typing import Optional

class DocumentCreate(BaseModel):
    employee_id: int
    document_type_id: int
    file_name: str

class DocumentRead(BaseModel):
    id: int
    name: str
    document_type_id: int
    file_path: str
    employee_id: int

    class Config:
        orm_mode = True

class EmployeeWithoutDocumentRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    employee_email: str

    class Config:
        orm_mode = True

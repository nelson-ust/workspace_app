from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from db.database import get_db
from schemas.employee_type_schemas import EmployeeTypeCreate, EmployeeTypeUpdate, EmployeeTypeResponse
from repositories.employee_type_repository import EmployeeTypeRepository
from schemas.user_schemas import UserRead
from auth.security import get_current_user
from auth.dependencies import role_checker
from logging_helpers import logging_helper

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/employee_type/", response_model=EmployeeTypeResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_employee_type(
    request: Request, 
    employee_type_data: EmployeeTypeCreate, 
    current_user: UserRead = Depends(get_current_user), 
    db: Session = Depends(get_db), 
    _= Depends(role_checker(['super_admin']))
) -> EmployeeTypeResponse:
    
    logging_helper.log_info("Accessing - Create Employee Type - Endpoint")
    employee_type_repo = EmployeeTypeRepository(db)
    try:
        new_employee_type = employee_type_repo.create_employee_type(employee_type_data)
        return new_employee_type
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error creating Employee Type: {str(e)}")


@router.get("/employee_type/", response_model=List[EmployeeTypeResponse], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_all_employee_types(
    request: Request, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    _= Depends(role_checker(['hq_backstop','unit_member','unit_lead','programs-lead', 'tech-lead', 'stl', 'tenant_admin', 'super_admin']))
) -> List[EmployeeTypeResponse]:
    
    try:
        logging_helper.log_info("Accessing - Read all Employee Types - Endpoint")
        employee_type_repo = EmployeeTypeRepository(db)
        employee_types = employee_type_repo.get_all_employee_types()
        return employee_types
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error retrieving Employee Types: {str(e)}")


@router.get("/employee_type/{employee_type_id}", response_model=EmployeeTypeResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_employee_type(
    request: Request, 
    employee_type_id: int, 
    db: Session = Depends(get_db), 
    _= Depends(role_checker(['hq_backstop','unit_member','unit_lead','programs-lead', 'tech-lead', 'stl', 'tenant_admin', 'super_admin']))
) -> EmployeeTypeResponse:
    
    try:
        logging_helper.log_info("Accessing - Read Employee Type - Endpoint")
        employee_type_repo = EmployeeTypeRepository(db)
        employee_type = employee_type_repo.get_employee_type_by_id(employee_type_id)
        if employee_type is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee Type not found")
        return employee_type
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error retrieving Employee Type: {str(e)}")


@router.put("/employee_type/{employee_type_id}", response_model=EmployeeTypeResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def update_employee_type(
    request: Request, 
    employee_type_id: int, 
    employee_type_data: EmployeeTypeUpdate, 
    db: Session = Depends(get_db), 
    _= Depends(role_checker(['super_admin']))
) -> EmployeeTypeResponse:
    
    try:
        logging_helper.log_info("Accessing - Update Employee Type - Endpoint")
        employee_type_repo = EmployeeTypeRepository(db)
        updated_employee_type = employee_type_repo.update_employee_type(employee_type_id, employee_type_data)
        if updated_employee_type is None:
            raise HTTPException(status_code=404, detail="Employee Type not found")
        return updated_employee_type
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error updating Employee Type: {str(e)}")


@router.post("/employee_type/{employee_type_id}/soft_delete")
@limiter.limit("5/minute")
async def soft_delete_employee_type(
    request: Request, 
    employee_type_id: int, 
    current_user: UserRead = Depends(get_current_user), 
    db: Session = Depends(get_db), 
    _= Depends(role_checker(['super_admin']))
) -> dict:
    
    try:
        logging_helper.log_info("Accessing - Soft Delete Employee Type - Endpoint")
        employee_type_repo = EmployeeTypeRepository(db)
        employee_type = employee_type_repo.soft_delete_employee_type(employee_type_id)
        if not employee_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee Type not found or not soft-deleted")
        return {"message": "Employee Type soft deleted successfully"}
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error soft deleting Employee Type: {str(e)}")


@router.post("/employee_type/{employee_type_id}/restore")
@limiter.limit("5/minute")
async def restore_employee_type(
    request: Request, 
    employee_type_id: int, 
    current_user: UserRead = Depends(get_current_user), 
    db: Session = Depends(get_db), 
    _= Depends(role_checker(['super_admin']))
) -> EmployeeTypeResponse:
    
    try:
        logging_helper.log_info("Accessing - Restore Employee Type - Endpoint")
        employee_type_repo = EmployeeTypeRepository(db)
        employee_type = employee_type_repo.restore(employee_type_id)
        if not employee_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee Type not found or not restored")
        return employee_type
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error restoring Employee Type: {str(e)}")

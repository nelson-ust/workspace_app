#routes/unit_routes.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request  
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from auth.dependencies import role_checker
from db.database import get_db  
from schemas.unit_schemas import UnitCreate, UnitRead, UnitUpdate  
from repositories.unit_repository import UnitRepository  
from logging_helpers import logging_helper
from schemas.user_schemas import UserRead
from auth.security import get_current_user

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/units/", response_model=UnitRead, status_code=status.HTTP_201_CREATED)
async def create_unit(unit_create: UnitCreate, db: Session = Depends(get_db), _=Depends(role_checker(["super_admin"]))):
    
    logging_helper.log_info("Accessing - Create Unit - Endpoint")
    unit_repo = UnitRepository(db)
    # Check if unit name already exists
    if unit_repo.check_unit_name_exists(unit_create.name):
        raise HTTPException(status_code=400, detail="Unit name already exists. Please choose a different name.")
    try:
        new_unit = unit_repo.create_unit(unit_create)
        return new_unit
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error creating unit: {str(e)}")


@router.get("/units/", response_model=List[UnitRead])
@limiter.limit("10/minute")
async def read_units(request: Request,skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user:UserRead=Depends(get_current_user), _=Depends(role_checker(['hq_backstop','unit_member','unit_lead','programs-lead', 'tech-lead', 'stl', 'tenant_admin', 'super_admin']))):
    try:
        logging_helper.log_info("Accessing - Read Units - Endpoint")
        unit_repo = UnitRepository(db)
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                units = unit_repo.get_units(skip=skip, limit=limit)
            else:
                units = unit_repo.get_units(skip=skip, limit=limit, unit_id=current_user.unit_id)
            return units
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error fetching unit: {str(e)}")


@router.get("/units/{unit_id}", response_model=UnitRead)
@limiter.limit("10/minute")
async def read_unit(request: Request,unit_id: int, db: Session = Depends(get_db), current_user:UserRead=Depends(get_current_user), _=Depends(role_checker(['hq_backstop','unit_member','unit_lead','programs-lead', 'tech-lead', 'stl', 'tenant_admin', 'super_admin']))):
    try:
        logging_helper.log_info("Accessing - Read Unit - Endpoint")
        unit_repo = UnitRepository(db)
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                unit = unit_repo.get_unit_by_id(unit_id)
            else:
                unit = unit_repo.get_unit_by_id(unit_id, unit_identity=current_user.unit_id)
            if unit is None:
                raise HTTPException(status_code=404, detail="Unit not found")
            return unit
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error fetching unit: {str(e)}")


@router.put("/units/{unit_id}")
@limiter.limit("5/minute")
async def update_unit(request: Request,unit_id: int, unit: UnitUpdate, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    try:
        logging_helper.log_info("Accessing - Update Unit - Endpoint")
        unit_repo = UnitRepository(db)
        updated_unit = unit_repo.update_unit(unit_id, unit)
        if updated_unit is None:
            raise HTTPException(status_code=404, detail="Unit not found")
        return updated_unit
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error updating unit: {str(e)}")


@router.delete("/units/{unit_id}/soft")
@limiter.limit("2/minute")
async def soft_delete_unit(request: Request,unit_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    try:
        logging_helper.log_info("Accessing - Soft Delete - Endpoint")
        unit_repo = UnitRepository(db)
        unit = unit_repo.delete_unit(unit_id)
        if unit is None:
            raise HTTPException(status_code=404, detail="Unit not found")
        return unit
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Unable to soft delete unit: {str(e)}")


@router.post("/units/{unit_id}/restore")
@limiter.limit("2/minute")
async def restore_unit(request: Request,unit_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    try:
        logging_helper.log_info("Accessing - Restore Unit - Endpoint")
        unit_repo = UnitRepository(db)
        restored_unit = unit_repo.restore_unit(unit_id)
        if restored_unit is None:
            raise HTTPException(status_code=404, detail="Unit not found or not deleted")
        return restored_unit
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error restoring unit: {str(e)}")


@router.get("/units/by-department/{department_name}", response_model=List[UnitRead], tags=["Units"])
async def get_units_by_department(department_name: str, db: Session = Depends(get_db), current_user:UserRead=Depends(get_current_user), _=Depends(role_checker(['hq_backstop','unit_member','unit_lead','programs-lead', 'tech-lead', 'stl', 'tenant_admin', 'super_admin']))):
    """
    Fetch units by department name.
    """
    try:
        logging_helper.log_info("Accessing - Get Unit by Department - Endpoint")
        unit_repo = UnitRepository(db)
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                units = unit_repo.get_units_by_department_name(department_name)

            else:
                units = unit_repo.get_units_by_department_name(department_name, department_id=current_user.department_id)

            if units is None:
                raise HTTPException(status_code=404, detail="No units found for this department")
            return units
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error fetching unit: {str(e)}")

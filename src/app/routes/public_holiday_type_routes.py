from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from db.database import get_db
from schemas.holiday_type_schemas import HolidayTypeCreate, HolidayTypeUpdate, HolidayTypeResponse
from repositories.public_holiday_type_repository import HolidayTypeRepository
from schemas.user_schemas import UserRead
from auth.dependencies import role_checker 
from logging_helpers import logging_helper
from logging_helpers import logging_helper
from auth.security import get_current_user

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/public_holiday_type/", response_model=HolidayTypeResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_public_holiday_type(
    request: Request, 
    holiday_type_data: HolidayTypeCreate, 
    current_user: UserRead = Depends(get_current_user), 
    db: Session = Depends(get_db), 
    _= Depends(role_checker(['super_admin']))
) -> HolidayTypeResponse:
    
    logging_helper.log_info("Accessing - Create Public Holiday Type - Endpoint")
    holiday_type_repo = HolidayTypeRepository(db)
    try:
        new_holiday_type = holiday_type_repo.create_holiday_type(holiday_type_data)
        return new_holiday_type
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error creating Public Holiday Type: {str(e)}")


@router.get("/public_holiday_type/", response_model=List[HolidayTypeResponse], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_all_public_holiday_types(
    request: Request, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    _= Depends(role_checker(['hq_backstop','unit_member','unit_lead','programs-lead', 'tech-lead', 'stl', 'tenant_admin', 'super_admin']))
) -> List[HolidayTypeResponse]:
    
    try:
        logging_helper.log_info("Accessing - Read all Public Holiday Types - Endpoint")
        holiday_type_repo = HolidayTypeRepository(db)
        holiday_types = holiday_type_repo.get_all_holiday_types()
        return holiday_types
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error retrieving Public Holiday Types: {str(e)}")


@router.get("/public_holiday_type/{holiday_type_id}", response_model=HolidayTypeResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_public_holiday_type(
    request: Request, 
    holiday_type_id: int, 
    db: Session = Depends(get_db), 
    _= Depends(role_checker(['hq_backstop','unit_member','unit_lead','programs-lead', 'tech-lead', 'stl', 'tenant_admin', 'super_admin']))
) -> HolidayTypeResponse:
    
    try:
        logging_helper.log_info("Accessing - Read Public Holiday Type - Endpoint")
        holiday_type_repo = HolidayTypeRepository(db)
        holiday_type = holiday_type_repo.get_holiday_type_by_id(holiday_type_id)
        if holiday_type is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Public Holiday Type not found")
        return holiday_type
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error retrieving Public Holiday Type: {str(e)}")


@router.put("/public_holiday_type/{holiday_type_id}", response_model=HolidayTypeResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def update_public_holiday_type(
    request: Request, 
    holiday_type_id: int, 
    holiday_type_data: HolidayTypeUpdate, 
    db: Session = Depends(get_db), 
    _= Depends(role_checker(['super_admin']))
) -> HolidayTypeResponse:
    try:
        logging_helper.log_info("Accessing - Update Public Holiday Type - Endpoint")
        holiday_type_repo = HolidayTypeRepository(db)
        updated_holiday_type = holiday_type_repo.update_holiday_type(holiday_type_id, holiday_type_data)
        if updated_holiday_type is None:
            raise HTTPException(status_code=404, detail="Public Holiday Type not found")
        return updated_holiday_type
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error updating Public Holiday Type: {str(e)}")


@router.post("/public_holiday_type/{holiday_type_id}/soft_delete")
@limiter.limit("5/minute")
async def soft_delete_public_holiday_type(
    request: Request, 
    holiday_type_id: int, 
    current_user: UserRead = Depends(get_current_user), 
    db: Session = Depends(get_db), 
    _= Depends(role_checker(['super_admin']))
) -> dict:
    
    try:
        logging_helper.log_info("Accessing - Soft Delete Public Holiday Type - Endpoint")
        holiday_type_repo = HolidayTypeRepository(db)
        holiday_type = holiday_type_repo.soft_delete_holiday_type(holiday_type_id)
        if not holiday_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Public Holiday Type not found or not soft-deleted")
        return {"message": "Public Holiday Type soft deleted successfully"}
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error soft deleting Public Holiday Type: {str(e)}")


@router.post("/public_holiday_type/{holiday_type_id}/restore")
@limiter.limit("5/minute")
async def restore_public_holiday_type(
    request: Request, 
    holiday_type_id: int, 
    current_user: UserRead = Depends(get_current_user), 
    db: Session = Depends(get_db), 
    _= Depends(role_checker(['super_admin']))
) -> HolidayTypeResponse:
    
    try:
        logging_helper.log_info("Accessing - Restore Public Holiday Type - Endpoint")
        holiday_type_repo = HolidayTypeRepository(db)
        holiday_type = holiday_type_repo.restore(holiday_type_id)
        if not holiday_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Public Holiday Type not found or not restored")
        return holiday_type
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error restoring Public Holiday Type: {str(e)}")

#routes/location_routes.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from auth.dependencies import role_checker
from db.database import get_db  # Adjust import path as needed
from schemas.maintenancetype_schemas import MaintenanceCreate, MaintenanceUpdate, MaintenanceRead  # Adjust import paths as necessary
from repositories.maintenancetype_repository import MaintenanceTypeRepository  # Adjust import path as needed
from logging_helpers import logging_helper

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/maintenancetype/", response_model=MaintenanceRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_maintenancetype(request: Request, maintenancetype_data:MaintenanceCreate, db: Session = Depends(get_db),_=Depends(role_checker(['super_admin']))):
    
    logging_helper.log_info("Accessing - Create Maintenancetype - Endpoint")
    maintenancetype_repo = MaintenanceTypeRepository(db)
    try:
        new_maintenancetype = maintenancetype_repo.create_maintenancetype(maintenancetype_data)
        return new_maintenancetype
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error creating Maintenance: Warning Unauthorized: {str(e)}")


@router.get("/maintenancetype/", response_model=List[MaintenanceRead], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_all_maintenancetype(request: Request, db: Session = Depends(get_db),_=Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    try:
        logging_helper.log_info("Accessing - Read all Maintenancetype - Endpoint")
        maintenancetype_repo = MaintenanceTypeRepository(db)
        print(f"Fetching maintenancetype")
        maintenancetype = maintenancetype_repo.get_all_maintenancetype()
        print(f"Found maintenancetype: {maintenancetype}")
        return maintenancetype
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


@router.get("/maintenancetype/{maintenancetype_id}", response_model=MaintenanceRead, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_maintenancetype(request: Request, maintenancetype_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    try:
        logging_helper.log_info("Accessing - Read Maintenancetype - Endpoint")
        maintenancetype_repo = MaintenanceTypeRepository(db)
        maintenancetype = maintenancetype_repo.get_maintenance_by_id(maintenancetype_id)
        if maintenancetype is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"maintenancetype not found")
        return maintenancetype
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


@router.put("/maintenancetype/{maintenancetype_id}")
@limiter.limit("10/minute")
async def update_maintenancetype(request: Request, maintenancetype_id: int, maintenancetype_data:MaintenanceUpdate, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    try:
        logging_helper.log_info("Accessing - Update Maintenancetype - Endpoint")
        maintenancetype_repo = MaintenanceTypeRepository(db)
        updated_maintenancetype = maintenancetype_repo.update_maintenancetype(maintenancetype_id, maintenancetype_data)
        if updated_maintenancetype is None:
            raise HTTPException(status_code=404, detail="Maintenancetype not found")
        return updated_maintenancetype
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


@router.delete("/maintenancetype/{maintenancetype_id}/soft_delete")
@limiter.limit("5/minute")
async def soft_delete_maintenancetype(request: Request, maintenancetype_id:int, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    try:
        logging_helper.log_info("Accessing - Soft Delete Maintenancetype - Endpoint")
        maintenancetype_repo = MaintenanceTypeRepository(db)
        maintenancetype = maintenancetype_repo.soft_delete_maintenancetype(maintenancetype_id)
        if not maintenancetype:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Maintenancetype not found")
        return maintenancetype
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


@router.post("/maintenancetype/{maintenancetype_id}/restore")
@limiter.limit("5/minute")
async def restore_maintenancetype(request: Request, maintenancetype_id:int, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    try:
        logging_helper.log_info("Accessing - Restore Maintenancetype - Endpoint")
        maintenancetype_repo = MaintenanceTypeRepository(db)
        maintenancetype = maintenancetype_repo.restore(maintenancetype_id)
        if not maintenancetype:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Maintenancetype not found")
        return maintenancetype
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")



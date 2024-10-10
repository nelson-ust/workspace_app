#routes/thematicarea_routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from auth.dependencies import role_checker
from db.database import get_db
from repositories.thematic_area_repository import ThematicAreaRepository
from slowapi.util import get_remote_address
from slowapi import Limiter
from schemas.thematic_area_schemas import ThematicAreaCreate, ThematicAreaUpdate, ThematicAreaRead
from logging_helpers import logging_helper

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/thematicarea/", response_model=ThematicAreaRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_thematic_area(request:Request, thematic_area_data: ThematicAreaCreate, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    logging_helper.log_info("Accessing - Create Thematic Area - Endpoint")
    thematic_repo = ThematicAreaRepository(db)
    try:
        thematic_area = thematic_repo.create_thematic_area(thematic_area_data)
        return thematic_area
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error creating Thematic Area: {str(e)}")


@router.get("/thematicarea/", response_model=List[ThematicAreaRead], status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def read_all_thematic_area(request:Request, db: Session = Depends(get_db), _=Depends(role_checker(['hq_backstop','unit_member','unit_lead','programs-lead', 'tech-lead', 'stl', 'tenant_admin', 'super_admin']))):
    
    logging_helper.log_info("Accessing - Read all Thematics Area - Endpoint")
    thematic_repo = ThematicAreaRepository(db)
    try:
        thematic_areas= thematic_repo.get_all_thematic_area()
        return thematic_areas
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error {str(err)}")


@router.get("/thematicarea/{thematic_area_id}", response_model=ThematicAreaRead)
@limiter.limit("5/minute")
async def read_thematic_area(request:Request, thematic_area_id:int, db: Session = Depends(get_db), _=Depends(role_checker(['hq_backstop','unit_member','unit_lead','programs-lead', 'tech-lead', 'stl', 'tenant_admin', 'super_admin']))):
    
    logging_helper.log_info("Accessing - Read Thematic Area - Endpoint")
    thematic_repo = ThematicAreaRepository(db)
    try:
        thematic_area = thematic_repo.get_thematic_area_by_id(thematic_area_id)
        return thematic_area
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error {str(err)}")


@router.put("/thematicarea/{thematic_area_id}")
@limiter.limit("5/minute")
async def update_thematic_area(request:Request, thematic_area_id: int, thematic_area_data: ThematicAreaUpdate, db: Session = Depends(get_db),_=Depends(role_checker(['super_admin']))):
    
    logging_helper.log_info("Accessing - Update Thematic Area - Endpoint")
    thematic_repo = ThematicAreaRepository(db)
    try:
        thematic_area = thematic_repo.update_thematic_area(thematic_area_id=thematic_area_id, thematic_area_update=thematic_area_data)
        return thematic_area
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error {str(err)}")


@router.delete("/thematicarea/{thematic_area_id}/softdelete")
@limiter.limit("5/minute")
async def soft_delete_thematic_area(request:Request, thematic_area_id: int,  db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    logging_helper.log_info("Accessing - Soft Delete Thematic Area - Endpoint")
    thematic_repo = ThematicAreaRepository(db)
    try:

        thematic_area = thematic_repo.soft_delete_thematic_area(thematic_area_id=thematic_area_id)
        if thematic_area is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Thematic Area not found or already deactivated")

        return thematic_area
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error {str(err)}")
    
    
@router.post("/thematicarea/{thematic_area_id}/reactivate")
@limiter.limit("5/minute")
async def reactivate_deleted_thematic_area(request:Request, thematic_area_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    logging_helper.log_info("Accessing - Reactivate Deleted Thematic Area - Endpoint")
    thematic_repo = ThematicAreaRepository(db)
    try:
        thematic_area = thematic_repo.reactivate_deleted_thematic_area(thematic_area_id=thematic_area_id)
        return thematic_area
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error {str(err)}")
        

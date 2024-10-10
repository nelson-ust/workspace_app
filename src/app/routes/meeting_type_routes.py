# routes/meeting_type_routes.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from repositories.meeting_type_repository import MeetingTypeRepository
from logging_helpers import logging_helper
from auth.security import get_current_user
from models.all_models import User, ActionEnum
from schemas.meeting_type_schemas import MeetingTypeCreate, MeetingTypeUpdate, MeetingTypeResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import json

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

@router.post("/meeting_types/", response_model=MeetingTypeResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def add_meeting_type(request: Request, meeting_type: MeetingTypeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logging_helper.log_info("Accessing - Create MeetingType - Endpoint")
    meeting_type_repo = MeetingTypeRepository(db)
    try:
        logging_helper.log_info(f"Creating new MeetingType with name: {meeting_type.name}")
        new_meeting_type = meeting_type_repo.create_meeting_type(meeting_type)
        logging_helper.log_info(f"Created MeetingType: {new_meeting_type}")
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "MeetingType", new_meeting_type.id, json.dumps(new_meeting_type, default=str))
        return MeetingTypeResponse.from_orm(new_meeting_type)
    except Exception as e:
        logging_helper.log_error(f"Failed to create meeting type: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create meeting type")

@router.get("/meeting_types/{meeting_type_id}", response_model=MeetingTypeResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_meeting_type(request: Request, meeting_type_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Read MeetingType - Endpoint")
    meeting_type_repo = MeetingTypeRepository(db)
    try:
        meeting_type = meeting_type_repo.get_meeting_type(meeting_type_id)
        if not meeting_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting type not found")
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "MeetingType", meeting_type_id, None)
        return MeetingTypeResponse.from_orm(meeting_type)
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch meeting type: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch meeting type")

@router.get("/meeting_types/", response_model=List[MeetingTypeResponse], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_meeting_types(request: Request, skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Read All MeetingTypes - Endpoint")
    meeting_type_repo = MeetingTypeRepository(db)
    try:
        meeting_types = meeting_type_repo.get_meeting_types(skip=skip, limit=limit)
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "MeetingType", None, "Read all meeting types")
        return meeting_types
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch meeting types: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch meeting types")

@router.put("/meeting_types/{meeting_type_id}", response_model=MeetingTypeResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def update_meeting_type(request: Request, meeting_type_id: int, meeting_type: MeetingTypeUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Update MeetingType - Endpoint")
    meeting_type_repo = MeetingTypeRepository(db)
    try:
        updated_meeting_type = meeting_type_repo.update_meeting_type(meeting_type_id, meeting_type)
        if not updated_meeting_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting type not found")
        logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "MeetingType", meeting_type_id, json.dumps(updated_meeting_type, default=str))
        return MeetingTypeResponse.from_orm(updated_meeting_type)
    except Exception as e:
        logging_helper.log_error(f"Failed to update meeting type: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update meeting type")

@router.delete("/meeting_types/{meeting_type_id}", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def delete_meeting_type(request: Request, meeting_type_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Delete MeetingType - Endpoint")
    meeting_type_repo = MeetingTypeRepository(db)
    try:
        deleted_meeting_type = meeting_type_repo.delete_meeting_type(meeting_type_id)
        if not deleted_meeting_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting type not found")
        logging_helper.log_audit(db, current_user.id, ActionEnum.DELETE, "MeetingType", meeting_type_id, json.dumps(deleted_meeting_type, default=str))
        return {"message": f"The MeetingType with ID: {meeting_type_id} deleted successfully!"}
    except Exception as e:
        logging_helper.log_error(f"Failed to delete meeting type: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete meeting type")

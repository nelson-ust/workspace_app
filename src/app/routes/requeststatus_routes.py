from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from auth.dependencies import role_checker
from db.database import get_db
from repositories.requeststatus_repository import RequestStatusRepository
from schemas.requeststatus_schemas import RequestStatusCreate, RequestStatusUpdate, RequestStatus
from logging_helpers import logging_helper

router = APIRouter()

@router.post("/request-statuses/", response_model=RequestStatus, status_code=status.HTTP_201_CREATED)
def create_request_status(request_status: RequestStatusCreate, db: Session = Depends(get_db), _=Depends(role_checker(['hr-admin', 'super_admin']))):
    
    logging_helper.log_info("Accessing - Create Request Status - Endpoint")
    repo = RequestStatusRepository(db)
    return repo.create_request_status(request_status)

@router.get("/request-statuses/", response_model=List[RequestStatus])
def read_all_request_statuses(db: Session = Depends(get_db), _=Depends(role_checker(['hr-admin', 'super_admin']))):
    
    logging_helper.log_info("Accessing - Read all Request Statuses - Endpoint")
    repo = RequestStatusRepository(db)
    return repo.get_all_request_statuses()

@router.get("/request-statuses/{request_status_id}", response_model=RequestStatus)
def read_request_status(request_status_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['hr-admin', 'super_admin']))):
    
    logging_helper.log_info("Accessing - Read Request Status - Endpoint")
    repo = RequestStatusRepository(db)
    return repo.get_request_status_by_id(request_status_id)

@router.put("/request-statuses/{request_status_id}", response_model=RequestStatus)
def update_request_status(request_status_id: int, request_status_update: RequestStatusUpdate, db: Session = Depends(get_db), _=Depends(role_checker(['hr-admin', 'super_admin']))):
    
    logging_helper.log_info("Accessing - Update Request Status - Endpoint")
    repo = RequestStatusRepository(db)
    return repo.update_request_status(request_status_id, request_status_update)

@router.patch("/request-statuses/{request_status_id}/deactivate", response_model=RequestStatus)
def soft_delete_request_status(request_status_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['hr-admin', 'super_admin']))):
    
    logging_helper.log_info("Accessing - Soft Delete request Status - Endpoint")
    repo = RequestStatusRepository(db)
    return repo.delete_request_status(request_status_id)


# ['approved','rejected','returned','pending']
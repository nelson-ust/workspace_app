#routes/srt_routes.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from auth.dependencies import role_checker
from db.database import get_db  # Adjust import path as needed
from schemas.srt_schemas import EmployeeInSRTRead, SRTCreate, SRTUpdate, SRTRead  # Adjust import path as needed
from repositories.srt_repository import SRTRepository  # Adjust import path as needed
from logging_helpers import logging_helper

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/srts/", response_model=SRTRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_srt(request: Request, srt_data: SRTCreate, db: Session = Depends(get_db)): #, _=Depends(role_checker(['programs-lead', 'tech-lead', 'stl', 'tenant_admin']))):
    
    logging_helper.log_info("Accessing - Create SRT - Endpoint")
    srt_repo = SRTRepository(db)
    try:
        new_srt = srt_repo.create_srt(srt_data)
        return new_srt
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating SRT: {str(e)}")

@router.get("/srts/{srt_id}", response_model=SRTRead)
@limiter.limit("10/minute")
async def read_srt(request: Request, srt_id: int, db: Session = Depends(get_db)): #, _=Depends(role_checker(['programs-lead', 'tech-lead', 'stl', 'tenant_admin']))):
    
    logging_helper.log_info("Accessing - Read SRT - Endpoint")
    srt_repo = SRTRepository(db)
    srt = srt_repo.get_srt_by_id(srt_id)
    if not srt:
        raise HTTPException(status_code=404, detail="SRT not found")
    return srt

@router.get("/srts/", response_model=list[SRTRead])
@limiter.limit("10/minute")
async def read_all_srts(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)): #, _=Depends(role_checker(['programs-lead', 'tech-lead', 'stl', 'tenant_admin']))):
    
    logging_helper.log_info("Accessing - Read all SRTs - Endpoint")
    srt_repo = SRTRepository(db)
    srts = srt_repo.get_srts(skip=skip, limit=limit)
    return srts

@router.put("/srts/{srt_id}", response_model=SRTRead)
@limiter.limit("5/minute")
async def update_srt(request: Request, srt_id: int, srt_data: SRTUpdate, db: Session = Depends(get_db)): #, _=Depends(role_checker(['programs-lead', 'tech-lead', 'stl', 'tenant_admin']))):
    
    logging_helper.log_info("Accessing - Update SRT - Endpoint")
    srt_repo = SRTRepository(db)
    updated_srt = srt_repo.update_srt(srt_id, srt_data)
    if not updated_srt:
        raise HTTPException(status_code=404, detail="SRT not found")
    return updated_srt

@router.delete("/srts/{srt_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def delete_srt(request: Request, srt_id: int, db: Session = Depends(get_db)): #, _=Depends(role_checker(['programs-lead', 'tech-lead', 'stl', 'tenant_admin']))):
    
    logging_helper.log_info("Accessing - Delete SRT - Endpoint")
    srt_repo = SRTRepository(db)
    try:
        srt_repo.delete_hard(srt_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"SRT not found or could not be deleted: {str(e)}")
    return {"detail": "SRT deleted successfully"}

@router.post("/srts/{srt_id}/soft-delete", response_model=SRTRead)
@limiter.limit("5/minute")
async def soft_delete_srt(request: Request, srt_id: int, db: Session = Depends(get_db)): #, _=Depends(role_checker(['programs-lead', 'tech-lead', 'stl', 'tenant_admin']))):
    
    logging_helper.log_info("Accessing - Soft Delete SRT - Endpoint")
    srt_repo = SRTRepository(db)
    soft_deleted_srt = srt_repo.soft_delete_srt(srt_id)
    if not soft_deleted_srt:
        raise HTTPException(status_code=404, detail="SRT not found or already soft-deleted")
    return soft_deleted_srt

@router.post("/srts/{srt_id}/restore", response_model=SRTRead)
@limiter.limit("5/minute")
async def restore_srt(request: Request, srt_id: int, db: Session = Depends(get_db)): #, _=Depends(role_checker(['programs-lead', 'tech-lead', 'stl', 'tenant_admin']))):
    
    logging_helper.log_info("Accessing - Restore SRT - Endpoint")
    srt_repo = SRTRepository(db)
    restored_srt = srt_repo.restore_srt(srt_id)
    if not restored_srt:
        raise HTTPException(status_code=404, detail="SRT not found or not deleted")
    return restored_srt


# @router.get("/srts/{srt_id}/employees", response_model=list[SRTRead])
# @limiter.limit("10/minute")
# async def get_employees_in_srt(request: Request, srt_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['programs-lead', 'tech-lead', 'stl', 'tenant_admin']))):
#     srt_repo = SRTRepository(db)
#     try:
#         employees = srt_repo.get_employees_in_srt(srt_id)
#         return employees
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error fetching employees for SRT: {str(e)}")

@router.get("/srts/{srt_id}/employees", response_model=List[EmployeeInSRTRead])
async def get_employees_in_srt(srt_id: int, db: Session = Depends(get_db)): #, _=Depends(role_checker(['programs-lead', 'tech-lead', 'stl', 'tenant_admin']))):
    
    logging_helper.log_info("Accessing - Get Employees in SRT - Endpoint")
    srt_repo = SRTRepository(db)
    employees = srt_repo.get_employees_in_srt(srt_id)
    if not employees:
        raise HTTPException(status_code=404, detail="No employees found for this SRT or SRT does not exist.")
    return employees
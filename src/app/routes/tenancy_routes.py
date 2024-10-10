from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter, _rate_limit_exceeded_handler
#from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from auth.dependencies import role_checker
from db.database import get_db  # Adjust your import based on your project structure
from schemas.tenancy_schemas import TenancyCreate, TenancyUpdate, TenancyRead  # Adjust your import
from repositories.tenancy_repository import TenancyRepository  # Adjust your import
from logging_helpers import logging_helper
from schemas.user_schemas import UserRead
from auth.security import get_current_user

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

# Register the rate limit exceeded handler
#router.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/tenancies/", response_model=TenancyRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_tenancy(request: Request,tenancy: TenancyCreate, current_user:UserRead=Depends(get_current_user), 
                        db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    try:
        logging_helper.log_info("Accessing - Creaate Tenancy - Endpoint")
        tenancy_repo = TenancyRepository(db)
    
        return tenancy_repo.create_tenancy(tenancy)
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")


@router.get("/tenancies/", response_model=List[TenancyRead])
@limiter.limit("10/minute")
async def read_tenancies(request: Request,skip: int = 0, limit: int = 100, current_user:UserRead=Depends(get_current_user), 
                        db: Session = Depends(get_db), _=Depends(role_checker(['hq_backstop','unit_member','unit_lead','programs-lead', 'tech-lead', 'stl', 'tenant_admin', 'super_admin']))):
    try:
        logging_helper.log_info("Accessing - Read Tenancies - Endpoint")
        tenancy_repo = TenancyRepository(db)
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", 'hq_backstop']:
                tenancies = tenancy_repo.get_tenancies(skip=skip, limit=limit)
            else:
                tenancies = tenancy_repo.get_tenancies(skip=skip, limit=limit, tenancy_id=current_user.tenancy_id)
            return tenancies
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")


@router.get("/tenancies/{tenancy_id}", response_model=TenancyRead)
@limiter.limit("10/minute")
async def read_tenancy(request: Request,tenancy_id: int, current_user:UserRead=Depends(get_current_user), 
                        db: Session = Depends(get_db), _=Depends(role_checker(['hq_backstop','unit_member','unit_lead','programs-lead', 'tech-lead', 'stl', 'tenant_admin', 'super_admin']))):
    try:
        logging_helper.log_info("Accessing - Read Tenancy - Endpoint")
        tenancy_repo = TenancyRepository(db)
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", 'hq_backstop']:
                tenancy = tenancy_repo.get_tenancy_by_id(tenancy_id)
                if tenancy is None:
                    raise HTTPException(status_code=404, detail="Tenancy not found")
            else:
                tenancy = tenancy_repo.get_tenancy_by_id(tenancy_id, tenanant_id=current_user.tenancy_id)
                if tenancy is None:
                    raise HTTPException(status_code=404, detail="Tenancy not found now")
            return tenancy
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")


@router.put("/tenancies/{tenancy_id}")
@limiter.limit("5/minute")
async def update_tenancy(request: Request,tenancy_id: int, tenancy: TenancyUpdate, db: Session = Depends(get_db), _=Depends(role_checker(["super_admin"]))):
    try:
        logging_helper.log_info("Accessing - Update Tenancy - Endpoint")
        tenancy_repo = TenancyRepository(db)
        updated_tenancy = tenancy_repo.update_tenancy(tenancy_id, tenancy)
        if updated_tenancy is None:
            raise HTTPException(status_code=404, detail="Tenancy not found")
        return updated_tenancy
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")
    

@router.delete("/tenancies/{tenancy_id}/soft")
@limiter.limit("5/minute")
async def soft_delete_tenancy(request: Request,tenancy_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    try:
        logging_helper.log_info("Accessing - Soft Delete Tenancy - Endpoint")
        tenancy_repo = TenancyRepository(db)
        if not tenancy_repo.soft_delete_tenancy(tenancy_id):
            raise HTTPException(status_code=404, detail="Tenancy not found or already deleted")
        return {"detail": "Tenancy soft-deleted successfully"}
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")

    

@router.post("/tenancies/{tenancy_id}/restore")
@limiter.limit("5/minute")
async def restore_tenancy(request: Request,tenancy_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    try:
        logging_helper.log_info("Accessing - Restore Tenancy - Endpoint")
        tenancy_repo = TenancyRepository(db)
        restored_tenancy = tenancy_repo.restore(tenancy_id)
        if restored_tenancy is None:
            raise HTTPException(status_code=404, detail="Tenancy not found or not deleted")
        return {"detail": "Tenancy restored successfully"}
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")


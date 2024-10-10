#routes/issuelogsource_routes.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from auth.dependencies import role_checker
from db.database import get_db  # Adjust import path as needed
from schemas.issueLogSource_schemas import IssueLogSourceCreate, IssueLogSourceUpdate, IssueLogSourceRead  # Adjust import paths as necessary
from repositories.issueLogSource_repository import IssueLogSourceRepository  # Adjust import path as needed
from logging_helpers import logging_helper


limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/issuelogsource/", response_model=IssueLogSourceRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_issuelogsource(request: Request, issuelogsource_data:IssueLogSourceCreate, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    logging_helper.log_info("Accessing - Create Issue Log Source - Endpoint")
    issuelogsource_repo = IssueLogSourceRepository(db)
    try:
        new_issuelogsource = issuelogsource_repo.create_issuelogsource(issuelogsource_data)
        return new_issuelogsource
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error creating IssueLog Source: Warning Unauthorized: {str(e)}")


@router.get("/issuelogsource/", response_model=List[IssueLogSourceRead], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_all_issuelogsource(request: Request, db: Session = Depends(get_db),_=Depends(role_checker(["unit_memeber", 'programs_lead', 'technical_lead', 'stl', 'tenant_admin','super_admin']))):
    
    try:
        logging_helper.log_info("Accessing - Read all Issue Log Source - Endpoint")
        issuelogsource_repo = IssueLogSourceRepository(db)
        print(f"Fetching issuelogsource")
        issuelogsource = issuelogsource_repo.get_all_issuelogsource()
        print(f"Found issuelogsource: {issuelogsource}")
        return issuelogsource
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


@router.get("/issuelogsource/{issuelogsource_id}", response_model=IssueLogSourceRead, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_issuelogsource(request: Request, issuelogsource_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['unit_memeber', 'programs_lead', 'technical_lead', 'stl', 'tenant_admin','super_admin']))):
    
    try:
        logging_helper.log_info("Accessing - Read Issue Log Sourse - Endpoint")
        issuelogsource_repo = IssueLogSourceRepository(db)
        issuelogsource = issuelogsource_repo.get_issuelogsource_by_id(issuelogsource_id)
        if issuelogsource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"issuelogsource not found")
        return issuelogsource
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


@router.put("/issuelogsource/{issuelogsource_id}")
@limiter.limit("10/minute")
async def update_issuelogsource(request: Request, issuelogsource_id: int, issuelogsource_data:IssueLogSourceUpdate, db: Session = Depends(get_db)): #, _=Depends(role_checker(['programs_lead', 'technical_lead', 'stl', 'tenant_admin','super_admin']))):
    
    try:
        logging_helper.log_info("Accessing - Update Issue Log Source - Endpoint")
        issuelogsource_repo = IssueLogSourceRepository(db)
        updated_issuelogsource = issuelogsource_repo.update_issuelogsource(issuelogsource_id, issuelogsource_data)
        if updated_issuelogsource is None:
            raise HTTPException(status_code=404, detail="Issuelogsource not found")
        return updated_issuelogsource
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


@router.post("/issuelogsource/{issuelogsource_id}/soft_delete")
@limiter.limit("5/minute")
async def soft_delete_issuelogsource(request: Request, issuelogsource_id:int, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    try:
        logging_helper.log_info("Accessing - Soft Delete Issue Log Source - Endpoint")
        issuelogsource_repo = IssueLogSourceRepository(db)
        issuelogsource = issuelogsource_repo.soft_delete_issuelogsource(issuelogsource_id)
        if not issuelogsource:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issuelogsource not found or not soft-deleted")
        return issuelogsource
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


@router.post("/issuelogsource/{issuelogsource_id}/restore")
@limiter.limit("5/minute")
async def restore_issuelogsource(request: Request, issuelogsource_id:int, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    try:
        logging_helper.log_info("Accessing - Restore Issue Log Source - Endpoint")
        issuelogsource_repo = IssueLogSourceRepository(db)
        issuelogsource = issuelogsource_repo.restore_issue_log_source(issuelogsource_id)
        if not issuelogsource:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issuelogsource not found or not soft-deleted")
        return issuelogsource
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")



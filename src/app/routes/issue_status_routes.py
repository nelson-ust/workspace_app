#routes/issue_status_routes.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from db.database import get_db 
from schemas.issue_status_schemas import IssueStatusCreate, IssueStatusUpdate, IssueStatusRead 
from repositories.issue_status_repository import IssueStatusRepository
from schemas.user_schemas import UserRead
from auth.security import get_current_user
from auth.dependencies import role_checker 
from logging_helpers import logging_helper

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/issue_status/", response_model=IssueStatusRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_issuelogsource(request: Request, issue_status_data:IssueStatusCreate, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    logging_helper.log_info("Accessing - Create Issue Log Source - Endpoint")
    issue_status_repo = IssueStatusRepository(db)
    try:
        new_issue_status = issue_status_repo.create_issue_status(issue_status_data)
        return new_issue_status
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error creating Issue Status: {str(e)}")


@router.get("/issue_status/", response_model=List[IssueStatusRead], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_all_issuelogsource(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(role_checker(['hq_backstop','unit_member','unit_lead','programs-lead', 'tech-lead', 'stl', 'tenant_admin', 'super_admin']))):
    
    try:
        logging_helper.log_info("Accessing - Read all Issue Log source - Endpoint")
        issue_status_repo = IssueStatusRepository(db)
        print(f"Fetching issuelogsource with skip={skip} and limit={limit}")
        issue_status = issue_status_repo.get_all_issue_status(skip=skip, limit=limit)
        print(f"Found IssueStatus: {issue_status}")
        return issue_status
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error with Issue Status: {str(e)}")


@router.get("/issue_status/{issue_status_id}", response_model=IssueStatusRead, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_issue_status(request: Request, issue_status_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['hq_backstop','unit_member','unit_lead','programs-lead', 'tech-lead', 'stl', 'tenant_admin', 'super_admin']))):
    
    try:
        logging_helper.log_info("Accessing - Read Issue Status - Endpoint")
        issue_status_repo = IssueStatusRepository(db)
        issue_status = issue_status_repo.get_issue_status_by_id(issue_status_id)
        if issue_status is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"IssueStatus not found")
        return issue_status
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error with Issue Status: {str(e)}")


@router.put("/issue_issue_status/{issue_status_id}", response_model=IssueStatusRead, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def update_issue_status(request: Request, issue_status_id: int, issue_status_data:IssueStatusUpdate, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    try:
        logging_helper.log_info("Accessing - Update Issue Status - Endpoint")
        issue_status_repo = IssueStatusRepository(db)
        updated_issue_status = issue_status_repo.update_issue_status(issue_status_id, issue_status_data)
        if updated_issue_status is None:
            raise HTTPException(status_code=404, detail="IssueStatus not found")
        return updated_issue_status
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error with Issue Status: {str(e)}")


@router.post("/issue_status/{issue_status_id}/soft_delete")
@limiter.limit("5/minute")
async def soft_delete_issue_status(request: Request, issue_status_id:int, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    try:
        logging_helper.log_info("Accessing - Soft Dele Issue Status - Endpoint")
        issue_status_repo = IssueStatusRepository(db)
        issue_status = issue_status_repo.soft_delete_issue_status(issue_status_id)
        if not issue_status:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"IssueStatus not found or not soft-deleted")
        return issue_status
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error with Issue Status: {str(e)}")


@router.post("/issue_status/{issue_status_id}/restore")
@limiter.limit("5/minute")
async def restore_issue_status(request: Request, issue_status_id:int, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    try:
        logging_helper.log_info("Accessing - restore Issue status - Endpoint")
        issue_status_repo = IssueStatusRepository(db)
        issue_status = issue_status_repo.restore(issue_status_id)
        if not issue_status:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"IssueStatus not found or not soft-deleted")
        return issue_status
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error with Issue Status: {str(e)}")



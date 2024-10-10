#routes/worklansource_routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from models.all_models import WorkPlanSource
from auth.dependencies import role_checker
from db.database import get_db
from repositories.workplanSource_repository import WorkPlanSourceRepository
from schemas.workplanSource_schemas import WorkPlanSourceCreate, WorkPlanSourceUpdate, WorkPlanSource
from logging_helpers import logging_helper
router = APIRouter()


@router.post("/workplan-sources/", response_model=WorkPlanSource, status_code=status.HTTP_201_CREATED)
def create_work_plan_source(work_plan_source: WorkPlanSourceCreate, db: Session = Depends(get_db),_=Depends(role_checker(['super_admin']))):
    logging_helper.log_info("Accessing - Create Workplan Source - Endpoint")
    try:
        repo = WorkPlanSourceRepository(db)
        return repo.create_work_plan_source(work_plan_source)
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")
    

@router.get("/workplan-sources/", response_model=List[WorkPlanSource])
def read_all_work_plan_sources(db: Session = Depends(get_db)): #, _=Depends(role_checker(['super_admin']))):
    logging_helper.log_info("Accessing - Read All Workplan Sources - Endpoint")
    try:
        repo = WorkPlanSourceRepository(db)
        return repo.get_all_work_plan_sources()
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")
    

@router.get("/workplan-sources/{work_plan_source_id}", response_model=WorkPlanSource)
def read_work_plan_source(work_plan_source_id: int, db: Session = Depends(get_db)): #, _=Depends(role_checker(['super_admin']))):
    logging_helper.log_info("Accessing - Read Workplan Sources - Endpoint")
    try:
        repo = WorkPlanSourceRepository(db)
        workplan = repo.get_work_plan_source_by_id(work_plan_source_id)
        if workplan is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workplan Source with ID {work_plan_source_id} not found")
        return workplan
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")


@router.put("/workplan-sources/{work_plan_source_id}")
def update_work_plan_source(work_plan_source_id: int, work_plan_source: WorkPlanSourceUpdate, db: Session = Depends(get_db),_=Depends(role_checker(['super_admin']))):
    logging_helper.log_info("Accessing - Update Work Plan Sources - Endpoint")
    try:
        repo = WorkPlanSourceRepository(db)
        return repo.update_work_plan_source(work_plan_source_id, work_plan_source)
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")


@router.patch("/workplan-sources/{work_plan_source_id}/deactivate")
def soft_delete_work_plan_source(work_plan_source_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    logging_helper.log_info("Accessing - Soft Delete Work Plan - Endpoint")
    repo = WorkPlanSourceRepository(db)
    try:
        work_plan_source = repo.delete_work_plan_source(work_plan_source_id)
        if work_plan_source is None:
            raise HTTPException(status_code=404, detail="WorkPlan Source not found")
        return work_plan_source
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")


@router.patch("/workplan-sources/{work_plan_source_id}/reactivate", status_code=status.HTTP_200_OK)
def reactivate_work_plan_source(work_plan_source_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    logging_helper.log_info("Accessing - Reactivate Work Plan Source - Endpoint")
    repo = WorkPlanSourceRepository(db)
    try:
        work_plan_source = repo.reactivate_work_plan_source(work_plan_source_id)
        if work_plan_source is None:
            raise HTTPException(status_code=404, detail="WorkPlan Source not found")
        return work_plan_source
    except HTTPException as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")




from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Dict, List
from db.database import get_db
from repositories.milestone_repository import MilestoneRepository
from logging_helpers import logging_helper
from auth.security import get_current_user
from schemas.milestone_schemas import MilestoneCreate, MilestoneUpdate, MilestoneResponse, MilestoneDetailResponse
from models.all_models import User, ActionEnum
from slowapi import Limiter
from slowapi.util import get_remote_address
import json
from datetime import date, datetime

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

def model_to_dict(instance):
    data = {c.name: getattr(instance, c.name) for c in instance.__table__.columns}
    # Convert date fields to strings
    for key, value in data.items():
        if isinstance(value, (date, datetime)):
            data[key] = value.isoformat()
    return data

@router.post("/milestones/", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_milestone(request: Request, milestone: MilestoneCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Create Milestone - Endpoint")
    milestone_repo = MilestoneRepository(db)
    try:
        new_milestone = milestone_repo.create_milestone(milestone)
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.CREATE, "Milestone", new_milestone.id, json.dumps(model_to_dict(new_milestone))
        )
        return MilestoneResponse.from_orm(new_milestone)
    except Exception as e:
        logging_helper.log_error(f"Failed to create milestone: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create milestone")

@router.get("/milestones/{milestone_id}", response_model=MilestoneDetailResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_milestone(request: Request, milestone_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Read Milestone - Endpoint")
    milestone_repo = MilestoneRepository(db)
    try:
        milestone_data = milestone_repo.get_milestone(milestone_id)
        if not milestone_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Milestone", milestone_id, None)
        return MilestoneDetailResponse(
            milestone=MilestoneResponse.from_orm(milestone_data["milestone"]),
            assignment_employees=milestone_data["assignment_employees"],
            responsible_employee=milestone_data["responsible_employee"]
        )
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch milestone: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch milestone")

@router.get("/milestones/", response_model=List[MilestoneDetailResponse], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_milestones(request: Request, skip: int = 0, limit: int = 10, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Read All Milestones - Endpoint")
    milestone_repo = MilestoneRepository(db)
    try:
        milestones_data = milestone_repo.get_milestones(skip=skip, limit=limit)
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Milestone", None, f"skip={skip}, limit={limit}")
        return [
            MilestoneDetailResponse(
                milestone=MilestoneResponse.from_orm(milestone_data["milestone"]),
                assignment_employees=milestone_data["assignment_employees"],
                responsible_employee=milestone_data["responsible_employee"]
            )
            for milestone_data in milestones_data
        ]
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch milestones: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch milestones: {str(e)}")

@router.put("/milestones/{milestone_id}", response_model=MilestoneResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def update_milestone(request: Request, milestone_id: int, milestone: MilestoneUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Update Milestone - Endpoint")
    milestone_repo = MilestoneRepository(db)
    try:
        updated_milestone = milestone_repo.update_milestone(milestone_id, milestone)
        if not updated_milestone:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.UPDATE, "Milestone", updated_milestone.id, json.dumps(model_to_dict(updated_milestone))
        )
        return MilestoneResponse.from_orm(updated_milestone)
    except Exception as e:
        logging_helper.log_error(f"Failed to update milestone: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update milestone: {str(e)}")

@router.delete("/milestones/{milestone_id}", response_model=Dict[str, str], status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def delete_milestone(request: Request, milestone_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Delete Milestone - Endpoint")
    milestone_repo = MilestoneRepository(db)
    try:
        deleted_milestone = milestone_repo.delete_milestone(milestone_id)
        if not deleted_milestone:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.DELETE, "Milestone", milestone_id, json.dumps(model_to_dict(deleted_milestone))
        )
        return {"message": f"The Milestone with ID: {milestone_id} deleted successfully!"}
    except Exception as e:
        logging_helper.log_error(f"Failed to delete milestone: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete milestone")



@router.put("/milestones/{milestone_id}/complete", status_code=status.HTTP_200_OK)
@limiter.limit("20/minute")
async def complete_milestone(request: Request, milestone_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info(f"Accessing - Complete Milestone - Endpoint for milestone ID {milestone_id}")
    milestone_repo = MilestoneRepository(db)
    try:
        completed_milestone = milestone_repo.complete_milestone(milestone_id, user_id=current_user.id)
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.UPDATE, "Milestone", milestone_id, f"Milestone completed: {completed_milestone}"
        )
        return completed_milestone
    except Exception as e:
        logging_helper.log_error(f"Failed to complete milestone with ID {milestone_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to complete milestone: {str(e)}")


@router.put("/milestones/{milestone_id}/substitute_responsible_person", response_model=MilestoneResponse)
@limiter.limit("5/minute")
async def substitute_responsible_person_for_milestone(
    request: Request,
    milestone_id: int,
    new_employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    milestone_repo = MilestoneRepository(db)
    try:
        result = milestone_repo.substitute_responsible_person_for_milestone(milestone_id, new_employee_id, current_user.id)
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.UPDATE,
            "Milestone",
            milestone_id,
            json.dumps(result),
        )
        return result
    except HTTPException as e:
        logging_helper.log_error(f"HTTP exception occurred: {e.detail}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unhandled exception occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
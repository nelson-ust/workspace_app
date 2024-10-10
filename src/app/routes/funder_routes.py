from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from repositories.funder_repository import FunderRepository
from schemas.funder_schemas import FunderCreate, FunderUpdate, FunderOut
from auth.dependencies import get_current_user, role_checker
from logging_helpers import logging_helper, AuditLog
#from models import AuditLog, ActionEnum
from models.all_models import ActionEnum

router = APIRouter()

@router.get("/funders/{funder_id}", response_model=FunderOut)
def get_funder(
    funder_id: int, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user), 
    _=Depends(role_checker(['super_admin', 'tenant_admin', 'hq_backstop']))
):
    logging_helper.log_info(f"User {current_user.username} is fetching funder with ID {funder_id}")
    repo = FunderRepository(db)
    try:
        funder = repo.get_funder(funder_id)
        if not funder:
            logging_helper.log_warning(f"Funder with ID {funder_id} not found")
            raise HTTPException(status_code=404, detail="Funder not found")

        logging_helper.log_info(f"Funder with ID {funder_id} fetched successfully")
        return funder
    except Exception as e:
        logging_helper.log_error(f"An error occurred while fetching funder with ID {funder_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/funders", response_model=List[FunderOut])
def get_funders(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user), 
    _=Depends(role_checker(['super_admin', 'tenant_admin', 'hq_backstop']))
):
    logging_helper.log_info(f"User {current_user.username} is fetching funders with skip={skip} and limit={limit}")
    repo = FunderRepository(db)
    try:
        funders = repo.get_funders(skip=skip, limit=limit)
        logging_helper.log_info(f"{len(funders)} funders fetched successfully")
        return funders
    except Exception as e:
        logging_helper.log_error(f"An error occurred while fetching funders: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/funders", response_model=FunderOut, status_code=status.HTTP_201_CREATED)
def create_funder(
    funder: FunderCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user), 
    _=Depends(role_checker(['super_admin', 'tenant_admin']))
):
    logging_helper.log_info(f"User {current_user.username} is creating a new funder with data: {funder.dict()}")
    repo = FunderRepository(db)
    try:
        new_funder = repo.create_funder(funder)

        # Log the action
        changes = {
            "action": "CREATE_FUNDER",
            "funder_id": new_funder.id,
            "funder_data": funder.dict()
        }
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, 'Funder', new_funder.id, changes)

        logging_helper.log_info(f"Funder created with ID {new_funder.id} successfully")
        return new_funder
    except Exception as e:
        logging_helper.log_error(f"An error occurred while creating funder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.put("/funders/{funder_id}", response_model=FunderOut)
def update_funder(
    funder_id: int, 
    funder: FunderUpdate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user), 
    _=Depends(role_checker(['super_admin', 'tenant_admin']))
):
    logging_helper.log_info(f"User {current_user.username} is updating funder with ID {funder_id} with data: {funder.dict()}")
    repo = FunderRepository(db)
    try:
        updated_funder = repo.update_funder(funder_id, funder)
        if not updated_funder:
            logging_helper.log_warning(f"Funder with ID {funder_id} not found")
            raise HTTPException(status_code=404, detail="Funder not found")

        # Log the action
        changes = {
            "action": "UPDATE_FUNDER",
            "funder_id": funder_id,
            "funder_data": funder.dict(exclude_unset=True)
        }
        logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, 'Funder', funder_id, changes)

        logging_helper.log_info(f"Funder with ID {funder_id} updated successfully")
        return updated_funder
    except Exception as e:
        logging_helper.log_error(f"An error occurred while updating funder with ID {funder_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.delete("/funders/{funder_id}", response_model=FunderOut)
def delete_funder(
    funder_id: int, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user), 
    _=Depends(role_checker(['super_admin', 'tenant_admin']))
):
    logging_helper.log_info(f"User {current_user.username} is deleting funder with ID {funder_id}")
    repo = FunderRepository(db)
    try:
        deleted_funder = repo.delete_funder(funder_id)
        if not deleted_funder:
            logging_helper.log_warning(f"Funder with ID {funder_id} not found")
            raise HTTPException(status_code=404, detail="Funder not found")

        # Log the action
        changes = {
            "action": "DELETE_FUNDER",
            "funder_id": funder_id
        }
        logging_helper.log_audit(db, current_user.id, ActionEnum.DELETE, 'Funder', funder_id, changes)

        logging_helper.log_info(f"Funder with ID {funder_id} deleted successfully")
        return deleted_funder
    except Exception as e:
        logging_helper.log_error(f"An error occurred while deleting funder with ID {funder_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

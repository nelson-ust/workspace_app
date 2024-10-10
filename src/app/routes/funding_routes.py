from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db  # Assuming you have a get_db function in your database module
from repositories.funding_repository import FundingRepository
from schemas.funding_schemas import FundingCreate, FundingUpdate, FundingOut
from auth.dependencies import role_checker
from auth.security import get_current_user
from schemas.user_schemas import UserRead
from logging_helpers import logging_helper

router = APIRouter()

@router.get("/fundings/{project_id}/{funder_id}/{component_id}", response_model=FundingOut)
async def get_funding(
    project_id: int, funder_id: int, component_id: int, 
    db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user), 
    _ = Depends(role_checker(['tenant_admin', 'super_admin']))
):
    repo = FundingRepository(db)
    logging_helper.log_info(f"User {current_user.username} is fetching funding for project_id={project_id}, funder_id={funder_id}, component_id={component_id}")
    try:
        funding = repo.get_funding(project_id, funder_id, component_id)
        if not funding:
            logging_helper.log_warning(f"Funding entry not found for project_id={project_id}, funder_id={funder_id}, component_id={component_id}")
            raise HTTPException(status_code=404, detail="Funding entry not found")
        return funding
    except Exception as e:
        logging_helper.log_error(f"An error occurred while fetching funding: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fundings", response_model=List[FundingOut])
async def get_fundings(
    skip: int = 0, limit: int = 100, 
    db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user), 
    _ = Depends(role_checker(['tenant_admin', 'super_admin']))
):
    repo = FundingRepository(db)
    logging_helper.log_info(f"User {current_user.username} is fetching fundings with skip={skip}, limit={limit}")
    try:
        fundings = repo.get_fundings(skip=skip, limit=limit)
        return fundings
    except Exception as e:
        logging_helper.log_error(f"An error occurred while fetching fundings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fundings", response_model=FundingOut, status_code=status.HTTP_201_CREATED)
async def create_funding(
    funding: FundingCreate, 
    db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user), 
    _ = Depends(role_checker(['tenant_admin', 'super_admin']))
):
    repo = FundingRepository(db)
    logging_helper.log_info(f"User {current_user.username} is creating a new funding with data: {funding.dict()}")
    try:
        new_funding = repo.create_funding(funding)

        # Log the action
        changes = {
            "action": "CREATE_FUNDING",
            "data": funding.dict()
        }
        logging_helper.log_audit(db, current_user.id, 'CREATE_FUNDING', 'Funding', new_funding.project_id, changes)

        logging_helper.log_info(f"Created funding with project_id={new_funding.project_id}, funder_id={new_funding.funder_id}, component_id={new_funding.component_id}")
        return new_funding
    except Exception as e:
        logging_helper.log_error(f"An error occurred while creating funding: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/fundings/{project_id}/{funder_id}/{component_id}", response_model=FundingOut)
async def update_funding(
    project_id: int, funder_id: int, component_id: int, 
    funding: FundingUpdate, db: Session = Depends(get_db), 
    current_user: UserRead = Depends(get_current_user), _ = Depends(role_checker(['tenant_admin', 'super_admin']))
):
    repo = FundingRepository(db)
    logging_helper.log_info(f"User {current_user.username} is updating funding for project_id={project_id}, funder_id={funder_id}, component_id={component_id} with data: {funding.dict(exclude_unset=True)}")
    try:
        updated_funding = repo.update_funding(project_id, funder_id, component_id, funding)
        if not updated_funding:
            logging_helper.log_warning(f"Funding entry not found for project_id={project_id}, funder_id={funder_id}, component_id={component_id}")
            raise HTTPException(status_code=404, detail="Funding entry not found")

        # Log the action
        changes = {
            "action": "UPDATE_FUNDING",
            "data": funding.dict(exclude_unset=True)
        }
        logging_helper.log_audit(db, current_user.id, 'UPDATE_FUNDING', 'Funding', project_id, changes)

        logging_helper.log_info(f"Updated funding for project_id={project_id}, funder_id={funder_id}, component_id={component_id}")
        return updated_funding
    except Exception as e:
        logging_helper.log_error(f"An error occurred while updating funding: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/fundings/{project_id}/{funder_id}/{component_id}", response_model=FundingOut)
async def delete_funding(
    project_id: int, funder_id: int, component_id: int, 
    db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user), 
    _ = Depends(role_checker(['tenant_admin', 'super_admin']))
):
    repo = FundingRepository(db)
    logging_helper.log_info(f"User {current_user.username} is deleting funding for project_id={project_id}, funder_id={funder_id}, component_id={component_id}")
    try:
        deleted_funding = repo.delete_funding(project_id, funder_id, component_id)
        if not deleted_funding:
            logging_helper.log_warning(f"Funding entry not found for project_id={project_id}, funder_id={funder_id}, component_id={component_id}")
            raise HTTPException(status_code=404, detail="Funding entry not found")

        # Log the action
        changes = {
            "action": "DELETE_FUNDING",
            "project_id": project_id,
            "funder_id": funder_id,
            "component_id": component_id
        }
        logging_helper.log_audit(db, current_user.id, 'DELETE_FUNDING', 'Funding', project_id, changes)

        logging_helper.log_info(f"Deleted funding for project_id={project_id}, funder_id={funder_id}, component_id={component_id}")
        return deleted_funding
    except Exception as e:
        logging_helper.log_error(f"An error occurred while deleting funding: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from schemas.designation_schemas import DesignationCreate, DesignationRead, DesignationUpdate
from repositories.designation_repository import DesignationRepository
from db.database import get_db  # Dependency to obtain DB session
from logging_helpers import logging_helper, ActionEnum
from auth.security import get_current_user
from schemas.user_schemas import UserRead
from auth.dependencies import role_checker

router = APIRouter()

@router.post("/designations/", response_model=DesignationRead, status_code=status.HTTP_201_CREATED)
def create_designation(designation: DesignationCreate, current_user:UserRead=Depends(get_current_user), 
                        db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    """
    Roles to Access the endpoint
        super_admin
    """
    try:
        logging_helper.log_info("Accessing - Create Designation - Endpoint")
        designation_repo = DesignationRepository(db)
        result = designation_repo.create_designation(designation)
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "Designation", result.id, f"Created designation: {result.id}")
        return result
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/designations/", response_model=List[DesignationRead])
def read_designations(skip: int = 0, limit: int = 100, current_user:UserRead=Depends(get_current_user), 
                        db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    """
    Roles to Access the endpoint
        unit_member
    """
    try:
        logging_helper.log_info("Accessing - Read Designations - Endpoint")
        designation_repo = DesignationRepository(db)
        return designation_repo.get_all_designations(skip=skip, limit=limit)
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/designations/{designation_id}", response_model=DesignationRead)
def read_designation(designation_id: int, current_user:UserRead=Depends(get_current_user), 
                        db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    """
    Roles to Access the endpoint
        unit_member
    """
    try:
        logging_helper.log_info("Accessing - Read Designation - Endpoint")
        designation_repo = DesignationRepository(db)
        designation = designation_repo.get_designation_by_id(designation_id)
        if designation is None:
            raise HTTPException(status_code=404, detail="Designation not found")
        return designation
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/designations/{designation_id}")
def update_designation(designation_id: int, designation: DesignationUpdate, current_user:UserRead=Depends(get_current_user), 
                        db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    """
    Roles to Access the endpoint
        super_admin
    """
    try:
        logging_helper.log_info("Accessing - Update designation - Endpoint")
        designation_repo = DesignationRepository(db)
        updated_designation = designation_repo.update_designation(designation_id, designation)
        if updated_designation is None:
            raise HTTPException(status_code=404, detail="Designation not found")
        logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "Designation", designation_id, f"Updated designation: {designation_id}")
        return updated_designation
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/designations/{designation_id}")
def soft_delete_designation(designation_id: int, current_user:UserRead=Depends(get_current_user), 
                        db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    """
    Roles to Access the endpoint
        super_admin
    """
    try:
        logging_helper.log_info("Accessing - Soft Delete Designation - Endpoint")
        designation_repo = DesignationRepository(db)
        restored_designation = designation_repo.soft_delete_designation(designation_id)
        if restored_designation is None:
            raise HTTPException(status_code=404, detail="Designation not found")
        logging_helper.log_audit(db, current_user.id, ActionEnum.DELETE, "Designation", designation_id, f"Soft deleted designation: {designation_id}")
        return restored_designation #{"detail": "Designation soft deleted successfully"}
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/designations/{designation_id}/restore")
def restore_designation(designation_id: int, current_user:UserRead=Depends(get_current_user), 
                        db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    
    """
    Roles to Access the endpoint
        super_admin
    """
    try:
        logging_helper.log_info("Accessing - Restore Designation - Endpoint")
        designation_repo = DesignationRepository(db)
        restored_designation = designation_repo.restore_designation(designation_id)
        if restored_designation is None:
            raise HTTPException(status_code=404, detail="Designation not found or not deleted")
        logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "Designation", designation_id, f"Restored designation: {designation_id}")
        return {"detail": "Designation restored successfully"}
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

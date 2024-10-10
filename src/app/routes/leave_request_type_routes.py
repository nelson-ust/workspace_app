from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from schemas.leave_request_type_schemas import LeaveTypeCreate, LeaveTypeUpdate, LeaveTypeResponse
from repositories.leave_request_type_repository import LeaveRequestTypeRepository

router = APIRouter()

@router.post("/leave-types/", response_model=LeaveTypeResponse, status_code=status.HTTP_201_CREATED)
def create_leave_type_route(leave_type: LeaveTypeCreate, db: Session = Depends(get_db)):
    """
    Create a new leave type.

    Args:
        leave_type (LeaveTypeCreate): The leave type data to create.
        db (Session): SQLAlchemy session object.

    Returns:
        LeaveTypeResponse: The created leave type object.
    """
    try:
        leave_type_repo = LeaveRequestTypeRepository(db)
        new_leave_type = leave_type_repo.create_leave_type(leave_type.name, leave_type.description)
        return new_leave_type
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/leave-types/", response_model=List[LeaveTypeResponse])
def get_all_leave_types_route(db: Session = Depends(get_db)):
    """
    Retrieve all leave types.

    Args:
        db (Session): SQLAlchemy session object.

    Returns:
        list[LeaveTypeResponse]: List of leave types.
    """
    try:
        leave_type_repo = LeaveRequestTypeRepository(db)
        leave_types = leave_type_repo.get_all_leave_types()
        return leave_types
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/leave-types/{leave_type_id}", response_model=LeaveTypeResponse)
def get_leave_type_by_id_route(leave_type_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific leave type by its ID.

    Args:
        leave_type_id (int): The ID of the leave type to retrieve.
        db (Session): SQLAlchemy session object.

    Returns:
        LeaveTypeResponse: The leave type object with the specified ID.
    """
    try:
        leave_type_repo = LeaveRequestTypeRepository(db)
        leave_type = leave_type_repo.get_leave_type_by_id(leave_type_id)
        return leave_type
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/leave-types/{leave_type_id}", response_model=LeaveTypeResponse)
def update_leave_type_route(leave_type_id: int, leave_type: LeaveTypeUpdate, db: Session = Depends(get_db)):
    """
    Update a leave type.

    Args:
        leave_type_id (int): The ID of the leave type to update.
        leave_type (LeaveTypeUpdate): The updated leave type data.
        db (Session): SQLAlchemy session object.

    Returns:
        LeaveTypeResponse: The updated leave type object.
    """
    try:
        leave_type_repo = LeaveRequestTypeRepository(db)
        updated_leave_type = leave_type_repo.update_leave_type(leave_type_id, leave_type.name, leave_type.description)
        return updated_leave_type
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/leave-types/{leave_type_id}", response_model=dict)
def delete_leave_type_route(leave_type_id: int, db: Session = Depends(get_db)):
    """
    Delete a leave type.

    Args:
        leave_type_id (int): The ID of the leave type to delete.
        db (Session): SQLAlchemy session object.

    Returns:
        dict: Confirmation of successful deletion.
    """
    try:
        leave_type_repo = LeaveRequestTypeRepository(db)
        result = leave_type_repo.delete_leave_type(leave_type_id)
        if result:
            return {"detail": "Leave type deleted successfully."}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave type not found.")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

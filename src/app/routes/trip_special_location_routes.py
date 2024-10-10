from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from auth.dependencies import get_db, get_current_user, role_checker
from schemas.trip_special_location_schemas import TenancyIDRequest, TenancyIDsRequest, TripStartLocationCreate, TripStartLocationResponse, TripStartLocationUpdate
from repositories.trip_special_location_repository import TripSpecialLocationRepository
from models.all_models import TripSpecialLocation, User, UserRole, AuditLog, ActionEnum
from logging_helpers import logging_helper
from datetime import datetime

router = APIRouter()


@router.post("/trip-special-location/", response_model=dict)
def create_trip_special_location(
    trip_start_location: TripStartLocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    role: str = Depends(role_checker(["super_admin", "tenant_admin"]))
):
    """
    Create a new TripStartLocation.
    
    :param trip_start_location: Data for the new TripStartLocation
    :param db: Database session
    :param current_user: The current authenticated user
    :return: A dictionary message indicating the result
    """
    repository = TripSpecialLocationRepository(db)
    try:
        logging_helper.log_info(f"User {current_user.username} is creating a new TripStartLocation")
        created_trip_start_location = repository.create_trip_special_location(
            name=trip_start_location.name,
            description=trip_start_location.description,
            latitude=trip_start_location.latitude,
            longitude=trip_start_location.longitude,
            tenancy_id=trip_start_location.tenancy_id
        )
        # Extract the trip special location ID from the message returned by the repository
        location_id = created_trip_start_location.get('message').split(':')[1].split()[0]
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "TripStartLocation", location_id, changes=trip_start_location.dict())
        return created_trip_start_location
    except ValueError as e:
        logging_helper.log_error(f"Validation error while creating TripStartLocation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except SQLAlchemyError as e:
        logging_helper.log_error(f"SQLAlchemy error while creating TripStartLocation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the trip start location: {str(e)}"
        )
    except Exception as e:
        logging_helper.log_error(f"Unexpected error while creating TripStartLocation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while creating the trip start location: {str(e)}"
        )


@router.get("/{id}", response_model=TripStartLocationResponse, dependencies=[Depends(get_current_user)])
def get_trip_special_location_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    role: str = Depends(role_checker(["unit_member", "super_admin", "tenant_admin"]))
):
    """
    Retrieve a TripStartLocation by its ID.
    
    :param id: ID of the TripStartLocation
    :param db: Database session
    :param current_user: The current authenticated user
    :return: TripStartLocation object if found, else raise HTTPException
    """
    repository = TripSpecialLocationRepository(db)
    logging_helper.log_info(f"User {current_user.username} is fetching TripStartLocation with ID {id}")
    trip_start_location = repository.get_trip_special_location_by_id(id)
    if not trip_start_location:
        logging_helper.log_error(f"TripStartLocation with ID {id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TripStartLocation not found"
        )
    return trip_start_location


@router.post("/", response_model=List[TripStartLocationResponse])
def get_all_trip_special_locations(
    request: TenancyIDRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all TripStartLocations for the specified tenancy IDs.
    
    :param request: Data containing the list of tenancy IDs
    :param db: Database session
    :param current_user: The current authenticated user
    :return: List of TripStartLocation objects
    """
    try:
        tenancy_ids = request.tenancy_ids
        repository = TripSpecialLocationRepository(db)
        logging_helper.log_info(f"User {current_user.username} is fetching all TripStartLocations for tenancy IDs: {tenancy_ids}")
        return repository.get_all_trip_special_locations(tenancy_ids)
    except Exception as e:
        logging_helper.log_error(f"Error fetching TripStartLocations for tenancy IDs {tenancy_ids}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching TripStartLocations: {str(e)}")


@router.put("/{id}", response_model=TripStartLocationResponse)
def update_trip_special_location(
    id: int,
    trip_start_location: TripStartLocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    role: str = Depends(role_checker(["super_admin", "tenant_admin"]))
):
    """
    Update an existing TripStartLocation.
    
    :param id: ID of the TripStartLocation to be updated
    :param trip_start_location: Data for updating the TripStartLocation
    :param db: Database session
    :param current_user: The current authenticated user
    :return: The updated TripStartLocation object
    """
    repository = TripSpecialLocationRepository(db)
    try:
        logging_helper.log_info(f"User {current_user.username} is updating TripStartLocation with ID {id}")
        updated_trip_start_location = repository.update_trip_special_location(
            id=id,
            name=trip_start_location.name,
            description=trip_start_location.description,
            latitude=trip_start_location.latitude,
            longitude=trip_start_location.longitude,
            tenancy_id=trip_start_location.tenancy_id
        )
        logging_helper.log_audit(db, current_user, ActionEnum.UPDATE, "TripStartLocation", id, changes=trip_start_location.dict())
        return updated_trip_start_location
    except ValueError as e:
        logging_helper.log_error(f"Validation error while updating TripStartLocation with ID {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except SQLAlchemyError as e:
        logging_helper.log_error(f"SQLAlchemy error while updating TripStartLocation with ID {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the trip start location."
        )
    except Exception as e:
        logging_helper.log_error(f"Unexpected error while updating TripStartLocation with ID {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the trip start location."
        )

@router.delete("/{id}")
def delete_trip_special_location(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    role: str = Depends(role_checker(["super_admin", "tenant_admin"]))
):
    """
    Delete a TripStartLocation by its ID.
    
    :param id: ID of the TripStartLocation to be deleted
    :param db: Database session
    :param current_user: The current authenticated user
    :return: True if deletion was successful, else raise HTTPException
    """
    repository = TripSpecialLocationRepository(db)
    try:
        logging_helper.log_info(f"User {current_user.username} is deleting TripStartLocation with ID {id}")
        success = repository.delete_trip_special_location(id)
        if success:
            logging_helper.log_audit(db, current_user, ActionEnum.DELETE, "TripStartLocation", id)
            return {"success": success}
        else:
            logging_helper.log_error(f"TripStartLocation with ID {id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="TripStartLocation not found"
            )
    except SQLAlchemyError as e:
        logging_helper.log_error(f"SQLAlchemy error while deleting TripStartLocation with ID {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the trip start location."
        )
    except Exception as e:
        logging_helper.log_error(f"Unexpected error while deleting TripStartLocation with ID {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the trip start location."
        )
#routes/location_routes.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from auth.dependencies import role_checker
from db.database import get_db  # Adjust import path as needed
from schemas.location_schemas import LocationCreate, LocationUpdate, LocationRead  # Adjust import paths as necessary
from repositories.location_repository import LocationRepository  # Adjust import path as needed
from logging_helpers import logging_helper
from schemas.user_schemas import UserRead
from auth.security import get_current_user

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/locations/", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_location(request: Request, location_data: LocationCreate, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin', 'tenant_admin']))):
    
    logging_helper.log_info("Accessing - Create Location - Endpoint")
    location_repo = LocationRepository(db)
    try:
        new_location = location_repo.create_location(location_data)
        return new_location
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    

@router.get("/locations/{location_id}", response_model=LocationRead)
@limiter.limit("10/minute")
async def read_location(request: Request, location_id: int, db: Session = Depends(get_db), current_user:UserRead=Depends(get_current_user), _=Depends(role_checker(['super_admin', 'unit_member','programs_lead', 'technical_lead', 'stl', 'tenant_admin']))):
    try:
        logging_helper.log_info("Accessing - Read Location - Endpoint")
        location_repo = LocationRepository(db)
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                location = location_repo.get_location_by_id(location_id)
            else:
                location = location_repo.get_location_by_id(location_id, tenancy_id=current_user.tenancy_id)
            if location is None:
                raise HTTPException(status_code=404, detail="Location not found")
            return location
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")


@router.get("/locations/", response_model=List[LocationRead], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_all_locations(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user:UserRead=Depends(get_current_user), _=Depends(role_checker(['super_admin','unit_member','programs_lead', 'technical_lead', 'stl', 'tenant_admin']))):
    try:
        logging_helper.log_info("Accessing - Read all Locations - Endpoint")
        location_repo =LocationRepository(db)
        print(f"Fetching locations with skip={skip} and limit={limit}")
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                locations = location_repo.get_all_locations(skip=skip, limit=limit)
            else:
                locations = location_repo.get_all_locations(skip=skip, limit=limit, tenancy_id=current_user.tenancy_id)
            print(f"Found locations: {locations}")
            return locations
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")


@router.put("/locations/{location_id}")
@limiter.limit("5/minute")
async def update_location(request: Request, location_id: int, location_data: LocationUpdate, db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin', 'super_admin']))):
    try:
        logging_helper.log_info("Accessing - Update location - Endpoint")
        location_repo = LocationRepository(db)
        updated_location = location_repo.update_location(location_id, location_data)
        if updated_location is None:
            raise HTTPException(status_code=404, detail="Location not found")
        return updated_location
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")


# Add routes for soft_delete, restore, and find_by_name as needed
# Continue from the existing code in location_routes.py

@router.post("/locations/{location_id}/soft-delete")
@limiter.limit("5/minute")
async def soft_delete_location(request: Request, location_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin', 'tenant_admin']))):
    try:
        logging_helper.log_info("Accessing - Soft Delete Location - Endpoint")
        location_repo = LocationRepository(db)
        location = location_repo.soft_delete(location_id)
        if location is None:
            raise HTTPException(status_code=404, detail="Location not found")
        return location
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")


@router.post("/locations/{location_id}/restore")
@limiter.limit("5/minute")
async def restore_location(request: Request, location_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin', 'tenant_admin']))):
    try:
        logging_helper.log_info("Accessing - Restore Location - Endpoint")
        location_repo = LocationRepository(db)
        location = location_repo.restore(location_id)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        return location
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

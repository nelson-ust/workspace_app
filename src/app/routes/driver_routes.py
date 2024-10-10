from fastapi import APIRouter, HTTPException, status, Request, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from db.database import get_db
from repositories.driver_repository import DriverRepository
from schemas.driver_schemas import DriverCreate, DriverUpdate, DriverRead
from schemas.user_schemas import UserRead
from auth.security import get_current_user
from auth.dependencies import role_checker 
from datetime import date, datetime, timedelta
from logging_helpers import logging_helper, ActionEnum

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/driver/", response_model=DriverRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_driver(request: Request, driver_data: DriverCreate, current_user: UserRead = Depends(get_current_user),
                        db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin', 'super_admin']))):
    logging_helper.log_info("Accessing - Create Driver - Endpoint")
    driver_repo = DriverRepository(db)

    """
    Roles to Access the endpoint
        super_admin, tenant_admin   
    """
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin" or current_user.tenancy_id == driver_data.tenancy_id:
                new_driver = driver_repo.create_driver(driver_data=driver_data)
                logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "Driver", new_driver.id, f"Created driver: {new_driver.id}")
                break
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{current_user.first_name} {current_user.last_name}, your authorized to create driver for only your state")
        return new_driver
    except HTTPException as err:
        logging_helper.log_error(message=f"Warning Unauthorized: {str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


@router.get("/driver/", response_model=List[DriverRead], status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def get_all_driver(request: Request, skip: int = 0, limit: int = 100, current_user: UserRead = Depends(get_current_user),
                         db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin', 'super_admin', 'admin_lead', 'admin_team', 'chief_driver', 'driver']))):
    logging_helper.log_info("Accessing - Get all Driver - Endpoint")
    driver_repo = DriverRepository(db)

    """
    Roles to Access the endpoint
        super_admin, tenant_admin, admin_lead, admin_team, chief_driver, driver
    """
    try:
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                return driver_repo.get_all_driver(skip=skip, limit=limit)
            else:
                return driver_repo.get_all_driver_for_tenancy(tenancy_id=current_user.tenancy_id, skip=skip, limit=limit)
    except HTTPException as err:
        logging_helper.log_error(message=f"Database error: {str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


@router.get("/driver/{driver_id}", response_model=DriverRead, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def get_driver_by_id(request: Request, driver_id: int, current_user: UserRead = Depends(get_current_user),
                           db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin', 'super_admin','admin_lead', 'admin_team', 'chief_driver', 'driver']))):
    logging_helper.log_info("Accessing - Get Driver by id - Endpoint")
    driver_repo = DriverRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_backstop"]:
                driver = driver_repo.get_driver_by_id(driver_id=driver_id)
                if not driver:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Driver with id {driver_id} is not found")
                return driver
            else:
                driver = driver_repo.get_driver_by_id_for_tenancy(driver_id=driver_id, tenancy_id=current_user.tenancy_id)
                if not driver:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Driver with id {driver_id} is not found")
                return driver
    except HTTPException as err:
        logging_helper.log_error(message=f"The Driver with id {driver_id} is not found {str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


@router.get("/driver/{licence_number}/licence_number", response_model=DriverRead, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def get_driver_by_licence_number(request: Request, licence_number: str, current_user: UserRead = Depends(get_current_user),
                                       db: Session = Depends(get_db), _=Depends(role_checker(['programs_lead', 'technical_lead', 'stl', 'tenant_admin', 'super_admin']))):
    logging_helper.log_info("Accessing - Get Driver by Licence Number - Endpoint")
    driver_repo = DriverRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_backstop"]:
                driver = driver_repo.get_driver_by_licence_number(licence_number=licence_number)
                if not driver:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Driver with licence_number {licence_number} is not found")
                return driver
            else:
                driver = driver_repo.get_driver_by_licence_number(licence_number=licence_number, tenancy_id=current_user.tenancy_id)
                if not driver:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Driver with licence_number {licence_number} is not found")
                return driver
    except HTTPException as err:
        logging_helper.log_error(message=f"The Driver with licence_number {licence_number} is not found {str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


@router.get("/driver/{expiration_date}/expiration_date", response_model=List[DriverRead], status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def get_driver_by_licence_expiration_date(request: Request, start_date: date = datetime.now().date(), end_date: date = (datetime.now() + timedelta(days=60)).date(), skip: int = 0, limit: int = 100, current_user: UserRead = Depends(get_current_user),
                                                db: Session = Depends(get_db), _=Depends(role_checker(['programs_lead', 'technical_lead', 'stl', 'tenant_admin', 'hq_staff', 'super_admin']))):
    logging_helper.log_info("Accessing - Get Driver by Licence expiration date - Endpoint")
    driver_repo = DriverRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_backstop"]:
                return driver_repo.get_driver_by_licence_expiration_date(start_date=start_date, end_date=end_date)
            else:
                return driver_repo.get_driver_by_licence_expiration_date(start_date=start_date, end_date=end_date, tenancy_id=current_user.tenancy_id)
    except HTTPException as err:
        logging_helper.log_error(message=f"Database error: {str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


@router.put("/driver/{driver_id}")
@limiter.limit("5/minute")
async def update_driver(request: Request, driver_id: str, driver_data: DriverUpdate, current_user: UserRead = Depends(get_current_user),
                        db: Session = Depends(get_db), _=Depends(role_checker(['programs_lead', 'technical_lead', 'stl', 'tenant_admin', 'super_admin']))):
    logging_helper.log_info("Accessing - Update Driver - Endpoint")
    driver_repo = DriverRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                driver = driver_repo.update_driver(driver_id=driver_id, driver_data=driver_data)
                if not driver:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Driver with id {driver_id} is not found")
                logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "Driver", driver_id, f"Updated driver: {driver_id}")
                return driver
            else:
                driver = driver_repo.update_driver(driver_id=driver_id, driver_data=driver_data, tenancy_id=current_user.tenancy_id)
                if not driver:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Driver with id {driver_id} is not found")
                logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "Driver", driver_id, f"Updated driver: {driver_id}")
                return driver
    except HTTPException as err:
        logging_helper.log_error(message=f"{str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


@router.delete("/driver/{driver_id}")
@limiter.limit("5/minute")
async def delete_hard_driver(request: Request, driver_id: int, current_user: UserRead = Depends(get_current_user),
                             db: Session = Depends(get_db), _=Depends(role_checker(['programs_lead', 'technical_lead', 'stl', 'tenant_admin', 'super_admin']))):
    logging_helper.log_info("Accessing - Delete Hard Driver - Endpoint")
    driver_repo = DriverRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                driver = driver_repo.delete_hard_driver(driver_id=driver_id)
                if not driver:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Driver with id {driver_id} is not found")
                logging_helper.log_audit(db, current_user.id, ActionEnum.DELETE, "Driver", driver_id, f"Deleted driver: {driver_id}")
                return {f" 'detail': 'Driver with id {driver_id} has been deleted successfully "}
            else:
                driver = driver_repo.delete_hard_driver(driver_id=driver_id, tenancy_id=current_user.tenancy_id)
                if not driver:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Driver with id {driver_id} is not found")
                logging_helper.log_audit(db, current_user.id, ActionEnum.DELETE, "Driver", driver_id, f"Deleted driver: {driver_id}")
                return {f" 'detail': 'Driver with id {driver_id} has been deleted successfully "}
    except HTTPException as err:
        logging_helper.log_error(message=f"{str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


@router.post("/driver/{driver_id}/soft_delete")
@limiter.limit("5/minute")
async def soft_delete_driver(request: Request, driver_id: int, current_user: UserRead = Depends(get_current_user),
                             db: Session = Depends(get_db), _=Depends(role_checker(['programs_lead', 'technical_lead', 'stl', 'tenant_admin', 'super_admin']))):
    logging_helper.log_info("Accessing - Soft Delete Driver - Endpoint")
    driver_repo = DriverRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                driver = driver_repo.soft_delete_driver(driver_id=driver_id)
                if not driver:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Driver with id {driver_id} is not found")
                logging_helper.log_audit(db, current_user.id, ActionEnum.SOFT_DELETE, "Driver", driver_id, f"Soft deleted driver: {driver_id}")
                return {f" 'detail': 'Driver with id {driver_id} has been deactivated successfully "}
            else:
                driver = driver_repo.soft_delete_driver(driver_id=driver_id, tenancy_id=current_user.tenancy_id)
                if not driver:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Driver with id {driver_id} is not found")
                logging_helper.log_audit(db, current_user.id, ActionEnum.SOFT_DELETE, "Driver", driver_id, f"Soft deleted driver: {driver_id}")
                return {f" 'detail': 'Driver with id {driver_id} has been deactivated successfully "}
    except HTTPException as err:
        logging_helper.log_error(message=f"{str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


@router.post("/driver/{driver_id}/restore")
@limiter.limit("5/minute")
async def restore_driver(request: Request, driver_id: int, current_user: UserRead = Depends(get_current_user),
                         db: Session = Depends(get_db), _=Depends(role_checker(['programs_lead', 'technical_lead', 'stl', 'tenant_admin', 'super_admin']))):
    logging_helper.log_info("Accessing - Restore Driver - Endpoint")
    driver_repo = DriverRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                driver = driver_repo.restore_driver(driver_id=driver_id)
                if not driver:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Driver with id {driver_id} is not found")
                logging_helper.log_audit(db, current_user.id, ActionEnum.RESTORE, "Driver", driver_id, f"Restored driver: {driver_id}")
                return {f" 'detail': 'Driver with id {driver_id} has been activated successfully "}
            else:
                driver = driver_repo.restore_driver(driver_id=driver_id, tenancy_id=current_user.tenancy_id)
                if not driver:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Driver with id {driver_id} is not found")
                logging_helper.log_audit(db, current_user.id, ActionEnum.RESTORE, "Driver", driver_id, f"Restored driver: {driver_id}")
                return {f" 'detail': 'Driver with id {driver_id} has been activated successfully "}
    except HTTPException as err:
        logging_helper.log_error(message=f"{str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


@router.put("/driver/{driver_id}/availability", response_model=DriverRead, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def update_driver_availability(request: Request, driver_id: int, is_available: bool,
                                     current_user: UserRead = Depends(get_current_user),
                                     db: Session = Depends(get_db),
                                     _=Depends(role_checker(['super_admin', 'tenant_admin', 'admin_lead', 'chief_pilot']))):
    logging_helper.log_info("Accessing - Update Driver Availability - Endpoint")
    driver_repo = DriverRepository(db)
    try:
        driver = driver_repo.update_driver_availability(driver_id=driver_id, is_available=is_available)
        if not driver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Driver with ID {driver_id} not found")

        logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "Driver", driver_id, f"Updated driver availability: {driver_id} to {is_available}")
        return driver
    except HTTPException as err:
        logging_helper.log_error(message=f"Failed to update driver availability: {str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


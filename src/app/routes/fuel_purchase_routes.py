from fastapi import APIRouter, HTTPException, status, Request, Depends, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address
from db.database import get_db
from repositories.fuel_purchase_repository import FuelPurchaseRepository
from schemas.fuel_purchase_schemas import FuelPurchaseUpdate, FuelPurchaseRead
from schemas.user_schemas import UserRead
from auth.security import get_current_user
from repositories.driver_repository import DriverRepository
from auth.dependencies import role_checker 
from datetime import date
from logging_helpers import logging_helper

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()



@router.post("/fuel_purchase/", response_model= FuelPurchaseRead, status_code=status.HTTP_201_CREATED) 
@limiter.limit("5/minute")
async def fuel_purchase_create(
    request:Request,
    vehicle_id:int,
    driver_id:int,
    quantity: float,
    unit_cost: float,
    #total_cost: float,
    purchase_date:date,
    tenancy_id:int,
    file:UploadFile = File(...),
    current_user:UserRead=Depends(get_current_user), 
    db: Session = Depends(get_db),_
    =Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin','super_admin']))
):
    logging_helper.log_info("Accessing - Fuel Purchase Create - Endpoint")
    fuel_purchase_repo = FuelPurchaseRepository(db)
    
    try:
        #super_admin check
        for role_dict in current_user.roles:
            if role_dict.name == "tenant_admin" or current_user.tenancy_id == tenancy_id:

                new_fuel_purchase = fuel_purchase_repo.fuel_purchase_create(
                    vehicle_id, driver_id, quantity, unit_cost, purchase_date, tenancy_id=tenancy_id, file=file)
                break
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{current_user.first_name} {current_user.last_name}, your authorized to create fuel purchase for only your state")
        return new_fuel_purchase
    except Exception as err:
        fuel_purchase_repo.handle_errors(e=err, message=f"Warning Unauthorized: {str(err)} !!!")




@router.get("/fuel_purchase/", response_model= List[FuelPurchaseRead], status_code=status.HTTP_201_CREATED) 
@limiter.limit("5/minute")
async def get_all_fuel_purchase(request:Request, skip:int=0, limit:int=100, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Get all Fuel Purchase - Endpoint")
    fuel_purchase_repo = FuelPurchaseRepository(db)
    driver = DriverRepository(db)
    try:
        for role_dict in current_user.roles:

            ##For Super Admin mapping all the Fuel Purchase for the 3 States
            if role_dict.name in ["super_admin"]:
                return fuel_purchase_repo.get_all_fuel_purchase(skip=skip, limit=limit)
            
            ##For Chief Driver, Admin Lead and Tenant Admin mapping all Fuel Purchase
            elif role_dict.name in ["chief_driver", "admin_lead", "tenant_admin"]:
                return fuel_purchase_repo.get_all_fuel_purchase(tenancy_id=current_user.tenancy_id, skip=skip, limit=limit)
            
            else:
                ##For Driver mapping only the Fuel Purchase of the Logged in Driver
                return fuel_purchase_repo.get_all_fuel_purchase(tenancy_id=current_user.tenancy_id, skip=skip, limit=limit, driver_id=driver.get_driver_by_user_id(current_user.id))
    except Exception as err:
        fuel_purchase_repo.handle_errors(e=err, message=f"Database error: {str(err)}")



@router.get("/fuel_purchase/{fuel_purchase_id}", response_model= FuelPurchaseRead, status_code=status.HTTP_201_CREATED) 
@limiter.limit("5/minute")
async def get_fuel_purchase_by_id(request:Request, fuel_purchase_id:int, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Get Fuel Purchase by id - Endpoint")
    fuel_purchase_repo = FuelPurchaseRepository(db)
    driver = DriverRepository(db)
    try:
        for role_dict in current_user.roles:

            ##For Super Admin mapping all the Fuel Purchase for the 3 States
            if role_dict.name in ["super_admin"]:
                return fuel_purchase_repo.get_fuel_purchase_by_id(fuel_purchase_id=fuel_purchase_id)
            
            ##For Chief Driver, Admin Lead and Tenant Admin mapping all Fuel Purchase
            elif role_dict.name in ["chief_driver", "admin_lead", "tenant_admin"]:
                return fuel_purchase_repo.get_fuel_purchase_by_id(fuel_purchase_id=fuel_purchase_id, tenancy_id=current_user.tenancy_id)
            
            else:
                ##For Driver mapping only the Fuel Purchase of the Logged in Driver
                return fuel_purchase_repo.get_fuel_purchase_by_id(fuel_purchase_id=fuel_purchase_id, tenancy_id=current_user.tenancy_id, driver_id=driver.get_driver_by_user_id(current_user.id))
    except Exception as err:
        fuel_purchase_repo.handle_errors(e=err, message=f"Database error: {str(err)}")



@router.put("/fuel_purchase/{fuel_purchase_id}/update_fuel_purchase", response_model= FuelPurchaseRead, status_code=status.HTTP_201_CREATED) 
@limiter.limit("5/minute")
async def update_fuel_purchase(request:Request, fuel_purchase_id:int, fuel_purchase_data:FuelPurchaseUpdate, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Update Fuel Purchase - Endpoint")
    fuel_purchase_repo = FuelPurchaseRepository(db)
    driver = DriverRepository(db)
    try:
        for role_dict in current_user.roles:

            ##For Super Admin mapping all the Fuel Purchase for the 3 States
            if role_dict.name in ["super_admin"]:
                return fuel_purchase_repo.update_fuel_purchase(fuel_purchase_id=fuel_purchase_id, fuel_purchase_data=fuel_purchase_data)
            
            ##For Chief Driver, Admin Lead and Tenant Admin mapping all Fuel Purchase
            elif role_dict.name in ["chief_driver", "admin_lead", "tenant_admin"]:
                return fuel_purchase_repo.update_fuel_purchase(fuel_purchase_id=fuel_purchase_id, fuel_purchase_data=fuel_purchase_data, tenancy_id=current_user.tenancy_id)
            
            else:
                ##For Driver mapping only the Fuel Purchase of the Logged in Driver
                return fuel_purchase_repo.update_fuel_purchase(fuel_purchase_id=fuel_purchase_id, fuel_purchase_data=fuel_purchase_data, tenancy_id=current_user.tenancy_id, driver_id=driver.get_driver_by_user_id(current_user.id))
    except Exception as err:
        fuel_purchase_repo.handle_errors(e=err, message=f"Database error: {str(err)}")



@router.delete("/fuel_purchase/{fuel_purchase_id}/delete_hard_fuel_purchase") 
@limiter.limit("5/minute")
async def delete_hard_fuel_purchase(request:Request, fuel_purchase_id:int, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Delete Hard Fuel Purchase - Endpoint")
    fuel_purchase_repo = FuelPurchaseRepository(db)
    driver = DriverRepository(db)
    try:
        for role_dict in current_user.roles:

            ##For Super Admin mapping all the Fuel Purchase for the 3 States
            if role_dict.name in ["super_admin"]:
                fuel_purchase = fuel_purchase_repo.delete_hard_fuel_purchase(fuel_purchase_id=fuel_purchase_id)
                return {f"'detail': 'FuelPurchase with ID {fuel_purchase_id} has been deleted successfully "}
            
            ##For Chief Driver, Admin Lead and Tenant Admin mapping all Fuel Purchase
            elif role_dict.name in ["chief_driver", "admin_lead", "tenant_admin"]:
                fuel_purchase = fuel_purchase_repo.delete_hard_fuel_purchase(fuel_purchase_id=fuel_purchase_id, tenancy_id=current_user.tenancy_id)
                return {f"'detail': 'FuelPurchase with ID {fuel_purchase_id} has been deleted successfully "}
            
            else:
                ##For Driver mapping only the Fuel Purchase of the Logged in Driver
                fuel_purchase = fuel_purchase_repo.delete_hard_fuel_purchase(fuel_purchase_id=fuel_purchase_id, tenancy_id=current_user.tenancy_id, driver_id=driver.get_driver_by_user_id(current_user.id))
                return {f"'detail': 'FuelPurchase with ID {fuel_purchase_id} has been deleted successfully "}
    except Exception as err:
        fuel_purchase_repo.handle_errors(e=err, message=f"Database error: {str(err)}")


@router.post("/fuel_purchase/{fuel_purchase_id}/soft_delete_fuel_purchase") 
@limiter.limit("5/minute")
async def soft_delete_fuel_purchase(request:Request, fuel_purchase_id:int, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Soft Delete Fuel Purchase - Endpoint")
    fuel_purchase_repo = FuelPurchaseRepository(db)
    driver = DriverRepository(db)
    try:
        for role_dict in current_user.roles:

            ##For Super Admin mapping all the Fuel Purchase for the 3 States
            if role_dict.name in ["super_admin"]:
                fuel_purchase = fuel_purchase_repo.soft_delete_fuel_purchase(fuel_purchase_id=fuel_purchase_id)
                return {f"'detail': 'FuelPurchase with ID {fuel_purchase_id} has been deactivated successfully "}
            
            ##For Chief Driver, Admin Lead and Tenant Admin mapping all Fuel Purchase
            elif role_dict.name in ["chief_driver", "admin_lead", "tenant_admin"]:
                fuel_purchase = fuel_purchase_repo.soft_delete_fuel_purchase(fuel_purchase_id=fuel_purchase_id, tenancy_id=current_user.tenancy_id)
                return {f"'detail': 'FuelPurchase with ID {fuel_purchase_id} has been deactivated successfully "}
            
            else:
                ##For Driver mapping only the Fuel Purchase of the Logged in Driver
                fuel_purchase = fuel_purchase_repo.soft_delete_fuel_purchase(fuel_purchase_id=fuel_purchase_id, tenancy_id=current_user.tenancy_id, driver_id=driver.get_driver_by_user_id(current_user.id))
                return {f"'detail': 'FuelPurchase with ID {fuel_purchase_id} has been deactivated successfully "}
    except Exception as err:
        fuel_purchase_repo.handle_errors(e=err, message=f"Database error: {str(err)}")


@router.post("/fuel_purchase/{fuel_purchase_id}/restore_fuel_purchase", response_model= FuelPurchaseRead, status_code=status.HTTP_201_CREATED) 
@limiter.limit("5/minute")
async def restore_fuel_purchase(request:Request, fuel_purchase_id:int, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Restore Fuel Purchase - Endpoint")
    fuel_purchase_repo = FuelPurchaseRepository(db)
    driver = DriverRepository(db)
    try:
        for role_dict in current_user.roles:

            ##For Super Admin mapping all the Fuel Purchase for the 3 States
            if role_dict.name in ["super_admin"]:
                fuel_purchase = fuel_purchase_repo.restore_fuel_purchase(fuel_purchase_id=fuel_purchase_id)
                return fuel_purchase
            
            ##For Chief Driver, Admin Lead and Tenant Admin mapping all Fuel Purchase
            elif role_dict.name in ["chief_driver", "admin_lead", "tenant_admin"]:
                fuel_purchase = fuel_purchase_repo.restore_fuel_purchase(fuel_purchase_id=fuel_purchase_id, tenancy_id=current_user.tenancy_id)
                return fuel_purchase
            
            else:
                ##For Driver mapping only the Fuel Purchase of the Logged in Driver
                fuel_purchase = fuel_purchase_repo.restore_fuel_purchase(fuel_purchase_id=fuel_purchase_id, tenancy_id=current_user.tenancy_id, driver_id=driver.get_driver_by_user_id(current_user.id))
                return fuel_purchase
    except Exception as err:
        fuel_purchase_repo.handle_errors(e=err, message=f"Database error: {str(err)}")



@router.get("/fuel_purchase/download/{fuel_purchase_id}", response_model=FuelPurchaseRead)
@limiter.limit("5/minute")
async def download_fuel_purchase_file(
    request: Request,
    fuel_purchase_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _=Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))
):
    
    logging_helper.log_info("Accessing - Download Fuel Purchase - Endpoint")
    fuel_purchase_repo = FuelPurchaseRepository(db)
    try:
        for role_dict in current_user.roles:
            # Allow Super Admin and Tenant Admin to download
            if role_dict.name in ["super_admin", "tenant_admin"]:
                file_path = fuel_purchase_repo.get_fuel_purchase_file_path(fuel_purchase_id=fuel_purchase_id)
                return FileResponse(file_path, media_type='application/octet-stream', filename=file_path.split('/')[-1])
            
            # Check if Driver, Chief Driver, Admin Lead is allowed
            elif role_dict.name in ["driver", "chief_driver", "admin_lead"]:
                file_path = fuel_purchase_repo.get_fuel_purchase_file_path(fuel_purchase_id=fuel_purchase_id)
                return FileResponse(file_path, media_type='application/octet-stream', filename=file_path.split('/')[-1])
            
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to download this file")
    except Exception as err:
        raise HTTPException(status_code=404, detail=str(err))














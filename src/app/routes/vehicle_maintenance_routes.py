from fastapi import APIRouter, HTTPException, status, Request, Depends
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from db.database import get_db
from repositories.vehicle_maintenance_repository import VehicleMaintenanceRepository
from schemas.vehicle_maintenance_schemas import VehicleMaintenanceCreate, VehicleMaintenanceUpdate, VehicleMaintenanceRead
from schemas.user_schemas import UserRead
from auth.security import get_current_user
from repositories.driver_repository import DriverRepository
from auth.dependencies import role_checker 
from datetime import date, datetime, timedelta
from logging_helpers import logging_helper

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/vehicle_maintenance/", response_model= VehicleMaintenanceRead, status_code=status.HTTP_201_CREATED) 
@limiter.limit("5/minute")
async def create_vehiclemaintenance(request:Request, vehice_maintenance_data:VehicleMaintenanceCreate, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['driver','chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Create Vehincle Maintenance - Endpoint")
    vehicle_maintenance_repo = VehicleMaintenanceRepository(db)
    
    try:
        #super_admin check
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin" or current_user.tenancy_id == vehice_maintenance_data.tenancy_id:
                new_vehicle_maintenance = vehicle_maintenance_repo.create_vehiclemaintenance(vehiclemaintenance_data=vehice_maintenance_data)
                break
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{current_user.first_name} {current_user.last_name}, your authorized to create vehicle maintenance for only your state")
        return new_vehicle_maintenance
    except Exception as err:
        vehicle_maintenance_repo.handle_errors(e=err, message=f"Warning Unauthorized: {str(err)} !!!")



@router.get("/vehicle_maintenance/", response_model= List[VehicleMaintenanceRead], status_code=status.HTTP_201_CREATED) 
@limiter.limit("5/minute")
async def get_all_vehicle_maintenance(request:Request, skip:int=0, limit:int=100, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Get all Vehincle Maintenance - Endpoint")
    vehicle_maintetnance_repo = VehicleMaintenanceRepository(db)
    try:
        for role_dict in current_user.roles:

            ##For Super Admin mapping all the VehicleMaintenance for the 3 States
            if role_dict.name in ["super_admin"]:
                return vehicle_maintetnance_repo.get_all_vehicle_maintenance(skip=skip, limit=limit)
            
            ##For Chief Driver, Admin Lead and Tenant Admin mapping all VehicleMaintenance
            else: 
                for role_dict.name in ["chief_driver", "admin_lead", "tenant_admin"]:
                    return vehicle_maintetnance_repo.get_all_vehicle_maintenance(tenancy_id=current_user.tenancy_id, skip=skip, limit=limit)
            
    except Exception as err:
        vehicle_maintetnance_repo.handle_errors(e=err, message=f"Database error: {str(err)}")



@router.get("/vehicle_maintetnance/{vehicle_maintetnance_id}", response_model= VehicleMaintenanceRead, status_code=status.HTTP_201_CREATED) 
@limiter.limit("5/minute")
async def get_vehicle_maintenance_by_id(request:Request, vehicle_maintetnance_id:int, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Get Vehincle Maintenance by id - Endpoint")
    vehicle_maintenance_repo = VehicleMaintenanceRepository(db)
    try:
        for role_dict in current_user.roles:

            ##For Super Admin mapping all the VehicleMaintenance for the 3 States
            if role_dict.name in ["super_admin"]:
                return vehicle_maintenance_repo.get_vehicle_maintenance_by_id(vehicle_maintenance_id=vehicle_maintetnance_id)
            
            ##For Chief Driver, Admin Lead and Tenant Admin mapping all VehicleMaintenance
            else: 
                for role_dict.name in ["chief_driver", "admin_lead", "tenant_admin"]:
                    return vehicle_maintenance_repo.get_vehicle_maintenance_by_id(vehicle_maintenance_id=vehicle_maintetnance_id, tenancy_id=current_user.tenancy_id)
            
    except Exception as err:
        vehicle_maintenance_repo.handle_errors(e=err, message=f"Database error: {str(err)}")



@router.put("/vehicle_maintetnance/{vehicle_maintenance_id}/update_vehicle_maintenance", response_model= VehicleMaintenanceRead, status_code=status.HTTP_201_CREATED) 
@limiter.limit("5/minute")
async def update_vehicle_maintenance(request:Request, vehicle_maintenance_id:int, vehicle_maintenance_data:VehicleMaintenanceUpdate, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Update Vehicle Mentainance - Endpoint")
    vehicle_maintenance_repo = VehicleMaintenanceRepository(db)
    try:
        for role_dict in current_user.roles:

            ##For Super Admin mapping all the VehicleMaintenance for the 3 States
            if role_dict.name in ["super_admin"]:
                return vehicle_maintenance_repo.update_vehicle_maintenance(vehicle_maintenance_id=vehicle_maintenance_id, vehicle_maintenance_data=vehicle_maintenance_data)
            
            ##For Chief Driver, Admin Lead and Tenant Admin mapping all VehicleMaintenance
            else: 
                for role_dict.name in ["chief_driver", "admin_lead", "tenant_admin"]:
                    return vehicle_maintenance_repo.update_vehicle_maintenance(vehicle_maintenance_id=vehicle_maintenance_id, vehicle_maintenance_data=vehicle_maintenance_data, tenancy_id=current_user.tenancy_id)
        
    except Exception as err:
        vehicle_maintenance_repo.handle_errors(e=err, message=f"Database error: {str(err)}")


@router.delete("/vehicle_maintenance/{vehicle_maintenance_id}/delete_hard_vehicle_maintenance") 
@limiter.limit("5/minute")
async def delete_hard_vehicle_maintenance(request:Request, vehicle_maintenance_id:int, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    
    logging_helper.log_info("Accessing - Delete hard Vehicle Maintenance - Endpoint")
    vehicle_maintenance_repo = VehicleMaintenanceRepository(db)
    try:
        for role_dict in current_user.roles:

            ##For Super Admin mapping all the VehicleMaintenance for the 3 States
            if role_dict.name in ["super_admin"]:
                vehicle_maintenance = vehicle_maintenance_repo.delete_hard_vehicle_maintenance(vehicle_maintenance_id=vehicle_maintenance_id)
                return {f"'detail': 'VehicleMaintenance with ID {vehicle_maintenance_id} has been deleted successfully "}
            
            ##For Chief Driver, Admin Lead and Tenant Admin mapping all VehicleMaintenance
            else: 
                for role_dict.name in ["chief_driver", "admin_lead", "tenant_admin"]:
                    vehicle_maintenance = vehicle_maintenance_repo.delete_hard_vehicle_maintenance(vehicle_maintenance_id=vehicle_maintenance_id, tenancy_id=current_user.tenancy_id)
                    return {f"'detail': 'VehicleMaintenance with ID {vehicle_maintenance_id} has been deleted successfully "}
            
    except Exception as err:
        vehicle_maintenance_repo.handle_errors(e=err, message=f"Database error: {str(err)}")


@router.post("/vehicle_maintenance/{vehicle_maintenance_id}/soft_delete_vehicle_maintenance") 
@limiter.limit("5/minute")
async def soft_delete_vehicle_maintenance(request:Request, vehicle_maintenance_id:int, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Soft Delete Vehincle Maintenace - Endpoint")
    vehicle_maintenance_repo = VehicleMaintenanceRepository(db)
    try:
        for role_dict in current_user.roles:

            ##For Super Admin mapping all the VehicleMaintenance for the 3 States
            for role_dict.name in ["super_admin"]:
                vehicle_maintenance = vehicle_maintenance_repo.soft_delete_vehicle_maintenance(vehicle_maintenance_id=vehicle_maintenance_id)
                return {f"'detail': 'VehicleMaintenance with ID {vehicle_maintenance_id} has been deactivated successfully "}
            
            ##For Chief Driver, Admin Lead and Tenant Admin mapping all VehicleMaintenance
            else:
                for role_dict.name in ["chief_driver", "admin_lead", "tenant_admin"]:
                    vehicle_maintenance = vehicle_maintenance_repo.soft_delete_vehicle_maintenance(vehicle_maintenance_id=vehicle_maintenance_id, tenancy_id=current_user.tenancy_id)
                    return {f"'detail': 'VehicleMaintenance with ID {vehicle_maintenance_id} has been deactivated successfully "}
            
    except Exception as err:
        vehicle_maintenance_repo.handle_errors(e=err, message=f"Database error: {str(err)}")


@router.post("/vehicle_maintenance/{vehicle_maintenance_id}/restore_vehicle_maintenance", response_model= VehicleMaintenanceRead, status_code=status.HTTP_201_CREATED) 
@limiter.limit("5/minute")
async def restore_vehicle_maintenance(request:Request, vehicle_maintenance_id:int, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Restore Vehincle Maintenance - endpoint")
    vehicle_maintenance_repo = VehicleMaintenanceRepository(db)
    try:
        for role_dict in current_user.roles:

            ##For Super Admin mapping all the VehicleMaintenance for the 3 States
            if role_dict.name in ["super_admin"]:
                vehicle_maintenance = vehicle_maintenance_repo.restore_vehicle_maintenance(vehicle_maintenance_id=vehicle_maintenance_id)
                return vehicle_maintenance
            
            ##For Chief Driver, Admin Lead and Tenant Admin mapping all VehicleMaintenance
            else: 
                for role_dict.name in ["chief_driver", "admin_lead", "tenant_admin"]:
                    vehicle_maintenance = vehicle_maintenance_repo.restore_vehicle_maintenance(vehicle_maintenance_id=vehicle_maintenance_id, tenancy_id=current_user.tenancy_id)
                    return vehicle_maintenance
            
    except Exception as err:
        vehicle_maintenance_repo.handle_errors(e=err, message=f"Database error: {str(err)}")


# @router.get("/vehicle_maintenance/logs", response_model=List[Dict], status_code=status.HTTP_200_OK)
# @limiter.limit("5/minute")
# async def get_vehicle_maintenance_logs(request: Request, start_date: datetime, end_date: datetime, tenancy_id: Optional[int] = None, current_user: UserRead = Depends(get_current_user),
#                                        db: Session = Depends(get_db), _=Depends(role_checker(['hq_backstop', 'chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))):
#     logging_helper.log_info("Accessing - Get Vehicle Maintenance Logs - Endpoint")
#     vehicle_maintenance_repo = VehicleMaintenanceRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name in ["hq_backstop", "super_admin"]:
#                 logs = vehicle_maintenance_repo.get_vehicle_maintenance_logs(start_date=start_date, end_date=end_date)
#                 break
#             else:
#                 if role_dict.name in ["chief_driver", "admin_lead", "tenant_admin"]:
#                     logs = vehicle_maintenance_repo.get_vehicle_maintenance_logs(start_date=start_date, end_date=end_date, tenancy_id=current_user.tenancy_id)
#                     break
#         return logs
#     except Exception as err:
#         vehicle_maintenance_repo.handle_errors(e=err, message=f"Database error: {str(err)}")

@router.get("/vehicle_maintenance/logs", response_model=List[Dict], status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def get_vehicle_maintenance_logs(request: Request, start_date: datetime, end_date: datetime, tenancy_id: Optional[int] = None, current_user: UserRead = Depends(get_current_user),
                                       db: Session = Depends(get_db), _=Depends(role_checker(['hq_backstop', 'chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))):
    logging_helper.log_info("Accessing - Get Vehicle Maintenance Logs - Endpoint")
    vehicle_maintenance_repo = VehicleMaintenanceRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name in ["hq_backstop", "super_admin"]:
                logs = vehicle_maintenance_repo.get_vehicle_maintenance_logs(start_date=start_date, end_date=end_date)
                break
            else:
                if role_dict.name in ["chief_driver", "admin_lead", "tenant_admin"]:
                    logs = vehicle_maintenance_repo.get_vehicle_maintenance_logs(start_date=start_date, end_date=end_date, tenancy_id=current_user.tenancy_id)
                    break
        return logs
    except Exception as err:
        vehicle_maintenance_repo.handle_errors(e=err, message=f"Database error: {str(err)}")



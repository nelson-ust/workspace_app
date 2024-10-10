

# from datetime import datetime
# from fastapi import APIRouter, HTTPException, Query, status, Request, Depends
# from fastapi.responses import StreamingResponse
# from sqlalchemy.orm import Session
# from typing import Dict, List, Optional
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# from db.database import get_db
# from repositories.vehicle_repository import VehicleRepository
# from schemas.vehicle_schemas import VehicleCreate, VehicleUpdate, VehicleRead #, Update_Fuel_Economy #, VehicleReadAll
# from schemas.user_schemas import UserRead
# from auth.security import get_current_user
# from auth.dependencies import role_checker 
# from logging_helpers import logging_helper, ActionEnum
# limiter = Limiter(key_func=get_remote_address)
# router = APIRouter()


# @router.post("/vehicle/", response_model= VehicleRead, status_code=status.HTTP_201_CREATED) 
# @limiter.limit("10/minute")
# async def create_vehicle(request: Request, vehicle_data: VehicleCreate, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['admin_lead', 'tenant_admin','super_admin']))):
#     vehicle_repo = VehicleRepository(db)
#     logging_helper.log_info("Accessing the Create Vehicle Endpoint")
#     try:
#         #super_admin check
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin" or current_user.tenancy_id == vehicle_data.tenancy_id:
#                 new_vehicle = vehicle_repo.create_vehicle(vehicle_info=vehicle_data)
#                 break
#             else:
#                 logging_helper.log_info(f"{current_user.first_name} {current_user.last_name}, your authorized to create vehicle for only your state")
#                 raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{current_user.first_name} {current_user.last_name}, your authorized to create vehicle for only your state")
#         return new_vehicle
#     except HTTPException as err:
#         logging_helper.log_error(message=f"Warning Unauthorized: {str(err)} !!!")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


# @router.get("/vehicle/", response_model=List[VehicleRead], status_code=status.HTTP_200_OK)
# @limiter.limit("10/minute")
# async def list_all_active_vehicles(request:Request, skip: int = 0, limit: int = 100, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['driver', 'chief_driver' 'admin_lead', 'hq_staff', 'tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - List all Active Vehicles - Endpoint")
#     vehicle_repo = VehicleRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name in ["super_admin", "hq_staff"]:
#                 return vehicle_repo.get_all_active_vehicles(skip=skip, limit=limit)
#             else:
#                 return vehicle_repo.get_all_active_vehicle_for_tenancy(tenancy_id=current_user.tenancy_id, skip=skip, limit=limit)

#         print(f"Fetching all Vehicles with skip={skip} and limit={limit}")
#         vehicles = vehicle_repo.get_all_active_vehicles(skip=skip, limit=limit)
#         print(f"Found Vehicles: {vehicles}")
#         return vehicles
#     except HTTPException as err:
#         logging_helper.log_error(message=f"{str(err)} !!!")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(err)}")


# @router.get("/vehicle/available/", response_model=List[VehicleRead], status_code=status.HTTP_200_OK)
# @limiter.limit("5/minute")
# async def list_available_vehicles(request:Request, skip: int = 0, limit: int = 100, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['driver', 'chief_driver' 'admin_lead', 'hq_staff', 'tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - List Available Vehicles - Endpoint")
#     vehicle_repo = VehicleRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name in ["super_admin", "hq_staff"]:
#                 vehicles = vehicle_repo.get_available_vehicles(skip=skip, limit=limit)
#                 return vehicles
#             else:
#                 vehicles = vehicle_repo.get_available_vehicles(tenancy_id=current_user.tenancy_id, skip=skip, limit=limit)
#                 return vehicles

#         print(f"Fetching all Vehicles with skip={skip} and limit={limit}")
#         print(f"Found all Vehicles: {vehicles}")
#         return vehicles
#     except HTTPException as err:
#         logging_helper.log_error(message=f"{str(err)} !!!")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(err)}")


# @router.get("/vehicle/{vehicle_id}/", response_model= VehicleRead, status_code=status.HTTP_200_OK)
# @limiter.limit("5/minute")
# async def get_vehicle_by_id(request:Request, vehicle_id:int, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['driver', 'chief_driver' 'admin_lead', 'hq_staff', 'tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Get Vehincle by id - Endpoint")
#     vehicle_repo = VehicleRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name in ["super_admin", "hq_staff"]:
#                 vehicle = vehicle_repo.get_vehicle_by_id(vehicle_id=vehicle_id)
#                 if not vehicle:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The vehicle with id {vehicle_id} is not found")
#                 return vehicle
#             else:
#                 vehicle = vehicle_repo.get_vehicle_by_id_for_tenancy(vehicle_id=vehicle_id, tenancy_id=current_user.tenancy_id)
#                 if not vehicle:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The vehicle with id {vehicle_id} is not found or does not belong to your state")
#                 return vehicle
#     except HTTPException as err:
#         logging_helper.log_error(message=f"{str(err)} !!!")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


# @router.get("/vehicle/license_plate/{licence_plate}", response_model= VehicleRead, status_code=status.HTTP_200_OK)
# @limiter.limit("5/minute")

# async def get_vehicle_licence_plate(request:Request, licence_plate:str, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['chief_driver','admin_lead', 'tenant_admin', 'hq_staff', 'super_admin']))):
#     logging_helper.log_info("Accessing - Get Vehincle Lincence Plate - Endpoint")
#     vehicle_repo = VehicleRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name in ["super_admin", "hq_staff"]:
#                 vehicle = vehicle_repo.get_vehicle_by_licence_plate(licence_plate=licence_plate)
#                 if not vehicle:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The vehicle with licence_plate {licence_plate} is not found")
#                 return vehicle
#             else:
#                 vehicle = vehicle_repo.get_vehicle_by_licence_plate(licence_plate=licence_plate, tenancy_id=current_user.tenancy_id)
#                 if not vehicle:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The vehicle with licence_plate {licence_plate} is not found or does not belong to your state")
#                 return vehicle
#     except HTTPException as err:
#         logging_helper.log_error(message=f"{str(err)} !!!")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {str(err)}")


# @router.put("/vehicle/{vehicle_id}", response_model=VehicleRead)
# @limiter.limit("5/minute")
# async def update_vehicle(request:Request, vehicle_id:int, vehicle_data:VehicleUpdate, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Update Vehincle - Endpoint")
#     vehicle_repo = VehicleRepository(db)

#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 driver = vehicle_repo.update_vehicle(vehicle_id=vehicle_id, vehicle_info=vehicle_data)
#                 if not driver:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with id {vehicle_id} is not found")
#                 return driver
#             else:
#                 driver = vehicle_repo.update_vehicle(vehicle_id=vehicle_id, vehicle_info=vehicle_data, tenancy_id=current_user.tenancy_id)
#                 if not driver:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with id {vehicle_id} is not found")
#                 return driver
#     except HTTPException as err:
#         logging_helper.log_error(message=f"{str(err)} !!!")
#         vehicle_repo.handle_errors(e=err, message=f"{str(err)}")
    

# @router.delete("/vehicle/{vehicle_id}")
# @limiter.limit("5/minute")
# async def delete_vehicle(request:Request, vehicle_id:int, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Delete Vehincle - Endpoint")
#     vehicle_repo = VehicleRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 vehicle = vehicle_repo.delete_vehicle(vehicle_id=vehicle_id)
#                 if not vehicle:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with id {vehicle_id} is not found")
#             else:
#                 vehicle = vehicle_repo.delete_vehicle(vehicle_id=vehicle_id, tenancy_id=current_user.tenancy_id)
#                 if not vehicle:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with id {vehicle_id} is not found")
#             return {f" 'detail': 'Vehicle with id {vehicle_id} has been deleted successfully "}

#     except HTTPException as err:
#         logging_helper.log_error(message=f"{str(err)} !!!")
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Database error: {str(err)}")
#     return {f" 'detail': 'Vehicle with id {vehicle_id} has been deleted successfully "}


# @router.post("/vehicle/{vehicle_id}/soft_delete")
# @limiter.limit("5/minute")
# async def soft_delete_vehicle(request:Request, vehicle_id:int, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Soft Delete Vehincle - Endpoint")
#     vehicle_repo = VehicleRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 vehicle = vehicle_repo.soft_delete_vehicle(vehicle_id=vehicle_id)
#                 if not vehicle:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with id {vehicle_id} is not found or not soft-deleted")
#             else:
#                 vehicle = vehicle_repo.soft_delete_vehicle(vehicle_id=vehicle_id, tenancy_id=current_user.tenancy_id)
#                 if not vehicle:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with id {vehicle_id} is not found or not soft-deleted")
#             return {f" 'detail': 'Vehicle with id {vehicle_id} has been deactivated successfully "}

#     except HTTPException as err:
#         logging_helper.log_error(message=f"{str(err)} !!!")
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Database error: {str(err)}")


# @router.post("/vehicle/{vehicle_id}/restore")
# @limiter.limit("5/minute")
# async def restore_vehicle(request: Request, vehicle_id:int, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Restore Vehincle - Endpoint")
#     vehicle_repo = VehicleRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 vehicle = vehicle_repo.restore_vehicle(vehicle_id=vehicle_id)
#                 if not vehicle:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with id {vehicle_id} is not found or not soft-deleted")
#             else:
#                 vehicle = vehicle_repo.restore_vehicle(vehicle_id=vehicle_id, tenancy_id=current_user.tenancy_id)
#                 if not vehicle:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with id {vehicle_id} is not found or not soft-deleted")
#             return {f" 'detail': 'Vehicle with id {vehicle_id} has been activated successfully "}
#     except HTTPException as err:
#         logging_helper.log_error(message=f"{str(err)} !!!")
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Database error: {str(err)}")
#     return {f" 'detail': 'Vehicle not found or not soft-deleted "}



# @router.put("/Vehicle/{licence_plate}/fuel_economy")
# @limiter.limit("5/minute")
# async def update_fuel_economy(request:Request, licence_plate:str, fuel_economy:float, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
#     """
#     Update Fuel Economy of a Vehicle using Licence Plate or Alternate Licence Plate
#     """
    
#     logging_helper.log_info("Accessing - Update Fuel Economy - Endpoint")
#     vehicle_repo = VehicleRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 vehicle = vehicle_repo.update_fuel_economy(licence_plate=licence_plate, new_fuel_economy=fuel_economy)
#                 if not vehicle:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with licence {licence_plate} is not found")
#             else:
#                 vehicle = vehicle_repo.update_fuel_economy(licence_plate=licence_plate, new_fuel_economy=fuel_economy, tenancy_id=current_user.tenancy_id)
#                 if not vehicle:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with licence {licence_plate} is not found")
#             return {"detail: The Fuel Economy has been updated successfully"}

#     except HTTPException as err:
#         logging_helper.log_error(message=f"{str(err)} !!!")
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Database error: {str(err)}")
    

# @router.put("/vehicle/{vehicle_id}/availability")
# @limiter.limit("5/minute")
# async def update_driver_availability(request: Request, vehicle_id: int, is_available: bool,
#                                      current_user: UserRead = Depends(get_current_user),
#                                      db: Session = Depends(get_db),
#                                      _=Depends(role_checker(['super_admin', 'tenant_admin', 'admin_lead', 'chief_pilot']))):
#     logging_helper.log_info("Accessing - Update Driver Availability - Endpoint")
#     driver_repo = VehicleRepository(db)
#     try:
#         vehicle = driver_repo.update_vehicle_availability(vehicle_id=vehicle_id, is_available=is_available)
#         if not vehicle:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Driver with ID {vehicle_id} not found")

#         logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "Vehicle", vehicle_id, f"Updated driver availability: {vehicle_id} to {is_available}")
#         return vehicle
#     except HTTPException as err:
#         logging_helper.log_error(message=f"Failed to update driver availability: {str(err)} !!!")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


# @router.get("/vehicle-movement-logs", response_model=List[Dict])
# def get_vehicle_movement_logs(
#     start_date: datetime,
#     end_date: datetime,
#     tenancy_ids: Optional[List[int]] = Query(None, description="Optional list of tenancy IDs to filter the results"),
#     db: Session = Depends(get_db),
#     current_user: UserRead = Depends(get_current_user),
#     _=Depends(role_checker(['chief_driver', 'admin_lead', 'hq_backstop', 'tenant_admin', 'super_admin']))
# ):
#     logging_helper.log_info(f"Accessing - Get Vehicle Movement Logs - Endpoint with tenancy_ids={tenancy_ids}")
#     try:
#         vehicle_repo = VehicleRepository(db)
#         result = vehicle_repo.get_vehicle_movement_logs(start_date, end_date, tenancy_ids)
#         logging_helper.log_info("Successfully retrieved vehicle movement logs")
#         return result
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTPException: {str(e.detail)}")
#         raise HTTPException(status_code=e.status_code, detail=e.detail)
#     except Exception as e:
#         logging_helper.log_error(f"Exception: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))



# @router.get("/vehicle-movement-logs-csv", response_class=StreamingResponse)
# def export_vehicle_movement_logs_to_csv(
#     start_date: datetime,
#     end_date: datetime,
#     tenancy_ids: Optional[List[int]] = Query(None, description="Optional list of tenancy IDs to filter the results"),
#     db: Session = Depends(get_db),
#     current_user: UserRead = Depends(get_current_user),
#     _=Depends(role_checker(['chief_driver', 'admin_lead', 'hq_backstop', 'tenant_admin', 'super_admin']))
# ):
#     logging_helper.log_info(f"Accessing - Export Vehicle Movement Logs to CSV - Endpoint with tenancy_ids={tenancy_ids}")
#     try:
#         vehicle_repo = VehicleRepository(db)
#         csv_data = vehicle_repo.generate_vehicle_movement_logs_csv(start_date, end_date, tenancy_ids)
#         logging_helper.log_info("Successfully generated vehicle movement logs CSV")
#         response = StreamingResponse(csv_data, media_type="text/csv")
#         response.headers["Content-Disposition"] = "attachment; filename=vehicle_movement_logs.csv"
#         return response
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTPException: {str(e.detail)}")
#         raise HTTPException(status_code=e.status_code, detail=e.detail)
#     except Exception as e:
#         logging_helper.log_error(f"Exception: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))



# @router.get("/vehicle-movement-logs-xlsx", response_class=StreamingResponse)
# def export_vehicle_movement_logs_to_xlsx(
#     start_date: datetime,
#     end_date: datetime,
#     tenancy_ids: Optional[List[int]] = Query(None, description="Optional list of tenancy IDs to filter the results"),
#     db: Session = Depends(get_db),
#     current_user: UserRead = Depends(get_current_user),
#     _=Depends(role_checker(['chief_driver', 'admin_lead', 'hq_backstop', 'tenant_admin', 'super_admin']))
# ):
#     logging_helper.log_info(f"Accessing - Export Vehicle Movement Logs to Excel - Endpoint with tenancy_ids={tenancy_ids}")
#     try:
#         vehicle_repo = VehicleRepository(db)
#         xlsx_data = vehicle_repo.generate_vehicle_movement_logs_xlsx(start_date, end_date, tenancy_ids)
#         logging_helper.log_info("Successfully generated vehicle movement logs Excel")
#         response = StreamingResponse(xlsx_data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
#         response.headers["Content-Disposition"] = "attachment; filename=vehicle_movement_logs.xlsx"
#         return response
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTPException: {str(e.detail)}")
#         raise HTTPException(status_code=e.status_code, detail=e.detail)
#     except Exception as e:
#         logging_helper.log_error(f"Exception: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))






from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, status, Request, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from db.database import get_db
from repositories.vehicle_repository import VehicleRepository
from schemas.vehicle_schemas import VehicleCreate, VehicleUpdate, VehicleRead #, Update_Fuel_Economy #, VehicleReadAll
from schemas.user_schemas import UserRead
from auth.security import get_current_user
from auth.dependencies import role_checker 
from logging_helpers import logging_helper, ActionEnum
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/vehicle/", response_model= VehicleRead, status_code=status.HTTP_201_CREATED) 
@limiter.limit("10/minute")
async def create_vehicle(request: Request, vehicle_data: VehicleCreate, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['admin_lead', 'tenant_admin','super_admin']))):
    vehicle_repo = VehicleRepository(db)
    logging_helper.log_info("Accessing the Create Vehicle Endpoint")
    try:
        #super_admin check
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin" or current_user.tenancy_id == vehicle_data.tenancy_id:
                new_vehicle = vehicle_repo.create_vehicle(vehicle_info=vehicle_data)
                break
            else:
                logging_helper.log_info(f"{current_user.first_name} {current_user.last_name}, your authorized to create vehicle for only your state")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{current_user.first_name} {current_user.last_name}, your authorized to create vehicle for only your state")
        return new_vehicle
    except HTTPException as err:
        logging_helper.log_error(message=f"Warning Unauthorized: {str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


@router.get("/vehicle/", response_model=List[VehicleRead], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def list_all_active_vehicles(request:Request, skip: int = 0, limit: int = 100, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['driver', 'chief_driver' 'admin_lead', 'hq_staff', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - List all Active Vehicles - Endpoint")
    vehicle_repo = VehicleRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_staff"]:
                return vehicle_repo.get_all_active_vehicles(skip=skip, limit=limit)
            else:
                return vehicle_repo.get_all_active_vehicle_for_tenancy(tenancy_id=current_user.tenancy_id, skip=skip, limit=limit)

        print(f"Fetching all Vehicles with skip={skip} and limit={limit}")
        vehicles = vehicle_repo.get_all_active_vehicles(skip=skip, limit=limit)
        print(f"Found Vehicles: {vehicles}")
        return vehicles
    except HTTPException as err:
        logging_helper.log_error(message=f"{str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(err)}")


@router.get("/vehicle/available/", response_model=List[VehicleRead], status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def list_available_vehicles(request:Request, skip: int = 0, limit: int = 100, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['driver', 'chief_driver' 'admin_lead', 'hq_staff', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - List Available Vehicles - Endpoint")
    vehicle_repo = VehicleRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_staff"]:
                vehicles = vehicle_repo.get_available_vehicles(skip=skip, limit=limit)
                return vehicles
            else:
                vehicles = vehicle_repo.get_available_vehicles(tenancy_id=current_user.tenancy_id, skip=skip, limit=limit)
                return vehicles

        print(f"Fetching all Vehicles with skip={skip} and limit={limit}")
        print(f"Found all Vehicles: {vehicles}")
        return vehicles
    except HTTPException as err:
        logging_helper.log_error(message=f"{str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(err)}")


@router.get("/vehicle/{vehicle_id}/", response_model= VehicleRead, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def get_vehicle_by_id(request:Request, vehicle_id:int, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['driver', 'chief_driver' 'admin_lead', 'hq_staff', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Get Vehincle by id - Endpoint")
    vehicle_repo = VehicleRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_staff"]:
                vehicle = vehicle_repo.get_vehicle_by_id(vehicle_id=vehicle_id)
                if not vehicle:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The vehicle with id {vehicle_id} is not found")
                return vehicle
            else:
                vehicle = vehicle_repo.get_vehicle_by_id_for_tenancy(vehicle_id=vehicle_id, tenancy_id=current_user.tenancy_id)
                if not vehicle:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The vehicle with id {vehicle_id} is not found or does not belong to your state")
                return vehicle
    except HTTPException as err:
        logging_helper.log_error(message=f"{str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


@router.get("/vehicle/license_plate/{licence_plate}", response_model= VehicleRead, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")

async def get_vehicle_licence_plate(request:Request, licence_plate:str, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['chief_driver','admin_lead', 'tenant_admin', 'hq_staff', 'super_admin']))):
    logging_helper.log_info("Accessing - Get Vehincle Lincence Plate - Endpoint")
    vehicle_repo = VehicleRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_staff"]:
                vehicle = vehicle_repo.get_vehicle_by_licence_plate(licence_plate=licence_plate)
                if not vehicle:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The vehicle with licence_plate {licence_plate} is not found")
                return vehicle
            else:
                vehicle = vehicle_repo.get_vehicle_by_licence_plate(licence_plate=licence_plate, tenancy_id=current_user.tenancy_id)
                if not vehicle:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The vehicle with licence_plate {licence_plate} is not found or does not belong to your state")
                return vehicle
    except HTTPException as err:
        logging_helper.log_error(message=f"{str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {str(err)}")


@router.put("/vehicle/{vehicle_id}", response_model=VehicleRead)
@limiter.limit("5/minute")
async def update_vehicle(request:Request, vehicle_id:int, vehicle_data:VehicleUpdate, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Update Vehincle - Endpoint")
    vehicle_repo = VehicleRepository(db)

    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                driver = vehicle_repo.update_vehicle(vehicle_id=vehicle_id, vehicle_info=vehicle_data)
                if not driver:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with id {vehicle_id} is not found")
                return driver
            else:
                driver = vehicle_repo.update_vehicle(vehicle_id=vehicle_id, vehicle_info=vehicle_data, tenancy_id=current_user.tenancy_id)
                if not driver:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with id {vehicle_id} is not found")
                return driver
    except HTTPException as err:
        logging_helper.log_error(message=f"{str(err)} !!!")
        vehicle_repo.handle_errors(e=err, message=f"{str(err)}")
    

@router.delete("/vehicle/{vehicle_id}")
@limiter.limit("5/minute")
async def delete_vehicle(request:Request, vehicle_id:int, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Delete Vehincle - Endpoint")
    vehicle_repo = VehicleRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                vehicle = vehicle_repo.delete_vehicle(vehicle_id=vehicle_id)
                if not vehicle:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with id {vehicle_id} is not found")
            else:
                vehicle = vehicle_repo.delete_vehicle(vehicle_id=vehicle_id, tenancy_id=current_user.tenancy_id)
                if not vehicle:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with id {vehicle_id} is not found")
            return {f" 'detail': 'Vehicle with id {vehicle_id} has been deleted successfully "}

    except HTTPException as err:
        logging_helper.log_error(message=f"{str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Database error: {str(err)}")
    return {f" 'detail': 'Vehicle with id {vehicle_id} has been deleted successfully "}


@router.post("/vehicle/{vehicle_id}/soft_delete")
@limiter.limit("5/minute")
async def soft_delete_vehicle(request:Request, vehicle_id:int, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Soft Delete Vehincle - Endpoint")
    vehicle_repo = VehicleRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                vehicle = vehicle_repo.soft_delete_vehicle(vehicle_id=vehicle_id)
                if not vehicle:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with id {vehicle_id} is not found or not soft-deleted")
            else:
                vehicle = vehicle_repo.soft_delete_vehicle(vehicle_id=vehicle_id, tenancy_id=current_user.tenancy_id)
                if not vehicle:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with id {vehicle_id} is not found or not soft-deleted")
            return {f" 'detail': 'Vehicle with id {vehicle_id} has been deactivated successfully "}

    except HTTPException as err:
        logging_helper.log_error(message=f"{str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Database error: {str(err)}")


@router.post("/vehicle/{vehicle_id}/restore")
@limiter.limit("5/minute")
async def restore_vehicle(request: Request, vehicle_id:int, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Restore Vehincle - Endpoint")
    vehicle_repo = VehicleRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                vehicle = vehicle_repo.restore_vehicle(vehicle_id=vehicle_id)
                if not vehicle:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with id {vehicle_id} is not found or not soft-deleted")
            else:
                vehicle = vehicle_repo.restore_vehicle(vehicle_id=vehicle_id, tenancy_id=current_user.tenancy_id)
                if not vehicle:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with id {vehicle_id} is not found or not soft-deleted")
            return {f" 'detail': 'Vehicle with id {vehicle_id} has been activated successfully "}
    except HTTPException as err:
        logging_helper.log_error(message=f"{str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Database error: {str(err)}")
    return {f" 'detail': 'Vehicle not found or not soft-deleted "}



@router.put("/Vehicle/{licence_plate}/fuel_economy")
@limiter.limit("5/minute")
async def update_fuel_economy(request:Request, licence_plate:str, fuel_economy:float, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin','super_admin']))):
    """
    Update Fuel Economy of a Vehicle using Licence Plate or Alternate Licence Plate
    """
    
    logging_helper.log_info("Accessing - Update Fuel Economy - Endpoint")
    vehicle_repo = VehicleRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                vehicle = vehicle_repo.update_fuel_economy(licence_plate=licence_plate, new_fuel_economy=fuel_economy)
                if not vehicle:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with licence {licence_plate} is not found")
            else:
                vehicle = vehicle_repo.update_fuel_economy(licence_plate=licence_plate, new_fuel_economy=fuel_economy, tenancy_id=current_user.tenancy_id)
                if not vehicle:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Vehicle with licence {licence_plate} is not found")
            return {"detail: The Fuel Economy has been updated successfully"}

    except HTTPException as err:
        logging_helper.log_error(message=f"{str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Database error: {str(err)}")
    

@router.put("/vehicle/{vehicle_id}/availability")
@limiter.limit("5/minute")
async def update_driver_availability(request: Request, vehicle_id: int, is_available: bool,
                                     current_user: UserRead = Depends(get_current_user),
                                     db: Session = Depends(get_db),
                                     _=Depends(role_checker(['super_admin', 'tenant_admin', 'admin_lead', 'chief_pilot']))):
    logging_helper.log_info("Accessing - Update Driver Availability - Endpoint")
    driver_repo = VehicleRepository(db)
    try:
        vehicle = driver_repo.update_vehicle_availability(vehicle_id=vehicle_id, is_available=is_available)
        if not vehicle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Driver with ID {vehicle_id} not found")

        logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "Vehicle", vehicle_id, f"Updated driver availability: {vehicle_id} to {is_available}")
        return vehicle
    except HTTPException as err:
        logging_helper.log_error(message=f"Failed to update driver availability: {str(err)} !!!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


# @router.get("/vehicle-movement-logs", response_model=List[Dict])
# def get_vehicle_movement_logs(
#     start_date: datetime,
#     end_date: datetime,
#     tenancy_id: List[int] = Query(None, description="Optional tenancy ID to filter the results"),
#     db: Session = Depends(get_db),
#     current_user: UserRead = Depends(get_current_user),
#     _=Depends(role_checker(['chief_driver', 'admin_lead','hq_backstop', 'tenant_admin','super_admin']))
# ):
#     logging_helper.log_info(f"Accessing - Get Vehicle Movement Logs - Endpoint with tenancy_id={tenancy_id}")
#     try:
#         vehicle_repo = VehicleRepository(db)
#         result = vehicle_repo.get_vehicle_movement_logs(start_date, end_date, tenancy_id)
#         logging_helper.log_info("Successfully retrieved vehicle movement logs")
#         return result
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTPException: {str(e.detail)}")
#         raise HTTPException(status_code=e.status_code, detail=e.detail)
#     except Exception as e:
#         logging_helper.log_error(f"Exception: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))
    


# @router.get("/vehicle-movement-logs-csv", response_class=StreamingResponse)
# def export_vehicle_movement_logs_to_csv(
#     start_date: datetime,
#     end_date: datetime,
#     tenancy_ids: Optional[List[int]] = Query(None, description="Optional list of tenancy IDs to filter the results"),
#     db: Session = Depends(get_db),
#     current_user: UserRead = Depends(get_current_user),
#     _=Depends(role_checker(['chief_driver', 'admin_lead', 'hq_backstop', 'tenant_admin', 'super_admin']))
# ):
#     logging_helper.log_info(f"Accessing - Export Vehicle Movement Logs to CSV - Endpoint with tenancy_ids={tenancy_ids}")
#     try:
#         vehicle_repo = VehicleRepository(db)
#         csv_data = vehicle_repo.generate_vehicle_movement_logs_csv(start_date, end_date, tenancy_ids)
#         logging_helper.log_info("Successfully generated vehicle movement logs CSV")
#         response = StreamingResponse(csv_data, media_type="text/csv")
#         response.headers["Content-Disposition"] = "attachment; filename=vehicle_movement_logs.csv"
#         return response
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTPException: {str(e.detail)}")
#         raise HTTPException(status_code=e.status_code, detail=e.detail)
#     except Exception as e:
#         logging_helper.log_error(f"Exception: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/vehicle-movement-logs", response_model=List[Dict])
# def get_vehicle_movement_logs(
#     start_date: datetime,
#     end_date: datetime,
#     tenancy_ids: Optional[List[int]] = Query(None, description="Optional list of tenancy IDs to filter the results"),
#     db: Session = Depends(get_db),
#     current_user: UserRead = Depends(get_current_user),
#     _=Depends(role_checker(['chief_driver', 'admin_lead', 'hq_backstop', 'tenant_admin', 'super_admin']))
# ):
#     logging_helper.log_info(f"Accessing - Get Vehicle Movement Logs - Endpoint with tenancy_ids={tenancy_ids}")
#     try:
#         vehicle_repo = VehicleRepository(db)
#         result = vehicle_repo.get_vehicle_movement_logs(start_date, end_date, tenancy_ids)
#         logging_helper.log_info("Successfully retrieved vehicle movement logs")
#         return result
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTPException: {str(e.detail)}")
#         raise HTTPException(status_code=e.status_code, detail=e.detail)
#     except Exception as e:
#         logging_helper.log_error(f"Exception: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


@router.get("/vehicle-movement-logs", response_model=List[Dict])
def get_vehicle_movement_logs(
    start_date: datetime,
    end_date: datetime,
    tenancy_ids: Optional[List[int]] = Query(None, description="Optional list of tenancy IDs to filter the results"),
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    _=Depends(role_checker(['chief_driver', 'admin_lead', 'hq_backstop', 'tenant_admin', 'super_admin']))
):
    logging_helper.log_info(f"Accessing - Get Vehicle Movement Logs - Endpoint with tenancy_ids={tenancy_ids}")
    try:
        vehicle_repo = VehicleRepository(db)
        result = vehicle_repo.get_vehicle_movement_logs(start_date, end_date, tenancy_ids)
        logging_helper.log_info("Successfully retrieved vehicle movement logs")
        return result
    except HTTPException as e:
        logging_helper.log_error(f"HTTPException: {str(e.detail)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logging_helper.log_error(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/vehicle-movement-logs-csv", response_class=StreamingResponse)
def export_vehicle_movement_logs_to_csv(
    start_date: datetime,
    end_date: datetime,
    tenancy_ids: Optional[List[int]] = Query(None, description="Optional list of tenancy IDs to filter the results"),
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    _=Depends(role_checker(['chief_driver', 'admin_lead', 'hq_backstop', 'tenant_admin', 'super_admin']))
):
    logging_helper.log_info(f"Accessing - Export Vehicle Movement Logs to CSV - Endpoint with tenancy_ids={tenancy_ids}")
    try:
        vehicle_repo = VehicleRepository(db)
        csv_data = vehicle_repo.generate_vehicle_movement_logs_csv(start_date, end_date, tenancy_ids)
        logging_helper.log_info("Successfully generated vehicle movement logs CSV")
        response = StreamingResponse(csv_data, media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=vehicle_movement_logs.csv"
        return response
    except HTTPException as e:
        logging_helper.log_error(f"HTTPException: {str(e.detail)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logging_helper.log_error(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/vehicle-movement-logs-xlsx", response_class=StreamingResponse)
def export_vehicle_movement_logs_to_xlsx(
    start_date: datetime,
    end_date: datetime,
    tenancy_ids: Optional[List[int]] = Query(None, description="Optional list of tenancy IDs to filter the results"),
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    _=Depends(role_checker(['chief_driver', 'admin_lead', 'hq_backstop', 'tenant_admin', 'super_admin']))
):
    logging_helper.log_info(f"Accessing - Export Vehicle Movement Logs to Excel - Endpoint with tenancy_ids={tenancy_ids}")
    try:
        vehicle_repo = VehicleRepository(db)
        xlsx_data = vehicle_repo.generate_vehicle_movement_logs_xlsx(start_date, end_date, tenancy_ids)
        logging_helper.log_info("Successfully generated vehicle movement logs Excel")
        response = StreamingResponse(xlsx_data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response.headers["Content-Disposition"] = "attachment; filename=vehicle_movement_logs.xlsx"
        return response
    except HTTPException as e:
        logging_helper.log_error(f"HTTPException: {str(e.detail)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logging_helper.log_error(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
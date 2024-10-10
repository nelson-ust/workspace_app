


# import json
# from typing import List, Optional, Tuple
# from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, status
# import sqlalchemy
# from sqlalchemy.orm import Session
# from auth.dependencies import role_checker
# from auth.security import get_current_user
# from models.all_models import ActionEnum
# from schemas.user_schemas import UserRead
# from db.database import get_db  
# from schemas.trip_schemas import ArrivalRequest, ArrivalResponse, AssignVehicleDriverRequest, DepartureRequest, DepartureResponse, DropEmployeesFromTripRequest, EmployeeRead, EndTripRequest, GetEmployeesNotInTripRequest, RecordMileageRequest, RecordStageRequest, TripArrivalRequest, TripArrivalResponse, TripSummary
# from repositories.trip_repo import TripRepository
# from logging_helpers import logging_helper

# router = APIRouter()

# @router.get("/trip-summary/{trip_id}", response_model=dict)  
# def trip_summary(trip_id: int, current_user: UserRead = Depends(get_current_user), 
#                  db: Session = Depends(get_db), _ = Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))):
#     """
#     Retrieve a detailed summary of a specific trip.
#     """
#     trip_repo = TripRepository(db_session=db)  # Assuming you have a repository class handling DB operations
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 result = trip_repo.get_trip_summary(trip_id)
#             else:
#                 result = trip_repo.get_trip_summary(trip_id, tenancy_id=current_user.tenancy_id)
#         if isinstance(result, str):
#             raise HTTPException(status_code=404, detail=result)
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# @router.get("/trips/summaries")  
# def get_all_trip_summaries(current_user: UserRead = Depends(get_current_user), 
#                            db: Session = Depends(get_db), _ = Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))):
#     """
#     Retrieves summaries for all trips including details such as employee names, sites, and vehicle information.
#     """
#     trip_repo = TripRepository(db)  
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 trip_summaries = trip_repo.get_all_trip_summaries()
#             else:
#                 trip_summaries = trip_repo.get_all_trip_summaries(tenancy_id=current_user.tenancy_id)
#         return trip_summaries
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/schedule_trip", status_code=status.HTTP_201_CREATED)
# def schedule_trip(
#     request: AssignVehicleDriverRequest,
#     background_tasks: BackgroundTasks,
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db),
#     _ = Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))
# ):
#     """
#     Assign a vehicle and a driver to a set of work plans.
#     """
#     try:
#         repo = TripRepository(db_session=db)
#         result = repo.schedule_trip(
#             work_plan_ids=request.work_plan_ids,
#             employee_ids=request.employee_ids,  # Add employee_ids to the function call
#             vehicle_id=request.vehicle_id,
#             driver_id=request.driver_id,
#             tenancy_id=current_user.tenancy_id,
#             auto_group_weekly=request.auto_group_weekly,
#             background_tasks=background_tasks
#         )
        
#         # Capture the changes in a dictionary
#         changes = {
#             "vehicle_id": request.vehicle_id,
#             "driver_id": request.driver_id,
#             "work_plan_ids": request.work_plan_ids,
#             "employee_ids": request.employee_ids,  # Include employee_ids in the changes
#             "auto_group_weekly": request.auto_group_weekly,
#             "assigned_trip_ids": result.get("trip_ids", [])
#         }
        
#         # Log the changes in the audit log
#         logging_helper.log_audit(
#             db, 
#             current_user.id, 
#             ActionEnum.SCHEDULE_TRIP, 
#             "Trip", 
#             0, 
#             changes  # Pass the dictionary as the log message
#         )
        
#         return {
#             "message": "Vehicle and driver assigned to work plans successfully.",
#             "details": result
#         }
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTPException: {e.detail}")
#         raise HTTPException(status_code=e.status_code, detail={"error": e.detail, "message": "Failed to assign vehicle and driver to work plans. Please check the details and try again."})
#     except Exception as e:
#         logging_helper.log_error(f"Exception: {str(e)}")
#         raise HTTPException(status_code=500, detail={"error": "ASSIGN_VEHICLE", "message": f"An unexpected error occurred: {str(e)}"})



# @router.post("/trips/{trip_id}/start", summary="Start a Trip")
# async def start_trip(trip_id: int, start_location_id: int, start_site_id: int, current_user: UserRead = Depends(get_current_user), 
#                      db: Session = Depends(get_db), _ = Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))):
#     """
#     Start a trip by setting the initial mileage from the vehicle's current mileage and creating the initial trip stage.

#     Parameters:
#     - trip_id (int): The ID of the trip to be started.
#     - start_location_id (int): The ID of the start location for the trip.
#     - start_site_id (int): The ID of the first site the vehicle will arrive at.
#     - current_user (UserRead): The current authenticated user.
#     - db (Session): The database session.
#     """
#     trip_start_repo = TripRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 # Start the trip without tenancy restriction for super_admin
#                 trip_start = trip_start_repo.start_trip(trip_id, start_location_id, start_site_id)
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.START_TRIP, "Trip", trip_id, f"Trip {trip_id} started by super_admin.")
#                 break
#             else:
#                 # Start the trip with tenancy restriction for other roles
#                 trip_start = trip_start_repo.start_trip(trip_id, start_location_id, start_site_id, current_user.tenancy_id)
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.START_TRIP, "Trip", trip_id, f"Trip {trip_id} started by {current_user.username} in tenancy {current_user.tenancy_id}.")
#                 break
#         return trip_start
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post("/trips/{trip_id}/arrival", response_model=TripArrivalResponse)
# def record_arrival(
#     trip_id: int,
#     stage_id:int,
#     arrival_request: TripArrivalRequest,
#     db: Session = Depends(get_db),
#     current_user: UserRead = Depends(get_current_user),
#     _ = Depends(role_checker(["super_admin", "driver"]))  # Role checking dependency
# ):
#     """
#     Record the arrival of a vehicle at a site.

#     Parameters:
#     - trip_id: The ID of the trip.
#     - arrival_request: The request body containing site_id and mileage_at_arrival.
#     - db: The database session.
#     - current_user: The current authenticated user.

#     Returns:
#     - TripArrivalResponse: The response containing the recorded trip stage details.
#     """
#     try:
#         trip_repo = TripRepository(db)
#         result = trip_repo.record_site_arrival(
#             trip_id=trip_id,
#             stage_id = stage_id,
#             mileage_at_arrival=arrival_request.mileage_at_arrival,
#             tenancy_id=current_user.tenancy_id
#         )
#         return result
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTPException while recording arrival: {e}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Exception while recording arrival: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post("/trips/{trip_id}/departure", response_model=DepartureResponse)
# def record_departure(
#     trip_id: int,
#     stage_id:int,
#     departure_request: DepartureRequest,
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db),
#     current_user: UserRead = Depends(get_current_user),
#     _ = Depends(role_checker(["super_admin", "driver"]))  # Role checking dependency
# ):
#     """
#     Record the departure of a vehicle from a site.

#     Parameters:
#     - trip_id: The ID of the trip.
#     - departure_request: The request body containing site_id and optional next_site_id.
#     - db: The database session.
#     - current_user: The current authenticated user.
#     - _: Role checking dependency to ensure the user has the required roles.

#     Returns:
#     - DepartureResponse: The response containing the recorded trip stage details.
#     """
#     try:
#         trip_repo = TripRepository(db)
#         result = trip_repo.record_site_departure(
#             trip_id=trip_id,
#             stage_id=stage_id,
#             next_site_id=departure_request.next_site_id,
#             tenancy_id=current_user.tenancy_id
#         )

#         # Log audit
#         logging_helper.log_audit(
#             db_session=db,
#             user_id=current_user.id,
#             action=ActionEnum.UPDATE,
#             model="TripStage",
#             model_id=trip_id,
#             changes={
#                 # "site_id": departure_request.site_id,
#                 "next_site_id": departure_request.next_site_id
#             }
#         )
#         return result
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTPException while recording departure: {e}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Exception while recording departure: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post("/trips/{trip_id}/end")
# def end_trip(
#     trip_id: int,
#     trip_data: EndTripRequest,
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db),
#     _ = Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))
# ):
#     """
#     Ends a trip with the given ID by updating the mileage at the end and calculating the distance traveled.
#     Requires the end mileage and trip_end_location_id to be specified.
#     """
#     trip_repo = TripRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 end_trip = trip_repo.end_trip(trip_id, trip_data.mileage_end, trip_data.trip_end_location_id)
#                 changes = {
#                     "message": f"Trip {trip_id} ended by super_admin.",
#                     "end_mileage": trip_data.mileage_end,
#                     "trip_end_location_id": trip_data.trip_end_location_id
#                 }
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.END_TRIP, "Trip", trip_id, changes)
#                 break
#             else:
#                 end_trip = trip_repo.end_trip(trip_id, trip_data.mileage_end, trip_data.trip_end_location_id, current_user.tenancy_id)
#                 changes = {
#                     "message": f"Trip {trip_id} ended by {current_user.username} in tenancy {current_user.tenancy_id}.",
#                     "end_mileage": trip_data.mileage_end,
#                     "trip_end_location_id": trip_data.trip_end_location_id
#                 }
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.END_TRIP, "Trip", trip_id, changes)
#                 break
#         result = end_trip
#         return result
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post("/add-employees-to-existing-trip", status_code=status.HTTP_200_OK)
# def add_employees_to_existing_trip(
#     existing_trip_id: int,
#     additional_work_plan_ids: List[int],
#     additional_employee_ids: List[int],
#     tenancy_id: Optional[int] = None,
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db),
#     _ = Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))
# ):
#     """
#     Add employees from additional work plans to an existing trip.

#     Args:
#         existing_trip_id (int): ID of the existing trip.
#         additional_work_plan_ids (List[int]): List of additional work plan IDs.
#         additional_employee_ids (List[int]): List of additional employee IDs.
#         tenancy_id (Optional[int]): ID of the tenancy (optional).

#     Returns:
#         dict: Message and details of the updated trip.
#     """
#     try:
#         repo = TripRepository(db_session=db)
#         result = repo.add_employees_to_existing_trip(
#             existing_trip_id=existing_trip_id,
#             additional_work_plan_ids=additional_work_plan_ids,
#             additional_employee_ids=additional_employee_ids,
#             tenancy_id=tenancy_id or current_user.tenancy_id
#         )
#         return result
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTPException: {e.detail}")
#         raise HTTPException(status_code=e.status_code, detail={"error": e.detail, "message": "Failed to add employees to the existing trip. Please check the details and try again."})
#     except Exception as e:
#         logging_helper.log_error(f"Exception: {str(e)}")
#         raise HTTPException(status_code=500, detail={"error": "ADD_EMPLOYEES", "message": f"An unexpected error occurred: {str(e)}"})


# @router.post("/trips/{trip_id}/drop_employees", response_model=dict)
# def drop_employees(
#     trip_id: int,
#     drop_request: DropEmployeesFromTripRequest,
#     db: Session = Depends(get_db),
#     current_user: UserRead = Depends(get_current_user),
#     _ = Depends(role_checker(["super_admin", "driver"]))
# ):
#     """
#     Remove employees from a trip.

#     Parameters:
#     - trip_id: The ID of the trip.
#     - drop_request: The request body containing a list of employee IDs to be removed.
#     - db: The database session.
#     - current_user: The current authenticated user.

#     Returns:
#     - dict: The response message indicating the result.
#     """
#     try:
#         trip_repo = TripRepository(db)
#         result = trip_repo.drop_employees_from_trip(
#             trip_id=trip_id,
#             employee_ids=drop_request.employee_ids,
#             tenancy_id=current_user.tenancy_id
#         )
#         return result
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTPException while removing employees from trip: {e}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Exception while removing employees from trip: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post("/get-employees-not-in-trip", status_code=status.HTTP_200_OK)
# def get_employees_not_in_trip(
#     request: GetEmployeesNotInTripRequest,
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db),
#     _ = Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))
# ):
#     """
#     Get all employees from selected work plans who are yet to be added to a Trip.

#     Args:
#         request (GetEmployeesNotInTripRequest): Request payload containing work_plan_ids.
#         current_user (UserRead): Current authenticated user.
#         db (Session): Database session.
#         _ : Role checker dependency.

#     Returns:
#         List[dict]: List of employees with their details who are yet to be added to a Trip.
#     """
#     try:
#         repo = TripRepository(db_session=db)
#         result = repo.get_employees_not_in_trip(
#             work_plan_ids=request.work_plan_ids,
#             tenancy_id=current_user.tenancy_id
#         )
#         return result
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTPException: {e.detail}")
#         raise HTTPException(status_code=e.status_code, detail={"error": e.detail, "message": "Failed to fetch employees not in any trip. Please check the details and try again."})
#     except Exception as e:
#         logging_helper.log_error(f"Exception: {str(e)}")
#         raise HTTPException(status_code=500, detail={"error": "GET_EMPLOYEES_NOT_IN_TRIP", "message": f"An unexpected error occurred: {str(e)}"})


# @router.post("/employees-associated-with-workplans", response_model=List[EmployeeRead], status_code=status.HTTP_200_OK)
# def employees_associated_with_workplans(
#     work_plan_ids: List[int],
#     tenancy_id: Optional[int] = None,
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db),
#     _ = Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))
# ):
#     """
#     Fetch employees associated with selected work plans.

#     Args:
#         work_plan_ids (List[int]): List of work plan IDs.
#         tenancy_id (Optional[int]): ID of the tenancy (optional).

#     Returns:
#         List[EmployeeRead]: List of employees associated with the work plans.
#     """
#     try:
#         repo = TripRepository(db_session=db)
#         employees = repo.get_employees_associated_with_workplans(work_plan_ids=work_plan_ids, tenancy_id=tenancy_id)
#         return employees
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTPException: {e.detail}")
#         raise HTTPException(status_code=e.status_code, detail={"error": e.detail, "message": "Failed to fetch employees associated with work plans. Please check the details and try again."})
#     except Exception as e:
#         logging_helper.log_error(f"Exception: {str(e)}")
#         raise HTTPException(status_code=500, detail={"error": "FETCH_EMPLOYEES", "message": f"An unexpected error occurred: {str(e)}"})


# @router.get("/trips-by-status/{status}", response_model=List[TripSummary])
# def get_trips_by_status(status: str, current_user: UserRead = Depends(get_current_user), 
#                         db: Session = Depends(get_db), _ = Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))):
#     """
#     Retrieve all trips by their status.
#     """
#     trip_repo = TripRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 trips = trip_repo.get_trips_by_status(status)
#             else:
#                 trips = trip_repo.get_trips_by_status(status, tenancy_id=current_user.tenancy_id)
#         return trips
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.get("/user/trips")
# def get_user_trips(current_user: UserRead = Depends(get_current_user), db: Session = Depends(get_db)):
#     try:
#         trip_repo = TripRepository(db)
#         return trip_repo.get_user_trips(current_user)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.get("/trips/{trip_id}/sites", response_model=List[dict])
# def get_trip_sites(trip_id: int, current_user: UserRead = Depends(get_current_user), db: Session = Depends(get_db)):
#     """
#     Get the list of sites associated with the trip.
#     """
#     trip_repo = TripRepository(db)
#     try:
#         sites = trip_repo.get_sites_for_trip(trip_id)
#         return sites
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# @router.post("/record-stage", status_code=status.HTTP_201_CREATED)
# def record_trip_stage(
#     request: RecordStageRequest,
#     background_tasks: BackgroundTasks,
#     current_user: UserRead = Depends(get_current_user), 
#     db: Session = Depends(get_db), _ = Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))):
#     """
#     Record the stage of a trip (arrival, departure, transit) and the mileage.
#     """
#     try:
#         repo = TripRepository(db_session=db)
#         result = repo.record_stage_and_mileage(
#             trip_id=request.trip_id,
#             site_id=request.site_id,
#             mileage_at_arrival=request.mileage,
#             tenancy_id=current_user.tenancy_id
#         )

#         changes = {
#             "trip_id": request.trip_id,
#             "site_id": request.site_id,
#             "mileage_at_arrival": request.mileage,
#             "stage_name": result.get("stage_name")
#         }

#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.UPDATE,
#             "TripStage",
#             0,
#             changes 
#         )

#         return {
#             "message": "Trip stage and mileage recorded successfully.",
#             "details": result
#         }
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTPException: {e.detail}")
#         raise HTTPException(status_code=e.status_code, detail={"error": e.detail, "message": "Failed to record trip stage and mileage. Please check the details and try again."})
#     except Exception as e:
#         logging_helper.log_error(f"Exception: {str(e)}")
#         raise HTTPException(status_code=500, detail={"error": "RECORD_STAGE_AND_MILEAGE", "message": f"An unexpected error occurred: {str(e)}"})


# @router.get("/trips/{trip_id}/status", status_code=status.HTTP_200_OK)
# def get_vehicle_trip_status(trip_id: int, current_user: UserRead = Depends(get_current_user), db: Session = Depends(get_db)):
#     """
#     Get the current status of a vehicle during a trip.
#     """
#     try:
#         trip_repo = TripRepository(db)
#         status = trip_repo.get_vehicle_trip_status(trip_id, current_user.tenancy_id)
#         return status
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"An error occurred while fetching the vehicle status: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"An error occurred while fetching the vehicle status: {str(e)}")
    

# @router.get("/trips/{trip_id}/unvisited-sites", response_model=List[Tuple[int, str]])
# def get_unvisited_sites(
#     trip_id: int,
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db), _ = Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))):
#     """
#     Get the list of unvisited sites for a trip.
#     """
#     try:
#         repo = TripRepository(db_session=db)
#         unvisited_sites = repo.get_unvisited_sites(trip_id=trip_id, tenancy_id=current_user.tenancy_id)
#         return unvisited_sites
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Error while fetching unvisited sites for trip ID: {trip_id}: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch unvisited sites. Please check the details and try again.")




import json
from typing import List, Optional, Tuple
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, status
import sqlalchemy
from sqlalchemy.orm import Session
from auth.dependencies import role_checker
from auth.security import get_current_user
from models.all_models import ActionEnum
from schemas.user_schemas import UserRead
from db.database import get_db  
from schemas.trip_schemas import ArrivalRequest, ArrivalResponse, AssignVehicleDriverRequest, DepartureRequest, DepartureResponse, DropEmployeesFromTripRequest, EmployeeRead, EndTripRequest, GetEmployeesNotInTripRequest, RecordMileageRequest, RecordStageRequest, TripArrivalRequest, TripArrivalResponse, TripSummary
from repositories.trip_repo import TripRepository
from logging_helpers import logging_helper

router = APIRouter()

@router.get("/trip-summary/{trip_id}", response_model=dict)  
def trip_summary(trip_id: int, current_user: UserRead = Depends(get_current_user), 
                 db: Session = Depends(get_db), _ = Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))):
    """
    Retrieve a detailed summary of a specific trip.
    """
    trip_repo = TripRepository(db_session=db)  # Assuming you have a repository class handling DB operations
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                result = trip_repo.get_trip_summary(trip_id)
            else:
                result = trip_repo.get_trip_summary(trip_id, tenancy_id=current_user.tenancy_id)
        if isinstance(result, str):
            raise HTTPException(status_code=404, detail=result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/trips/summaries")  
def get_all_trip_summaries(current_user: UserRead = Depends(get_current_user), 
                           db: Session = Depends(get_db), _ = Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))):
    """
    Retrieves summaries for all trips including details such as employee names, sites, and vehicle information.
    """
    trip_repo = TripRepository(db)  
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                trip_summaries = trip_repo.get_all_trip_summaries()
            else:
                trip_summaries = trip_repo.get_all_trip_summaries(tenancy_id=current_user.tenancy_id)
        return trip_summaries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedule_trip", status_code=status.HTTP_201_CREATED)
def schedule_trip(
    request: AssignVehicleDriverRequest,
    background_tasks: BackgroundTasks,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))
):
    """
    Assign a vehicle and a driver to a set of work plans.
    """
    try:
        repo = TripRepository(db_session=db)
        result = repo.schedule_trip(
            work_plan_ids=request.work_plan_ids,
            employee_ids=request.employee_ids,  # Add employee_ids to the function call
            vehicle_id=request.vehicle_id,
            driver_id=request.driver_id,
            tenancy_id=current_user.tenancy_id,
            auto_group_weekly=request.auto_group_weekly,
            background_tasks=background_tasks
        )
        
        # Capture the changes in a dictionary
        changes = {
            "vehicle_id": request.vehicle_id,
            "driver_id": request.driver_id,
            "work_plan_ids": request.work_plan_ids,
            "employee_ids": request.employee_ids,  # Include employee_ids in the changes
            "auto_group_weekly": request.auto_group_weekly,
            "assigned_trip_ids": result.get("trip_ids", [])
        }
        
        # Log the changes in the audit log
        logging_helper.log_audit(
            db, 
            current_user.id, 
            ActionEnum.SCHEDULE_TRIP, 
            "Trip", 
            0, 
            changes  # Pass the dictionary as the log message
        )
        
        return {
            "message": "Vehicle and driver assigned to work plans successfully.",
            "details": result
        }
    except HTTPException as e:
        logging_helper.log_error(f"HTTPException: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail={"error": e.detail, "message": "Failed to assign vehicle and driver to work plans. Please check the details and try again."})
    except Exception as e:
        logging_helper.log_error(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": "ASSIGN_VEHICLE", "message": f"An unexpected error occurred: {str(e)}"})



@router.post("/trips/{trip_id}/start", summary="Start a Trip")
async def start_trip(trip_id: int, start_location_id: int, start_site_id: int, current_user: UserRead = Depends(get_current_user), 
                     db: Session = Depends(get_db), _ = Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))):
    """
    Start a trip by setting the initial mileage from the vehicle's current mileage and creating the initial trip stage.

    Parameters:
    - trip_id (int): The ID of the trip to be started.
    - start_location_id (int): The ID of the start location for the trip.
    - start_site_id (int): The ID of the first site the vehicle will arrive at.
    - current_user (UserRead): The current authenticated user.
    - db (Session): The database session.
    """
    trip_start_repo = TripRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                # Start the trip without tenancy restriction for super_admin
                trip_start = trip_start_repo.start_trip(trip_id, start_location_id, start_site_id)
                logging_helper.log_audit(db, current_user.id, ActionEnum.START_TRIP, "Trip", trip_id, f"Trip {trip_id} started by super_admin.")
                break
            else:
                # Start the trip with tenancy restriction for other roles
                trip_start = trip_start_repo.start_trip(trip_id, start_location_id, start_site_id, current_user.tenancy_id)
                logging_helper.log_audit(db, current_user.id, ActionEnum.START_TRIP, "Trip", trip_id, f"Trip {trip_id} started by {current_user.username} in tenancy {current_user.tenancy_id}.")
                break
        return trip_start
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trips/{trip_id}/arrival", response_model=TripArrivalResponse)
def record_arrival(
    trip_id: int,
    stage_id:int,
    arrival_request: TripArrivalRequest,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    _ = Depends(role_checker(["super_admin", "driver"]))  # Role checking dependency
):
    """
    Record the arrival of a vehicle at a site.

    Parameters:
    - trip_id: The ID of the trip.
    - arrival_request: The request body containing site_id and mileage_at_arrival.
    - db: The database session.
    - current_user: The current authenticated user.

    Returns:
    - TripArrivalResponse: The response containing the recorded trip stage details.
    """
    try:
        trip_repo = TripRepository(db)
        result = trip_repo.record_site_arrival(
            trip_id=trip_id,
            stage_id = stage_id,
            mileage_at_arrival=arrival_request.mileage_at_arrival,
            tenancy_id=current_user.tenancy_id
        )
        return result
    except HTTPException as e:
        logging_helper.log_error(f"HTTPException while recording arrival: {e}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Exception while recording arrival: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trips/{trip_id}/departure", response_model=DepartureResponse)
def record_departure(
    trip_id: int,
    stage_id:int,
    departure_request: DepartureRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    _ = Depends(role_checker(["super_admin", "driver"]))  # Role checking dependency
):
    """
    Record the departure of a vehicle from a site.

    Parameters:
    - trip_id: The ID of the trip.
    - departure_request: The request body containing site_id and optional next_site_id.
    - db: The database session.
    - current_user: The current authenticated user.
    - _: Role checking dependency to ensure the user has the required roles.

    Returns:
    - DepartureResponse: The response containing the recorded trip stage details.
    """
    try:
        trip_repo = TripRepository(db)
        result = trip_repo.record_site_departure(
            trip_id=trip_id,
            stage_id=stage_id,
            next_site_id=departure_request.next_site_id,
            tenancy_id=current_user.tenancy_id
        )

        # Log audit
        logging_helper.log_audit(
            db_session=db,
            user_id=current_user.id,
            action=ActionEnum.UPDATE,
            model="TripStage",
            model_id=trip_id,
            changes={
                # "site_id": departure_request.site_id,
                "next_site_id": departure_request.next_site_id
            }
        )
        return result
    except HTTPException as e:
        logging_helper.log_error(f"HTTPException while recording departure: {e}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Exception while recording departure: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trips/{trip_id}/end")
def end_trip(
    trip_id: int,
    trip_data: EndTripRequest,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))
):
    """
    Ends a trip with the given ID by updating the mileage at the end and calculating the distance traveled.
    Requires the end mileage and trip_end_location_id to be specified.
    """
    trip_repo = TripRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                end_trip = trip_repo.end_trip(trip_id, trip_data.mileage_end, trip_data.trip_end_location_id)
                changes = {
                    "message": f"Trip {trip_id} ended by super_admin.",
                    "end_mileage": trip_data.mileage_end,
                    "trip_end_location_id": trip_data.trip_end_location_id
                }
                logging_helper.log_audit(db, current_user.id, ActionEnum.END_TRIP, "Trip", trip_id, changes)
                break
            else:
                end_trip = trip_repo.end_trip(trip_id, trip_data.mileage_end, trip_data.trip_end_location_id, current_user.tenancy_id)
                changes = {
                    "message": f"Trip {trip_id} ended by {current_user.username} in tenancy {current_user.tenancy_id}.",
                    "end_mileage": trip_data.mileage_end,
                    "trip_end_location_id": trip_data.trip_end_location_id
                }
                logging_helper.log_audit(db, current_user.id, ActionEnum.END_TRIP, "Trip", trip_id, changes)
                break
        result = end_trip
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-employees-to-existing-trip", status_code=status.HTTP_200_OK)
def add_employees_to_existing_trip(
    existing_trip_id: int,
    additional_work_plan_ids: List[int],
    additional_employee_ids: List[int],
    tenancy_id: Optional[int] = None,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))
):
    """
    Add employees from additional work plans to an existing trip.

    Args:
        existing_trip_id (int): ID of the existing trip.
        additional_work_plan_ids (List[int]): List of additional work plan IDs.
        additional_employee_ids (List[int]): List of additional employee IDs.
        tenancy_id (Optional[int]): ID of the tenancy (optional).

    Returns:
        dict: Message and details of the updated trip.
    """
    try:
        repo = TripRepository(db_session=db)
        result = repo.add_employees_to_existing_trip(
            existing_trip_id=existing_trip_id,
            additional_work_plan_ids=additional_work_plan_ids,
            additional_employee_ids=additional_employee_ids,
            tenancy_id=tenancy_id or current_user.tenancy_id
        )
        return result
    except HTTPException as e:
        logging_helper.log_error(f"HTTPException: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail={"error": e.detail, "message": "Failed to add employees to the existing trip. Please check the details and try again."})
    except Exception as e:
        logging_helper.log_error(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": "ADD_EMPLOYEES", "message": f"An unexpected error occurred: {str(e)}"})


@router.post("/trips/{trip_id}/drop_employees", response_model=dict)
def drop_employees(
    trip_id: int,
    drop_request: DropEmployeesFromTripRequest,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    _ = Depends(role_checker(["super_admin", "driver"]))
):
    """
    Remove employees from a trip.

    Parameters:
    - trip_id: The ID of the trip.
    - drop_request: The request body containing a list of employee IDs to be removed.
    - db: The database session.
    - current_user: The current authenticated user.

    Returns:
    - dict: The response message indicating the result.
    """
    try:
        trip_repo = TripRepository(db)
        result = trip_repo.drop_employees_from_trip(
            trip_id=trip_id,
            employee_ids=drop_request.employee_ids,
            tenancy_id=current_user.tenancy_id
        )
        return result
    except HTTPException as e:
        logging_helper.log_error(f"HTTPException while removing employees from trip: {e}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Exception while removing employees from trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get-employees-not-in-trip", status_code=status.HTTP_200_OK)
def get_employees_not_in_trip(
    request: GetEmployeesNotInTripRequest,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))
):
    """
    Get all employees from selected work plans who are yet to be added to a Trip.

    Args:
        request (GetEmployeesNotInTripRequest): Request payload containing work_plan_ids.
        current_user (UserRead): Current authenticated user.
        db (Session): Database session.
        _ : Role checker dependency.

    Returns:
        List[dict]: List of employees with their details who are yet to be added to a Trip.
    """
    try:
        repo = TripRepository(db_session=db)
        result = repo.get_employees_not_in_trip(
            work_plan_ids=request.work_plan_ids,
            tenancy_id=current_user.tenancy_id
        )
        return result
    except HTTPException as e:
        logging_helper.log_error(f"HTTPException: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail={"error": e.detail, "message": "Failed to fetch employees not in any trip. Please check the details and try again."})
    except Exception as e:
        logging_helper.log_error(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": "GET_EMPLOYEES_NOT_IN_TRIP", "message": f"An unexpected error occurred: {str(e)}"})


@router.post("/employees-associated-with-workplans", response_model=List[EmployeeRead], status_code=status.HTTP_200_OK)
def employees_associated_with_workplans(
    work_plan_ids: List[int],
    tenancy_id: Optional[int] = None,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))
):
    """
    Fetch employees associated with selected work plans.

    Args:
        work_plan_ids (List[int]): List of work plan IDs.
        tenancy_id (Optional[int]): ID of the tenancy (optional).

    Returns:
        List[EmployeeRead]: List of employees associated with the work plans.
    """
    try:
        repo = TripRepository(db_session=db)
        employees = repo.get_employees_associated_with_workplans(work_plan_ids=work_plan_ids, tenancy_id=tenancy_id)
        return employees
    except HTTPException as e:
        logging_helper.log_error(f"HTTPException: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail={"error": e.detail, "message": "Failed to fetch employees associated with work plans. Please check the details and try again."})
    except Exception as e:
        logging_helper.log_error(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": "FETCH_EMPLOYEES", "message": f"An unexpected error occurred: {str(e)}"})


@router.get("/trips-by-status/{status}", response_model=List[TripSummary])
def get_trips_by_status(status: str, current_user: UserRead = Depends(get_current_user), 
                        db: Session = Depends(get_db), _ = Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))):
    """
    Retrieve all trips by their status.
    """
    trip_repo = TripRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                trips = trip_repo.get_trips_by_status(status)
            else:
                trips = trip_repo.get_trips_by_status(status, tenancy_id=current_user.tenancy_id)
        return trips
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/trips")
def get_user_trips(current_user: UserRead = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        trip_repo = TripRepository(db)
        return trip_repo.get_user_trips(current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trips/{trip_id}/sites", response_model=List[dict])
def get_trip_sites(trip_id: int, current_user: UserRead = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get the list of sites associated with the trip.
    """
    trip_repo = TripRepository(db)
    try:
        sites = trip_repo.get_sites_for_trip(trip_id)
        return sites
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/record-stage", status_code=status.HTTP_201_CREATED)
def record_trip_stage(
    request: RecordStageRequest,
    background_tasks: BackgroundTasks,
    current_user: UserRead = Depends(get_current_user), 
    db: Session = Depends(get_db), _ = Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))):
    """
    Record the stage of a trip (arrival, departure, transit) and the mileage.
    """
    try:
        repo = TripRepository(db_session=db)
        result = repo.record_stage_and_mileage(
            trip_id=request.trip_id,
            site_id=request.site_id,
            mileage_at_arrival=request.mileage,
            tenancy_id=current_user.tenancy_id
        )

        changes = {
            "trip_id": request.trip_id,
            "site_id": request.site_id,
            "mileage_at_arrival": request.mileage,
            "stage_name": result.get("stage_name")
        }

        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.UPDATE,
            "TripStage",
            0,
            changes 
        )

        return {
            "message": "Trip stage and mileage recorded successfully.",
            "details": result
        }
    except HTTPException as e:
        logging_helper.log_error(f"HTTPException: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail={"error": e.detail, "message": "Failed to record trip stage and mileage. Please check the details and try again."})
    except Exception as e:
        logging_helper.log_error(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": "RECORD_STAGE_AND_MILEAGE", "message": f"An unexpected error occurred: {str(e)}"})


@router.get("/trips/{trip_id}/status", status_code=status.HTTP_200_OK)
def get_vehicle_trip_status(trip_id: int, current_user: UserRead = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get the current status of a vehicle during a trip.
    """
    try:
        trip_repo = TripRepository(db)
        status = trip_repo.get_vehicle_trip_status(trip_id, current_user.tenancy_id)
        return status
    except HTTPException as e:
        raise e
    except Exception as e:
        logging_helper.log_error(f"An error occurred while fetching the vehicle status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching the vehicle status: {str(e)}")
    

@router.get("/trips/{trip_id}/unvisited-sites", response_model=List[Tuple[int, str]])
def get_unvisited_sites(
    trip_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db), _ = Depends(role_checker(['driver', 'chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))):
    """
    Get the list of unvisited sites for a trip.
    """
    try:
        repo = TripRepository(db_session=db)
        unvisited_sites = repo.get_unvisited_sites(trip_id=trip_id, tenancy_id=current_user.tenancy_id)
        return unvisited_sites
    except HTTPException as e:
        raise e
    except Exception as e:
        logging_helper.log_error(f"Error while fetching unvisited sites for trip ID: {trip_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch unvisited sites. Please check the details and try again.")
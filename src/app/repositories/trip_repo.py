

# from fastapi import HTTPException, BackgroundTasks
# import sqlalchemy
# from sqlalchemy.orm import Session, aliased, joinedload
# from sqlalchemy.exc import IntegrityError, SQLAlchemyError
# from sqlalchemy import func  # Import func for date comparison
# from datetime import datetime
# from datetime import datetime, date, timezone
# from auth.email import notify_trip_creation, send_driver_trip_details
# from auth.message import send_whatsapp_message

# from models.all_models import (
#     SRT,
#     Department,
#     Driver,
#     Employee,
#     Site,
#     ThematicArea,
#     TripSpecialLocation,
#     Unit,
#     User,
#     Trip,
#     Vehicle,
#     WorkPlan,
#     WorkPlanSource,
#     TripStage,
#     workplan_employee_association,
#     trip_workplan_association,
#     workplan_site_association,
#     trip_employee_association,
    
# )
# from schemas.user_schemas import UserRead
# from typing import List, Optional
# from logging_helpers import logging_helper


# class TripRepository:
#     def __init__(self, db_session: Session):
#         self.db_session = db_session

#     def generate_trip_code(self, trip: Trip) -> str:
#         try:
#             trip_code = f"TRP-{trip.id}-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M')}"
#             logging_helper.log_info(f"Trip Code Created: {trip_code} for Trip ID: {trip.id}")
#             return trip_code
#         except Exception as e:
#             logging_helper.log_error(f"Error Generating Trip Code for Trip ID: {trip.id}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error Generating Trip Code: {e}")

#     def fetch_vehicle_and_driver(self, vehicle_id: int, driver_id: int):
#         try:
#             vehicle = self.db_session.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.is_available == True).first()
#             driver = self.db_session.query(Driver).filter(Driver.id == driver_id, Driver.is_available == True).first()

#             if not vehicle:
#                 logging_helper.log_error(f"Selected vehicle ID: {vehicle_id} is not available.")
#                 raise HTTPException(status_code=400, detail="Selected vehicle is not available.")
#             if not driver:
#                 logging_helper.log_error(f"Selected driver ID: {driver_id} is not available.")
#                 raise HTTPException(status_code=400, detail="Selected driver is not available.")

#             logging_helper.log_info(f"Fetched vehicle ID: {vehicle_id} and driver ID: {driver_id}")
#             return vehicle, driver
#         except Exception as e:
#             logging_helper.log_error(f"Error fetching vehicle ID: {vehicle_id} and driver ID: {driver_id}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error fetching vehicle and driver: {e}")

#     def fetch_work_plan(self, work_plan_id: int):
#         try:
#             work_plan = self.db_session.query(WorkPlan).filter(WorkPlan.id == work_plan_id).first()
#             if not work_plan:
#                 logging_helper.log_error(f"Work plan ID: {work_plan_id} does not exist.")
#                 raise HTTPException(status_code=404, detail="Work plan does not exist.")
#             if not work_plan.is_approved:
#                 logging_helper.log_error(f"Work plan ID: {work_plan_id} has not been approved.")
#                 raise HTTPException(status_code=400, detail="Work plan has not been approved.")

#             logging_helper.log_info(f"Fetched work plan ID: {work_plan_id}")
#             return work_plan
#         except Exception as e:
#             logging_helper.log_error(f"Error fetching work plan ID: {work_plan_id}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error fetching work plan: {e}")

#     def fetch_weekly_work_plans(self, work_plan: WorkPlan):
#         try:
#             start_of_week = work_plan.activity_date - datetime.timedelta(days=work_plan.activity_date.weekday())
#             end_of_week = start_of_week + datetime.timedelta(days=6)

#             if work_plan.group_id:
#                 weekly_work_plans = self.db_session.query(WorkPlan).filter(
#                     WorkPlan.group_id == work_plan.group_id,
#                     WorkPlan.activity_date >= start_of_week,
#                     WorkPlan.activity_date <= end_of_week,
#                     WorkPlan.is_approved == True,
#                 ).all()
#             else:
#                 weekly_work_plans = [work_plan]

#             if not weekly_work_plans:
#                 logging_helper.log_error(f"No eligible work plans found for the week for group ID: {work_plan.group_id}")
#                 raise HTTPException(status_code=404, detail="No eligible work plans found for the week.")

#             logging_helper.log_info(f"Fetched weekly work plans for work plan ID: {work_plan.id}")
#             return weekly_work_plans
#         except Exception as e:
#             logging_helper.log_error(f"Error fetching weekly work plans for work plan ID: {work_plan.id}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error fetching weekly work plans: {e}")

#     def notify_employees(self, background_tasks: BackgroundTasks, trip, plan, driver, vehicle):
#         try:
#             employee_emails = [(emp.first_name, emp.employee_email) for emp in plan.employees if emp.employee_email]
#             background_tasks.add_task(
#                 notify_trip_creation,
#                 employee_emails,
#                 trip.start_time,
#                 f"{driver.user.employee.first_name} {driver.user.employee.last_name}",
#                 driver.licence_number,
#                 vehicle.name,
#                 vehicle.licence_plate,
#                 plan.activity_date.strftime("%Y-%m-%d"),
#             )
#             logging_helper.log_info(f"Notified employees about trip {trip.trip_code}")
#         except Exception as e:
#             logging_helper.log_error(f"Error notifying employees about trip {trip.trip_code}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error notifying employees: {e}")

#     def create_trip(self, driver, vehicle, plan):
#         try:
#             trip = Trip(
#                 driver_id=driver.id,
#                 start_time=plan.activity_start_time,
#                 tenancy_id=plan.tenancy_id,
#                 trip_code=self.generate_trip_code(),
#                 vehicle_id=vehicle.id,
#                 start_location=plan.start_location,
#             )
#             self.db_session.add(trip)
#             self.db_session.flush()
#             self.db_session.execute(trip_workplan_association.insert().values(trip_id=trip.id, work_plan_id=plan.id))
#             logging_helper.log_info(f"Created trip {trip.trip_code} for work plan ID: {plan.id}")
#             return trip
#         except IntegrityError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"IntegrityError while creating trip for work plan ID: {plan.id}: {e}")
#             raise HTTPException(status_code=400, detail=str(e))
#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error creating trip for work plan ID: {plan.id}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error creating trip: {e}")

#     def create_and_assign_weekly_trips(self, background_tasks: BackgroundTasks, work_plan_id: int, num_teams: int, vehicle_id: int, driver_id: int):
#         try:
#             logging_helper.log_info(f"Starting weekly trip assignment for work plan ID: {work_plan_id}")
#             work_plan = self.fetch_work_plan(work_plan_id)
#             weekly_work_plans = self.fetch_weekly_work_plans(work_plan)
#             vehicle, driver = self.fetch_vehicle_and_driver(vehicle_id, driver_id)

#             for plan in weekly_work_plans:
#                 try:
#                     trip = self.create_trip(driver, vehicle, plan)
#                     self.notify_employees(background_tasks, trip, plan, driver, vehicle)
#                 except IntegrityError as e:
#                     logging_helper.log_error(f"IntegrityError while assigning trip to work plan ID: {plan.id}: {e}")
#                     continue

#             vehicle.is_available = False
#             driver.is_available = False
#             self.db_session.commit()
#             logging_helper.log_info("Trips for the week have been successfully assigned.")
#             return "Trips for the week have been successfully assigned."
#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error creating and assigning weekly trips for work plan ID: {work_plan_id}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error creating and assigning weekly trips: {e}")


#     def schedule_trip(
#         self,
#         work_plan_ids: list,
#         employee_ids: list,
#         vehicle_id: int,
#         driver_id: int,
#         tenancy_id: int,
#         auto_group_weekly: bool,
#         background_tasks: BackgroundTasks
#     ):
#         """
#         Assigns a vehicle and driver to a list of work plans, ensuring that employees are mapped to the vehicle until it is filled up.
#         It also handles WhatsApp and email notifications and retries sending messages in case of failures.

#         Args:
#             work_plan_ids (list): List of work plan IDs to be assigned.
#             employee_ids (list): List of employee IDs to be assigned.
#             vehicle_id (int): ID of the vehicle to be assigned.
#             driver_id (int): ID of the driver to be assigned.
#             tenancy_id (int): ID of the tenancy.
#             auto_group_weekly (bool): Flag to determine if work plans should be auto-grouped weekly.
#             background_tasks: Background tasks for sending notifications.

#         Returns:
#             dict: Message, details of the created or updated trips, list of employees already associated with a trip for the day, 
#                 and list of employees not assigned to the provided work plans.

#         Raises:
#             HTTPException: If there are any errors during the assignment process.
#         """
#         try:
#             logging_helper.log_info(f"Assigning vehicle ID: {vehicle_id} and driver ID: {driver_id} to work plans: {work_plan_ids}")

#             # Fetch the vehicle and driver, ensuring they belong to the specified tenancy
#             vehicle = self.db_session.query(Vehicle).filter_by(id=vehicle_id, tenancy_id=tenancy_id).first()
#             driver = self.db_session.query(Driver).filter_by(id=driver_id, tenancy_id=tenancy_id).first()

#             # Check if the vehicle and driver are available
#             if not vehicle or not driver:
#                 logging_helper.log_error("Vehicle or driver is not available.")
#                 raise HTTPException(status_code=400, detail="Vehicle or driver is not available.")

#             # Check if the driver has any active trips
#             active_trip = self.db_session.query(Trip).filter_by(driver_id=driver.id, end_time=None, tenancy_id=tenancy_id).first()
#             if active_trip and active_trip.actual_start_time is not None:
#                 logging_helper.log_error("Driver is already on another active trip.")
#                 raise HTTPException(status_code=400, detail="Driver is already on another active trip.")

#             # Fetch approved work plans with activity dates not in the past
#             work_plans = self.db_session.query(WorkPlan).filter(
#                 WorkPlan.id.in_(work_plan_ids),
#                 WorkPlan.is_approved == True,
#                 WorkPlan.tenancy_id == tenancy_id,
#                 WorkPlan.activity_date >= date.today(),
#             ).all()

#             if not work_plans:
#                 logging_helper.log_info("No approved WorkPlans found or The Activity date for this Workplan is past.")
#                 raise HTTPException(status_code=404, detail="No approved WorkPlans found or The Activity date for this Workplan is past.")

#             # Ensure all work plans have the same activity date
#             if len(set(wp.activity_date for wp in work_plans)) > 1:
#                 logging_helper.log_info("All work plans must have the same activity date.")
#                 raise HTTPException(status_code=400, detail="All work plans must have the same activity date.")

#             # Ensure all employee IDs are associated with the provided work plans
#             valid_employee_ids = []
#             employees_not_assigned_to_workplan = []
#             for wp in work_plans:
#                 valid_employee_ids.extend([emp.id for emp in wp.employees])

#             for emp_id in employee_ids:
#                 if emp_id not in valid_employee_ids:
#                     employees_not_assigned_to_workplan.append(emp_id)

#             if employees_not_assigned_to_workplan:
#                 logging_helper.log_error("Some employees are not associated with the provided work plans.")
#                 raise HTTPException(status_code=400, detail="Some employees are not associated with the provided work plans.")

#             # Filter out employees who already have trips scheduled for the same day
#             employees_not_in_trip = []
#             employees_in_another_trip = []
#             for emp_id in valid_employee_ids:
#                 # Fetch all trips that an employee is associated with, which occur on the same day
#                 existing_trip = (
#                     self.db_session.query(trip_employee_association)
#                     .join(Trip)
#                     .filter(
#                         trip_employee_association.c.employee_id == emp_id,
#                         func.date(Trip.start_time) == work_plans[0].activity_date  # Use func.date to extract the date part
#                     )
#                     .first()
#                 )
#                 if existing_trip:
#                     employees_in_another_trip.append(emp_id)
#                 else:
#                     employees_not_in_trip.append(emp_id)

#             if not employees_not_in_trip:
#                 logging_helper.log_info("All employees already have trips scheduled for the day.")
#                 raise HTTPException(status_code=400, detail="All employees already have trips scheduled for the day.")

#             grouped_work_plans = work_plans
#             if auto_group_weekly:
#                 group_ids = {wp.group_id for wp in work_plans}
#                 grouped_work_plans = self.db_session.query(WorkPlan).filter(
#                     WorkPlan.group_id.in_(group_ids),
#                     WorkPlan.tenancy_id == tenancy_id,
#                     WorkPlan.is_approved == True,
#                     WorkPlan.activity_date >= date.today(),
#                 ).all()

#             # Group work plans by activity date
#             date_grouped_workplans = {}
#             for wp in grouped_work_plans:
#                 if wp.activity_date not in date_grouped_workplans:
#                     date_grouped_workplans[wp.activity_date] = []
#                 date_grouped_workplans[wp.activity_date].append(wp)

#             trip_ids = []
#             trip_details_list = []

#             # Assign employees to vehicles until the vehicle is full
#             remaining_employee_ids = employees_not_in_trip.copy()
#             start_trip_time = datetime.combine(grouped_work_plans[0].activity_date, grouped_work_plans[0].activity_start_time)

#             while remaining_employee_ids:
#                 trip = Trip(
#                     driver_id=driver.id,
#                     vehicle_id=vehicle_id,
#                     start_time=start_trip_time,
#                     tenancy_id=tenancy_id,
#                 )
#                 self.db_session.add(trip)
#                 self.db_session.flush()
#                 trip_ids.append(trip.id)

#                 remaining_capacity = vehicle.seat_capacity
#                 assigned_employee_ids = []

#                 for emp_id in remaining_employee_ids:
#                     if remaining_capacity > 0:
#                         for wp in grouped_work_plans:
#                             if emp_id in [emp.id for emp in wp.employees]:
#                                 # Check if the association already exists
#                                 existing_association = self.db_session.query(trip_workplan_association).filter_by(trip_id=trip.id, work_plan_id=wp.id).one_or_none()
#                                 if not existing_association:
#                                     self.db_session.execute(trip_workplan_association.insert().values(trip_id=trip.id, work_plan_id=wp.id))

#                                 existing_employee_association = self.db_session.query(trip_employee_association).filter_by(trip_id=trip.id, employee_id=emp_id).one_or_none()
#                                 if not existing_employee_association:
#                                     self.db_session.execute(trip_employee_association.insert().values(trip_id=trip.id, employee_id=emp_id))
                                
#                                 remaining_capacity -= 1
#                                 assigned_employee_ids.append(emp_id)
#                                 break
#                     else:
#                         break

#                 remaining_employee_ids = [emp_id for emp_id in remaining_employee_ids if emp_id not in assigned_employee_ids]

#                 workplan_codes = [wp.workplan_code for wp in grouped_work_plans if any(emp.id in assigned_employee_ids for emp in wp.employees)]
#                 trip_details_list.append({"trip_id": trip.id, "workplan_codes": workplan_codes})

#             # Check if all employees in the work plans are assigned to trips
#             for wp in grouped_work_plans:
#                 wp_employee_ids = [emp.id for emp in wp.employees]
#                 assigned_emp_ids = [emp_id for emp_id in employee_ids if emp_id in wp_employee_ids]
                
#                 # Set vehicle_assigned to True only if all employees are mapped
#                 if set(wp_employee_ids) == set(assigned_emp_ids):
#                     wp.status = "Scheduled"
#                     wp.vehicle_assigned = True
#                 else:
#                     wp.vehicle_assigned = False

#             vehicle.is_available = driver.is_available = False
#             self.db_session.commit()

#             driver_name = f"{driver.user.employee.first_name} {driver.user.employee.last_name}"
#             passengers = ", ".join([f"{emp.first_name} {emp.last_name}" for emp_id in employees_not_in_trip for emp in self.db_session.query(Employee).filter(Employee.id == emp_id)])
#             location_details = ", ".join(set(wp.activity_title for wp in grouped_work_plans))

#             trip_info = {
#                 "take_off_time": trip.start_time.strftime("%H:%M %p"),
#                 "driver_name": driver_name,
#                 "vehicle_info": f"{vehicle.make} {vehicle.licence_plate}",
#             }
#             employee_emails = [(emp.first_name, emp.employee_email) for emp_id in employees_not_in_trip for emp in self.db_session.query(Employee).filter(Employee.id == emp_id)]
#             employee_phone_numbers = [emp.phone_number for emp_id in employees_not_in_trip for emp in self.db_session.query(Employee).filter(Employee.id == emp_id)]
            
#             logging_helper.log_info("Started sending email asynchronously to the employees and the driver involved in the trip...")
#             for attempt in range(3):  # Try up to 3 times
#                 try:
#                     background_tasks.add_task(notify_trip_creation, employee_emails, trip.start_time, driver_name, driver.licence_number, vehicle.name, vehicle.licence_plate, location_details, trip.start_time.strftime("%Y-%m-%d"))
#                     background_tasks.add_task(send_driver_trip_details, driver.user.email, driver_name, vehicle.name, vehicle.licence_plate, passengers, trip.start_time.strftime("%H:%M %p"), location_details, trip.start_time.strftime("%Y-%m-%d"))

#                     # WhatsApp notifications
#                     for phone_number in employee_phone_numbers:
#                         background_tasks.add_task(
#                             send_whatsapp_message, 
#                             phone_number, 
#                             f"Your trip is scheduled for {trip_info['take_off_time']}. Driver: {trip_info['driver_name']}, Vehicle: {trip_info['vehicle_info']}"
#                         )
#                     break  # Exit the loop if successful
#                 except Exception as e:
#                     logging_helper.log_error(f"Attempt {attempt + 1} failed: {e}")
#                     if attempt == 2:  # If this was the last attempt
#                         raise HTTPException(status_code=500, detail="Failed to send notifications after multiple attempts.")

#             logging_helper.log_info(f"Trips created or updated successfully: {trip_ids}")
#             return {
#                 "message": "Trips created and vehicle and driver assigned successfully.",
#                 "trip_ids": trip_ids,
#                 "trip_details": trip_details_list,
#                 "employees_in_another_trip": employees_in_another_trip,
#                 "employees_not_assigned_to_workplan": employees_not_assigned_to_workplan,
#             }
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"SQLAlchemyError while assigning vehicle and driver to work plans: {work_plan_ids}: {e}")
#             raise HTTPException(status_code=500, detail=f"SQLAlchemyError while assigning vehicle and driver to work plans: {work_plan_ids}: {e}")
#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error while assigning vehicle and driver to work plans: {work_plan_ids}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error while assigning vehicle and driver to work plans: {e}")

#     def add_employees_to_existing_trip(
#         self,
#         existing_trip_id: int,
#         additional_work_plan_ids: List[int],
#         additional_employee_ids: List[int],
#         tenancy_id: int,
#     ):
#         """
#         Adds employees from additional work plans to an existing trip, ensuring the vehicle is not fully utilized
#         and the employees are going to the same location or site.

#         Args:
#             existing_trip_id (int): ID of the existing trip.
#             additional_work_plan_ids (List[int]): List of additional work plan IDs.
#             additional_employee_ids (List[int]): List of additional employee IDs.
#             tenancy_id (int): ID of the tenancy.

#         Returns:
#             dict: Message and details of the updated trip.

#         Raises:
#             HTTPException: If there are any errors during the process.
#         """
#         try:
#             logging_helper.log_info(f"Adding employees to existing trip ID: {existing_trip_id}")

#             # Fetch the existing trip
#             trip = self.db_session.query(Trip).filter_by(id=existing_trip_id, tenancy_id=tenancy_id).first()
#             if not trip:
#                 logging_helper.log_error(f"Trip ID {existing_trip_id} not found.")
#                 raise HTTPException(status_code=404, detail=f"Trip ID {existing_trip_id} not found.")

#             # Fetch the associated vehicle and check its remaining capacity
#             vehicle = trip.vehicle
#             remaining_capacity = vehicle.seat_capacity - len(trip.employees)

#             if remaining_capacity <= 0:
#                 logging_helper.log_info("The vehicle for this trip is already fully utilized.")
#                 raise HTTPException(status_code=400, detail="The vehicle for this trip is already fully utilized.")

#             # Fetch the additional work plans and validate their association with the same site/location
#             additional_work_plans = self.db_session.query(WorkPlan).filter(
#                 WorkPlan.id.in_(additional_work_plan_ids),
#                 WorkPlan.tenancy_id == tenancy_id,
#                 WorkPlan.is_approved == True,
#                 WorkPlan.activity_date == trip.start_time.date()
#             ).all()

#             if not additional_work_plans:
#                 logging_helper.log_error("No valid additional work plans found.")
#                 raise HTTPException(status_code=404, detail="No valid additional work plans found.")

#             # Validate employees' association with provided work plans
#             valid_employee_ids = []
#             for wp in additional_work_plans:
#                 valid_employee_ids.extend([emp.id for emp in wp.employees])

#             if not all(emp_id in valid_employee_ids for emp_id in additional_employee_ids):
#                 logging_helper.log_error("Some employees are not associated with the provided work plans.")
#                 raise HTTPException(status_code=400, detail="Some employees are not associated with the provided work plans.")

#             # Ensure employees are going to the same site/location as the trip
#             trip_sites = {site.id for site in trip.work_plans[0].sites}
#             for wp in additional_work_plans:
#                 if not any(site.id in trip_sites for site in wp.sites):
#                     logging_helper.log_info("Work plan sites do not match the trip's site.")
#                     raise HTTPException(status_code=400, detail="Work plan sites do not match the trip's site.")

#             # Add employees to the trip until the vehicle is full
#             assigned_employee_ids = []
#             for emp_id in additional_employee_ids:
#                 if remaining_capacity > 0:
#                     self.db_session.execute(trip_employee_association.insert().values(trip_id=trip.id, employee_id=emp_id))
#                     remaining_capacity -= 1
#                     assigned_employee_ids.append(emp_id)
#                 else:
#                     break

#             # Update work plans association with the trip
#             for wp in additional_work_plans:
#                 if not self.db_session.query(trip_workplan_association).filter_by(trip_id=trip.id, work_plan_id=wp.id).one_or_none():
#                     self.db_session.execute(trip_workplan_association.insert().values(trip_id=trip.id, work_plan_id=wp.id))

#             self.db_session.commit()

#             logging_helper.log_info(f"Employees added to trip ID: {trip.id}")
#             return {
#                 "message": "Employees added to the existing trip successfully.",
#                 "trip_id": trip.id,
#                 "assigned_employee_ids": assigned_employee_ids
#             }
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"SQLAlchemyError while adding employees to existing trip: {e}")
#             raise HTTPException(status_code=500, detail=f"SQLAlchemyError while adding employees to existing trip: {e}")
#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error while adding employees to existing trip: {e}")
#             raise HTTPException(status_code=500, detail=f"Error while adding employees to existing trip: {e}")

#     def drop_employees_from_trip(
#         self, 
#         trip_id: int, 
#         employee_ids: List[int], 
#         tenancy_id: Optional[int] = None
#     ):
#         try:
#             logging_helper.log_info(f"Removing employees from trip ID: {trip_id}")

#             trip_query = self.db_session.query(Trip).filter_by(id=trip_id)
#             if tenancy_id:
#                 trip_query = trip_query.filter(Trip.tenancy_id == tenancy_id)
#             trip = trip_query.first()

#             if not trip:
#                 logging_helper.log_error(f"Trip not found with ID: {trip_id}")
#                 raise HTTPException(status_code=404, detail="Trip not found.")

#             for employee_id in employee_ids:
#                 association = self.db_session.query(trip_employee_association).filter_by(trip_id=trip_id, employee_id=employee_id).first()
#                 if association:
#                     self.db_session.delete(association)

#             self.db_session.commit()

#             logging_helper.log_info(f"Removed employees from trip ID: {trip_id}")

#             return {"message": "Employees removed from trip successfully."}
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"SQLAlchemyError while removing employees from trip ID: {trip_id}: {e}")
#             raise HTTPException(status_code=500, detail=f"SQLAlchemyError: {str(e)}")
#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error while removing employees from trip ID: {trip_id}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error removing employees from trip: {e}")


#     def get_employees_not_in_trip(self, work_plan_ids: List[int], tenancy_id: Optional[int] = None) -> List[dict]:
#         """
#         Get all employees from selected work plans who are yet to be added to a Trip.

#         Args:
#             work_plan_ids (List[int]): List of work plan IDs to check.
#             tenancy_id (Optional[int]): ID of the tenancy (optional).

#         Returns:
#             List[dict]: List of employees with their details who are yet to be added to a Trip.
#         """
#         try:
#             logging_helper.log_info(f"Fetching employees not in any trip for work plans: {work_plan_ids}")

#             # Fetch approved work plans with activity dates not in the past
#             work_plans = self.db_session.query(WorkPlan).filter(
#                 WorkPlan.id.in_(work_plan_ids),
#                 WorkPlan.is_approved == True,
#                 WorkPlan.activity_date >= date.today(),
#                 (WorkPlan.tenancy_id == tenancy_id) if tenancy_id else True
#             ).all()

#             if not work_plans:
#                 logging_helper.log_info("No approved WorkPlans found or The Activity date for these Workplans is past.")
#                 return []

#             # Fetch employees associated with the given work plans
#             employees = self.db_session.query(Employee).join(workplan_employee_association).join(WorkPlan).filter(
#                 WorkPlan.id.in_([wp.id for wp in work_plans])
#             ).all()

#             if not employees:
#                 logging_helper.log_info("No employees found for the provided work plans.")
#                 return []

#             # Get employees who are not in any trips
#             employees_not_in_trip = []
#             for emp in employees:
#                 if not self.db_session.query(trip_employee_association).filter_by(employee_id=emp.id).first():
#                     emp_work_plan_ids = [wp.id for wp in emp.work_plans if wp.id in work_plan_ids]
#                     employees_not_in_trip.append({
#                         "employee_id": emp.id,
#                         "full_name": f"{emp.first_name} {emp.last_name}",
#                         "work_plan_ids": emp_work_plan_ids
#                     })

#             logging_helper.log_info(f"Found {len(employees_not_in_trip)} employees not in any trip.")
#             return employees_not_in_trip

#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"SQLAlchemyError while fetching employees not in any trip: {e}")
#             raise HTTPException(status_code=500, detail=f"SQLAlchemyError while fetching employees not in any trip: {e}")
#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error while fetching employees not in any trip: {e}")
#             raise HTTPException(status_code=500, detail=f"Error while fetching employees not in any trip: {e}")


#     def get_employees_associated_with_workplans(self, work_plan_ids: list, tenancy_id: int = None):
#         """
#         Returns a list of employees associated with the selected work plans.

#         Args:
#             work_plan_ids (list): List of work plan IDs.
#             tenancy_id (int, optional): ID of the tenancy.

#         Returns:
#             list: List of employees associated with the work plans.

#         Raises:
#             HTTPException: If there are any errors during the retrieval process.
#         """
#         try:
#             logging_helper.log_info(f"Fetching employees associated with work plans: {work_plan_ids}")

#             # Fetch approved work plans with activity dates not in the past
#             query = self.db_session.query(WorkPlan).filter(
#                 WorkPlan.id.in_(work_plan_ids),
#                 WorkPlan.is_approved == True,
#                 WorkPlan.activity_date >= date.today(),
#             )

#             if tenancy_id is not None:
#                 query = query.filter(WorkPlan.tenancy_id == tenancy_id)

#             work_plans = query.all()

#             if not work_plans:
#                 logging_helper.log_info("No approved WorkPlans found or The Activity date for this Workplan is past.")
#                 raise HTTPException(status_code=404, detail="No approved WorkPlans found or The Activity date for this Workplan is past.")

#             # Retrieve employees associated with the selected work plans
#             employees = []
#             for wp in work_plans:
#                 employees.extend(wp.employees)

#             # Ensure employees are unique
#             unique_employees = {emp.id: emp for emp in employees}.values()

#             # Prepare the result
#             employee_list = [
#                 {
#                     "id": emp.id,
#                     "first_name": emp.first_name,
#                     "last_name": emp.last_name,
#                     "full_name": f"{emp.first_name} {emp.last_name}",
#                     "email": emp.employee_email,
#                     "phone_number": emp.phone_number
#                 }
#                 for emp in unique_employees
#             ]

#             logging_helper.log_info(f"Successfully fetched employees associated with work plans: {work_plan_ids}")
#             return employee_list

#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"SQLAlchemyError while fetching employees associated with work plans: {work_plan_ids}: {e}")
#             raise HTTPException(status_code=500, detail=f"SQLAlchemyError while fetching employees associated with work plans: {work_plan_ids}: {e}")
#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error while fetching employees associated with work plans: {work_plan_ids}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error while fetching employees associated with work plans: {e}")


#     def get_trip_summary(self, trip_id: int, tenancy_id: Optional[int] = None):
#         try:
#             logging_helper.log_info(f"Fetching trip summary for trip ID: {trip_id}")
#             srt_alias = aliased(SRT)
#             unit_alias = aliased(Unit)
#             department_alias = aliased(Department)
#             thematic_area_alias = aliased(ThematicArea)
#             workplan_source_alias = aliased(WorkPlanSource)

#             implementing_team = sqlalchemy.case(
#                 (WorkPlan.initiating_srt_id != None, srt_alias.name),
#                 (WorkPlan.initiating_unit_id != None, unit_alias.name),
#                 (WorkPlan.initiating_department_id != None, department_alias.name),
#                 (WorkPlan.initiating_thematic_area_id != None, thematic_area_alias.name),
#                 else_="Unknown",
#             ).label("implementing_team")

#             query = self.db_session.query(
#                 Trip,
#                 implementing_team,
#                 workplan_source_alias.name.label("workplan_source_name"),
#             ).select_from(Trip).join(Trip.driver).join(Trip.vehicle).join(Trip.work_plans).outerjoin(
#                 srt_alias, WorkPlan.initiating_srt_id == srt_alias.id).outerjoin(
#                 unit_alias, WorkPlan.initiating_unit_id == unit_alias.id).outerjoin(
#                 department_alias, WorkPlan.initiating_department_id == department_alias.id).outerjoin(
#                 thematic_area_alias, WorkPlan.initiating_thematic_area_id == thematic_area_alias.id).join(
#                 workplan_source_alias, WorkPlan.workplan_source_id == workplan_source_alias.id).filter(Trip.id == trip_id)

#             if tenancy_id:
#                 query = query.filter(Trip.tenancy_id == tenancy_id)

#             trip_data = query.first()

#             if not trip_data:
#                 logging_helper.log_error(f"No trip found with ID: {trip_id}")
#                 return "No trip found with the given ID."

#             trip, team, source_name = trip_data

#             employees = [f"{emp.first_name} {emp.last_name}" for wp in trip.work_plans for emp in wp.employees]
#             locations = list(set(loc.name for wp in trip.work_plans for loc in wp.locations))
#             sites = list(set(site.name for wp in trip.work_plans for site in wp.sites))

#             trip_lead = next(
#                 (f"{lead.activity_lead.first_name} {lead.activity_lead.last_name}" for lead in trip.work_plans if lead.activity_lead),
#                 "No lead assigned",
#             )
#             driver_name = f"{trip.driver.user.employee.first_name} {trip.driver.user.employee.last_name}" if trip.driver and trip.driver.user and trip.driver.user.employee else "Driver details not available"
#             formatted_actual_start_time = trip.actual_start_time.strftime("%H:%M %p") if trip.actual_start_time else "Not started"

#             trip_details = {
#                 "trip_id": trip.id,
#                 "activity_title": next((wp.activity_title for wp in trip.work_plans), "No title"),
#                 "workplan_code": next((wp.workplan_code for wp in trip.work_plans if wp.workplan_code), "No code"),
#                 "trip_start_time": trip.start_time.strftime("%H:%M %p") if trip.start_time else "No start time",
#                 "actual_start_time": formatted_actual_start_time,
#                 "activity_date": min(wp.activity_date for wp in trip.work_plans).strftime("%Y-%m-%d"),
#                 "workplan_source_name": source_name,
#                 "implementing_team": team,
#                 "trip_status": trip.status,
#                 "trip_lead": trip_lead,
#                 "employee_names": employees,
#                 "vehicle_name": trip.vehicle.name,
#                 "vehicle_license_plate": trip.vehicle.licence_plate,
#                 "driver_name": driver_name,
#                 "location_names": locations,
#                 "site_names": sites,
#             }
#             logging_helper.log_info(f"Trip summary for trip ID: {trip_id} fetched successfully")
#             return trip_details
#         except Exception as e:
#             logging_helper.log_error(f"Error while fetching trip summary for trip ID: {trip_id}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error fetching trip summary: {e}")

#     def get_all_trip_summaries(self, tenancy_id: Optional[int] = None):
#         try:
#             logging_helper.log_info("Fetching all trip summaries")
#             srt_alias = aliased(SRT)
#             unit_alias = aliased(Unit)
#             department_alias = aliased(Department)
#             thematic_area_alias = aliased(ThematicArea)
#             workplan_source_alias = aliased(WorkPlanSource)

#             implementing_team = sqlalchemy.case(
#                 (WorkPlan.initiating_srt_id != None, srt_alias.name),
#                 (WorkPlan.initiating_unit_id != None, unit_alias.name),
#                 (WorkPlan.initiating_department_id != None, department_alias.name),
#                 (WorkPlan.initiating_thematic_area_id != None, thematic_area_alias.name),
#                 else_="Unknown",
#             ).label("implementing_team")

#             trips = self.db_session.query(
#                 Trip,
#                 implementing_team,
#                 workplan_source_alias.name.label("workplan_source_name"),
#                 WorkPlan.id.label("work_plan_id"),
#                 WorkPlan.initiating_srt_id.label("srt_id"),
#                 WorkPlan.initiating_unit_id.label("unit_id"),
#                 WorkPlan.initiating_department_id.label("department_id"),
#                 sqlalchemy.func.array_agg(sqlalchemy.func.json_build_object('id', Site.id, 'site_name', Site.name)).label("site_details")
#             ).join(Trip.work_plans).outerjoin(srt_alias, WorkPlan.initiating_srt_id == srt_alias.id).outerjoin(unit_alias, WorkPlan.initiating_unit_id == unit_alias.id).outerjoin(department_alias, WorkPlan.initiating_department_id == department_alias.id).outerjoin(thematic_area_alias, WorkPlan.initiating_thematic_area_id == thematic_area_alias.id).join(workplan_source_alias, WorkPlan.workplan_source_id == workplan_source_alias.id).outerjoin(
#                 workplan_site_association, WorkPlan.id == workplan_site_association.c.work_plan_id).outerjoin(Site, Site.id == workplan_site_association.c.site_id).options(
#                 joinedload(Trip.driver).joinedload(Driver.user).joinedload(User.employee),
#                 joinedload(Trip.vehicle),
#                 joinedload(Trip.work_plans).joinedload(WorkPlan.activity_lead),
#                 joinedload(Trip.work_plans).joinedload(WorkPlan.locations),
#                 joinedload(Trip.work_plans).joinedload(WorkPlan.sites),
#             ).group_by(
#                 Trip.id, srt_alias.name, unit_alias.name, department_alias.name, thematic_area_alias.name, workplan_source_alias.name,
#                 WorkPlan.id, WorkPlan.initiating_srt_id, WorkPlan.initiating_unit_id, WorkPlan.initiating_department_id
#             )

#             if tenancy_id:
#                 trips = trips.filter(Trip.tenancy_id == tenancy_id)

#             trips = trips.distinct(WorkPlan.id).all()

#             logging_helper.log_info("Fetched all trip summaries")
#             return self.build_trip_summaries(trips)
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"SQLAlchemyError while fetching all trip summaries: {e}")
#             raise HTTPException(status_code=500, detail=f"SQLAlchemyError while fetching all trip summaries: {e}")
#         except Exception as e:
#             logging_helper.log_error(f"Error fetching all trip summaries: {e}")
#             raise HTTPException(status_code=500, detail=f"Error fetching all trip summaries: {e}")

#     def build_trip_summaries(self, trips):
#         try:
#             trip_summaries = []

#             for trip, team, source_name, work_plan_id, srt_id, unit_id, department_id, site_details in trips:
#                 employees = [f"{emp.first_name} {emp.last_name}" for wp in trip.work_plans for emp in wp.employees]
#                 locations = list(set(loc.name for wp in trip.work_plans for loc in wp.locations))
#                 sites = [{"site_name": site["site_name"], "id": site["id"]} for site in site_details]
#                 trip_lead = next(
#                     (f"{lead.activity_lead.first_name} {lead.activity_lead.last_name}" for lead in trip.work_plans if lead.activity_lead),
#                     "No lead assigned",
#                 )
#                 driver_name = f"{trip.driver.user.employee.first_name} {trip.driver.user.employee.last_name}" if trip.driver and trip.driver.user and trip.driver.user.employee else "Driver details not available"
#                 formatted_actual_start_time = trip.actual_start_time.strftime("%H:%M %p") if trip.actual_start_time else "Not started"

#                 trip_summary = {
#                     "trip_id": trip.id,
#                     "work_plan_id": work_plan_id,
#                     "activity_title": next((wp.activity_title for wp in trip.work_plans), "No title"),
#                     "workplan_code": next((wp.workplan_code for wp in trip.work_plans if wp.workplan_code), "No code"),
#                     "trip_start_time": trip.start_time.strftime("%H:%M %p") if trip.start_time else "No start time",
#                     "actual_start_time": formatted_actual_start_time,
#                     "activity_date": min(wp.activity_date for wp in trip.work_plans).strftime("%Y-%m-%d"),
#                     "workplan_source_name": source_name,
#                     "implementing_team": team,
#                     "trip_status": trip.status,
#                     "trip_lead": trip_lead,
#                     "employee_names": employees,
#                     "vehicle_name": trip.vehicle.name,
#                     "vehicle_license_plate": trip.vehicle.licence_plate,
#                     "driver_name": driver_name,
#                     "location_names": locations,
#                     "site_names": sites,
#                     "srt_id": srt_id,
#                     "unit_id": unit_id,
#                     "department_id": department_id,
#                 }
#                 trip_summaries.append(trip_summary)
#             logging_helper.log_info(f"Built {len(trip_summaries)} trip summaries.")
#             return trip_summaries
#         except Exception as e:
#             logging_helper.log_error(f"Error building trip summaries: {e}")
#             raise HTTPException(status_code=500, detail=f"Error building trip summaries: {e}")


#     def get_trips_by_status(self, status: str, tenancy_id: Optional[int] = None):
#         try:
#             logging_helper.log_info(f"Fetching trips with status: {status}")
#             srt_alias = aliased(SRT)
#             unit_alias = aliased(Unit)
#             department_alias = aliased(Department)
#             thematic_area_alias = aliased(ThematicArea)
#             workplan_source_alias = aliased(WorkPlanSource)

#             implementing_team = sqlalchemy.case(
#                 (WorkPlan.initiating_srt_id != None, srt_alias.name),
#                 (WorkPlan.initiating_unit_id != None, unit_alias.name),
#                 (WorkPlan.initiating_department_id != None, department_alias.name),
#                 (WorkPlan.initiating_thematic_area_id != None, thematic_area_alias.name),
#                 else_="Unknown",
#             ).label("implementing_team")

#             trips = self.db_session.query(
#                 Trip,
#                 implementing_team,
#                 workplan_source_alias.name.label("workplan_source_name"),
#                 WorkPlan.id.label("work_plan_id"),
#             ).join(Trip.work_plans).outerjoin(srt_alias, WorkPlan.initiating_srt_id == srt_alias.id).outerjoin(unit_alias, WorkPlan.initiating_unit_id == unit_alias.id).outerjoin(department_alias, WorkPlan.initiating_department_id == department_alias.id).outerjoin(thematic_area_alias, WorkPlan.initiating_thematic_area_id == thematic_area_alias.id).join(workplan_source_alias, WorkPlan.workplan_source_id == workplan_source_alias.id).filter(Trip.status == status).options(
#                 joinedload(Trip.driver).joinedload(Driver.user).joinedload(User.employee),
#                 joinedload(Trip.vehicle),
#                 joinedload(Trip.work_plans).joinedload(WorkPlan.activity_lead),
#                 joinedload(Trip.work_plans).joinedload(WorkPlan.locations),
#                 joinedload(Trip.work_plans).joinedload(WorkPlan.sites),
#             )

#             if tenancy_id:
#                 trips = trips.filter(Trip.tenancy_id == tenancy_id)

#             trips = trips.distinct(WorkPlan.id).all()

#             logging_helper.log_info(f"Fetched {len(trips)} trips with status: {status}")
#             return self.build_trip_summaries(trips)
#         except Exception as e:
#             logging_helper.log_error(f"Error fetching trips with status: {status}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error fetching trips with status: {status}: {e}")


#     def start_trip(self, trip_id: int, start_location_id: int, start_site_id: int, tenancy_id: Optional[int] = None):
#         """
#         Start a trip by setting the initial mileage from the vehicle's current mileage and creating the initial trip stage.

#         Parameters:
#         - trip_id (int): The ID of the trip to be started.
#         - start_location_id (int): The ID of the start location for the trip.
#         - start_site_id (int): The ID of the first site the vehicle will arrive at.
#         - tenancy_id (Optional[int]): The ID of the tenancy, used to filter trips by tenancy.

#         Returns:
#         - dict: A dictionary containing the message, trip code, actual start time, and vehicle availability status.

#         Raises:
#         - HTTPException: If the trip, vehicle, driver, start location, or start site is not found, or if there is a SQLAlchemy error.
#         """
#         try:
#             logging_helper.log_info(f"Trying to start trip with ID: {trip_id}")

#             # Fetch the trip by ID and tenancy ID
#             trip = self.db_session.query(Trip).filter_by(id=trip_id)
#             if tenancy_id:
#                 trip = trip.filter(Trip.tenancy_id == tenancy_id)
#             trip = trip.first()

#             # Check if the trip exists and hasn't already started
#             if not trip:
#                 logging_helper.log_error(f"Trip not found with ID: {trip_id}")
#                 raise HTTPException(status_code=404, detail="Trip not found.")
#             if trip.mileage_at_start is not None:
#                 logging_helper.log_error(f"Trip with ID: {trip.id} has already been started")
#                 raise HTTPException(status_code=400, detail="Trip has already been started.")

#             # Ensure the trip can only be started on its activity date
#             today = datetime.now(timezone.utc).date()
#             if not any(wp.activity_date == today for wp in trip.work_plans):
#                 logging_helper.log_error(f"The trip can only be started on its activity date: {trip.id}")
#                 raise HTTPException(status_code=400, detail="Trip can only be started on its activity date.")

#             # Fetch the associated vehicle and driver
#             vehicle = trip.vehicle
#             driver = trip.driver
#             if not vehicle:
#                 logging_helper.log_error(f"Associated vehicle not found for trip ID: {trip.id}")
#                 raise HTTPException(status_code=404, detail="Associated vehicle not found.")
#             if not driver:
#                 logging_helper.log_error(f"Associated driver not found for trip ID: {trip.id}")
#                 raise HTTPException(status_code=404, detail="Associated driver not found.")

#             # Fetch the start location by ID and tenancy ID
#             logging_helper.log_info(f"Fetching start location with ID: {start_location_id} and tenancy ID: {tenancy_id}")
#             start_location = self.db_session.query(TripSpecialLocation).filter_by(id=start_location_id).first()
#             if start_location is None:
#                 logging_helper.log_error(f"Start location not found with ID: {start_location_id} for tenancy ID: {tenancy_id}")
#                 raise HTTPException(status_code=404, detail="Start location not found.")

#             # Fetch the start site by ID
#             start_site = self.db_session.query(Site).filter_by(id=start_site_id).first()
#             if not start_site:
#                 logging_helper.log_error(f"Start site not found with ID: {start_site_id}")
#                 raise HTTPException(status_code=404, detail="Start site not found.")

#             # Generate a unique trip code
#             trip_code = f"TRP-{trip_id}-{datetime.now(timezone.utc).strftime('%y%m%d%H%M')}"

#             # Update the trip details
#             trip.trip_code = trip_code
#             trip.mileage_at_start = vehicle.current_mileage
#             trip.actual_start_time = datetime.now(timezone.utc)
#             vehicle.is_available = False
#             driver.is_available = False
#             trip.status = "Trip Started"
#             trip.trip_start_location_id = start_location_id

#             # Create initial TripStage
#             trip_stage = TripStage(
#                 trip_id=trip.id,
#                 site_id=start_site_id,
#                 stage_name=f"On Transit to {start_site.name}"
#             )
#             self.db_session.add(trip_stage)

#             # Commit the changes to the database
#             self.db_session.flush()

#             logging_helper.log_info(f"Trip with code: {trip_code} started successfully with a starting mileage of {vehicle.current_mileage}.")
#             return {
#                 "message": f"Trip with code: {trip_code} started successfully with a starting mileage of {vehicle.current_mileage}.",
#                 "trip_code": trip_code,
#                 "actual_start_time": trip.actual_start_time.strftime("%Y-%m-%d %H:%M:%S"),
#                 "vehicle_availability_status": "On a Trip",
#                 "stage_id" : trip_stage.id
#             }
#         except sqlalchemy.exc.SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"SQLAlchemyError while starting trip with ID: {trip_id}: {e}")
#             raise HTTPException(status_code=500, detail=str(e))
#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error while starting trip with ID: {trip_id}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error starting trip: {e}")


#     def record_site_arrival(self, trip_id: int, stage_id, mileage_at_arrival: float, tenancy_id: Optional[int] = None):
#         """
#         Record the arrival of a vehicle at a specific site during a trip.

#         Args:
#             trip_id (int): The ID of the trip.
#             site_id (int): The ID of the site where the vehicle has arrived.
#             mileage_at_arrival (float): The vehicle's mileage at the time of arrival.
#             tenancy_id (Optional[int]): The ID of the tenancy (optional for multi-tenancy support).

#         Returns:
#             dict: A dictionary containing a success message, details of the recorded trip stage, and the updated vehicle mileage.

#         Raises:
#             HTTPException: If any of the following conditions are met:
#                 - The trip is not found.
#                 - The site is not found.
#                 - The associated vehicle for the trip is not found.
#                 - The site is not associated with the linked work plan.
#                 - The mileage_at_arrival is less than or equal to the vehicle's current mileage.
#                 - The mileage_at_arrival is less than or equal to the previously recorded mileage for the last visited site.
#                 - Any SQLAlchemy error occurs during the database operations.

#         Example:
#             >>> record_site_arrival(trip_id=1, site_id=2, mileage_at_arrival=5000.5)
#             {
#                 "message": "Arrival recorded successfully.",
#                 "trip_stage": {
#                     "trip_id": 1,
#                     "site_id": 2,
#                     "stage_name": "Arrived at Site Name",
#                     "mileage_at_arrival": 5000.5,
#                     "arrival_time": "2024-07-18T12:34:56"
#                 },
#                 "vehicle_current_mileage": 5000.5
#             }
#         """
#         try:
#             # Query the Trip Stage to return the stage record
#             trip_stage = self.db_session.query(TripStage).filter(TripStage.id == stage_id).first()

#             logging_helper.log_info(f"Recording arrival for trip ID: {trip_id}, site ID: {trip_stage.site_id}")

#             # Fetch the trip details
#             trip_query = self.db_session.query(Trip).filter_by(id=trip_id)
#             if tenancy_id:
#                 trip_query = trip_query.filter(Trip.tenancy_id == tenancy_id)
#             trip = trip_query.first()

#             if not trip:
#                 logging_helper.log_error(f"Trip not found with ID: {trip_id}")
#                 raise HTTPException(status_code=404, detail="Trip not found.")

#             # Fetch the site details
#             site = self.db_session.query(Site).filter_by(id=trip_stage.site_id).first()
#             if not site:
#                 logging_helper.log_error(f"Site not found with ID: {trip_stage.site_id}")
#                 raise HTTPException(status_code=404, detail="Site not found.")

#             # Fetch the associated vehicle
#             vehicle = trip.vehicle
#             if not vehicle:
#                 logging_helper.log_error(f"Associated vehicle not found for trip ID: {trip.id}")
#                 raise HTTPException(status_code=404, detail="Associated vehicle not found.")

#             # Validate mileage_at_arrival
#             if mileage_at_arrival <= vehicle.current_mileage:
#                 logging_helper.log_error("Mileage at arrival must be greater than the vehicle's current mileage.")
#                 raise HTTPException(status_code=400, detail="Mileage at arrival must be greater than the vehicle's current mileage.")

#             # Validate if the site is associated with the linked work plan
#             work_plans = self.db_session.query(WorkPlan).join(trip_workplan_association).filter_by(trip_id=trip_id).all()
#             sites = set()
#             for wp in work_plans:
#                 for s in wp.sites:
#                     sites.add(s)

#             if site not in sites:
#                 logging_helper.log_error(f"The site with ID: {trip_stage.site_id} is not associated with the linked work plan.")
#                 raise HTTPException(status_code=400, detail="The site is not associated with the linked work plan.")

#             # Check if mileage_at_arrival is 0.0 and allow user to override it with the newly supplied mileage_at_arrival
#             existing_trip_stage = (
#                 self.db_session.query(TripStage)
#                 .filter_by(trip_id=trip.id, site_id=site.id)
#                 .order_by(TripStage.arrival_time.desc())
#                 .first()
#             )
#             if existing_trip_stage and existing_trip_stage.mileage_at_arrival == 0.0:
#                 existing_trip_stage.mileage_at_arrival = mileage_at_arrival


#             # Record the new trip stage
#             trip_stage.stage_name = f"Arrived at {site.name}"
#             trip_stage.arrival_time = datetime.now(timezone.utc)
#             trip_stage.mileage_at_arrival = mileage_at_arrival

#             # self.db_session.add(trip_stage)
#             vehicle.current_mileage = mileage_at_arrival
#             self.db_session.commit()

#             logging_helper.log_info(f"Recorded arrival at site ID: {trip_stage.site_id} for trip ID: {trip_id}")

#             return {
#                 "message": "Arrival recorded successfully.",
#                 "trip_stage": {
#                     "trip_id": trip.id,
#                     "site_id": site.id,
#                     "stage_name": trip_stage.stage_name,
#                     "mileage_at_arrival": mileage_at_arrival,
#                     "arrival_time": trip_stage.arrival_time
#                 },
#                 "vehicle_current_mileage": vehicle.current_mileage
#             }
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"SQLAlchemyError while recording arrival for trip ID: {trip_id}, site ID: {trip_stage.site_id}: {e}")
#             raise HTTPException(status_code=500, detail=f"SQLAlchemyError: {str(e)}")
#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error while recording arrival for trip ID: {trip_id}, site ID: {trip_stage.site_id}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error recording arrival: {e}")

#     def record_site_departure(
#         self, 
#         trip_id: int,
#         stage_id:int,  
#         next_site_id: Optional[int] = None, 
#         tenancy_id: Optional[int] = None
#     ):
#         try:
#             # Query the Trip Stage to return the stage record
#             trip_stage = self.db_session.query(TripStage).filter(TripStage.id == stage_id).first()
            
#             logging_helper.log_info(f"Recording departure for trip ID: {trip_id}, site ID: {trip_stage.site_id}")

#             trip_query = self.db_session.query(Trip).filter_by(id=trip_id)
#             if tenancy_id:
#                 trip_query = trip_query.filter(Trip.tenancy_id == tenancy_id)
#             trip = trip_query.first()

#             if not trip:
#                 logging_helper.log_error(f"Trip not found with ID: {trip_id}")
#                 raise HTTPException(status_code=404, detail="Trip not found.")

#             # Ensure the site is associated with the trip's work plans
#             associated_sites = {
#                 site.id for wp in trip.work_plans for site in wp.sites
#             }
#             if trip_stage.site_id not in associated_sites:
#                 logging_helper.log_error(f"Site ID: {trip_stage.site_id} is not associated with the trip's work plans.")
#                 raise HTTPException(status_code=400, detail="Site is not associated with the trip's work plans.")

#             site = self.db_session.query(Site).filter_by(id=trip_stage.site_id).first()
#             if not site:
#                 logging_helper.log_error(f"Site not found with ID: {trip_stage.site_id}")
#                 raise HTTPException(status_code=404, detail="Site not found.")

#             if not trip_stage or trip_stage.departure_time is not None:
#                 logging_helper.log_error(f"No valid arrival record found for trip ID: {trip_id} at site ID: {trip_stage.site_id} or site already departed.")
#                 raise HTTPException(status_code=400, detail="No valid arrival record found or site already departed.")

#             # Automatically set the departure time to the current UTC time
#             departure_time = datetime.now(timezone.utc)
#             trip_stage.departure_time = departure_time
#             trip_stage.stage_name = f"Departed from {site.name}"

#             remaining_sites = associated_sites - {stage.site_id for stage in trip.trip_stages}

#             if not remaining_sites and next_site_id is not None:
#                 logging_helper.log_error("No remaining sites to visit but next_site_id was provided.")
#                 raise HTTPException(status_code=400, detail="No remaining sites to visit but next_site_id was provided.")
            
#             if remaining_sites and next_site_id is None:
#                 logging_helper.log_error("There are remaining sites to visit but next_site_id was not provided.")
#                 raise HTTPException(status_code=400, detail="There are remaining sites to visit but next_site_id was not provided.")

#             if next_site_id :
#                 if next_site_id not in associated_sites:
#                     logging_helper.log_error(f"Next site ID: {next_site_id} is not associated with the trip's work plans.")
#                     raise HTTPException(status_code=400, desuccessfullytail="Next site is not associated with the trip's work plans.")
                
#                 next_site = self.db_session.query(Site).filter_by(id=next_site_id).first()
#                 if not next_site:
#                     logging_helper.log_error(f"Next site not found with ID: {next_site_id}")
#                     raise HTTPException(status_code=404, detail="Next site not found.")

#                 # Provide default values for mileage_at_arrival and arrival_time
#                 next_trip_stage = TripStage(
#                     trip_id=trip.id,
#                     site_id=next_site.id,
#                     stage_name=f"Heading to {next_site.name}",
#                 )
#                 self.db_session.add(next_trip_stage)

#             self.db_session.flush()

#             logging_helper.log_info(f"Recorded departure from site ID: {trip_stage.site_id} for trip ID: {trip_id}")

#             return {
#                 "message": "Departure recorded successfully.",
#                 "trip_stage": {
#                     "trip_id": trip.id,
#                     "site_id": site.id,
#                     "stage_name": trip_stage.stage_name,
#                     "departure_time": trip_stage.departure_time
#                 },
#                 "next_site_id": next_site_id if next_site_id else None,
#                 "next_stage_id" : next_trip_stage.id if next_site_id else None
#             }
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"SQLAlchemyError while recording departure for trip ID: {trip_id}, site ID: {trip_stage.site_id}: {e}")
#             raise HTTPException(status_code=500, detail=f"SQLAlchemyError: {str(e)}")
#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error while recording departure for trip ID: {trip_id}, site ID: {trip_stage.site_id}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error recording departure: {e}")


#     def end_trip(self, trip_id: int, mileage_end: float, trip_end_location_id: int, tenancy_id: Optional[int] = None):
#         try:
#             logging_helper.log_info(f"Ending trip with ID: {trip_id}")
#             trip_query = self.db_session.query(Trip).filter_by(id=trip_id)
#             if tenancy_id:
#                 trip_query = trip_query.filter(Trip.tenancy_id == tenancy_id)
#             trip = trip_query.first()

#             if not trip:
#                 logging_helper.log_error(f"Trip not found with ID: {trip_id}")
#                 raise HTTPException(status_code=404, detail="Trip not found.")
#             if trip.mileage_at_end is not None:
#                 logging_helper.log_error(f"Trip with ID: {trip.id} has already been ended")
#                 raise HTTPException(status_code=400, detail="Trip has already been ended.")
#             if trip.mileage_at_start is None:
#                 logging_helper.log_error(f"Trip with ID: {trip.id} has not started yet.")
#                 raise HTTPException(status_code=400, detail="Trip has not been started.")

#             mileage_at_start = float(trip.mileage_at_start)
#             if mileage_end <= mileage_at_start:
#                 logging_helper.log_error(f"End mileage: {mileage_end} cannot be less than or equal to the start mileage: {mileage_at_start} for trip ID: {trip.id}")
#                 raise HTTPException(status_code=400, detail="End mileage cannot be less than start mileage.")

#             # Fetch related work plans to get sites
#             work_plans = self.db_session.query(WorkPlan).join(Trip.work_plans).filter(Trip.id == trip_id).all()
#             all_sites = set()
#             for wp in work_plans:
#                 for s in wp.sites:
#                     all_sites.add(s.id)

#             # Fetch visited sites
#             visited_sites = set(ts.site_id for ts in trip.trip_stages)

#             # Check if all sites were visited
#             if all_sites != visited_sites:
#                 logging_helper.log_error(f"Not all sites were visited for trip ID: {trip.id}.")
#                 raise HTTPException(status_code=400, detail="Not all sites were visited before ending the trip.")

#             vehicle = trip.vehicle
#             if not vehicle:
#                 logging_helper.log_error(f"Associated vehicle not found for trip ID: {trip.id}")
#                 raise HTTPException(status_code=404, detail="Associated vehicle not found.")
#             if vehicle.fuel_economy is None or float(vehicle.fuel_economy) <= 0:
#                 logging_helper.log_error("Invalid or unspecified vehicle fuel economy. Fuel economy must be a positive number.")
#                 raise HTTPException(
#                     status_code=400,
#                     detail="Invalid or unspecified vehicle fuel economy. Fuel economy must be a positive number.",
#                 )

#             distance_traveled = mileage_end - mileage_at_start
#             fuel_economy = float(vehicle.fuel_economy)
#             fuel_consumed = distance_traveled / fuel_economy

#             # Set the trip end location
#             trip.trip_end_location_id = trip_end_location_id

#             trip.status = "Trip Ended"
#             trip.mileage_at_end = mileage_end
#             trip.distance = distance_traveled
#             trip.fuel_consumed = fuel_consumed
#             trip.end_time = datetime.now(timezone.utc)

#             # Add a final TripStage for the end location
#             trip_end_location = self.db_session.query(TripSpecialLocation).filter_by(id=trip_end_location_id).first()
#             if not trip_end_location:
#                 logging_helper.log_error(f"End location not found with ID: {trip_end_location_id}")
#                 raise HTTPException(status_code=404, detail="End location not found.")

#             vehicle.current_mileage = mileage_end
#             vehicle.is_available = True

#             if trip.driver:
#                 trip.driver.is_available = True

#             self.db_session.commit()
#             logging_helper.log_info(f"Trip with code: {trip.trip_code} ended successfully with end mileage: {mileage_end}, distance covered: {distance_traveled}, estimated fuel consumed: {fuel_consumed}.")
#             return {
#                 "message": "Trip ended successfully.",
#                 "trip_code": trip.trip_code,
#                 "end_mileage": mileage_end,
#                 "distance_traveled": distance_traveled,
#                 "estimated_fuel_consumed": f"{fuel_consumed:.2f} liters",
#             }
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"SQLAlchemyError while ending trip with ID: {trip_id}: {e}")
#             raise HTTPException(status_code=500, detail=str(e))
#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error while ending trip with ID: {trip_id}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error ending trip: {e}")



#     def get_sites_for_trip(self, trip_id: int) -> List[dict]:
#         """
#         Returns a list of dictionaries containing site_id and site_name for the sites associated with the trip.
#         """
#         try:
#             # Query to get the trip along with associated work plans and their sites
#             trip = self.db_session.query(Trip).filter(Trip.id == trip_id).first()
#             if not trip:
#                 raise HTTPException(status_code=404, detail="Trip not found.")

#             sites = []
#             # Extract sites from each work plan associated with the trip
#             for work_plan in trip.work_plans:
#                 for site in work_plan.sites:
#                     sites.append({"site_id": site.id, "site_name": site.name})

#             # Remove duplicates if any
#             sites = [dict(t) for t in {tuple(d.items()) for d in sites}]
#             return sites
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"An error occurred while fetching sites for the trip: {str(e)}")


#     def get_user_trips(self, current_user: UserRead):
#         try:
#             logging_helper.log_info(f"Fetching trips associated with user ID: {current_user.id}")
#             user = self.db_session.query(User).filter_by(id=current_user.id).first()
#             if not user:
#                 logging_helper.log_error(f"User not found with ID: {current_user.id}")
#                 raise HTTPException(status_code=404, detail="User not found.")

#             if not user.employee:
#                 logging_helper.log_error(f"Employee not found for user ID: {current_user.id}")
#                 raise HTTPException(status_code=404, detail="Employee not found for the current user.")

#             employee_id = user.employee.id
#             logging_helper.log_info(f"Found employee with ID: {employee_id}")

#             srt_alias = aliased(SRT)
#             unit_alias = aliased(Unit)
#             department_alias = aliased(Department)
#             thematic_area_alias = aliased(ThematicArea)
#             workplan_source_alias = aliased(WorkPlanSource)

#             implementing_team = sqlalchemy.case(
#                 (WorkPlan.initiating_srt_id != None, srt_alias.name),
#                 (WorkPlan.initiating_unit_id != None, unit_alias.name),
#                 (WorkPlan.initiating_department_id != None, department_alias.name),
#                 (WorkPlan.initiating_thematic_area_id != None, thematic_area_alias.name),
#                 else_="Unknown",
#             ).label("implementing_team")

#             trips = self.db_session.query(
#                 Trip,
#                 implementing_team,
#                 workplan_source_alias.name.label("workplan_source_name"),
#                 WorkPlan.id.label("work_plan_id"),
#             ).join(Trip.work_plans).join(
#                 workplan_employee_association,
#                 workplan_employee_association.c.work_plan_id == WorkPlan.id,
#             ).outerjoin(srt_alias, WorkPlan.initiating_srt_id == srt_alias.id).outerjoin(unit_alias, WorkPlan.initiating_unit_id == unit_alias.id).outerjoin(department_alias, WorkPlan.initiating_department_id == department_alias.id).outerjoin(thematic_area_alias, WorkPlan.initiating_thematic_area_id == thematic_area_alias.id).join(workplan_source_alias, WorkPlan.workplan_source_id == workplan_source_alias.id).filter(
#                 workplan_employee_association.c.employee_id == employee_id).distinct(WorkPlan.id).all()

#             if not trips:
#                 logging_helper.log_error(f"No trips found for employee ID: {employee_id}")
#                 return {"message": "No trips found for the current user."}

#             logging_helper.log_info(f"Trips fetched for user ID: {current_user.id}")
#             return self.build_trip_summaries(trips)
#         except Exception as e:
#             logging_helper.log_error(f"Error while fetching user trips for user ID: {current_user.id}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error fetching user trips: {e}")


# #        self.db_session = db_session

#     def record_stage_and_mileage(
#         self,
#         trip_id: int,
#         site_id: int,
#         mileage_at_arrival: float,
#         tenancy_id: int
#     ):
#         try:
#             # Fetch the trip by ID and tenancy ID
#             trip = self.db_session.query(Trip).filter_by(id=trip_id, tenancy_id=tenancy_id).first()
#             if not trip:
#                 raise HTTPException(status_code=404, detail="Trip not found.")

#             # Fetch the site by ID
#             site = self.db_session.query(Site).filter_by(id=site_id).first()
#             if not site:
#                 raise HTTPException(status_code=404, detail="Site not found.")

#             # Fetch the vehicle associated with the trip
#             vehicle = trip.vehicle
#             if not vehicle:
#                 raise HTTPException(status_code=404, detail="Vehicle not found.")

#             # Fetch related work plans to get associated sites
#             work_plans = self.db_session.query(WorkPlan).join(trip_workplan_association).filter_by(trip_id=trip_id).all()
#             sites = set()
#             for wp in work_plans:
#                 for s in wp.sites:
#                     sites.add(s)

#             # Ensure the site is associated with the linked work plan
#             if site not in sites:
#                 raise HTTPException(status_code=400, detail="The site is not associated with the linked work plan.")

#             # Fetch all trip stages for the given trip ID, ordered by arrival time
#             trip_stages = self.db_session.query(TripStage).filter_by(trip_id=trip_id).order_by(TripStage.arrival_time).all()

#             # Determine the stage name based on the current site and trip state
#             if not trip_stages:
#                 stage_name = f"Arrived at {site.name}"
#             else:
#                 last_stage = trip_stages[-1]
#                 if "Arrived at" in last_stage.stage_name:
#                     stage_name = f"Departed from {last_stage.site.name}"
#                 elif "Departed from" in last_stage.stage_name:
#                     stage_name = f"Arrived at {site.name}"
#                 else:
#                     stage_name = f"Arrived at {site.name}"

#             # Record the trip stage and mileage
#             trip_stage = TripStage(
#                 trip_id=trip_id,
#                 site_id=site_id,
#                 mileage_at_arrival=mileage_at_arrival,
#                 stage_name=stage_name,
#                 arrival_time=datetime.utcnow()
#             )

#             self.db_session.add(trip_stage)

#             # Update the vehicle's current mileage
#             vehicle.current_mileage = mileage_at_arrival

#             self.db_session.commit()

#             # Log the information about the recorded trip stage
#             logging_helper.log_info(f"Recorded trip stage: {stage_name} for trip_id: {trip_id}")

#             # Return the result
#             return {
#                 "trip_id": trip_id,
#                 "site_id": site_id,
#                 "stage_name": stage_name,
#                 "mileage_at_arrival": mileage_at_arrival,
#                 "arrival_time": trip_stage.arrival_time
#             }
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"SQLAlchemyError while recording the trip stage and mileage: {str(e)}")
#             raise HTTPException(status_code=500, detail=f"SQLAlchemyError: {str(e)}")
#         except HTTPException as e:
#             raise e
#         except Exception as e:
#             # Log the error and raise an HTTP exception
#             logging_helper.log_error(f"An error occurred while recording the trip stage and mileage: {str(e)}")
     


#     def get_vehicle_trip_status(self, trip_id: int, tenancy_id: int):
#         """
#         Get the current status of a vehicle during a trip.

#         Parameters:
#         - trip_id (int): The ID of the trip.
#         - tenancy_id (int): The ID of the tenancy.

#         Returns:
#         - dict: A dictionary containing the current status of the vehicle, site name, mileage at arrival, and arrival time.
#         """
#         try:
#             # Fetch the trip by ID and tenancy ID
#             trip = self.db_session.query(Trip).filter_by(id=trip_id, tenancy_id=tenancy_id).first()
#             if not trip:
#                 raise HTTPException(status_code=404, detail="Trip not found.")

#             # Fetch the latest trip stage for the given trip ID
#             latest_stage = self.db_session.query(TripStage).filter_by(trip_id=trip_id).order_by(TripStage.arrival_time.desc()).first()
#             if not latest_stage:
#                 return {
#                     "status": "No stages recorded",
#                     "message": "The trip has not started yet."
#                 }

#             # Determine the current status based on the latest stage
#             status = latest_stage.stage_name
#             site_name = self.db_session.query(Site).filter_by(id=latest_stage.site_id).first().name

#             return {
#                 "trip_id": trip_id,
#                 "status": status,
#                 "site_name": site_name,
#                 "mileage_at_arrival": latest_stage.mileage_at_arrival,
#                 "arrival_time": latest_stage.arrival_time,
#                 "departure_time":latest_stage.departure_time
#             }
#         except Exception as e:
#             logging_helper.log_error(f"An error occurred while fetching the vehicle status: {str(e)}")
#             raise HTTPException(status_code=500, detail=f"An error occurred while fetching the vehicle status: {str(e)}")


#     def get_unvisited_sites(self, trip_id: int, tenancy_id: Optional[int] = None):
#         try:
#             logging_helper.log_info(f"Fetching unvisited sites for trip ID: {trip_id}")
            
#             trip_query = self.db_session.query(Trip).filter_by(id=trip_id)
#             if tenancy_id:
#                 trip_query = trip_query.filter(Trip.tenancy_id == tenancy_id)
#             trip = trip_query.first()

#             if not trip:
#                 logging_helper.log_error(f"Trip not found with ID: {trip_id}")
#                 raise HTTPException(status_code=404, detail="Trip not found.")

#             # Fetch related work plans to get sites
#             work_plans = self.db_session.query(WorkPlan).join(Trip.work_plans).filter(Trip.id == trip_id).all()
#             all_sites = set()
#             for wp in work_plans:
#                 for s in wp.sites:
#                     all_sites.add((s.id, s.name))

#             # Fetch visited sites
#             visited_sites = set(ts.site_id for ts in trip.trip_stages)

#             # Determine unvisited sites
#             unvisited_sites = [(site_id, site_name) for site_id, site_name in all_sites if site_id not in visited_sites]

#             logging_helper.log_info(f"Unvisited sites for trip ID: {trip_id}: {unvisited_sites}")

#             return unvisited_sites

#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"SQLAlchemyError while fetching unvisited sites for trip ID: {trip_id}: {e}")
#             raise HTTPException(status_code=500, detail=str(e))
#         except Exception as e:
#             logging_helper.log_error(f"Error while fetching unvisited sites for trip ID: {trip_id}: {e}")
#             raise HTTPException(status_code=500, detail=f"Error fetching unvisited sites: {e}")






from fastapi import HTTPException, BackgroundTasks
import sqlalchemy
from sqlalchemy.orm import Session, aliased, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import func  # Import func for date comparison
from datetime import datetime
from datetime import datetime, date, timezone
from auth.email import notify_trip_creation, send_driver_trip_details
from auth.message import send_whatsapp_message

from models.all_models import (
    SRT,
    Department,
    Driver,
    Employee,
    Site,
    ThematicArea,
    TripSpecialLocation,
    Unit,
    User,
    Trip,
    Vehicle,
    WorkPlan,
    WorkPlanSource,
    TripStage,
    workplan_employee_association,
    trip_workplan_association,
    workplan_site_association,
    trip_employee_association,
    
)
from schemas.user_schemas import UserRead
from typing import List, Optional
from logging_helpers import logging_helper


class TripRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def generate_trip_code(self, trip: Trip) -> str:
        try:
            trip_code = f"TRP-{trip.id}-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M')}"
            logging_helper.log_info(f"Trip Code Created: {trip_code} for Trip ID: {trip.id}")
            return trip_code
        except Exception as e:
            logging_helper.log_error(f"Error Generating Trip Code for Trip ID: {trip.id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error Generating Trip Code: {e}")

    def fetch_vehicle_and_driver(self, vehicle_id: int, driver_id: int):
        try:
            vehicle = self.db_session.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.is_available == True).first()
            driver = self.db_session.query(Driver).filter(Driver.id == driver_id, Driver.is_available == True).first()

            if not vehicle:
                logging_helper.log_error(f"Selected vehicle ID: {vehicle_id} is not available.")
                raise HTTPException(status_code=400, detail="Selected vehicle is not available.")
            if not driver:
                logging_helper.log_error(f"Selected driver ID: {driver_id} is not available.")
                raise HTTPException(status_code=400, detail="Selected driver is not available.")

            logging_helper.log_info(f"Fetched vehicle ID: {vehicle_id} and driver ID: {driver_id}")
            return vehicle, driver
        except Exception as e:
            logging_helper.log_error(f"Error fetching vehicle ID: {vehicle_id} and driver ID: {driver_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching vehicle and driver: {e}")

    def fetch_work_plan(self, work_plan_id: int):
        try:
            work_plan = self.db_session.query(WorkPlan).filter(WorkPlan.id == work_plan_id).first()
            if not work_plan:
                logging_helper.log_error(f"Work plan ID: {work_plan_id} does not exist.")
                raise HTTPException(status_code=404, detail="Work plan does not exist.")
            if not work_plan.is_approved:
                logging_helper.log_error(f"Work plan ID: {work_plan_id} has not been approved.")
                raise HTTPException(status_code=400, detail="Work plan has not been approved.")

            logging_helper.log_info(f"Fetched work plan ID: {work_plan_id}")
            return work_plan
        except Exception as e:
            logging_helper.log_error(f"Error fetching work plan ID: {work_plan_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching work plan: {e}")

    def fetch_weekly_work_plans(self, work_plan: WorkPlan):
        try:
            start_of_week = work_plan.activity_date - datetime.timedelta(days=work_plan.activity_date.weekday())
            end_of_week = start_of_week + datetime.timedelta(days=6)

            if work_plan.group_id:
                weekly_work_plans = self.db_session.query(WorkPlan).filter(
                    WorkPlan.group_id == work_plan.group_id,
                    WorkPlan.activity_date >= start_of_week,
                    WorkPlan.activity_date <= end_of_week,
                    WorkPlan.is_approved == True,
                ).all()
            else:
                weekly_work_plans = [work_plan]

            if not weekly_work_plans:
                logging_helper.log_error(f"No eligible work plans found for the week for group ID: {work_plan.group_id}")
                raise HTTPException(status_code=404, detail="No eligible work plans found for the week.")

            logging_helper.log_info(f"Fetched weekly work plans for work plan ID: {work_plan.id}")
            return weekly_work_plans
        except Exception as e:
            logging_helper.log_error(f"Error fetching weekly work plans for work plan ID: {work_plan.id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching weekly work plans: {e}")

    def notify_employees(self, background_tasks: BackgroundTasks, trip, plan, driver, vehicle):
        try:
            employee_emails = [(emp.first_name, emp.employee_email) for emp in plan.employees if emp.employee_email]
            background_tasks.add_task(
                notify_trip_creation,
                employee_emails,
                trip.start_time,
                f"{driver.user.employee.first_name} {driver.user.employee.last_name}",
                driver.licence_number,
                vehicle.name,
                vehicle.licence_plate,
                plan.activity_date.strftime("%Y-%m-%d"),
            )
            logging_helper.log_info(f"Notified employees about trip {trip.trip_code}")
        except Exception as e:
            logging_helper.log_error(f"Error notifying employees about trip {trip.trip_code}: {e}")
            raise HTTPException(status_code=500, detail=f"Error notifying employees: {e}")

    def create_trip(self, driver, vehicle, plan):
        try:
            trip = Trip(
                driver_id=driver.id,
                start_time=plan.activity_start_time,
                tenancy_id=plan.tenancy_id,
                trip_code=self.generate_trip_code(),
                vehicle_id=vehicle.id,
                start_location=plan.start_location,
            )
            self.db_session.add(trip)
            self.db_session.flush()
            self.db_session.execute(trip_workplan_association.insert().values(trip_id=trip.id, work_plan_id=plan.id))
            logging_helper.log_info(f"Created trip {trip.trip_code} for work plan ID: {plan.id}")
            return trip
        except IntegrityError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"IntegrityError while creating trip for work plan ID: {plan.id}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error creating trip for work plan ID: {plan.id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating trip: {e}")

    def create_and_assign_weekly_trips(self, background_tasks: BackgroundTasks, work_plan_id: int, num_teams: int, vehicle_id: int, driver_id: int):
        try:
            logging_helper.log_info(f"Starting weekly trip assignment for work plan ID: {work_plan_id}")
            work_plan = self.fetch_work_plan(work_plan_id)
            weekly_work_plans = self.fetch_weekly_work_plans(work_plan)
            vehicle, driver = self.fetch_vehicle_and_driver(vehicle_id, driver_id)

            for plan in weekly_work_plans:
                try:
                    trip = self.create_trip(driver, vehicle, plan)
                    self.notify_employees(background_tasks, trip, plan, driver, vehicle)
                except IntegrityError as e:
                    logging_helper.log_error(f"IntegrityError while assigning trip to work plan ID: {plan.id}: {e}")
                    continue

            vehicle.is_available = False
            driver.is_available = False
            self.db_session.commit()
            logging_helper.log_info("Trips for the week have been successfully assigned.")
            return "Trips for the week have been successfully assigned."
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error creating and assigning weekly trips for work plan ID: {work_plan_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating and assigning weekly trips: {e}")


    def schedule_trip(
        self,
        work_plan_ids: list,
        employee_ids: list,
        vehicle_id: int,
        driver_id: int,
        tenancy_id: int,
        auto_group_weekly: bool,
        background_tasks: BackgroundTasks
    ):
        """
        Assigns a vehicle and driver to a list of work plans, ensuring that employees are mapped to the vehicle until it is filled up.
        It also handles WhatsApp and email notifications and retries sending messages in case of failures.

        Args:
            work_plan_ids (list): List of work plan IDs to be assigned.
            employee_ids (list): List of employee IDs to be assigned.
            vehicle_id (int): ID of the vehicle to be assigned.
            driver_id (int): ID of the driver to be assigned.
            tenancy_id (int): ID of the tenancy.
            auto_group_weekly (bool): Flag to determine if work plans should be auto-grouped weekly.
            background_tasks: Background tasks for sending notifications.

        Returns:
            dict: Message, details of the created or updated trips, list of employees already associated with a trip for the day, 
                and list of employees not assigned to the provided work plans.

        Raises:
            HTTPException: If there are any errors during the assignment process.
        """
        try:
            logging_helper.log_info(f"Assigning vehicle ID: {vehicle_id} and driver ID: {driver_id} to work plans: {work_plan_ids}")

            # Fetch the vehicle and driver, ensuring they belong to the specified tenancy
            vehicle = self.db_session.query(Vehicle).filter_by(id=vehicle_id, tenancy_id=tenancy_id).first()
            driver = self.db_session.query(Driver).filter_by(id=driver_id, tenancy_id=tenancy_id).first()

            # Check if the vehicle and driver are available
            if not vehicle or not driver:
                logging_helper.log_error("Vehicle or driver is not available.")
                raise HTTPException(status_code=400, detail="Vehicle or driver is not available.")

            # Check if the driver has any active trips
            active_trip = self.db_session.query(Trip).filter_by(driver_id=driver.id, end_time=None, tenancy_id=tenancy_id).first()
            if active_trip and active_trip.actual_start_time is not None:
                logging_helper.log_error("Driver is already on another active trip.")
                raise HTTPException(status_code=400, detail="Driver is already on another active trip.")

            # Fetch approved work plans with activity dates not in the past
            work_plans = self.db_session.query(WorkPlan).filter(
                WorkPlan.id.in_(work_plan_ids),
                WorkPlan.is_approved == True,
                WorkPlan.tenancy_id == tenancy_id,
                WorkPlan.activity_date >= date.today(),
            ).all()

            if not work_plans:
                logging_helper.log_info("No approved WorkPlans found or The Activity date for this Workplan is past.")
                raise HTTPException(status_code=404, detail="No approved WorkPlans found or The Activity date for this Workplan is past.")

            # Ensure all work plans have the same activity date
            if len(set(wp.activity_date for wp in work_plans)) > 1:
                logging_helper.log_info("All work plans must have the same activity date.")
                raise HTTPException(status_code=400, detail="All work plans must have the same activity date.")

            # Ensure all employee IDs are associated with the provided work plans
            valid_employee_ids = []
            employees_not_assigned_to_workplan = []
            for wp in work_plans:
                valid_employee_ids.extend([emp.id for emp in wp.employees])

            for emp_id in employee_ids:
                if emp_id not in valid_employee_ids:
                    employees_not_assigned_to_workplan.append(emp_id)

            if employees_not_assigned_to_workplan:
                logging_helper.log_error("Some employees are not associated with the provided work plans.")
                raise HTTPException(status_code=400, detail="Some employees are not associated with the provided work plans.")

            # Filter out employees who already have trips scheduled for the same day
            employees_not_in_trip = []
            employees_in_another_trip = []
            for emp_id in valid_employee_ids:
                # Fetch all trips that an employee is associated with, which occur on the same day
                existing_trip = (
                    self.db_session.query(trip_employee_association)
                    .join(Trip)
                    .filter(
                        trip_employee_association.c.employee_id == emp_id,
                        func.date(Trip.start_time) == work_plans[0].activity_date  # Use func.date to extract the date part
                    )
                    .first()
                )
                if existing_trip:
                    employees_in_another_trip.append(emp_id)
                else:
                    employees_not_in_trip.append(emp_id)

            if not employees_not_in_trip:
                logging_helper.log_info("All employees already have trips scheduled for the day.")
                raise HTTPException(status_code=400, detail="All employees already have trips scheduled for the day.")

            grouped_work_plans = work_plans
            if auto_group_weekly:
                group_ids = {wp.group_id for wp in work_plans}
                grouped_work_plans = self.db_session.query(WorkPlan).filter(
                    WorkPlan.group_id.in_(group_ids),
                    WorkPlan.tenancy_id == tenancy_id,
                    WorkPlan.is_approved == True,
                    WorkPlan.activity_date >= date.today(),
                ).all()

            # Group work plans by activity date
            date_grouped_workplans = {}
            for wp in grouped_work_plans:
                if wp.activity_date not in date_grouped_workplans:
                    date_grouped_workplans[wp.activity_date] = []
                date_grouped_workplans[wp.activity_date].append(wp)

            trip_ids = []
            trip_details_list = []

            # Assign employees to vehicles until the vehicle is full
            remaining_employee_ids = employees_not_in_trip.copy()
            start_trip_time = datetime.combine(grouped_work_plans[0].activity_date, grouped_work_plans[0].activity_start_time)

            while remaining_employee_ids:
                trip = Trip(
                    driver_id=driver.id,
                    vehicle_id=vehicle_id,
                    start_time=start_trip_time,
                    tenancy_id=tenancy_id,
                )
                self.db_session.add(trip)
                self.db_session.flush()
                trip_ids.append(trip.id)

                remaining_capacity = vehicle.seat_capacity
                assigned_employee_ids = []

                for emp_id in remaining_employee_ids:
                    if remaining_capacity > 0:
                        for wp in grouped_work_plans:
                            if emp_id in [emp.id for emp in wp.employees]:
                                # Check if the association already exists
                                existing_association = self.db_session.query(trip_workplan_association).filter_by(trip_id=trip.id, work_plan_id=wp.id).one_or_none()
                                if not existing_association:
                                    self.db_session.execute(trip_workplan_association.insert().values(trip_id=trip.id, work_plan_id=wp.id))

                                existing_employee_association = self.db_session.query(trip_employee_association).filter_by(trip_id=trip.id, employee_id=emp_id).one_or_none()
                                if not existing_employee_association:
                                    self.db_session.execute(trip_employee_association.insert().values(trip_id=trip.id, employee_id=emp_id))
                                
                                remaining_capacity -= 1
                                assigned_employee_ids.append(emp_id)
                                break
                    else:
                        break

                remaining_employee_ids = [emp_id for emp_id in remaining_employee_ids if emp_id not in assigned_employee_ids]

                workplan_codes = [wp.workplan_code for wp in grouped_work_plans if any(emp.id in assigned_employee_ids for emp in wp.employees)]
                trip_details_list.append({"trip_id": trip.id, "workplan_codes": workplan_codes})

            # Check if all employees in the work plans are assigned to trips
            for wp in grouped_work_plans:
                wp_employee_ids = [emp.id for emp in wp.employees]
                assigned_emp_ids = [emp_id for emp_id in employee_ids if emp_id in wp_employee_ids]
                
                # Set vehicle_assigned to True only if all employees are mapped
                if set(wp_employee_ids) == set(assigned_emp_ids):
                    wp.status = "Scheduled"
                    wp.vehicle_assigned = True
                else:
                    wp.vehicle_assigned = False

            vehicle.is_available = driver.is_available = False
            self.db_session.commit()

            driver_name = f"{driver.user.employee.first_name} {driver.user.employee.last_name}"
            passengers = ", ".join([f"{emp.first_name} {emp.last_name}" for emp_id in employees_not_in_trip for emp in self.db_session.query(Employee).filter(Employee.id == emp_id)])
            location_details = ", ".join(set(wp.activity_title for wp in grouped_work_plans))

            trip_info = {
                "take_off_time": trip.start_time.strftime("%H:%M %p"),
                "driver_name": driver_name,
                "vehicle_info": f"{vehicle.make} {vehicle.licence_plate}",
            }
            employee_emails = [(emp.first_name, emp.employee_email) for emp_id in employees_not_in_trip for emp in self.db_session.query(Employee).filter(Employee.id == emp_id)]
            employee_phone_numbers = [emp.phone_number for emp_id in employees_not_in_trip for emp in self.db_session.query(Employee).filter(Employee.id == emp_id)]
            
            logging_helper.log_info("Started sending email asynchronously to the employees and the driver involved in the trip...")
            for attempt in range(3):  # Try up to 3 times
                try:
                    background_tasks.add_task(notify_trip_creation, employee_emails, trip.start_time, driver_name, driver.licence_number, vehicle.name, vehicle.licence_plate, location_details, trip.start_time.strftime("%Y-%m-%d"))
                    background_tasks.add_task(send_driver_trip_details, driver.user.email, driver_name, vehicle.name, vehicle.licence_plate, passengers, trip.start_time.strftime("%H:%M %p"), location_details, trip.start_time.strftime("%Y-%m-%d"))

                    # WhatsApp notifications
                    for phone_number in employee_phone_numbers:
                        background_tasks.add_task(
                            send_whatsapp_message, 
                            phone_number, 
                            f"Your trip is scheduled for {trip_info['take_off_time']}. Driver: {trip_info['driver_name']}, Vehicle: {trip_info['vehicle_info']}"
                        )
                    break  # Exit the loop if successful
                except Exception as e:
                    logging_helper.log_error(f"Attempt {attempt + 1} failed: {e}")
                    if attempt == 2:  # If this was the last attempt
                        raise HTTPException(status_code=500, detail="Failed to send notifications after multiple attempts.")

            logging_helper.log_info(f"Trips created or updated successfully: {trip_ids}")
            return {
                "message": "Trips created and vehicle and driver assigned successfully.",
                "trip_ids": trip_ids,
                "trip_details": trip_details_list,
                "employees_in_another_trip": employees_in_another_trip,
                "employees_not_assigned_to_workplan": employees_not_assigned_to_workplan,
            }
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"SQLAlchemyError while assigning vehicle and driver to work plans: {work_plan_ids}: {e}")
            raise HTTPException(status_code=500, detail=f"SQLAlchemyError while assigning vehicle and driver to work plans: {work_plan_ids}: {e}")
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error while assigning vehicle and driver to work plans: {work_plan_ids}: {e}")
            raise HTTPException(status_code=500, detail=f"Error while assigning vehicle and driver to work plans: {e}")

    def add_employees_to_existing_trip(
        self,
        existing_trip_id: int,
        additional_work_plan_ids: List[int],
        additional_employee_ids: List[int],
        tenancy_id: int,
    ):
        """
        Adds employees from additional work plans to an existing trip, ensuring the vehicle is not fully utilized
        and the employees are going to the same location or site.

        Args:
            existing_trip_id (int): ID of the existing trip.
            additional_work_plan_ids (List[int]): List of additional work plan IDs.
            additional_employee_ids (List[int]): List of additional employee IDs.
            tenancy_id (int): ID of the tenancy.

        Returns:
            dict: Message and details of the updated trip.

        Raises:
            HTTPException: If there are any errors during the process.
        """
        try:
            logging_helper.log_info(f"Adding employees to existing trip ID: {existing_trip_id}")

            # Fetch the existing trip
            trip = self.db_session.query(Trip).filter_by(id=existing_trip_id, tenancy_id=tenancy_id).first()
            if not trip:
                logging_helper.log_error(f"Trip ID {existing_trip_id} not found.")
                raise HTTPException(status_code=404, detail=f"Trip ID {existing_trip_id} not found.")

            # Fetch the associated vehicle and check its remaining capacity
            vehicle = trip.vehicle
            remaining_capacity = vehicle.seat_capacity - len(trip.employees)

            if remaining_capacity <= 0:
                logging_helper.log_info("The vehicle for this trip is already fully utilized.")
                raise HTTPException(status_code=400, detail="The vehicle for this trip is already fully utilized.")

            # Fetch the additional work plans and validate their association with the same site/location
            additional_work_plans = self.db_session.query(WorkPlan).filter(
                WorkPlan.id.in_(additional_work_plan_ids),
                WorkPlan.tenancy_id == tenancy_id,
                WorkPlan.is_approved == True,
                WorkPlan.activity_date == trip.start_time.date()
            ).all()

            if not additional_work_plans:
                logging_helper.log_error("No valid additional work plans found.")
                raise HTTPException(status_code=404, detail="No valid additional work plans found.")

            # Validate employees' association with provided work plans
            valid_employee_ids = []
            for wp in additional_work_plans:
                valid_employee_ids.extend([emp.id for emp in wp.employees])

            if not all(emp_id in valid_employee_ids for emp_id in additional_employee_ids):
                logging_helper.log_error("Some employees are not associated with the provided work plans.")
                raise HTTPException(status_code=400, detail="Some employees are not associated with the provided work plans.")

            # Ensure employees are going to the same site/location as the trip
            trip_sites = {site.id for site in trip.work_plans[0].sites}
            for wp in additional_work_plans:
                if not any(site.id in trip_sites for site in wp.sites):
                    logging_helper.log_info("Work plan sites do not match the trip's site.")
                    raise HTTPException(status_code=400, detail="Work plan sites do not match the trip's site.")

            # Add employees to the trip until the vehicle is full
            assigned_employee_ids = []
            for emp_id in additional_employee_ids:
                if remaining_capacity > 0:
                    self.db_session.execute(trip_employee_association.insert().values(trip_id=trip.id, employee_id=emp_id))
                    remaining_capacity -= 1
                    assigned_employee_ids.append(emp_id)
                else:
                    break

            # Update work plans association with the trip
            for wp in additional_work_plans:
                if not self.db_session.query(trip_workplan_association).filter_by(trip_id=trip.id, work_plan_id=wp.id).one_or_none():
                    self.db_session.execute(trip_workplan_association.insert().values(trip_id=trip.id, work_plan_id=wp.id))

            self.db_session.commit()

            logging_helper.log_info(f"Employees added to trip ID: {trip.id}")
            return {
                "message": "Employees added to the existing trip successfully.",
                "trip_id": trip.id,
                "assigned_employee_ids": assigned_employee_ids
            }
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"SQLAlchemyError while adding employees to existing trip: {e}")
            raise HTTPException(status_code=500, detail=f"SQLAlchemyError while adding employees to existing trip: {e}")
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error while adding employees to existing trip: {e}")
            raise HTTPException(status_code=500, detail=f"Error while adding employees to existing trip: {e}")

    def drop_employees_from_trip(
        self, 
        trip_id: int, 
        employee_ids: List[int], 
        tenancy_id: Optional[int] = None
    ):
        try:
            logging_helper.log_info(f"Removing employees from trip ID: {trip_id}")

            trip_query = self.db_session.query(Trip).filter_by(id=trip_id)
            if tenancy_id:
                trip_query = trip_query.filter(Trip.tenancy_id == tenancy_id)
            trip = trip_query.first()

            if not trip:
                logging_helper.log_error(f"Trip not found with ID: {trip_id}")
                raise HTTPException(status_code=404, detail="Trip not found.")

            for employee_id in employee_ids:
                association = self.db_session.query(trip_employee_association).filter_by(trip_id=trip_id, employee_id=employee_id).first()
                if association:
                    self.db_session.delete(association)

            self.db_session.commit()

            logging_helper.log_info(f"Removed employees from trip ID: {trip_id}")

            return {"message": "Employees removed from trip successfully."}
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"SQLAlchemyError while removing employees from trip ID: {trip_id}: {e}")
            raise HTTPException(status_code=500, detail=f"SQLAlchemyError: {str(e)}")
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error while removing employees from trip ID: {trip_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error removing employees from trip: {e}")


    def get_employees_not_in_trip(self, work_plan_ids: List[int], tenancy_id: Optional[int] = None) -> List[dict]:
        """
        Get all employees from selected work plans who are yet to be added to a Trip.

        Args:
            work_plan_ids (List[int]): List of work plan IDs to check.
            tenancy_id (Optional[int]): ID of the tenancy (optional).

        Returns:
            List[dict]: List of employees with their details who are yet to be added to a Trip.
        """
        try:
            logging_helper.log_info(f"Fetching employees not in any trip for work plans: {work_plan_ids}")

            # Fetch approved work plans with activity dates not in the past
            work_plans = self.db_session.query(WorkPlan).filter(
                WorkPlan.id.in_(work_plan_ids),
                WorkPlan.is_approved == True,
                WorkPlan.activity_date >= date.today(),
                (WorkPlan.tenancy_id == tenancy_id) if tenancy_id else True
            ).all()

            if not work_plans:
                logging_helper.log_info("No approved WorkPlans found or The Activity date for these Workplans is past.")
                return []

            # Fetch employees associated with the given work plans
            employees = self.db_session.query(Employee).join(workplan_employee_association).join(WorkPlan).filter(
                WorkPlan.id.in_([wp.id for wp in work_plans])
            ).all()

            if not employees:
                logging_helper.log_info("No employees found for the provided work plans.")
                return []

            # Get employees who are not in any trips
            employees_not_in_trip = []
            for emp in employees:
                if not self.db_session.query(trip_employee_association).filter_by(employee_id=emp.id).first():
                    emp_work_plan_ids = [wp.id for wp in emp.work_plans if wp.id in work_plan_ids]
                    employees_not_in_trip.append({
                        "employee_id": emp.id,
                        "full_name": f"{emp.first_name} {emp.last_name}",
                        "work_plan_ids": emp_work_plan_ids
                    })

            logging_helper.log_info(f"Found {len(employees_not_in_trip)} employees not in any trip.")
            return employees_not_in_trip

        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"SQLAlchemyError while fetching employees not in any trip: {e}")
            raise HTTPException(status_code=500, detail=f"SQLAlchemyError while fetching employees not in any trip: {e}")
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error while fetching employees not in any trip: {e}")
            raise HTTPException(status_code=500, detail=f"Error while fetching employees not in any trip: {e}")


    def get_employees_associated_with_workplans(self, work_plan_ids: list, tenancy_id: int = None):
        """
        Returns a list of employees associated with the selected work plans.

        Args:
            work_plan_ids (list): List of work plan IDs.
            tenancy_id (int, optional): ID of the tenancy.

        Returns:
            list: List of employees associated with the work plans.

        Raises:
            HTTPException: If there are any errors during the retrieval process.
        """
        try:
            logging_helper.log_info(f"Fetching employees associated with work plans: {work_plan_ids}")

            # Fetch approved work plans with activity dates not in the past
            query = self.db_session.query(WorkPlan).filter(
                WorkPlan.id.in_(work_plan_ids),
                WorkPlan.is_approved == True,
                WorkPlan.activity_date >= date.today(),
            )

            if tenancy_id is not None:
                query = query.filter(WorkPlan.tenancy_id == tenancy_id)

            work_plans = query.all()

            if not work_plans:
                logging_helper.log_info("No approved WorkPlans found or The Activity date for this Workplan is past.")
                raise HTTPException(status_code=404, detail="No approved WorkPlans found or The Activity date for this Workplan is past.")

            # Retrieve employees associated with the selected work plans
            employees = []
            for wp in work_plans:
                employees.extend(wp.employees)

            # Ensure employees are unique
            unique_employees = {emp.id: emp for emp in employees}.values()

            # Prepare the result
            employee_list = [
                {
                    "id": emp.id,
                    "first_name": emp.first_name,
                    "last_name": emp.last_name,
                    "full_name": f"{emp.first_name} {emp.last_name}",
                    "email": emp.employee_email,
                    "phone_number": emp.phone_number
                }
                for emp in unique_employees
            ]

            logging_helper.log_info(f"Successfully fetched employees associated with work plans: {work_plan_ids}")
            return employee_list

        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"SQLAlchemyError while fetching employees associated with work plans: {work_plan_ids}: {e}")
            raise HTTPException(status_code=500, detail=f"SQLAlchemyError while fetching employees associated with work plans: {work_plan_ids}: {e}")
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error while fetching employees associated with work plans: {work_plan_ids}: {e}")
            raise HTTPException(status_code=500, detail=f"Error while fetching employees associated with work plans: {e}")


    def get_trip_summary(self, trip_id: int, tenancy_id: Optional[int] = None):
        try:
            logging_helper.log_info(f"Fetching trip summary for trip ID: {trip_id}")
            srt_alias = aliased(SRT)
            unit_alias = aliased(Unit)
            department_alias = aliased(Department)
            thematic_area_alias = aliased(ThematicArea)
            workplan_source_alias = aliased(WorkPlanSource)

            implementing_team = sqlalchemy.case(
                (WorkPlan.initiating_srt_id != None, srt_alias.name),
                (WorkPlan.initiating_unit_id != None, unit_alias.name),
                (WorkPlan.initiating_department_id != None, department_alias.name),
                (WorkPlan.initiating_thematic_area_id != None, thematic_area_alias.name),
                else_="Unknown",
            ).label("implementing_team")

            query = self.db_session.query(
                Trip,
                implementing_team,
                workplan_source_alias.name.label("workplan_source_name"),
            ).select_from(Trip).join(Trip.driver).join(Trip.vehicle).join(Trip.work_plans).outerjoin(
                srt_alias, WorkPlan.initiating_srt_id == srt_alias.id).outerjoin(
                unit_alias, WorkPlan.initiating_unit_id == unit_alias.id).outerjoin(
                department_alias, WorkPlan.initiating_department_id == department_alias.id).outerjoin(
                thematic_area_alias, WorkPlan.initiating_thematic_area_id == thematic_area_alias.id).join(
                workplan_source_alias, WorkPlan.workplan_source_id == workplan_source_alias.id).filter(Trip.id == trip_id)

            if tenancy_id:
                query = query.filter(Trip.tenancy_id == tenancy_id)

            trip_data = query.first()

            if not trip_data:
                logging_helper.log_error(f"No trip found with ID: {trip_id}")
                return "No trip found with the given ID."

            trip, team, source_name = trip_data

            employees = [f"{emp.first_name} {emp.last_name}" for wp in trip.work_plans for emp in wp.employees]
            locations = list(set(loc.name for wp in trip.work_plans for loc in wp.locations))
            sites = list(set(site.name for wp in trip.work_plans for site in wp.sites))

            trip_lead = next(
                (f"{lead.activity_lead.first_name} {lead.activity_lead.last_name}" for lead in trip.work_plans if lead.activity_lead),
                "No lead assigned",
            )
            driver_name = f"{trip.driver.user.employee.first_name} {trip.driver.user.employee.last_name}" if trip.driver and trip.driver.user and trip.driver.user.employee else "Driver details not available"
            formatted_actual_start_time = trip.actual_start_time.strftime("%H:%M %p") if trip.actual_start_time else "Not started"

            trip_details = {
                "trip_id": trip.id,
                "activity_title": next((wp.activity_title for wp in trip.work_plans), "No title"),
                "workplan_code": next((wp.workplan_code for wp in trip.work_plans if wp.workplan_code), "No code"),
                "trip_start_time": trip.start_time.strftime("%H:%M %p") if trip.start_time else "No start time",
                "actual_start_time": formatted_actual_start_time,
                "activity_date": min(wp.activity_date for wp in trip.work_plans).strftime("%Y-%m-%d"),
                "workplan_source_name": source_name,
                "implementing_team": team,
                "trip_status": trip.status,
                "trip_lead": trip_lead,
                "employee_names": employees,
                "vehicle_name": trip.vehicle.name,
                "vehicle_license_plate": trip.vehicle.licence_plate,
                "driver_name": driver_name,
                "location_names": locations,
                "site_names": sites,
            }
            logging_helper.log_info(f"Trip summary for trip ID: {trip_id} fetched successfully")
            return trip_details
        except Exception as e:
            logging_helper.log_error(f"Error while fetching trip summary for trip ID: {trip_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching trip summary: {e}")

    def get_all_trip_summaries(self, tenancy_id: Optional[int] = None):
        try:
            logging_helper.log_info("Fetching all trip summaries")
            srt_alias = aliased(SRT)
            unit_alias = aliased(Unit)
            department_alias = aliased(Department)
            thematic_area_alias = aliased(ThematicArea)
            workplan_source_alias = aliased(WorkPlanSource)

            implementing_team = sqlalchemy.case(
                (WorkPlan.initiating_srt_id != None, srt_alias.name),
                (WorkPlan.initiating_unit_id != None, unit_alias.name),
                (WorkPlan.initiating_department_id != None, department_alias.name),
                (WorkPlan.initiating_thematic_area_id != None, thematic_area_alias.name),
                else_="Unknown",
            ).label("implementing_team")

            trips = self.db_session.query(
                Trip,
                implementing_team,
                workplan_source_alias.name.label("workplan_source_name"),
                WorkPlan.id.label("work_plan_id"),
                WorkPlan.initiating_srt_id.label("srt_id"),
                WorkPlan.initiating_unit_id.label("unit_id"),
                WorkPlan.initiating_department_id.label("department_id"),
                sqlalchemy.func.array_agg(sqlalchemy.func.json_build_object('id', Site.id, 'site_name', Site.name)).label("site_details")
            ).join(Trip.work_plans).outerjoin(srt_alias, WorkPlan.initiating_srt_id == srt_alias.id).outerjoin(unit_alias, WorkPlan.initiating_unit_id == unit_alias.id).outerjoin(department_alias, WorkPlan.initiating_department_id == department_alias.id).outerjoin(thematic_area_alias, WorkPlan.initiating_thematic_area_id == thematic_area_alias.id).join(workplan_source_alias, WorkPlan.workplan_source_id == workplan_source_alias.id).outerjoin(
                workplan_site_association, WorkPlan.id == workplan_site_association.c.work_plan_id).outerjoin(Site, Site.id == workplan_site_association.c.site_id).options(
                joinedload(Trip.driver).joinedload(Driver.user).joinedload(User.employee),
                joinedload(Trip.vehicle),
                joinedload(Trip.work_plans).joinedload(WorkPlan.activity_lead),
                joinedload(Trip.work_plans).joinedload(WorkPlan.locations),
                joinedload(Trip.work_plans).joinedload(WorkPlan.sites),
            ).group_by(
                Trip.id, srt_alias.name, unit_alias.name, department_alias.name, thematic_area_alias.name, workplan_source_alias.name,
                WorkPlan.id, WorkPlan.initiating_srt_id, WorkPlan.initiating_unit_id, WorkPlan.initiating_department_id
            )

            if tenancy_id:
                trips = trips.filter(Trip.tenancy_id == tenancy_id)

            trips = trips.distinct(WorkPlan.id).all()

            logging_helper.log_info("Fetched all trip summaries")
            return self.build_trip_summaries(trips)
        except SQLAlchemyError as e:
            logging_helper.log_error(f"SQLAlchemyError while fetching all trip summaries: {e}")
            raise HTTPException(status_code=500, detail=f"SQLAlchemyError while fetching all trip summaries: {e}")
        except Exception as e:
            logging_helper.log_error(f"Error fetching all trip summaries: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching all trip summaries: {e}")

    def build_trip_summaries(self, trips):
        try:
            trip_summaries = []

            for trip, team, source_name, work_plan_id, srt_id, unit_id, department_id, site_details in trips:
                employees = [f"{emp.first_name} {emp.last_name}" for wp in trip.work_plans for emp in wp.employees]
                locations = list(set(loc.name for wp in trip.work_plans for loc in wp.locations))
                sites = [{"site_name": site["site_name"], "id": site["id"]} for site in site_details]
                trip_lead = next(
                    (f"{lead.activity_lead.first_name} {lead.activity_lead.last_name}" for lead in trip.work_plans if lead.activity_lead),
                    "No lead assigned",
                )
                driver_name = f"{trip.driver.user.employee.first_name} {trip.driver.user.employee.last_name}" if trip.driver and trip.driver.user and trip.driver.user.employee else "Driver details not available"
                formatted_actual_start_time = trip.actual_start_time.strftime("%H:%M %p") if trip.actual_start_time else "Not started"

                trip_summary = {
                    "trip_id": trip.id,
                    "work_plan_id": work_plan_id,
                    "activity_title": next((wp.activity_title for wp in trip.work_plans), "No title"),
                    "workplan_code": next((wp.workplan_code for wp in trip.work_plans if wp.workplan_code), "No code"),
                    "trip_start_time": trip.start_time.strftime("%H:%M %p") if trip.start_time else "No start time",
                    "actual_start_time": formatted_actual_start_time,
                    "activity_date": min(wp.activity_date for wp in trip.work_plans).strftime("%Y-%m-%d"),
                    "workplan_source_name": source_name,
                    "implementing_team": team,
                    "trip_status": trip.status,
                    "trip_lead": trip_lead,
                    "employee_names": employees,
                    "vehicle_name": trip.vehicle.name,
                    "vehicle_license_plate": trip.vehicle.licence_plate,
                    "driver_name": driver_name,
                    "location_names": locations,
                    "site_names": sites,
                    "srt_id": srt_id,
                    "unit_id": unit_id,
                    "department_id": department_id,
                }
                trip_summaries.append(trip_summary)
            logging_helper.log_info(f"Built {len(trip_summaries)} trip summaries.")
            return trip_summaries
        except Exception as e:
            logging_helper.log_error(f"Error building trip summaries: {e}")
            raise HTTPException(status_code=500, detail=f"Error building trip summaries: {e}")


    def get_trips_by_status(self, status: str, tenancy_id: Optional[int] = None):
        try:
            logging_helper.log_info(f"Fetching trips with status: {status}")
            srt_alias = aliased(SRT)
            unit_alias = aliased(Unit)
            department_alias = aliased(Department)
            thematic_area_alias = aliased(ThematicArea)
            workplan_source_alias = aliased(WorkPlanSource)

            implementing_team = sqlalchemy.case(
                (WorkPlan.initiating_srt_id != None, srt_alias.name),
                (WorkPlan.initiating_unit_id != None, unit_alias.name),
                (WorkPlan.initiating_department_id != None, department_alias.name),
                (WorkPlan.initiating_thematic_area_id != None, thematic_area_alias.name),
                else_="Unknown",
            ).label("implementing_team")

            trips = self.db_session.query(
                Trip,
                implementing_team,
                workplan_source_alias.name.label("workplan_source_name"),
                WorkPlan.id.label("work_plan_id"),
            ).join(Trip.work_plans).outerjoin(srt_alias, WorkPlan.initiating_srt_id == srt_alias.id).outerjoin(unit_alias, WorkPlan.initiating_unit_id == unit_alias.id).outerjoin(department_alias, WorkPlan.initiating_department_id == department_alias.id).outerjoin(thematic_area_alias, WorkPlan.initiating_thematic_area_id == thematic_area_alias.id).join(workplan_source_alias, WorkPlan.workplan_source_id == workplan_source_alias.id).filter(Trip.status == status).options(
                joinedload(Trip.driver).joinedload(Driver.user).joinedload(User.employee),
                joinedload(Trip.vehicle),
                joinedload(Trip.work_plans).joinedload(WorkPlan.activity_lead),
                joinedload(Trip.work_plans).joinedload(WorkPlan.locations),
                joinedload(Trip.work_plans).joinedload(WorkPlan.sites),
            )

            if tenancy_id:
                trips = trips.filter(Trip.tenancy_id == tenancy_id)

            trips = trips.distinct(WorkPlan.id).all()

            logging_helper.log_info(f"Fetched {len(trips)} trips with status: {status}")
            return self.build_trip_summaries(trips)
        except Exception as e:
            logging_helper.log_error(f"Error fetching trips with status: {status}: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching trips with status: {status}: {e}")


    def start_trip(self, trip_id: int, start_location_id: int, start_site_id: int, tenancy_id: Optional[int] = None):
        """
        Start a trip by setting the initial mileage from the vehicle's current mileage and creating the initial trip stage.

        Parameters:
        - trip_id (int): The ID of the trip to be started.
        - start_location_id (int): The ID of the start location for the trip.
        - start_site_id (int): The ID of the first site the vehicle will arrive at.
        - tenancy_id (Optional[int]): The ID of the tenancy, used to filter trips by tenancy.

        Returns:
        - dict: A dictionary containing the message, trip code, actual start time, and vehicle availability status.

        Raises:
        - HTTPException: If the trip, vehicle, driver, start location, or start site is not found, or if there is a SQLAlchemy error.
        """
        try:
            logging_helper.log_info(f"Trying to start trip with ID: {trip_id}")

            # Fetch the trip by ID and tenancy ID
            trip = self.db_session.query(Trip).filter_by(id=trip_id)
            if tenancy_id:
                trip = trip.filter(Trip.tenancy_id == tenancy_id)
            trip = trip.first()

            # Check if the trip exists and hasn't already started
            if not trip:
                logging_helper.log_error(f"Trip not found with ID: {trip_id}")
                raise HTTPException(status_code=404, detail="Trip not found.")
            if trip.mileage_at_start is not None:
                logging_helper.log_error(f"Trip with ID: {trip.id} has already been started")
                raise HTTPException(status_code=400, detail="Trip has already been started.")

            # Ensure the trip can only be started on its activity date
            today = datetime.now(timezone.utc).date()
            if not any(wp.activity_date == today for wp in trip.work_plans):
                logging_helper.log_error(f"The trip can only be started on its activity date: {trip.id}")
                raise HTTPException(status_code=400, detail="Trip can only be started on its activity date.")

            # Fetch the associated vehicle and driver
            vehicle = trip.vehicle
            driver = trip.driver
            if not vehicle:
                logging_helper.log_error(f"Associated vehicle not found for trip ID: {trip.id}")
                raise HTTPException(status_code=404, detail="Associated vehicle not found.")
            if not driver:
                logging_helper.log_error(f"Associated driver not found for trip ID: {trip.id}")
                raise HTTPException(status_code=404, detail="Associated driver not found.")

            # Fetch the start location by ID and tenancy ID
            logging_helper.log_info(f"Fetching start location with ID: {start_location_id} and tenancy ID: {tenancy_id}")
            start_location = self.db_session.query(TripSpecialLocation).filter_by(id=start_location_id).first()
            if start_location is None:
                logging_helper.log_error(f"Start location not found with ID: {start_location_id} for tenancy ID: {tenancy_id}")
                raise HTTPException(status_code=404, detail="Start location not found.")

            # Fetch the start site by ID
            start_site = self.db_session.query(Site).filter_by(id=start_site_id).first()
            if not start_site:
                logging_helper.log_error(f"Start site not found with ID: {start_site_id}")
                raise HTTPException(status_code=404, detail="Start site not found.")

            # Generate a unique trip code
            trip_code = f"TRP-{trip_id}-{datetime.now(timezone.utc).strftime('%y%m%d%H%M')}"

            # Update the trip details
            trip.trip_code = trip_code
            trip.mileage_at_start = vehicle.current_mileage
            trip.actual_start_time = datetime.now(timezone.utc)
            vehicle.is_available = False
            driver.is_available = False
            trip.status = "Trip Started"
            trip.trip_start_location_id = start_location_id

            # Create initial TripStage
            trip_stage = TripStage(
                trip_id=trip.id,
                site_id=start_site_id,
                stage_name=f"On Transit to {start_site.name}"
            )
            self.db_session.add(trip_stage)

            # Commit the changes to the database
            self.db_session.flush()

            logging_helper.log_info(f"Trip with code: {trip_code} started successfully with a starting mileage of {vehicle.current_mileage}.")
            return {
                "message": f"Trip with code: {trip_code} started successfully with a starting mileage of {vehicle.current_mileage}.",
                "trip_code": trip_code,
                "actual_start_time": trip.actual_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "vehicle_availability_status": "On a Trip",
                "stage_id" : trip_stage.id
            }
        except sqlalchemy.exc.SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"SQLAlchemyError while starting trip with ID: {trip_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error while starting trip with ID: {trip_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error starting trip: {e}")


    def record_site_arrival(self, trip_id: int, stage_id, mileage_at_arrival: float, tenancy_id: Optional[int] = None):
        """
        Record the arrival of a vehicle at a specific site during a trip.

        Args:
            trip_id (int): The ID of the trip.
            site_id (int): The ID of the site where the vehicle has arrived.
            mileage_at_arrival (float): The vehicle's mileage at the time of arrival.
            tenancy_id (Optional[int]): The ID of the tenancy (optional for multi-tenancy support).

        Returns:
            dict: A dictionary containing a success message, details of the recorded trip stage, and the updated vehicle mileage.

        Raises:
            HTTPException: If any of the following conditions are met:
                - The trip is not found.
                - The site is not found.
                - The associated vehicle for the trip is not found.
                - The site is not associated with the linked work plan.
                - The mileage_at_arrival is less than or equal to the vehicle's current mileage.
                - The mileage_at_arrival is less than or equal to the previously recorded mileage for the last visited site.
                - Any SQLAlchemy error occurs during the database operations.

        Example:
            >>> record_site_arrival(trip_id=1, site_id=2, mileage_at_arrival=5000.5)
            {
                "message": "Arrival recorded successfully.",
                "trip_stage": {
                    "trip_id": 1,
                    "site_id": 2,
                    "stage_name": "Arrived at Site Name",
                    "mileage_at_arrival": 5000.5,
                    "arrival_time": "2024-07-18T12:34:56"
                },
                "vehicle_current_mileage": 5000.5
            }
        """
        try:
            # Query the Trip Stage to return the stage record
            trip_stage = self.db_session.query(TripStage).filter(TripStage.id == stage_id).first()

            logging_helper.log_info(f"Recording arrival for trip ID: {trip_id}, site ID: {trip_stage.site_id}")

            # Fetch the trip details
            trip_query = self.db_session.query(Trip).filter_by(id=trip_id)
            if tenancy_id:
                trip_query = trip_query.filter(Trip.tenancy_id == tenancy_id)
            trip = trip_query.first()

            if not trip:
                logging_helper.log_error(f"Trip not found with ID: {trip_id}")
                raise HTTPException(status_code=404, detail="Trip not found.")

            # Fetch the site details
            site = self.db_session.query(Site).filter_by(id=trip_stage.site_id).first()
            if not site:
                logging_helper.log_error(f"Site not found with ID: {trip_stage.site_id}")
                raise HTTPException(status_code=404, detail="Site not found.")

            # Fetch the associated vehicle
            vehicle = trip.vehicle
            if not vehicle:
                logging_helper.log_error(f"Associated vehicle not found for trip ID: {trip.id}")
                raise HTTPException(status_code=404, detail="Associated vehicle not found.")

            # Validate mileage_at_arrival
            if mileage_at_arrival <= vehicle.current_mileage:
                logging_helper.log_error("Mileage at arrival must be greater than the vehicle's current mileage.")
                raise HTTPException(status_code=400, detail="Mileage at arrival must be greater than the vehicle's current mileage.")

            # Validate if the site is associated with the linked work plan
            work_plans = self.db_session.query(WorkPlan).join(trip_workplan_association).filter_by(trip_id=trip_id).all()
            sites = set()
            for wp in work_plans:
                for s in wp.sites:
                    sites.add(s)

            if site not in sites:
                logging_helper.log_error(f"The site with ID: {trip_stage.site_id} is not associated with the linked work plan.")
                raise HTTPException(status_code=400, detail="The site is not associated with the linked work plan.")

            # Check if mileage_at_arrival is 0.0 and allow user to override it with the newly supplied mileage_at_arrival
            existing_trip_stage = (
                self.db_session.query(TripStage)
                .filter_by(trip_id=trip.id, site_id=site.id)
                .order_by(TripStage.arrival_time.desc())
                .first()
            )
            if existing_trip_stage and existing_trip_stage.mileage_at_arrival == 0.0:
                existing_trip_stage.mileage_at_arrival = mileage_at_arrival


            # Record the new trip stage
            trip_stage.stage_name = f"Arrived at {site.name}"
            trip_stage.arrival_time = datetime.now(timezone.utc)
            trip_stage.mileage_at_arrival = mileage_at_arrival

            # self.db_session.add(trip_stage)
            vehicle.current_mileage = mileage_at_arrival
            self.db_session.commit()

            logging_helper.log_info(f"Recorded arrival at site ID: {trip_stage.site_id} for trip ID: {trip_id}")

            return {
                "message": "Arrival recorded successfully.",
                "trip_stage": {
                    "trip_id": trip.id,
                    "site_id": site.id,
                    "stage_name": trip_stage.stage_name,
                    "mileage_at_arrival": mileage_at_arrival,
                    "arrival_time": trip_stage.arrival_time
                },
                "vehicle_current_mileage": vehicle.current_mileage
            }
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"SQLAlchemyError while recording arrival for trip ID: {trip_id}, site ID: {trip_stage.site_id}: {e}")
            raise HTTPException(status_code=500, detail=f"SQLAlchemyError: {str(e)}")
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error while recording arrival for trip ID: {trip_id}, site ID: {trip_stage.site_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error recording arrival: {e}")

    def record_site_departure(
        self, 
        trip_id: int,
        stage_id:int,  
        next_site_id: Optional[int] = None, 
        tenancy_id: Optional[int] = None
    ):
        try:
            # Query the Trip Stage to return the stage record
            trip_stage = self.db_session.query(TripStage).filter(TripStage.id == stage_id).first()
            
            logging_helper.log_info(f"Recording departure for trip ID: {trip_id}, site ID: {trip_stage.site_id}")

            trip_query = self.db_session.query(Trip).filter_by(id=trip_id)
            if tenancy_id:
                trip_query = trip_query.filter(Trip.tenancy_id == tenancy_id)
            trip = trip_query.first()

            if not trip:
                logging_helper.log_error(f"Trip not found with ID: {trip_id}")
                raise HTTPException(status_code=404, detail="Trip not found.")

            # Ensure the site is associated with the trip's work plans
            associated_sites = {
                site.id for wp in trip.work_plans for site in wp.sites
            }
            if trip_stage.site_id not in associated_sites:
                logging_helper.log_error(f"Site ID: {trip_stage.site_id} is not associated with the trip's work plans.")
                raise HTTPException(status_code=400, detail="Site is not associated with the trip's work plans.")

            site = self.db_session.query(Site).filter_by(id=trip_stage.site_id).first()
            if not site:
                logging_helper.log_error(f"Site not found with ID: {trip_stage.site_id}")
                raise HTTPException(status_code=404, detail="Site not found.")

            if not trip_stage or trip_stage.departure_time is not None:
                logging_helper.log_error(f"No valid arrival record found for trip ID: {trip_id} at site ID: {trip_stage.site_id} or site already departed.")
                raise HTTPException(status_code=400, detail="No valid arrival record found or site already departed.")

            # Automatically set the departure time to the current UTC time
            departure_time = datetime.now(timezone.utc)
            trip_stage.departure_time = departure_time
            trip_stage.stage_name = f"Departed from {site.name}"

            remaining_sites = associated_sites - {stage.site_id for stage in trip.trip_stages}

            if not remaining_sites and next_site_id is not None:
                logging_helper.log_error("No remaining sites to visit but next_site_id was provided.")
                raise HTTPException(status_code=400, detail="No remaining sites to visit but next_site_id was provided.")
            
            if remaining_sites and next_site_id is None:
                logging_helper.log_error("There are remaining sites to visit but next_site_id was not provided.")
                raise HTTPException(status_code=400, detail="There are remaining sites to visit but next_site_id was not provided.")

            if next_site_id :
                if next_site_id not in associated_sites:
                    logging_helper.log_error(f"Next site ID: {next_site_id} is not associated with the trip's work plans.")
                    raise HTTPException(status_code=400, desuccessfullytail="Next site is not associated with the trip's work plans.")
                
                next_site = self.db_session.query(Site).filter_by(id=next_site_id).first()
                if not next_site:
                    logging_helper.log_error(f"Next site not found with ID: {next_site_id}")
                    raise HTTPException(status_code=404, detail="Next site not found.")

                # Provide default values for mileage_at_arrival and arrival_time
                next_trip_stage = TripStage(
                    trip_id=trip.id,
                    site_id=next_site.id,
                    stage_name=f"Heading to {next_site.name}",
                )
                self.db_session.add(next_trip_stage)

            self.db_session.flush()

            logging_helper.log_info(f"Recorded departure from site ID: {trip_stage.site_id} for trip ID: {trip_id}")

            return {
                "message": "Departure recorded successfully.",
                "trip_stage": {
                    "trip_id": trip.id,
                    "site_id": site.id,
                    "stage_name": trip_stage.stage_name,
                    "departure_time": trip_stage.departure_time
                },
                "next_site_id": next_site_id if next_site_id else None,
                "next_stage_id" : next_trip_stage.id if next_site_id else None
            }
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"SQLAlchemyError while recording departure for trip ID: {trip_id}, site ID: {trip_stage.site_id}: {e}")
            raise HTTPException(status_code=500, detail=f"SQLAlchemyError: {str(e)}")
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error while recording departure for trip ID: {trip_id}, site ID: {trip_stage.site_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error recording departure: {e}")


    def end_trip(self, trip_id: int, mileage_end: float, trip_end_location_id: int, tenancy_id: Optional[int] = None):
        try:
            logging_helper.log_info(f"Ending trip with ID: {trip_id}")
            trip_query = self.db_session.query(Trip).filter_by(id=trip_id)
            if tenancy_id:
                trip_query = trip_query.filter(Trip.tenancy_id == tenancy_id)
            trip = trip_query.first()

            if not trip:
                logging_helper.log_error(f"Trip not found with ID: {trip_id}")
                raise HTTPException(status_code=404, detail="Trip not found.")
            if trip.mileage_at_end is not None:
                logging_helper.log_error(f"Trip with ID: {trip.id} has already been ended")
                raise HTTPException(status_code=400, detail="Trip has already been ended.")
            if trip.mileage_at_start is None:
                logging_helper.log_error(f"Trip with ID: {trip.id} has not started yet.")
                raise HTTPException(status_code=400, detail="Trip has not been started.")

            mileage_at_start = float(trip.mileage_at_start)
            #current_mileage = self.db_session.query.filter(Vehicle.current_mileage)
            if mileage_end <= mileage_at_start:
                logging_helper.log_error(f"End mileage: {mileage_end} cannot be less than or equal to the start mileage: {mileage_at_start} for trip ID: {trip.id}")
                raise HTTPException(status_code=400, detail="End mileage cannot be less than start mileage.")

            # Fetch related work plans to get sites
            work_plans = self.db_session.query(WorkPlan).join(Trip.work_plans).filter(Trip.id == trip_id).all()
            all_sites = set()
            for wp in work_plans:
                for s in wp.sites:
                    all_sites.add(s.id)

            # Fetch visited sites
            visited_sites = set(ts.site_id for ts in trip.trip_stages)

            # Check if all sites were visited
            if all_sites != visited_sites:
                logging_helper.log_error(f"Not all sites were visited for trip ID: {trip.id}.")
                raise HTTPException(status_code=400, detail="Not all sites were visited before ending the trip.")

            vehicle = trip.vehicle
            if not vehicle:
                logging_helper.log_error(f"Associated vehicle not found for trip ID: {trip.id}")
                raise HTTPException(status_code=404, detail="Associated vehicle not found.")
            if vehicle.fuel_economy is None or float(vehicle.fuel_economy) <= 0:
                logging_helper.log_error("Invalid or unspecified vehicle fuel economy. Fuel economy must be a positive number.")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid or unspecified vehicle fuel economy. Fuel economy must be a positive number.",
                )

            distance_traveled = mileage_end - mileage_at_start
            fuel_economy = float(vehicle.fuel_economy)
            fuel_consumed = distance_traveled / fuel_economy

            # Set the trip end location
            trip.trip_end_location_id = trip_end_location_id

            trip.status = "Trip Ended"
            trip.mileage_at_end = mileage_end
            trip.distance = distance_traveled
            trip.fuel_consumed = fuel_consumed
            trip.end_time = datetime.now(timezone.utc)

            # Add a final TripStage for the end location
            trip_end_location = self.db_session.query(TripSpecialLocation).filter_by(id=trip_end_location_id).first()
            if not trip_end_location:
                logging_helper.log_error(f"End location not found with ID: {trip_end_location_id}")
                raise HTTPException(status_code=404, detail="End location not found.")

            vehicle.current_mileage = mileage_end
            
            vehicle.is_available = True

            if trip.driver:
                trip.driver.is_available = True

            self.db_session.commit()
            logging_helper.log_info(f"Trip with code: {trip.trip_code} ended successfully with end mileage: {mileage_end}, distance covered: {distance_traveled}, estimated fuel consumed: {fuel_consumed}.")
            return {
                "message": "Trip ended successfully.",
                "trip_code": trip.trip_code,
                "end_mileage": mileage_end,
                "distance_traveled": distance_traveled,
                "estimated_fuel_consumed": f"{fuel_consumed:.2f} liters",
            }
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"SQLAlchemyError while ending trip with ID: {trip_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error while ending trip with ID: {trip_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error ending trip: {e}")



    def get_sites_for_trip(self, trip_id: int) -> List[dict]:
        """
        Returns a list of dictionaries containing site_id and site_name for the sites associated with the trip.
        """
        try:
            # Query to get the trip along with associated work plans and their sites
            trip = self.db_session.query(Trip).filter(Trip.id == trip_id).first()
            if not trip:
                raise HTTPException(status_code=404, detail="Trip not found.")

            sites = []
            # Extract sites from each work plan associated with the trip
            for work_plan in trip.work_plans:
                for site in work_plan.sites:
                    sites.append({"site_id": site.id, "site_name": site.name})

            # Remove duplicates if any
            sites = [dict(t) for t in {tuple(d.items()) for d in sites}]
            return sites
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while fetching sites for the trip: {str(e)}")


    def get_user_trips(self, current_user: UserRead):
        try:
            logging_helper.log_info(f"Fetching trips associated with user ID: {current_user.id}")
            user = self.db_session.query(User).filter_by(id=current_user.id).first()
            if not user:
                logging_helper.log_error(f"User not found with ID: {current_user.id}")
                raise HTTPException(status_code=404, detail="User not found.")

            if not user.employee:
                logging_helper.log_error(f"Employee not found for user ID: {current_user.id}")
                raise HTTPException(status_code=404, detail="Employee not found for the current user.")

            employee_id = user.employee.id
            logging_helper.log_info(f"Found employee with ID: {employee_id}")

            srt_alias = aliased(SRT)
            unit_alias = aliased(Unit)
            department_alias = aliased(Department)
            thematic_area_alias = aliased(ThematicArea)
            workplan_source_alias = aliased(WorkPlanSource)

            implementing_team = sqlalchemy.case(
                (WorkPlan.initiating_srt_id != None, srt_alias.name),
                (WorkPlan.initiating_unit_id != None, unit_alias.name),
                (WorkPlan.initiating_department_id != None, department_alias.name),
                (WorkPlan.initiating_thematic_area_id != None, thematic_area_alias.name),
                else_="Unknown",
            ).label("implementing_team")

            trips = self.db_session.query(
                Trip,
                implementing_team,
                workplan_source_alias.name.label("workplan_source_name"),
                WorkPlan.id.label("work_plan_id"),
            ).join(Trip.work_plans).join(
                workplan_employee_association,
                workplan_employee_association.c.work_plan_id == WorkPlan.id,
            ).outerjoin(srt_alias, WorkPlan.initiating_srt_id == srt_alias.id).outerjoin(unit_alias, WorkPlan.initiating_unit_id == unit_alias.id).outerjoin(department_alias, WorkPlan.initiating_department_id == department_alias.id).outerjoin(thematic_area_alias, WorkPlan.initiating_thematic_area_id == thematic_area_alias.id).join(workplan_source_alias, WorkPlan.workplan_source_id == workplan_source_alias.id).filter(
                workplan_employee_association.c.employee_id == employee_id).distinct(WorkPlan.id).all()

            if not trips:
                logging_helper.log_error(f"No trips found for employee ID: {employee_id}")
                return {"message": "No trips found for the current user."}

            logging_helper.log_info(f"Trips fetched for user ID: {current_user.id}")
            return self.build_trip_summaries(trips)
        except Exception as e:
            logging_helper.log_error(f"Error while fetching user trips for user ID: {current_user.id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching user trips: {e}")


#        self.db_session = db_session

    def record_stage_and_mileage(
        self,
        trip_id: int,
        site_id: int,
        mileage_at_arrival: float,
        tenancy_id: int
    ):
        try:
            # Fetch the trip by ID and tenancy ID
            trip = self.db_session.query(Trip).filter_by(id=trip_id, tenancy_id=tenancy_id).first()
            if not trip:
                raise HTTPException(status_code=404, detail="Trip not found.")

            # Fetch the site by ID
            site = self.db_session.query(Site).filter_by(id=site_id).first()
            if not site:
                raise HTTPException(status_code=404, detail="Site not found.")

            # Fetch the vehicle associated with the trip
            vehicle = trip.vehicle
            if not vehicle:
                raise HTTPException(status_code=404, detail="Vehicle not found.")

            # Fetch related work plans to get associated sites
            work_plans = self.db_session.query(WorkPlan).join(trip_workplan_association).filter_by(trip_id=trip_id).all()
            sites = set()
            for wp in work_plans:
                for s in wp.sites:
                    sites.add(s)

            # Ensure the site is associated with the linked work plan
            if site not in sites:
                raise HTTPException(status_code=400, detail="The site is not associated with the linked work plan.")

            # Fetch all trip stages for the given trip ID, ordered by arrival time
            trip_stages = self.db_session.query(TripStage).filter_by(trip_id=trip_id).order_by(TripStage.arrival_time).all()

            # Determine the stage name based on the current site and trip state
            if not trip_stages:
                stage_name = f"Arrived at {site.name}"
            else:
                last_stage = trip_stages[-1]
                if "Arrived at" in last_stage.stage_name:
                    stage_name = f"Departed from {last_stage.site.name}"
                elif "Departed from" in last_stage.stage_name:
                    stage_name = f"Arrived at {site.name}"
                else:
                    stage_name = f"Arrived at {site.name}"

            # Record the trip stage and mileage
            trip_stage = TripStage(
                trip_id=trip_id,
                site_id=site_id,
                mileage_at_arrival=mileage_at_arrival,
                stage_name=stage_name,
                arrival_time=datetime.utcnow()
            )

            self.db_session.add(trip_stage)

            # Update the vehicle's current mileage
            vehicle.current_mileage = mileage_at_arrival

            self.db_session.commit()

            # Log the information about the recorded trip stage
            logging_helper.log_info(f"Recorded trip stage: {stage_name} for trip_id: {trip_id}")

            # Return the result
            return {
                "trip_id": trip_id,
                "site_id": site_id,
                "stage_name": stage_name,
                "mileage_at_arrival": mileage_at_arrival,
                "arrival_time": trip_stage.arrival_time
            }
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"SQLAlchemyError while recording the trip stage and mileage: {str(e)}")
            raise HTTPException(status_code=500, detail=f"SQLAlchemyError: {str(e)}")
        except HTTPException as e:
            raise e
        except Exception as e:
            # Log the error and raise an HTTP exception
            logging_helper.log_error(f"An error occurred while recording the trip stage and mileage: {str(e)}")
     


    def get_vehicle_trip_status(self, trip_id: int, tenancy_id: int):
        """
        Get the current status of a vehicle during a trip.

        Parameters:
        - trip_id (int): The ID of the trip.
        - tenancy_id (int): The ID of the tenancy.

        Returns:
        - dict: A dictionary containing the current status of the vehicle, site name, mileage at arrival, and arrival time.
        """
        try:
            # Fetch the trip by ID and tenancy ID
            trip = self.db_session.query(Trip).filter_by(id=trip_id, tenancy_id=tenancy_id).first()
            if not trip:
                raise HTTPException(status_code=404, detail="Trip not found.")

            # Fetch the latest trip stage for the given trip ID
            latest_stage = self.db_session.query(TripStage).filter_by(trip_id=trip_id).order_by(TripStage.arrival_time.desc()).first()
            if not latest_stage:
                return {
                    "status": "No stages recorded",
                    "message": "The trip has not started yet."
                }

            # Determine the current status based on the latest stage
            status = latest_stage.stage_name
            site_name = self.db_session.query(Site).filter_by(id=latest_stage.site_id).first().name

            return {
                "trip_id": trip_id,
                "status": status,
                "site_name": site_name,
                "mileage_at_arrival": latest_stage.mileage_at_arrival,
                "arrival_time": latest_stage.arrival_time,
                "departure_time":latest_stage.departure_time
            }
        except Exception as e:
            logging_helper.log_error(f"An error occurred while fetching the vehicle status: {str(e)}")
            raise HTTPException(status_code=500, detail=f"An error occurred while fetching the vehicle status: {str(e)}")


    def get_unvisited_sites(self, trip_id: int, tenancy_id: Optional[int] = None):
        try:
            logging_helper.log_info(f"Fetching unvisited sites for trip ID: {trip_id}")
            
            trip_query = self.db_session.query(Trip).filter_by(id=trip_id)
            if tenancy_id:
                trip_query = trip_query.filter(Trip.tenancy_id == tenancy_id)
            trip = trip_query.first()

            if not trip:
                logging_helper.log_error(f"Trip not found with ID: {trip_id}")
                raise HTTPException(status_code=404, detail="Trip not found.")

            # Fetch related work plans to get sites
            work_plans = self.db_session.query(WorkPlan).join(Trip.work_plans).filter(Trip.id == trip_id).all()
            all_sites = set()
            for wp in work_plans:
                for s in wp.sites:
                    all_sites.add((s.id, s.name))

            # Fetch visited sites
            visited_sites = set(ts.site_id for ts in trip.trip_stages)

            # Determine unvisited sites
            unvisited_sites = [(site_id, site_name) for site_id, site_name in all_sites if site_id not in visited_sites]

            logging_helper.log_info(f"Unvisited sites for trip ID: {trip_id}: {unvisited_sites}")

            return unvisited_sites

        except SQLAlchemyError as e:
            logging_helper.log_error(f"SQLAlchemyError while fetching unvisited sites for trip ID: {trip_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logging_helper.log_error(f"Error while fetching unvisited sites for trip ID: {trip_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching unvisited sites: {e}")


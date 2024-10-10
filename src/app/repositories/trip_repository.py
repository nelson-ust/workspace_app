# #import datetime
# from decimal import Decimal
# import logging
# from typing import List, Optional
# from fastapi import BackgroundTasks, HTTPException
# import sqlalchemy
# from datetime import datetime, timezone
# import sqlalchemy.exc
# from fastapi import HTTPException
# from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound
# from sqlalchemy.exc import DBAPIError
# from sqlalchemy.orm import Session
# from sqlalchemy.orm import joinedload
# from sqlalchemy.orm import aliased
# from auth.email import notify_employees_about_trip, notify_trip_creation, send_driver_trip_details, send_reminder_email
# from models.all_models import SRT, Department, Driver, ThematicArea, Trip, Unit, User, Vehicle, WorkPlan, WorkPlanSource


import datetime
from decimal import Decimal
import logging
from typing import List, Optional
from fastapi import BackgroundTasks, HTTPException, Query, File, UploadFile
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session, joinedload, aliased
from auth.email import notify_employees_about_trip, notify_trip_creation, send_driver_trip_details, send_reminder_email
from models.all_models import SRT, Department, Driver, ThematicArea, Trip, Unit, User, Vehicle, WorkPlan, WorkPlanSource, Employee, Location, trip_workplan_association, workplan_employee_association, workplan_location_association


from models.all_models import Trip, WorkPlan, Employee, Vehicle, Location, trip_workplan_association, workplan_employee_association, workplan_location_association
from typing import List

class TripRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def generate_trip_code(self, trip: Trip) -> str:
        # Generates a trip code using the current UTC time, formatted to include year, month, day, hour, and minute.
        return f"TRP-{trip.id}-{datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M')}"

    def create_and_assign_weekly_trips(self, background_tasks: BackgroundTasks, work_plan_id: int, num_teams: int, vehicle_id: int, driver_id: int):
        # Fetch the specified work plan
        work_plan = self.db_session.query(WorkPlan).filter(WorkPlan.id == work_plan_id).first()
        if not work_plan:
            raise HTTPException(status_code=404, detail="Work plan does not exist.")

        if not work_plan.is_approved:
            raise HTTPException(status_code=400, detail="Work plan has not been approved.")

        # Define the week range based on the work plan's activity date
        start_of_week = work_plan.activity_date - datetime.timedelta(days=work_plan.activity_date.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)

        # Fetch work plans either grouped or standalone within the same week and approved
        if work_plan.group_id:
            # Work plans in the same group and week
            weekly_work_plans = self.db_session.query(WorkPlan).filter(
                WorkPlan.group_id == work_plan.group_id,
                WorkPlan.activity_date >= start_of_week,
                WorkPlan.activity_date <= end_of_week,
                WorkPlan.is_approved == True
            ).all()
        else:
            # Handle standalone work plan
            weekly_work_plans = [work_plan]

        if not weekly_work_plans:
            raise HTTPException(status_code=404, detail="No eligible work plans found for the week.")

        # Retrieve the selected vehicle and driver
        vehicle = self.db_session.query(Vehicle).filter(
            Vehicle.id == vehicle_id,
            Vehicle.is_available == True
        ).first()
        if not vehicle:
            raise HTTPException(status_code=400, detail="Selected vehicle is not available.")

        driver = self.db_session.query(Driver).filter(
            Driver.id == driver_id,
            Driver.is_available == True
        ).first()
        if not driver:
            raise HTTPException(status_code=400, detail="Selected driver is not available.")

        # Assign the vehicle and driver to each work plan in the week
        for plan in weekly_work_plans:
            # Create a trip for each plan
            try:
                trip = Trip(
                    driver_id=driver.id,
                    start_time=plan.activity_start_time,
                    tenancy_id=plan.tenancy_id,
                    trip_code=self.generate_trip_code(),
                    vehicle_id =vehicle_id
                )
                self.db_session.add(trip)
                self.db_session.flush()

                # Associate trip with vehicle and work plan
               # self.db_session.execute(trip_vehicle_association.insert().values(trip_id=trip.id, vehicle_id=vehicle.id))
                self.db_session.execute(trip_workplan_association.insert().values(trip_id=trip.id, work_plan_id=plan.id))

                # Send notifications
                employee_emails = [(emp.first_name, emp.employee_email) for emp in plan.employees if emp.employee_email]
                background_tasks.add_task(
                    notify_trip_creation,
                    employee_emails,
                    trip.start_time,
                    f"{driver.user.employee.first_name} {driver.user.employee.last_name}",
                    driver.licence_number,
                    vehicle.name,
                    vehicle.licence_plate,
                    plan.activity_date.strftime('%Y-%m-%d')
                )

            except IntegrityError as e:
                self.db_session.rollback()
                raise HTTPException(status_code=400, detail=str(e))

        # Mark resources as unavailable
        vehicle.is_available = False
        driver.is_available = False
        self.db_session.commit()

        return "Trips for the week have been successfully assigned."


    def get_trip_summary(self, trip_id: int):
        try:
            # Define alias for clarity in conditional joins
            srt_alias = aliased(SRT)
            unit_alias = aliased(Unit)
            department_alias = aliased(Department)
            thematic_area_alias = aliased(ThematicArea)
            workplan_source_alias = aliased(WorkPlanSource)

            # Case statement for dynamically determining the implementing team
            implementing_team = sqlalchemy.case(
                (WorkPlan.initiating_srt_id != None, srt_alias.name),
                (WorkPlan.initiating_unit_id != None, unit_alias.name),
                (WorkPlan.initiating_department_id != None, department_alias.name),
                (WorkPlan.initiating_thematic_area_id != None, thematic_area_alias.name),
                else_="Unknown").label("implementing_team")

            # Begin building the query
            query = self.db_session.query(
                Trip,
                implementing_team,
                workplan_source_alias.name.label("workplan_source_name")
            ).select_from(Trip)

            # Adjust join to directly access the vehicle and driver
            query = query.join(Trip.driver)\
                        .join(Trip.vehicle)\
                        .join(Trip.work_plans)\
                        .outerjoin(srt_alias, WorkPlan.initiating_srt_id == srt_alias.id)\
                        .outerjoin(unit_alias, WorkPlan.initiating_unit_id == unit_alias.id)\
                        .outerjoin(department_alias, WorkPlan.initiating_department_id == department_alias.id)\
                        .outerjoin(thematic_area_alias, WorkPlan.initiating_thematic_area_id == thematic_area_alias.id)\
                        .join(workplan_source_alias, WorkPlan.workplan_source_id == workplan_source_alias.id)

            # Filter by trip ID
            query = query.filter(Trip.id == trip_id)

            # Execute the query
            trip_data = query.first()

            if not trip_data:
                return "No trip found with the given ID."

            trip, team, source_name = trip_data

            # Construct the list of employees, locations, and sites
            employees = [f"{emp.first_name} {emp.last_name}" for wp in trip.work_plans for emp in wp.employees]
            locations = list(set(loc.name for wp in trip.work_plans for loc in wp.locations))
            sites = list(set(site.name for wp in trip.work_plans for site in wp.sites))

            # Simplify the extraction of other details
            trip_lead = next((f"{lead.activity_lead.first_name} {lead.activity_lead.last_name}" for lead in trip.work_plans if lead.activity_lead), "No lead assigned")
            driver_name = f"{trip.driver.user.employee.first_name} {trip.driver.user.employee.last_name}" if trip.driver and trip.driver.user and trip.driver.user.employee else "Driver details not available"

            # Format the actual start time if it exists
            formatted_actual_start_time = trip.actual_start_time.strftime('%H:%M %p') if trip.actual_start_time else "Not started"

            # Aggregate other details
            trip_details = {
                "activity_title": next((wp.activity_title for wp in trip.work_plans), "No title"),
                "workplan_code": next((wp.workplan_code for wp in trip.work_plans if wp.workplan_code), "No code"),
                "trip_start_time": trip.start_time.strftime('%H:%M %p') if trip.start_time else "No start time",
                "actual_start_time": formatted_actual_start_time,  # Include actual start time
                "activity_date": min(wp.activity_date for wp in trip.work_plans).strftime('%Y-%m-%d'),
                "workplan_source_name": source_name,
                "implementing_team": team,
                "trip_status": trip.status,
                "trip_lead": trip_lead,
                "employee_names": employees,
                "vehicle_name": trip.vehicle.name,
                "vehicle_license_plate": trip.vehicle.licence_plate,
                "driver_name": driver_name,
                "location_names": locations,
                "site_names": sites
            }
            return trip_details
        except Exception as e:
            # Handle unexpected errors
            return {"error": "An error occurred while fetching trip summaries", "details": str(e)}


    # def get_trips_by_status(self, status: str):
    #     try:
    #         # Aliases for conditional joins
    #         srt_alias = aliased(SRT)
    #         unit_alias = aliased(Unit)
    #         department_alias = aliased(Department)
    #         thematic_area_alias = aliased(ThematicArea)
    #         workplan_source_alias = aliased(WorkPlanSource)

    #         # Define the case statement for dynamically determining the implementing team
    #         implementing_team = sqlalchemy.case(
    #             (WorkPlan.initiating_srt_id != None, srt_alias.name),
    #             (WorkPlan.initiating_unit_id != None, unit_alias.name),
    #             (WorkPlan.initiating_department_id != None, department_alias.name),
    #             (WorkPlan.initiating_thematic_area_id != None, thematic_area_alias.name),
    #             else_="Unknown").label("implementing_team")

    #         # Query trips with necessary joins and filter by status
    #         trips = self.db_session.query(
    #             Trip,
    #             implementing_team,
    #             workplan_source_alias.name.label("workplan_source_name")
    #         ).join(
    #             Trip.work_plans
    #         ).outerjoin(
    #             srt_alias, WorkPlan.initiating_srt_id == srt_alias.id
    #         ).outerjoin(
    #             unit_alias, WorkPlan.initiating_unit_id == unit_alias.id
    #         ).outerjoin(
    #             department_alias, WorkPlan.initiating_department_id == department_alias.id
    #         ).outerjoin(
    #             thematic_area_alias, WorkPlan.initiating_thematic_area_id == thematic_area_alias.id
    #         ).join(
    #             workplan_source_alias, WorkPlan.workplan_source_id == workplan_source_alias.id
    #         ).filter(
    #             Trip.status == status  # Filter trips by status
    #         ).options(
    #             joinedload(Trip.driver).joinedload(Driver.user).joinedload(User.employee),
    #             joinedload(Trip.vehicle),
    #             joinedload(Trip.work_plans).joinedload(WorkPlan.activity_lead),
    #             joinedload(Trip.work_plans).joinedload(WorkPlan.locations),
    #             joinedload(Trip.work_plans).joinedload(WorkPlan.sites)
    #         ).all()

    #         trip_summaries = []

    #         for trip, team, source_name in trips:
    #             employees = [f"{emp.first_name} {emp.last_name}" for wp in trip.work_plans for emp in wp.employees]
    #             locations = list(set(loc.name for wp in trip.work_plans for loc in wp.locations))
    #             sites = list(set(site.name for wp in trip.work_plans for site in wp.sites))
    #             trip_lead = next((f"{lead.activity_lead.first_name} {lead.activity_lead.last_name}" for lead in trip.work_plans if lead.activity_lead), "No lead assigned")
    #             driver_name = f"{trip.driver.user.employee.first_name} {trip.driver.user.employee.last_name}" if trip.driver and trip.driver.user and trip.driver.user.employee else "Driver details not available"

    #             formatted_actual_start_time = trip.actual_start_time.strftime('%H:%M %p') if trip.actual_start_time else "Not started"

    #             trip_summary = {
    #                 "activity_title": next((wp.activity_title for wp in trip.work_plans), "No title"),
    #                 "workplan_code": next((wp.workplan_code for wp in trip.work_plans if wp.workplan_code), "No code"),
    #                 "trip_start_time": trip.start_time.strftime('%H:%M %p') if trip.start_time else "No start time",
    #                 "actual_start_time": formatted_actual_start_time,
    #                 "activity_date": min(wp.activity_date for wp in trip.work_plans).strftime('%Y-%m-%d'),
    #                 "workplan_source_name": source_name,
    #                 "implementing_team": team,
    #                 "trip_status": trip.status,
    #                 "trip_lead": trip_lead,
    #                 "employee_names": employees,
    #                 "vehicle_name": trip.vehicle.name,
    #                 "vehicle_license_plate": trip.vehicle.licence_plate,
    #                 "driver_name": driver_name,
    #                 "location_names": locations,
    #                 "site_names": sites
    #             }
    #             trip_summaries.append(trip_summary)

    #         return trip_summaries

    #     except Exception as e:
    #         # Handle unexpected errors
    #         return {"error": "An error occurred while fetching trip summaries", "details": str(e)}


    def get_trips_by_status(self, status: str):
        try:
            # Aliases for conditional joins
            srt_alias = aliased(SRT)
            unit_alias = aliased(Unit)
            department_alias = aliased(Department)
            thematic_area_alias = aliased(ThematicArea)
            workplan_source_alias = aliased(WorkPlanSource)

            # Define the case statement for dynamically determining the implementing team
            implementing_team = sqlalchemy.case(
                (WorkPlan.initiating_srt_id != None, srt_alias.name),
                (WorkPlan.initiating_unit_id != None, unit_alias.name),
                (WorkPlan.initiating_department_id != None, department_alias.name),
                (WorkPlan.initiating_thematic_area_id != None, thematic_area_alias.name),
                else_="Unknown").label("implementing_team")

            # Query trips with necessary joins and filter by status
            trips = self.db_session.query(
                Trip,
                implementing_team,
                workplan_source_alias.name.label("workplan_source_name"),
                WorkPlan.id.label("work_plan_id")
            ).join(
                Trip.work_plans
            ).outerjoin(
                srt_alias, WorkPlan.initiating_srt_id == srt_alias.id
            ).outerjoin(
                unit_alias, WorkPlan.initiating_unit_id == unit_alias.id
            ).outerjoin(
                department_alias, WorkPlan.initiating_department_id == department_alias.id
            ).outerjoin(
                thematic_area_alias, WorkPlan.initiating_thematic_area_id == thematic_area_alias.id
            ).join(
                workplan_source_alias, WorkPlan.workplan_source_id == workplan_source_alias.id
            ).filter(
                Trip.status == status
            ).options(
                joinedload(Trip.driver).joinedload(Driver.user).joinedload(User.employee),
                joinedload(Trip.vehicle),
                joinedload(Trip.work_plans).joinedload(WorkPlan.activity_lead),
                joinedload(Trip.work_plans).joinedload(WorkPlan.locations),
                joinedload(Trip.work_plans).joinedload(WorkPlan.sites)
            ).distinct(WorkPlan.id).all()  # Ensure distinctness based on work_plan_id

            # Build trip summaries
            trip_summaries = []

            for trip, team, source_name, work_plan_id in trips:
                employees = [f"{emp.first_name} {emp.last_name}" for wp in trip.work_plans for emp in wp.employees]
                locations = list(set(loc.name for wp in trip.work_plans for loc in wp.locations))
                sites = list(set(site.name for wp in trip.work_plans for site in wp.sites))
                trip_lead = next((f"{lead.activity_lead.first_name} {lead.activity_lead.last_name}" for lead in trip.work_plans if lead.activity_lead), "No lead assigned")
                driver_name = f"{trip.driver.user.employee.first_name} {trip.driver.user.employee.last_name}" if trip.driver and trip.driver.user and trip.driver.user.employee else "Driver details not available"

                formatted_actual_start_time = trip.actual_start_time.strftime('%H:%M %p') if trip.actual_start_time else "Not started"

                trip_summary = {
                    "work_plan_id": work_plan_id,
                    "activity_title": next((wp.activity_title for wp in trip.work_plans), "No title"),
                    "workplan_code": next((wp.workplan_code for wp in trip.work_plans if wp.workplan_code), "No code"),
                    "trip_start_time": trip.start_time.strftime('%H:%M %p') if trip.start_time else "No start time",
                    "actual_start_time": formatted_actual_start_time,
                    "activity_date": min(wp.activity_date for wp in trip.work_plans).strftime('%Y-%m-%d'),
                    "workplan_source_name": source_name,
                    "implementing_team": team,
                    "trip_status": trip.status,
                    "trip_lead": trip_lead,
                    "employee_names": employees,
                    "vehicle_name": trip.vehicle.name,
                    "vehicle_license_plate": trip.vehicle.licence_plate,
                    "driver_name": driver_name,
                    "location_names": locations,
                    "site_names": sites
                }
                trip_summaries.append(trip_summary)

            return trip_summaries

        except Exception as e:
            # Handle unexpected errors
            return {"error": "An error occurred while fetching trip summaries", "details": str(e)}


    def get_all_trip_summaries(self):
        try:
            # Aliases for conditional joins
            srt_alias = aliased(SRT)
            unit_alias = aliased(Unit)
            department_alias = aliased(Department)
            thematic_area_alias = aliased(ThematicArea)
            workplan_source_alias = aliased(WorkPlanSource)

            # Define the case statement for dynamically determining the implementing team
            implementing_team = sqlalchemy.case(
                (WorkPlan.initiating_srt_id != None, srt_alias.name),
                (WorkPlan.initiating_unit_id != None, unit_alias.name),
                (WorkPlan.initiating_department_id != None, department_alias.name),
                (WorkPlan.initiating_thematic_area_id != None, thematic_area_alias.name),
                else_="Unknown").label("implementing_team")

            # Query trips with necessary joins and filter by status
            trips = self.db_session.query(
                Trip,
                implementing_team,
                workplan_source_alias.name.label("workplan_source_name"),
                WorkPlan.id.label("work_plan_id")
            ).join(
                Trip.work_plans
            ).outerjoin(
                srt_alias, WorkPlan.initiating_srt_id == srt_alias.id
            ).outerjoin(
                unit_alias, WorkPlan.initiating_unit_id == unit_alias.id
            ).outerjoin(
                department_alias, WorkPlan.initiating_department_id == department_alias.id
            ).outerjoin(
                thematic_area_alias, WorkPlan.initiating_thematic_area_id == thematic_area_alias.id
            ).join(
                workplan_source_alias, WorkPlan.workplan_source_id == workplan_source_alias.id
            ).options(
                joinedload(Trip.driver).joinedload(Driver.user).joinedload(User.employee),
                joinedload(Trip.vehicle),
                joinedload(Trip.work_plans).joinedload(WorkPlan.activity_lead),
                joinedload(Trip.work_plans).joinedload(WorkPlan.locations),
                joinedload(Trip.work_plans).joinedload(WorkPlan.sites)
            ).distinct(WorkPlan.id).all()  # Ensure distinctness based on work_plan_id

            # Build trip summaries
            trip_summaries = []

            for trip, team, source_name, work_plan_id in trips:
                employees = [f"{emp.first_name} {emp.last_name}" for wp in trip.work_plans for emp in wp.employees]
                locations = list(set(loc.name for wp in trip.work_plans for loc in wp.locations))
                sites = list(set(site.name for wp in trip.work_plans for site in wp.sites))
                trip_lead = next((f"{lead.activity_lead.first_name} {lead.activity_lead.last_name}" for lead in trip.work_plans if lead.activity_lead), "No lead assigned")
                driver_name = f"{trip.driver.user.employee.first_name} {trip.driver.user.employee.last_name}" if trip.driver and trip.driver.user and trip.driver.user.employee else "Driver details not available"

                formatted_actual_start_time = trip.actual_start_time.strftime('%H:%M %p') if trip.actual_start_time else "Not started"

                trip_summary = {
                    "work_plan_id": work_plan_id,
                    "activity_title": next((wp.activity_title for wp in trip.work_plans), "No title"),
                    "workplan_code": next((wp.workplan_code for wp in trip.work_plans if wp.workplan_code), "No code"),
                    "trip_start_time": trip.start_time.strftime('%H:%M %p') if trip.start_time else "No start time",
                    "actual_start_time": formatted_actual_start_time,
                    "activity_date": min(wp.activity_date for wp in trip.work_plans).strftime('%Y-%m-%d'),
                    "workplan_source_name": source_name,
                    "implementing_team": team,
                    "trip_status": trip.status,
                    "trip_lead": trip_lead,
                    "employee_names": employees,
                    "vehicle_name": trip.vehicle.name,
                    "vehicle_license_plate": trip.vehicle.licence_plate,
                    "driver_name": driver_name,
                    "location_names": locations,
                    "site_names": sites
                }
                trip_summaries.append(trip_summary)

            return trip_summaries


        except Exception as e:
            # Handle unexpected errors
            return {"error": "An error occurred while fetching trip summaries", "details": str(e)}


    # def start_trip(self, trip_id: int, tenancy_id:int):
    #     # Fetch the trip based on trip_id
    #     trip = self.db_session.query(Trip).filter_by(id=trip_id, tenancy_id=tenancy_id).first()

    #     if not trip:
    #         raise HTTPException(status_code=404, detail="Trip not found.")
    #     if trip.mileage_at_start is not None:
    #         raise HTTPException(status_code=400, detail="Trip has already been started.")

    #     # Check if today's date matches the trip's activity date
    #     today = datetime.now(timezone.utc).date()
    #     if trip.activity_date != today:
    #         raise HTTPException(status_code=400, detail="Trip can only be started on its activity date.")

    #     # Fetch the associated vehicle directly from the relationship
    #     vehicle = trip.vehicle  # Accessing directly since now we have a direct relationship

    #     #Fetch the associated vehicle directly from the relationship
    #     driver = trip.driver 

    #     if not vehicle:
    #         raise HTTPException(status_code=404, detail="Associated vehicle not found.")

    #     if  not driver: 
    #         raise HTTPException(status_code=404, detail="Associated driver not found.")
    #     # Generate trip code
    #     # trip_code = f"TRP-{trip_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    #     trip_code = f"TRP-{trip_id}-{datetime.now(timezone.utc).strftime('%y%m%d%H%M')}"

    #     # Update trip details
    #     try:
    #         trip.trip_code = trip_code
    #         trip.mileage_at_start = vehicle.current_mileage
    #         trip.actual_start_time = datetime.now(timezone.utc)
    #         vehicle.is_available = False  # Set vehicle availability to false as the trip starts
    #         driver.is_available = False # Set driver availability status to false as the trip starts
    #         trip.status = "Trip Started"

    #         self.db_session.commit()
    #         return {
    #             "message": f"Trip with Code: {trip_code} started successfully with a starting mileage of {vehicle.current_mileage}.",
    #             "trip_code": trip_code,
    #             "actual_start_time": trip.actual_start_time.strftime("%Y-%m-%d %H:%M:%S"),
    #             "vehicle_availability_status": "Unavailable"
    #         }
    #     except sqlalchemy.exc.SQLAlchemyError as e:
    #         self.db_session.rollback()
    #         raise HTTPException(status_code=500,  detail=str(e))

    def start_trip(self, trip_id: int, tenancy_id: int):
        # Fetch the trip based on trip_id and tenancy_id
        trip = self.db_session.query(Trip).filter_by(id=trip_id, tenancy_id=tenancy_id).first()

        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found.")
        if trip.mileage_at_start is not None:
            raise HTTPException(status_code=400, detail="Trip has already been started.")

        # Check if today's date matches the trip's activity date
        today = datetime.datetime.now(datetime.timezone.utc).date()
        if not any(wp.activity_date == today for wp in trip.work_plans):
            raise HTTPException(status_code=400, detail="Trip can only be started on its activity date.")

        # Fetch the associated vehicle and driver directly from the relationship
        vehicle = trip.vehicle
        driver = trip.driver

        if not vehicle:
            raise HTTPException(status_code=404, detail="Associated vehicle not found.")
        if not driver:
            raise HTTPException(status_code=404, detail="Associated driver not found.")

        # Generate trip code
        trip_code = f"TRP-{trip_id}-{datetime.datetime.now(datetime.timezone.utc).strftime('%y%m%d%H%M')}"

        # Update trip details
        try:
            trip.trip_code = trip_code
            trip.mileage_at_start = vehicle.current_mileage
            trip.actual_start_time = datetime.datetime.now(datetime.timezone.utc)
            vehicle.is_available = False  # Set vehicle availability to false as the trip starts
            driver.is_available = False  # Set driver availability status to false as the trip starts
            trip.status = "Trip Started"

            self.db_session.commit()
            return {
                "message": f"Trip with Code: {trip_code} started successfully with a starting mileage of {vehicle.current_mileage}.",
                "trip_code": trip_code,
                "actual_start_time": trip.actual_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "vehicle_availability_status": "Unavailable"
            }
        except sqlalchemy.exc.SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=str(e))



    def end_trip(self, trip_id: int, mileage_end: float, tenancy_id):
        # Fetch the trip based on trip_id
        trip = self.db_session.query(Trip).filter_by(id=trip_id,tenancy_id=tenancy_id).first()
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found.")
        if trip.mileage_at_end is not None:
            raise HTTPException(status_code=400, detail="Trip has already been ended.")
        if trip.mileage_at_start is None:
            raise HTTPException(status_code=400, detail="Trip has not been started.")

        # Ensure mileage_end is valid
        mileage_at_start = float(trip.mileage_at_start)
        if mileage_end <= mileage_at_start:
            raise HTTPException(status_code=400, detail="End mileage cannot be less than start mileage.")

        # Access the vehicle directly through the relationship
        vehicle = trip.vehicle
        if not vehicle:
            raise HTTPException(status_code=404, detail="Associated vehicle not found.")

        # Validate fuel economy
        if vehicle.fuel_economy is None or float(vehicle.fuel_economy) <= 0:
            raise HTTPException(status_code=400, detail="Invalid or unspecified vehicle fuel economy. Fuel economy must be a positive number.")

        # Calculate the distance traveled and the fuel consumed
        distance_traveled = mileage_end - mileage_at_start
        fuel_economy = float(vehicle.fuel_economy)  # Convert Decimal to float
        fuel_consumed = distance_traveled / fuel_economy

        # Update trip details
        try:
            trip.status = "Trip Ended"
            trip.mileage_at_end = mileage_end
            trip.distance = distance_traveled
            trip.fuel_consumed = fuel_consumed
            trip.end_time = datetime.now()

            # Update the vehicle's current mileage and set it to available
            vehicle.current_mileage = mileage_end
            vehicle.is_available = True

            # Access the driver directly through the relationship and set availability
            if trip.driver:
                trip.driver.is_available = True

            
            self.db_session.commit()
            return {
                "message": "Trip ended successfully.",
                "trip_code": trip.trip_code,
                "end_mileage": mileage_end,
                "distance_traveled": distance_traveled,
                "estimated_fuel_consumed": f"{fuel_consumed:.2f} liters"
            }
        except sqlalchemy.exc.SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=str(e))


    def assign_vehicle_and_driver_to_workplan(
        self,
        work_plan_ids: list, 
        vehicle_id: int, 
        driver_id: int,
        tenancy_id: int,
        auto_group_weekly: bool,
        background_tasks
    ):
        vehicle = self.db_session.query(Vehicle).filter_by(id=vehicle_id, is_available=True, tenancy_id=tenancy_id).first()
        driver = self.db_session.query(Driver).filter_by(id=driver_id, is_available=True, tenancy_id=tenancy_id).first()

        if not vehicle:
            raise HTTPException(status_code=400, detail="Vehicle is not available.")

        if not driver:
            raise HTTPException(status_code=400, detail="Driver is not available.")

        active_trip = self.db_session.query(Trip).filter_by(driver_id=driver.id, end_time=None, tenancy_id=tenancy_id).first()
        if active_trip and active_trip.actual_start_time is not None:
            raise HTTPException(status_code=400, detail="Driver is already on another active trip.")

        work_plans = self.db_session.query(WorkPlan).filter(WorkPlan.id.in_(work_plan_ids), WorkPlan.is_approved==True, WorkPlan.tenancy_id==tenancy_id).all()
        if not work_plans:
            raise HTTPException(status_code=404, detail="One or more WorkPlans not found or not approved.")

        if len(set(wp.activity_date for wp in work_plans)) > 1:
            raise HTTPException(status_code=400, detail="All work plans must have the same activity date.")

        if auto_group_weekly:
            group_ids = {wp.group_id for wp in work_plans}
            grouped_work_plans = self.db_session.query(WorkPlan).filter(
                WorkPlan.group_id.in_(group_ids), 
                WorkPlan.tenancy_id == tenancy_id
            ).all()
        else:
            grouped_work_plans = work_plans

        date_grouped_workplans = {}
        for wp in grouped_work_plans:
            if wp.activity_date not in date_grouped_workplans:
                date_grouped_workplans[wp.activity_date] = []
            date_grouped_workplans[wp.activity_date].append(wp)

        trip_ids = []
        trip_details_list = []
        for date, daily_work_plans in date_grouped_workplans.items():
            total_employees = sum(len(wp.employees) for wp in daily_work_plans)
            trip = self.db_session.query(Trip).filter_by(
                vehicle_id=vehicle_id, 
                start_time=date,
                tenancy_id=tenancy_id
            ).one_or_none()

            if trip is None or (sum(len(wp.employees) for wp in trip.work_plans) + total_employees > vehicle.seat_capacity):
                if total_employees > vehicle.seat_capacity:
                    raise HTTPException(status_code=400, detail=f"Total number of employees exceeds vehicle's seating capacity for {date}.")
                trip = Trip(driver_id=driver.id, vehicle_id=vehicle_id, start_time=date, tenancy_id=tenancy_id,)
                self.db_session.add(trip)
                self.db_session.flush()  # Ensure trip ID is generated before proceeding
                trip_ids.append(trip.id)

            workplan_codes = []
            for work_plan in daily_work_plans:
                if not self.db_session.query(trip_workplan_association).filter_by(trip_id=trip.id, work_plan_id=work_plan.id).one_or_none():
                    self.db_session.execute(trip_workplan_association.insert().values(trip_id=trip.id, work_plan_id=work_plan.id))
                    workplan_codes.append(work_plan.workplan_code)
                    work_plan.vehicle_assigned = True  # Set vehicle_assigned to True when assigned

            trip_details_list.append({"trip_id": trip.id, "workplan_codes": workplan_codes})
       
        vehicle.is_available = driver.is_available = sum(len(wp.employees) for wp in trip.work_plans) < vehicle.seat_capacity
        #vehicle.is_available = driver.is_available = False
        #wp.vehicle_assigned=True
        self.db_session.commit()

        # Send email notifications
        driver_name = f"{driver.user.employee.first_name} {driver.user.employee.last_name}"
        trip_info = {
            "take_off_time": trip.start_time.strftime('%H:%M %p'),
            "driver_name": driver_name,
            "vehicle_info": f"{vehicle.make} {vehicle.licence_plate}"
        }
        employee_emails = [(emp.first_name, emp.employee_email) for wp in grouped_work_plans for emp in wp.employees]
        background_tasks.add_task(notify_employees_about_trip, employee_emails, trip_info)
        background_tasks.add_task(notify_trip_creation, employee_emails, trip.start_time, driver_name, driver.licence_number, vehicle.name, vehicle.licence_plate, ", ".join(set(wp.activity_title for wp in grouped_work_plans)), trip.start_time.strftime('%Y-%m-%d'))

        return {"message": "Trips created or updated successfully.", "trip_ids": trip_ids, "trip_details": trip_details_list}


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

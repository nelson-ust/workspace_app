# trip_report_repository.py
from datetime import datetime, timedelta, timezone
import logging
import os
import sqlalchemy
from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy.exc import SQLAlchemyError, NoResultFound, MultipleResultsFound
#from sqlalchemy.orm import NoResultFound, MultipleResultsFound
import shutil
from fastapi import HTTPException, UploadFile
from models.all_models import SRT, Department, Driver, IssueLog, ThematicArea, TripReport, Trip, Unit, User, WorkPlan,Employee, WorkPlanSource, workplan_employee_association
from typing import Dict, Optional,List
from sqlalchemy.orm import joinedload
from logging_helpers import logging_helper
from schemas.trip_report_schemas import IssueDetail
workplan_employee_association

class TripReportRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session


    # def submit_trip_report(
    #     self,
    #     trip_id: int,
    #     workplan_id: int,
    #     document: Optional[UploadFile] = None,
    #     summary: Optional[str] = None,
    #     trip_outcome: Optional[str] = None,
    #     observations: Optional[str] = None,
    #     issue_identified: Optional[bool] = None,
    #     trip_completed: Optional[bool] = None,
    #     reason: Optional[str] = None,
    #     site_ids: Optional[List[int]] = None,
    #     issues: Optional[List[IssueDetail]] = None  # List of issues
    # ):
    #     try:
    #         logging_helper.log_info("Starting the process of submitting a trip report.")
    #         # Validate the existence of trip and work plan
    #         trip = self.db_session.query(Trip).filter(Trip.id == trip_id).first()
    #         work_plan = self.db_session.query(WorkPlan).filter(WorkPlan.id == workplan_id).first()
    #         if not trip:
    #             logging_helper.log_error(f"Trip not found for trip_id: {trip_id}")
    #             raise HTTPException(status_code=404, detail="Trip not found")
    #         if not work_plan:
    #             logging_helper.log_error(f"WorkPlan not found for workplan_id: {workplan_id}")
    #             raise HTTPException(status_code=404, detail="Associated WorkPlan not found")

    #         logging_helper.log_info(f"Validated trip and work plan existence for trip_id: {trip_id}, workplan_id: {workplan_id}")

    #         # Check for existing submitted report
    #         existing_report = self.db_session.query(TripReport).filter(
    #             TripReport.workplan_id == work_plan.id, TripReport.is_submitted == True).first()
    #         if existing_report:
    #             logging_helper.log_error(f"A report for this Activity with workplan_id: {workplan_id} has already been submitted")
    #             raise HTTPException(status_code=400, detail=f"A report for this Activity with WorkPlan ID: {workplan_id} has already been submitted")

    #         if trip_completed:
    #             if not document:
    #                 logging_helper.log_error("Document must be provided if the trip is completed")
    #                 raise HTTPException(status_code=400, detail="Document must be provided if the trip is completed")
    #             # Save the document
    #             file_directory = "./trip_reports"
    #             os.makedirs(file_directory, exist_ok=True)
    #             file_location = f"{file_directory}/{document.filename}"
    #             with open(file_location, "wb") as file_object:
    #                 shutil.copyfileobj(document.file, file_object)
    #             document.file.close()

    #             logging_helper.log_info(f"Document saved at location: {file_location}")

    #             # Create a completed TripReport
    #             trip_report = TripReport(
    #                 file_path=file_location,
    #                 trip_id=trip_id,
    #                 workplan_id=work_plan.id,
    #                 tenancy_id=trip.tenancy_id,
    #                 is_submitted=True,
    #                 trip_outcome=trip_outcome,
    #                 observations=observations,
    #                 summary=summary,
    #                 issue_identified=issue_identified,
    #                 trip_completed=True
    #             )
    #             # Generate report code
    #             report_code = f"TREPT-{trip_report.id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    #             trip_report.report_code = report_code
    #             self.db_session.add(trip_report)
    #             logging_helper.log_info(f"Trip report created and report code generated: {report_code}")

    #             # Handle identified issues
    #             if issue_identified and issues:
    #                 for issue, site_id in zip(issues, site_ids):
    #                     issue_log = IssueLog(
    #                         issue="Issue identified in trip report",
    #                         issue_description=issue.issue_description,
    #                         reported_by_id=work_plan.activity_lead_id,
    #                         thematic_area_id=work_plan.initiating_thematic_area_id,
    #                         site_id=site_id,
    #                         source_id=1,
    #                         status_id=issue.status_id,
    #                         date_reported=datetime.now(),
    #                         time_line_date=issue.time_line_date,
    #                         key_recommendation=issue.key_recommendation,
    #                         tenancy_id=trip.tenancy_id
    #                     )
    #                     if issue.focal_persons:
    #                         issue_log.employees = [self.db_session.query(Employee).get(fp) for fp in issue.focal_persons]
    #                     self.db_session.add(issue_log)
    #                     logging_helper.log_info(f"Issue log created for site_id: {site_id}")

    #         else:
    #             if not reason:
    #                 logging_helper.log_error("Reason must be provided if the trip is not completed")
    #                 raise HTTPException(status_code=400, detail="Reason must be provided if the trip is not completed")
    #             # Create an incomplete TripReport
    #             trip_report = TripReport(
    #                 trip_id=trip_id,
    #                 workplan_id=work_plan.id,
    #                 tenancy_id=trip.tenancy_id,
    #                 is_submitted=False,
    #                 trip_completed=False,
    #                 reason=reason
    #             )
    #             self.db_session.add(trip_report)
    #             logging_helper.log_info(f"Incomplete trip report created for trip_id: {trip_id}")

    #         # Commit changes
    #         self.db_session.commit()
    #         logging_helper.log_info("Trip report committed to the database.")

    #         # Update is_report_submitted for all WorkPlans in the same group
    #         if work_plan.group_id:
    #             self.db_session.query(WorkPlan).filter(
    #                 WorkPlan.group_id == work_plan.group_id
    #             ).update({WorkPlan.is_report_submitted: True}, synchronize_session='fetch')
    #             self.db_session.commit()
    #             logging_helper.log_info(f"Updated is_report_submitted for all work plans in group_id: {work_plan.group_id}")

    #         return {"message": "Trip report submitted successfully", "trip_report_id": trip_report.id}

    #     except SQLAlchemyError as e:
    #         self.db_session.rollback()
    #         logging_helper.log_error(f"SQLAlchemy error: {str(e)}")
    #         raise HTTPException(status_code=500, detail=f"SQLAlchemy error: {str(e)}")
    #     except Exception as e:
    #         self.db_session.rollback()
    #         logging_helper.log_error(f"An error occurred: {str(e)}")
    #         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


    def submit_trip_report(
        self,
        trip_id: int,
        workplan_id: int,
        document: Optional[UploadFile] = None,
        summary: Optional[str] = None,
        trip_outcome: Optional[str] = None,
        observations: Optional[str] = None,
        issue_identified: Optional[bool] = None,
        trip_completed: Optional[bool] = None,
        reason: Optional[str] = None,
        issue_description: Optional[str] = None,
        site_ids: Optional[List[int]] = None,
        status_id: Optional[int] = None,
        time_line_date: Optional[datetime] = None,
        key_recommendation: Optional[str] = None,
        focal_persons: Optional[List[int]] = None  # Updated to accept a list of focal persons
    ):
        try:
            logging_helper.log_info("Starting the process of submitting a trip report.")
            # Validate the existence of trip and work plan
            trip = self.db_session.query(Trip).filter(Trip.id == trip_id).first()
            work_plan = self.db_session.query(WorkPlan).filter(WorkPlan.id == workplan_id).first()
            if not trip:
                logging_helper.log_error(f"Trip not found for trip_id: {trip_id}")
                raise HTTPException(status_code=404, detail="Trip not found")
            if not work_plan:
                logging_helper.log_error(f"WorkPlan not found for workplan_id: {workplan_id}")
                raise HTTPException(status_code=404, detail="Associated WorkPlan not found")

            logging_helper.log_info(f"Validated trip and work plan existence for trip_id: {trip_id}, workplan_id: {workplan_id}")

            # Check for existing submitted report
            existing_report = self.db_session.query(TripReport).filter(
                TripReport.workplan_id == work_plan.id, TripReport.is_submitted == True).first()
            if existing_report:
                logging_helper.log_error(f"A report for this Activity with workplan_id: {workplan_id} has already been submitted")
                raise HTTPException(status_code=400, detail=f"A report for this Activity with WorkPlan ID: {workplan_id} has already been submitted")

            if trip_completed:
                if not document:
                    logging_helper.log_error("Document must be provided if the trip is completed")
                    raise HTTPException(status_code=400, detail="Document must be provided if the trip is completed")
                # Save the document
                file_directory = "./trip_reports"
                os.makedirs(file_directory, exist_ok=True)
                file_location = f"{file_directory}/{document.filename}"
                with open(file_location, "wb") as file_object:
                    shutil.copyfileobj(document.file, file_object)
                document.file.close()

                logging_helper.log_info(f"Document saved at location: {file_location}")

                # Create a completed TripReport
                trip_report = TripReport(
                    file_path=file_location,
                    trip_id=trip_id,
                    workplan_id=work_plan.id,
                    tenancy_id=trip.tenancy_id,
                    is_submitted=True,
                    trip_outcome=trip_outcome,
                    observations=observations,
                    summary=summary,
                    issue_identified=issue_identified,
                    trip_completed=True
                )
                # Generate report code
                report_code = f"TREPT-{trip_report.id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
                trip_report.report_code = report_code
                self.db_session.add(trip_report)
                logging_helper.log_info(f"Trip report created and report code generated: {report_code}")

                # Handle identified issues
                if issue_identified and site_ids:
                    for site_id in site_ids:
                        issue_log = IssueLog(
                            issue="Issue identified during trip.",
                            issue_description=issue_description,
                            reported_by_id=work_plan.activity_lead_id,
                            thematic_area_id=work_plan.initiating_thematic_area_id,
                            #srt_id=work_plan.initiating_srt_id,
                            unit_id=work_plan.initiating_unit_id,
                            #department_id=work_plan.initiating_department_id,
                            site_id=site_id,
                            source_id=1,
                            status_id=status_id,
                            date_reported=datetime.now(),
                            time_line_date=time_line_date,
                            key_recommendation=key_recommendation,
                            tenancy_id=trip.tenancy_id
                        )
                        if focal_persons:
                            issue_log.employees = [self.db_session.query(Employee).get(fp) for fp in focal_persons]
                        self.db_session.add(issue_log)
                        logging_helper.log_info(f"Issue log created for site_id: {site_id}")

            else:
                if not reason:
                    logging_helper.log_error("Reason must be provided if the trip is not completed")
                    raise HTTPException(status_code=400, detail="Reason must be provided if the trip is not completed")
                # Create an incomplete TripReport
                trip_report = TripReport(
                    trip_id=trip_id,
                    workplan_id=work_plan.id,
                    tenancy_id=trip.tenancy_id,
                    is_submitted=False,
                    trip_completed=False,
                    reason=reason
                )
                self.db_session.add(trip_report)
                logging_helper.log_info(f"Incomplete trip report created for trip_id: {trip_id}")

            # Commit changes
            self.db_session.commit()
            logging_helper.log_info("Trip report committed to the database.")

            # Update is_report_submitted for all WorkPlans in the same group
            if work_plan.group_id:
                self.db_session.query(WorkPlan).filter(
                    WorkPlan.group_id == work_plan.group_id
                ).update({WorkPlan.is_report_submitted: True}, synchronize_session='fetch')
                self.db_session.commit()
                logging_helper.log_info(f"Updated is_report_submitted for all work plans in group_id: {work_plan.group_id}")

            return {"message": "Trip report submitted successfully", "trip_report_id": trip_report.id}

        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"SQLAlchemy error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"SQLAlchemy error: {str(e)}")
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"An error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


    def get_trip_report_by_id(self, trip_report_id: int):
        """
        Retrieves a trip report based on its ID.

        Args:
            trip_report_id (int): The ID of the trip report to retrieve.

        Returns:
            A dictionary containing trip report details if found, otherwise raises HTTPException.

        Raises:
            HTTPException: If the trip report is not found.
        """
        try:
        # Query the database for the trip report
            trip_report = self.db_session.query(TripReport).filter(TripReport.id == trip_report_id).first()
            
            # If no trip report is found, raise an HTTPException
            if not trip_report:
                raise HTTPException(status_code=404, detail="Trip report not found")

            # Return a dictionary with details of the trip report
            return {
                "id": trip_report.id,
                "report_code": trip_report.report_code,
                "trip_id": trip_report.trip_id,
                "workplan_id": trip_report.workplan_id,
                "tenancy_id": trip_report.tenancy_id,
                "is_submitted": trip_report.is_submitted,
                "trip_outcome": trip_report.trip_outcome,
                "observations": trip_report.observations,
                "summary": trip_report.summary,
                "issue_identified": trip_report.issue_identified
            }
        except Exception as e:
            # Handle unexpected errors
            self.db_session.rollback()  # Ensure any failed transaction is rolled back
            raise HTTPException(status_code=500, detail=f"An error occurred while fetching the Trip Report with id {trip_report_id}: {str(e)}")


    def get_all_trip_reports(self) -> List[dict]:
        """Retrieve all trip reports with associated work plans and employee details."""
        try:
            trip_reports = self.db_session.query(TripReport).options(
                joinedload(TripReport.work_plan).joinedload(WorkPlan.employees)
            ).all()

            results = []
            for report in trip_reports:
                # Handling the situation when work_plan might not be iterable
                work_plans = []
                if report.work_plan:
                    work_plans.append({
                        "workplan_code": report.work_plan.workplan_code,
                        "activity_title": report.work_plan.activity_title,
                        "activity_date": report.work_plan.activity_date.isoformat(),
                        "employees": [{"name": f"{emp.first_name} {emp.last_name}"} for emp in report.work_plan.employees]
                    })

                results.append({
                    "trip_report_id": report.id,
                    "trip_report_code": report.report_code,
                    "trip_id": report.trip_id,
                    "workplan_details": work_plans,
                    "summary": report.summary,
                    "observations": report.observations,
                    "trip_outcome": report.trip_outcome,
                    "issue_identified": report.issue_identified,
                    "date_submitted": report.date_created
                })
            return results
        except Exception as e:
            # Handle unexpected errors gracefully
            raise Exception(f"An error occurred while fetching trip reports: {str(e)}")
        

    def get_trip_report_file_path(self, workplan_id: int) -> str:
        """Retrieve the file path for a given WorkPlan ID, or for any trip report in the same group if the specific report isn't found."""
        try:
            # Fetch the WorkPlan to verify the group_id
            work_plan = self.db_session.query(WorkPlan).filter(WorkPlan.id == workplan_id).one_or_none()
            if not work_plan:
                raise ValueError("WorkPlan not found")

            # Try to find the TripReport directly associated with the given WorkPlan ID
            trip_report = (
                self.db_session.query(TripReport)
                .filter(TripReport.workplan_id == workplan_id)
                .one_or_none()
            )

            # If not found, try to find any TripReport in the same group that is submitted
            if not trip_report and work_plan.group_id:
                trip_report = (
                    self.db_session.query(TripReport)
                    .join(WorkPlan, WorkPlan.group_id == work_plan.group_id)
                    .filter(WorkPlan.group_id == work_plan.group_id, TripReport.is_submitted == True)
                    .first()
                )

            if not trip_report:
                raise ValueError("No Trip Report found for the given WorkPlan ID.")

            if not trip_report.file_path:
                raise ValueError("File path for the Trip Report is not available.")

            return trip_report.file_path

        except NoResultFound:
            raise Exception("No Trip Report or WorkPlan found with the given IDs.")
        except MultipleResultsFound:
            raise Exception("Multiple entries found. Data inconsistency detected.")
        except Exception as e:
            raise Exception(f"An error occurred while downloading the file: {str(e)} It seem The Trip did not Hold")



    # def get_completed_trips_without_reports(self):
    #     logging_helper.log_info("Fetching completed trips without trip reports")
    #     try:
    #         # Query to find completed trips with no trip reports turned in
    #         completed_trips = (
    #             self.db_session.query(Trip)
    #             .outerjoin(TripReport, TripReport.trip_id == Trip.id)
    #             .filter(Trip.end_time.isnot(None))
    #             .filter(TripReport.id.is_(None))  # No TripReport associated
    #             .all()
    #         )

    #         logging_helper.log_info(f"Found {len(completed_trips)} completed trips without trip reports")

    #         results = []
    #         for trip in completed_trips:
    #             workplans = trip.work_plans
    #             for workplan in workplans:
    #                 employee_details = [
    #                     {"name": f"{emp.first_name} {emp.last_name}", "email": emp.employee_email}
    #                     for emp in workplan.employees
    #                 ]
    #                 results.append({
    #                     "work_plan_id": workplan.id,
    #                     "workplan_code": workplan.workplan_code,
    #                     "activity_title": workplan.activity_title,
    #                     "trip_id": trip.id,
    #                     "trip_code": trip.trip_code,
    #                     "trip_end_time": trip.end_time,
    #                     "employees": employee_details
    #                 })

    #         logging_helper.log_info("Successfully fetched completed trips without trip reports")
    #         return results
    #     except Exception as e:
    #         logging_helper.log_error(f"An error occurred while fetching completed trips without trip reports: {str(e)}")
    #         raise Exception(f"An error occurred: {str(e)}")

    def get_completed_trips_without_reports(self, tenancy_id: Optional[int] = None):
        logging_helper.log_info("Fetching completed trips without trip reports")
        try:
            # Base query to find completed trips with no trip reports turned in
            query = self.db_session.query(Trip).outerjoin(TripReport, TripReport.trip_id == Trip.id).filter(
                Trip.end_time.isnot(None),
                TripReport.id.is_(None)  # No TripReport associated
            )

            # Filter by tenancy_id if provided
            if tenancy_id:
                query = query.filter(Trip.tenancy_id == tenancy_id)

            completed_trips = query.all()

            logging_helper.log_info(f"Found {len(completed_trips)} completed trips without trip reports")

            results = []
            for trip in completed_trips:
                workplans = trip.work_plans
                for workplan in workplans:
                    employee_details = [
                        {"name": f"{emp.first_name} {emp.last_name}", "email": emp.employee_email}
                        for emp in workplan.employees
                    ]
                    results.append({
                        "work_plan_id": workplan.id,
                        "workplan_code": workplan.workplan_code,
                        "activity_title": workplan.activity_title,
                        "trip_id": trip.id,
                        "trip_code": trip.trip_code,
                        "trip_end_time": trip.end_time,
                        "employees": employee_details
                    })

            logging_helper.log_info("Successfully fetched completed trips without trip reports")
            return results
        except Exception as e:
            logging_helper.log_error(f"An error occurred while fetching completed trips without trip reports: {str(e)}")
            raise Exception(f"An error occurred: {str(e)}")
        

    # def get_trips_without_reports_details(self, tenancy_id: Optional[int] = None) -> List[Dict]:
    #     """
    #     Retrieves details of all trips without a submitted report, regardless of completion status.

    #     Args:
    #         tenancy_id (Optional[int]): The ID of the tenancy to filter by, if applicable.

    #     Returns:
    #         List[dict]: A list of dictionaries containing trip and work plan details.
    #     """
    #     logging_helper.log_info("Fetching details of trips without submitted reports")
    #     try:
    #         # Base query to find trips with no trip reports turned in
    #         query = (
    #             self.db_session.query(Trip)
    #             .outerjoin(TripReport, TripReport.trip_id == Trip.id)
    #             .filter(TripReport.id.is_(None))
    #         )

    #         # Filter by tenancy_id if provided
    #         if tenancy_id:
    #             query = query.filter(Trip.tenancy_id == tenancy_id)

    #         trips_without_reports = query.all()
    #         logging_helper.log_info(f"Found {len(trips_without_reports)} trips without trip reports")

    #         results = []
    #         for trip in trips_without_reports:
    #             workplans = trip.work_plans
    #             driver_fullname = f"{trip.driver.user.employee.first_name} {trip.driver.user.employee.last_name}" if trip.driver and trip.driver.user and trip.driver.user.employee else "Driver details not available"
    #             vehicle_details = {
    #                 "vehicle_id": trip.vehicle.id if trip.vehicle else None,
    #                 "vehicle_name": trip.vehicle.name if trip.vehicle else "Vehicle details not available",
    #                 "vehicle_license_plate": trip.vehicle.licence_plate if trip.vehicle else "Vehicle details not available"
    #             }
    #             for workplan in workplans:
    #                 employee_details = [
    #                     {"id": emp.id, "name": f"{emp.first_name} {emp.last_name}", "email": emp.employee_email}
    #                     for emp in workplan.employees
    #                 ]
    #                 location_details = [
    #                     {"location_id": loc.id, "location_name": loc.name}
    #                     for loc in workplan.locations
    #                 ]
    #                 site_details = [
    #                     {"site_id": site.id, "site_name": site.name}
    #                     for site in workplan.sites
    #                 ]
    #                 results.append({
    #                     "work_plan_id": workplan.id,
    #                     "workplan_code": workplan.workplan_code,
    #                     "activity_title": workplan.activity_title,
    #                     "trip_id": trip.id,
    #                     "trip_code": trip.trip_code,
    #                     "trip_status": trip.status,
    #                     "driver_id": trip.driver_id,
    #                     "driver_fullname": driver_fullname,
    #                     "vehicle_details": vehicle_details,
    #                     "employees": employee_details,
    #                     "locations": location_details,
    #                     "sites": site_details
    #                 })

    #         logging_helper.log_info("Successfully fetched details of trips without submitted reports")
    #         return results
    #     except Exception as e:
    #         logging_helper.log_error(f"An error occurred while fetching details of trips without submitted reports: {str(e)}")
    #         raise Exception(f"An error occurred: {str(e)}")


    def get_trips_without_reports_details(self, tenancy_id: Optional[int] = None) -> List[Dict]:
        """
        Retrieves details of all trips without a submitted report, regardless of completion status.

        Args:
            tenancy_id (Optional[int]): The ID of the tenancy to filter by, if applicable.

        Returns:
            List[dict]: A list of dictionaries containing trip and work plan details.
        """
        logging_helper.log_info("Fetching details of trips without submitted reports")
        try:
            # Base query to find trips with no trip reports turned in
            query = (
                self.db_session.query(Trip)
                .outerjoin(TripReport, TripReport.trip_id == Trip.id)
                .filter(TripReport.id.is_(None))
            )

            # Filter by tenancy_id if provided
            if tenancy_id:
                query = query.filter(Trip.tenancy_id == tenancy_id)

            trips_without_reports = query.all()
            logging_helper.log_info(f"Found {len(trips_without_reports)} trips without trip reports")

            results = []
            for trip in trips_without_reports:
                workplans = trip.work_plans
                driver_fullname = f"{trip.driver.user.employee.first_name} {trip.driver.user.employee.last_name}" if trip.driver and trip.driver.user and trip.driver.user.employee else "Driver details not available"
                vehicle_details = {
                    "vehicle_id": trip.vehicle.id if trip.vehicle else None,
                    "vehicle_name": trip.vehicle.name if trip.vehicle else "Vehicle details not available",
                    "vehicle_license_plate": trip.vehicle.licence_plate if trip.vehicle else "Vehicle details not available"
                }
                for workplan in workplans:
                    employee_details = [
                        {"id": emp.id, "name": f"{emp.first_name} {emp.last_name}", "email": emp.employee_email}
                        for emp in workplan.employees
                    ]
                    location_details = [
                        {"location_id": loc.id, "location_name": loc.name}
                        for loc in workplan.locations
                    ]
                    site_details = [
                        {"site_id": site.id, "site_name": site.name}
                        for site in workplan.sites
                    ]
                    results.append({
                        "work_plan_id": workplan.id,
                        "workplan_code": workplan.workplan_code,
                        "activity_title": workplan.activity_title,
                        "trip_id": trip.id,
                        "trip_code": trip.trip_code,
                        "trip_status": trip.status,
                        "driver_id": trip.driver_id,
                        "driver_fullname": driver_fullname,
                        "vehicle_details": vehicle_details,
                        "employees": employee_details,
                        "locations": location_details,
                        "sites": site_details
                    })

            logging_helper.log_info("Successfully fetched details of trips without submitted reports")
            return results
        except Exception as e:
            logging_helper.log_error(f"An error occurred while fetching details of trips without submitted reports: {str(e)}")
            raise Exception(f"An error occurred: {str(e)}")

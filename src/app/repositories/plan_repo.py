import itertools
import random
from typing import List, Optional, Union
from fastapi import BackgroundTasks, HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, case, exists, func, or_
from sqlalchemy.orm import Session, aliased
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import joinedload, selectinload
from models.all_models import (
    SRT,
    Department,
    Driver,
    Trip,
    Unit,
    User,
    Vehicle,
    WorkPlan,
    Site,
    Employee,
    Location,
    WorkPlanSource,
    workplan_employee_association,
    ThematicArea,
    workplan_site_association,
    workplan_location_association,
    trip_workplan_association,
)
from schemas.workplan_schemas import EmployeeModel, WorkPlanCreate, WorkPlanUpdate
from datetime import date, datetime, time, timedelta, timezone

# from datetime import datetime
import logging
from auth.email import (
    notify_driver_about_trip_assignment,
    notify_employees_about_trip,
    notify_initiator_about_work_plan,
    notify_trip_creation,
    notify_work_plan_approval,
    notify_work_plan_creation,
    notify_work_plan_denial,
    notify_work_plan_reschedule,
    notify_work_plan_updates,
    send_driver_trip_details,
)


class WorkPlanRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def generate_work_plan_code(self, work_plan: WorkPlan) -> str:
        # This is just a placeholder
        return f"WP-{work_plan.id}-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    
    def generate_trip_code(self, trip: Trip) -> str:
        # This is just a placeholder
        return f"TP-{trip.id}-{datetime.utcnow().strftime('%Y%m%d%H%M')}"    

    def _find_existing_group(self, work_plan_data: WorkPlanCreate):
        start_of_week = work_plan_data.activity_date - timedelta(
            days=work_plan_data.activity_date.weekday()
        )
        end_of_week = start_of_week + timedelta(days=6)

        query = self.db_session.query(WorkPlan).filter(
            # WorkPlan.initiating_user_id == work_plan_data.initiating_user_id,
            WorkPlan.workplan_source_id == work_plan_data.workplan_source_id,
            WorkPlan.activity_date.between(start_of_week, end_of_week),
        )

        # Check for associated employees
        query = query.filter(
            WorkPlan.employees.any(Employee.id.in_(work_plan_data.employee_ids))
        )

        filters = []
        if work_plan_data.initiating_unit_id:
            filters.append(
                WorkPlan.initiating_unit_id == work_plan_data.initiating_unit_id
            )
        if work_plan_data.initiating_department_id:
            filters.append(
                WorkPlan.initiating_department_id
                == work_plan_data.initiating_department_id
            )
        if work_plan_data.initiating_srt_id:
            filters.append(
                WorkPlan.initiating_srt_id == work_plan_data.initiating_srt_id
            )
        if work_plan_data.initiating_thematic_area_id:
            filters.append(
                WorkPlan.initiating_thematic_area_id
                == work_plan_data.initiating_thematic_area_id
            )

        if filters:
            query = query.filter(or_(*filters))

        earliest_work_plan = query.order_by(WorkPlan.date_created).first()
        return earliest_work_plan

    def _valid_id(self, id_value, model):
        return (
            id_value
            if self.db_session.query(model).filter(model.id == id_value).count() > 0
            else None
        )

    # def check_existing_work_plan(self, work_plan_data: WorkPlanCreate):
    #     """Check for existing work plan based on activity title, source, and date."""
    #     existing_work_plan = self.db_session.query(WorkPlan).filter(
    #         WorkPlan.activity_title == work_plan_data.activity_title,
    #         WorkPlan.workplan_source_id == work_plan_data.workplan_source_id,
    #         WorkPlan.activity_date == work_plan_data.activity_date,

    #     ).first()
    #     return existing_work_plan

    def check_existing_work_plan(self, work_plan_data: WorkPlanCreate):
        """Check for existing work plan based on activity title, source, date, and associated employees."""
        existing_work_plan = self.db_session.query(WorkPlan).filter(
            WorkPlan.activity_title == work_plan_data.activity_title,
            WorkPlan.workplan_source_id == work_plan_data.workplan_source_id,
            WorkPlan.activity_date == work_plan_data.activity_date,
        )

        # Check for associated employees
        existing_work_plan = existing_work_plan.filter(
            WorkPlan.employees.any(Employee.id.in_(work_plan_data.employee_ids))
        )
        return existing_work_plan.first()

    def check_employee_schedule_conflict(self, employee_ids, activity_date):
        """Check if any employee is already assigned to a work plan on the given date."""
        existing_work_plan = (
            self.db_session.query(WorkPlan)
            .join(WorkPlan.employees)
            .filter(
                Employee.id.in_(employee_ids), WorkPlan.activity_date == activity_date
            )
            .first()
        )
        return existing_work_plan

    def create_work_plan(
        self, background_tasks: BackgroundTasks, work_plan_data: WorkPlanCreate
    ):
        STATUS_PENDING = "Pending"
        try:
            # Check for non-empty lists of employee_ids, site_ids, and location_ids
            if not work_plan_data.employee_ids or all(
                id == 0 for id in work_plan_data.employee_ids
            ):
                raise ValueError("At least one valid employee is required.")
            if not work_plan_data.site_ids or all(
                id == 0 for id in work_plan_data.site_ids
            ):
                raise ValueError("At least one valid site is required.")
            if not work_plan_data.location_ids or all(
                id == 0 for id in work_plan_data.location_ids
            ):
                raise ValueError("At least one valid location is required.")

            # Verify the existence of all entities referred by foreign keys
            initiator = (
                self.db_session.query(User)
                .filter(User.id == work_plan_data.initiating_user_id)
                .first()
            )
            if not initiator:
                raise HTTPException(status_code=404, detail="Initiating user not found")

            # Check for report submission issues from previous trips
            over_two_weeks_ago = date.today() - timedelta(days=14)
            employees_with_unsubmitted_reports = self.db_session.query(Employee).join(WorkPlan.employees).filter(
                Employee.id.in_(work_plan_data.employee_ids),
                WorkPlan.activity_date < over_two_weeks_ago,
                WorkPlan.is_report_submitted.is_(False),
                WorkPlan.is_approved.is_(True)
            ).distinct()

            if employees_with_unsubmitted_reports.count() > 0:
                employee_names = ", ".join(f"{emp.first_name} {emp.last_name}" for emp in employees_with_unsubmitted_reports)
                raise HTTPException(
                    status_code=400,
                    detail=f" {employee_names}, who have not submitted their trip report(s) from over two weeks ago Trip embarked on, cannot be added to this workplan. Kndly drop them to Proceed"
                )

            # Fetch the initiator's name and email
            initiator_name = (
                f"{initiator.employee.first_name} {initiator.employee.last_name}"
                if initiator.employee
                else initiator.username
            )
            initiator_email = initiator.email

            # Map workplan_source_id to the corresponding initiating ID field and validate
            source_id_to_field = {
                1: ("initiating_unit_id", Unit),
                2: ("initiating_department_id", Department),
                3: ("initiating_srt_id", SRT),
                4: ("initiating_thematic_area_id", ThematicArea),
            }
            if work_plan_data.workplan_source_id not in source_id_to_field:
                raise ValueError("Invalid workplan source ID.")

            field_name, field_class = source_id_to_field[
                work_plan_data.workplan_source_id
            ]
            initiating_id = getattr(work_plan_data, field_name)
            if initiating_id is None or initiating_id == 0:
                raise ValueError(
                    f"Required initiating ID for the selected workplan source is not provided or invalid."
                )
            # Validate activity_lead_id
            if not work_plan_data.activity_lead_id:
                raise ValueError("Activity lead is required.")

            # Validate foreign key IDs if provided
            initiating_unit_id = (
                self._valid_id(work_plan_data.initiating_unit_id, Unit)
                if work_plan_data.initiating_unit_id
                else None
            )
            initiating_department_id = (
                self._valid_id(work_plan_data.initiating_department_id, Department)
                if work_plan_data.initiating_department_id
                else None
            )
            initiating_srt_id = (
                self._valid_id(work_plan_data.initiating_srt_id, SRT)
                if work_plan_data.initiating_srt_id
                else None
            )
            initiating_thematic_area_id = (
                self._valid_id(work_plan_data.initiating_thematic_area_id, ThematicArea)
                if work_plan_data.initiating_thematic_area_id
                else None
            )
            if not self._valid_id(work_plan_data.workplan_source_id, WorkPlanSource):
                raise HTTPException(
                    status_code=404, detail="Work plan source not found"
                )
            # Check for an existing work plan with the same title, source, and date
            if self.check_existing_work_plan(work_plan_data):
                raise HTTPException(
                    status_code=400, detail="A similar work plan already exists."
                )
            # Check for employee schedule conflicts
            schedule_conflict = self.check_employee_schedule_conflict(
                work_plan_data.employee_ids, work_plan_data.activity_date
            )
            if schedule_conflict:
                conflicting_employee_names = [
                    employee.first_name
                    for employee in schedule_conflict.employees
                    if employee.id in work_plan_data.employee_ids
                ]
                # raise HTTPException(
                #     status_code=400,
                #     detail="One or more employees are already assigned to another work plan on the chosen date:\n"
                #     + "\n ,".join(conflicting_employee_names)
                # )
                raise HTTPException(
                    status_code=400,
                    detail=f"One or more employees are already assigned to another work plan on the chosen date. {', '.join(conflicting_employee_names)}",
                )
                # #raise HTTPException(status_code=400, detail=f"One or more employees are already assigned to another work plan on the chosen date.+"\n" {', '.join(conflicting_employee_names)}")
            #
            # #raise HTTPException(status_code=400, detail=f"One or more employees are already assigned to another work plan on the chosen date.+"\n" {', '.join(conflicting_employee_names)}") Find an existing group or create a new one based on the criteria
            existing_group = self._find_existing_group(work_plan_data)
            new_work_plan = WorkPlan(
                activity_title=work_plan_data.activity_title,
                specific_task=work_plan_data.specific_task,
                logistics_required=work_plan_data.logistics_required,
                activity_date=work_plan_data.activity_date,
                tenancy_id=work_plan_data.tenancy_id,
                activity_start_time=work_plan_data.activity_start_time,
                initiating_user_id=work_plan_data.initiating_user_id,
                activity_lead_id=work_plan_data.activity_lead_id,
                initiating_unit_id=initiating_unit_id,
                initiating_srt_id=initiating_srt_id,
                initiating_department_id=initiating_department_id,
                initiating_thematic_area_id=initiating_thematic_area_id,
                workplan_source_id=work_plan_data.workplan_source_id,
                status=STATUS_PENDING,
                need_vehicle=work_plan_data.need_vehicle,
                group_id=existing_group.id if existing_group else None,
            )
            self.db_session.add(new_work_plan)
            self.db_session.flush()

            # If no existing group, set the group_id to its own ID
            if not existing_group:
                new_work_plan.group_id = new_work_plan.id
                self.db_session.commit()
            # Associate sites, employees, and locations
            new_work_plan.sites.extend(
                self.db_session.query(Site)
                .filter(Site.id.in_(work_plan_data.site_ids))
                .all()
            )
            new_work_plan.employees.extend(
                self.db_session.query(Employee)
                .filter(Employee.id.in_(work_plan_data.employee_ids))
                .all()
            )
            new_work_plan.locations.extend(
                self.db_session.query(Location)
                .filter(Location.id.in_(work_plan_data.location_ids))
                .all()
            )

            self.db_session.commit()

            # Prepare recipients list for the associated employees
            recipients = [
                (employee.first_name, employee.employee_email)
                for employee in new_work_plan.employees
                if employee.employee_email
            ]
            if initiator_email not in [email for _, email in recipients]:
                recipients.append(
                    (
                        (
                            initiator.employee.first_name
                            if initiator.employee
                            else initiator.username.split("@")[0]
                        ),
                        initiator_email,
                    )
                )

            # Add tasks to send emails asynchronously
            background_tasks.add_task(
                notify_work_plan_creation,
                recipients,
                new_work_plan.activity_title,
                initiator_name,
                STATUS_PENDING,
            )
            background_tasks.add_task(
                notify_initiator_about_work_plan,
                initiator_email,
                initiator_name,
                new_work_plan.activity_title,
                STATUS_PENDING,
            )

            return new_work_plan

        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        

    def send_emails_in_background(
        self, recipients, activity_title, initiator_name, status
    ):
        notify_work_plan_creation(recipients, activity_title, initiator_name, status)
        initiator_email = next((email for _, email in recipients if email), None)
        if initiator_email:
            notify_initiator_about_work_plan(
                initiator_email, initiator_name, activity_title, status
            )

    def update_work_plan(
        self,
        work_plan_id: int,
        update_data: WorkPlanUpdate,
        tenancy_id: Optional[int] = None,
    ):
        try:
            if tenancy_id:
                work_plan = (
                    self.db_session.query(WorkPlan)
                    .filter(
                        WorkPlan.id == work_plan_id, WorkPlan.tenancy_id == work_plan_id
                    )
                    .first()
                )
                if not work_plan:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Work plan ID {work_plan_id} not found or does not belong to your state",
                    )
            else:
                work_plan = (
                    self.db_session.query(WorkPlan)
                    .filter(WorkPlan.id == work_plan_id)
                    .first()
                )
                if not work_plan:
                    raise HTTPException(
                        status_code=404, detail=f"Work plan ID {work_plan_id} not found"
                    )

            if (
                update_data.workplan_source_id is None
                or update_data.workplan_source_id == 0
            ):
                raise ValueError("workplan_source_id cannot be zero.")

            regroup_needed = False
            changes_detected = {}

            # Update scalar fields
            fields_to_check = [
                "activity_title",
                "specific_task",
                "logistics_required",
                "activity_date",
                "activity_start_time",
                "activity_lead_id",
            ]
            for field in fields_to_check:
                new_value = getattr(update_data, field, None)
                if new_value is not None and new_value != getattr(work_plan, field):
                    changes_detected[field] = (getattr(work_plan, field), new_value)
                    setattr(work_plan, field, new_value)
                    regroup_needed = True

            # Validate foreign key IDs if provided
            field_class_map = {
                "initiating_unit_id": Unit,
                "initiating_department_id": Department,
                "initiating_srt_id": SRT,
                "initiating_thematic_area_id": ThematicArea,
            }

            # Handling correct and reset of initiating fields based on workplan_source_id
            source_id_to_field = {
                1: "initiating_unit_id",
                2: "initiating_department_id",
                3: "initiating_srt_id",
                4: "initiating_thematic_area_id",
            }
            correct_field = source_id_to_field.get(update_data.workplan_source_id, None)
            if correct_field:
                correct_id = getattr(update_data, correct_field, None)
                if correct_id is None or correct_id == 0:
                    setattr(work_plan, correct_field, None)
                else:
                    if not self._valid_id(correct_id, field_class_map[correct_field]):
                        raise HTTPException(
                            status_code=400, detail=f"Invalid {correct_field} provided."
                        )
                    setattr(work_plan, correct_field, correct_id)
                regroup_needed = True
                # Reset other fields to None
                for field, clazz in field_class_map.items():
                    if field != correct_field:
                        setattr(work_plan, field, None)

            # Check for employee schedule conflicts
            if update_data.employee_ids:
                schedule_conflict = self.check_employee_schedule_conflict(
                    update_data.employee_ids, update_data.activity_date
                )
                if schedule_conflict and schedule_conflict.id != work_plan_id:
                    conflicting_employee_names = [
                        employee.first_name
                        for employee in schedule_conflict.employees
                        if employee.id in update_data.employee_ids
                    ]
                    raise HTTPException(
                        status_code=400,
                        detail=f"One or more employees are already assigned to another work plan on the chosen date. {', '.join(conflicting_employee_names)}",
                    )

            # Update relationships using the existing association tables
            if update_data.employee_ids is not None:
                new_employees = (
                    self.db_session.query(Employee)
                    .filter(Employee.id.in_(update_data.employee_ids))
                    .all()
                )
                work_plan.employees = new_employees
                changes_detected["employees"] = [e.id for e in new_employees]

            if update_data.site_ids is not None:
                new_sites = (
                    self.db_session.query(Site)
                    .filter(Site.id.in_(update_data.site_ids))
                    .all()
                )
                work_plan.sites = new_sites
                changes_detected["sites"] = [s.id for s in new_sites]

            if update_data.location_ids is not None:
                new_locations = (
                    self.db_session.query(Location)
                    .filter(Location.id.in_(update_data.location_ids))
                    .all()
                )
                work_plan.locations = new_locations
                changes_detected["locations"] = [l.id for l in new_locations]

            if regroup_needed:
                new_group = self._find_existing_group(work_plan)
                work_plan.group_id = new_group.id if new_group else work_plan.id

            self.db_session.commit()

            # Notify about changes
            if changes_detected:
                recipients = [
                    (emp.first_name, emp.employee_email) for emp in work_plan.employees
                ]
                notify_work_plan_updates(
                    recipients, work_plan.activity_title, changes_detected
                )

            return work_plan

        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Failed to update work plan: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def fetch_pending_work_plans_for_week(
        self, tenancy_id: Optional[int] = None, employee_id: Optional[int] = None
    ):
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday

        # Alias for employees to use in subqueries
        employee_alias = aliased(Employee)

        # Define the case statement for dynamically determining the implementing team
        implementing_team = case(
            (WorkPlan.initiating_srt_id == SRT.id, SRT.name),
            (WorkPlan.initiating_unit_id == Unit.id, Unit.name),
            (WorkPlan.initiating_department_id == Department.id, Department.name),
            (
                WorkPlan.initiating_thematic_area_id == ThematicArea.id,
                ThematicArea.name,
            ),
            else_="Unknown",
        )

        # Subquery to get employee names associated with each work plan
        employee_names = (
            self.db_session.query(
                WorkPlan.id.label("work_plan_id"),
                func.string_agg(
                    employee_alias.first_name + " " + employee_alias.last_name, ", "
                ).label("employee_names"),
                func.count(employee_alias.id).label(
                    "employee_count"
                ),  # Count of employees
            )
            .join(
                workplan_employee_association,
                workplan_employee_association.c.work_plan_id == WorkPlan.id,
            )
            .join(
                employee_alias,
                employee_alias.id == workplan_employee_association.c.employee_id,
            )
            .group_by(WorkPlan.id)
            .subquery()
        )

        # Main query to fetch work plans and associated data
        work_plans = (
            self.db_session.query(
                WorkPlan.id,
                WorkPlan.activity_title,
                WorkPlan.activity_date,
                WorkPlan.status,  # Include status
                Location.name.label("location_name"),
                WorkPlanSource.name.label("workplan_source_name"),
                implementing_team.label("implementing_team"),
                employee_names.c.employee_names,
                employee_names.c.employee_count,  # Include count of employees
                WorkPlan.tenancy_id,
            )
            .join(WorkPlan.locations)
            .join(WorkPlan.workplan_source)
            .outerjoin(SRT, WorkPlan.initiating_srt_id == SRT.id)
            .outerjoin(Unit, WorkPlan.initiating_unit_id == Unit.id)
            .outerjoin(Department, WorkPlan.initiating_department_id == Department.id)
            .outerjoin(
                ThematicArea, WorkPlan.initiating_thematic_area_id == ThematicArea.id
            )
            .outerjoin(employee_names, employee_names.c.work_plan_id == WorkPlan.id)
            .filter(
                WorkPlan.status == "Pending",
                WorkPlan.is_active == True,
                WorkPlan.activity_date >= start_of_week,
                WorkPlan.activity_date <= end_of_week,
            )
        )

        ## Filter out Tenanacy where True
        if tenancy_id:
            work_plans = work_plans.filter(WorkPlan.tenancy_id == tenancy_id)

        ## Filter out Employee where True
        if employee_id:
            work_plans = work_plans.join(
                workplan_employee_association,
                workplan_employee_association.c.work_plan_id == WorkPlan.id,
            )  # .filter(work_plans.id ==employee_id)
            work_plans = work_plans.filter(
                workplan_employee_association.c.employee_id == employee_id
            )

        list_of_work_plans = (
            work_plans.group_by(
                WorkPlan.id,
                WorkPlan.activity_title,
                WorkPlan.activity_date,
                WorkPlan.status,
                Location.name,
                WorkPlanSource.name,
                implementing_team,
                employee_names.c.employee_names,
                employee_names.c.employee_count,
                WorkPlan.tenancy_id,
            )
            .order_by(WorkPlan.group_id)
            .all()
        )

        return [
            {
                "workplan_id": wp.id,
                "activity_title": wp.activity_title,
                "activity_date": wp.activity_date.strftime("%Y-%m-%d"),
                # "status": wp.status,
                "location_name": wp.location_name,
                "workplan_source_name": wp.workplan_source_name,
                "implementing_team": wp.implementing_team,
                "employee_names": [
                    wp.employee_names
                ],  # Comma-separated list of employee names
                "no_of_staff": wp.employee_count,  # Number of employees associated with the work plan
                "tenancy_id": wp.tenancy_id,
            }
            for wp in list_of_work_plans
        ]


    def fetch_current_week_work_plans_with_status(self,  start_of_week: date, end_of_week: date, vehicle_assigned:Optional[bool], tenancy_id: Optional[int] = None, employee_id: Optional[int] = None):
        # today = date.today()
        # start_of_week = today - timedelta(days=today.weekday())  # Monday
        # end_of_week = start_of_week + timedelta(days=6)  # Sunday

        try:
            # Alias for employees to use in subqueries
            employee_alias = aliased(Employee)

            # Define the case statement for dynamically determining the implementing team
            implementing_team = case(
                
                    (WorkPlan.initiating_srt_id == SRT.id, SRT.name),
                    (WorkPlan.initiating_unit_id == Unit.id, Unit.name),
                    (WorkPlan.initiating_department_id == Department.id, Department.name),
                    (WorkPlan.initiating_thematic_area_id == ThematicArea.id, ThematicArea.name),
                
                else_="Unknown",
            )

            # Subquery to get employee details associated with each work plan
            employee_details = (
                self.db_session.query(
                    workplan_employee_association.c.work_plan_id.label("work_plan_id"),
                    func.array_agg(employee_alias.id).label("employee_ids"),
                    func.string_agg(employee_alias.first_name + ' ' + employee_alias.last_name, ', ').label("employee_names"),
                    func.count().label("employee_count")
                )
                .join(employee_alias, employee_alias.id == workplan_employee_association.c.employee_id)
                .group_by(workplan_employee_association.c.work_plan_id)
                .subquery()
            )

            # Main query to fetch work plans and associated data
            work_plans_query = (
                self.db_session.query(
                    WorkPlan.id,
                    WorkPlan.workplan_code,
                    WorkPlan.activity_title,
                    WorkPlan.activity_date,
                    WorkPlan.status,
                    WorkPlan.vehicle_assigned,
                    Location.name.label("location_name"),
                    WorkPlanSource.name.label("workplan_source_name"),
                    implementing_team.label("implementing_team"),
                    WorkPlan.initiating_user_id,
                    employee_details.c.employee_ids,
                    employee_details.c.employee_names,
                    employee_details.c.employee_count,
                    WorkPlan.tenancy_id,
                )
                .join(WorkPlan.locations)
                .join(WorkPlan.workplan_source)
                .outerjoin(SRT, WorkPlan.initiating_srt_id == SRT.id)
                .outerjoin(Unit, WorkPlan.initiating_unit_id == Unit.id)
                .outerjoin(Department, WorkPlan.initiating_department_id == Department.id)
                .outerjoin(ThematicArea, WorkPlan.initiating_thematic_area_id == ThematicArea.id)
                .outerjoin(employee_details, employee_details.c.work_plan_id == WorkPlan.id)
                .filter(
                    WorkPlan.is_active == True,
                    WorkPlan.activity_date >= start_of_week,
                    WorkPlan.activity_date <= end_of_week,
                    #WorkPlan.vehicle_assigned==vehicle_assigned
                )
            )
            if vehicle_assigned:
                work_plans_query=work_plans_query.filter(WorkPlan.vehicle_assigned)
            if tenancy_id:
                work_plans_query = work_plans_query.filter(WorkPlan.tenancy_id == tenancy_id)
            if employee_id:
                work_plans_query = work_plans_query.filter(employee_details.c.employee_ids.any(employee_id))

            work_plans = work_plans_query.distinct(WorkPlan.id).all()

            return [{
                "workplan_id": wp.id,
                "workplan_code": wp.workplan_code,
                "activity_title": wp.activity_title,
                "activity_date": wp.activity_date.strftime("%Y-%m-%d"),
                "status": wp.status,
                "vehicle_assigned": wp.vehicle_assigned,
                "location_name": wp.location_name,
                "workplan_source_name": wp.workplan_source_name,
                "implementing_team": wp.implementing_team,
                "initiating_user_id":wp.initiating_user_id,
                "employee_ids": wp.employee_ids,
                "employee_names": wp.employee_names,
                "no_of_staff": wp.employee_count,
                "tenancy_id": wp.tenancy_id,
            } for wp in work_plans]

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


    def approve_work_plan(
        self, background_tasks: BackgroundTasks, work_plan_id: int, approver_id: int
    ):
        """Approve a work plan and set the approver."""
        STATUS_APPROVED = "Approved"

        if approver_id is None:
            raise ValueError("Approver ID is required")

        db_work_plan = self.get_work_plan_by_id(work_plan_id)
        if db_work_plan is None:
            raise HTTPException(status_code=404, detail="Work plan not found")

        # Check if the plan has already been Approved
        if db_work_plan.is_approved:
            raise HTTPException(status_code=400, detail="Work plan already approved")

        # Revert if the Plan was initially Re-Scheduled
        if db_work_plan.is_rescheduled:
            db_work_plan.is_rescheduled = False
            db_work_plan.date_rescheduled = None

        # Revert if the Plan was Initially Denied
        if db_work_plan.is_denied:
            db_work_plan.is_denied = False
            db_work_plan.date_denied = None

        # Revert the reason back to null
        if db_work_plan.reason is not None:
            db_work_plan.reason = None

        # Generate a unique code for the work plan
        work_plan_code = self.generate_work_plan_code(db_work_plan)
        if not db_work_plan.workplan_code:
            db_work_plan.workplan_code = work_plan_code

        # Set approver details and update the work plan status
        db_work_plan.approved_by = approver_id
        db_work_plan.is_approved =True
        db_work_plan.date_approved = datetime.now(timezone.utc)  # datetime.utcnow()
        db_work_plan.status = STATUS_APPROVED
        work_plan_code = self.generate_work_plan_code(db_work_plan)
        db_work_plan.workplan_code = work_plan_code or db_work_plan.workplan_code

        try:
            self.db_session.commit()
            recipients = [
                (emp.first_name, emp.employee_email)
                for emp in db_work_plan.employees
                if emp.employee_email
            ]
            background_tasks.add_task(
                notify_work_plan_approval,
                recipients,
                db_work_plan.activity_title,
                db_work_plan.workplan_code,
                db_work_plan.activity_date,
                db_work_plan.activity_start_time,
                STATUS_APPROVED,
            )
            return db_work_plan
        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Failed to approve work plan: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to approve work plan due to an error: {e}",
            )

            # raise HTTPException(status_code=500, detail="Failed to approve work plan")

    def reschedule_work_plan(
        self,
        background_tasks: BackgroundTasks,
        work_plan_id: int,
        reason: str,
        new_date: datetime,
    ) -> Union[WorkPlan, dict]:
        """Reschedule a work plan to a new date and adjust status if previously approved."""
        STATUS_RESCHEDULED = "Re-Scheduled"
        db_work_plan = self.get_work_plan_by_id(work_plan_id)
        if db_work_plan:
            if not db_work_plan.is_rescheduled:
                db_work_plan.is_rescheduled = True
                db_work_plan.reason = reason
                db_work_plan.date_rescheduled = datetime.utcnow()
                db_work_plan.activity_date = new_date
                db_work_plan.status = STATUS_RESCHEDULED

                # Reset approval if the plan was previously approved
                if db_work_plan.is_approved:
                    db_work_plan.is_approved = False
                    db_work_plan.is_rescheduled=True
                    db_work_plan.date_approved = None
                    db_work_plan.approved_by = None
                    db_work_plan.workplan_code = None

                # Reset Denial if the plan was previously Denied
                if db_work_plan.is_denied:
                    db_work_plan.is_denied = False
                    db_work_plan.date_denied = None

                try:
                    self.db_session.commit()
                    # Prepare the list of recipients with their first names and email addresses
                    recipients = [
                        (emp.first_name, emp.employee_email)
                        for emp in db_work_plan.employees
                        if emp.employee_email
                    ]

                    # Schedule email notification to be sent asynchronously
                    background_tasks.add_task(
                        notify_work_plan_reschedule,
                        recipients,
                        db_work_plan.activity_title,
                        db_work_plan.workplan_code,
                        reason,
                        new_date.strftime("%Y-%m-%d"),
                    )

                    return db_work_plan

                except Exception as e:
                    self.db_session.rollback()
                    logging.error(f"Failed to reschedule work plan: {e}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to reschedule work plan due to an error: {e}",
                    )
            else:
                raise HTTPException(
                    status_code=400, detail="Work plan has already been rescheduled"
                )
        else:
            raise HTTPException(status_code=404, detail="Work plan not found")

    def deny_work_plan(
        self, background_tasks: BackgroundTasks, work_plan_id: int, reason: str
    ) -> WorkPlan:
        """
        Deny a work plan and record the reason. If the work plan was previously approved,
        reverse the approval. This function now also schedules an email notification as a background task.
        """
        STATUS_DENIED = "Denied"
        db_work_plan = self.get_work_plan_by_id(work_plan_id)
        if db_work_plan is None:
            raise HTTPException(status_code=404, detail="Work plan not found")

        if db_work_plan.is_denied:
            raise HTTPException(status_code=400, detail="Work plan already denied")

        # If the work plan was approved, reverse the approval status
        if db_work_plan.is_approved:
            db_work_plan.is_approved = False
            db_work_plan.date_approved = None
            db_work_plan.approved_by = None

        if db_work_plan.is_rescheduled:
            db_work_plan.is_rescheduled = False
            db_work_plan.date_rescheduled = None

        # Set the work plan as denied and record the reason
        db_work_plan.is_denied = True
        db_work_plan.reason = reason
        db_work_plan.date_denied = datetime.utcnow()
        db_work_plan.status = STATUS_DENIED

        try:
            self.db_session.commit()

            # Prepare the list of recipients with first names and emails
            recipients = [
                (employee.first_name, employee.employee_email)
                for employee in db_work_plan.employees
                if employee.employee_email
            ]

            # Schedule the email notification to be sent asynchronously
            background_tasks.add_task(
                notify_work_plan_denial,
                recipients,
                db_work_plan.activity_title,
                db_work_plan.workplan_code,
                reason,
                STATUS_DENIED,
            )

            return db_work_plan
        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Failed to deny work plan: {e}")
            raise HTTPException(status_code=500, detail="Failed to deny work plan")

    def update_work_plan_if_pending(self, work_plan_id: int, updates: dict):
        """
        Updates a work plan only if its current status is 'Pending'.
        :param work_plan_id: The ID of the work plan to update.
        :param updates: A dictionary containing the fields to update.
        :return: The updated work plan or raises an HTTPException if the work plan is not in a 'Pending' status.
        """
        try:
            # Retrieve the work plan by ID
            work_plan = self.get_work_plan_by_id(work_plan_id)
            if work_plan is None:
                raise HTTPException(status_code=404, detail="Work plan not found.")

            # Check if the current status is 'Pending'
            if work_plan.status != "Pending":
                raise HTTPException(
                    status_code=400,
                    detail="Work plan is not in a pending state and cannot be updated.",
                )

            # Update the fields from the updates dictionary
            for key, value in updates.items():
                if hasattr(work_plan, key):
                    setattr(work_plan, key, value)

            # Commit the changes to the database
            self.db_session.commit()
            return work_plan
        except Exception as e:
            self.db_session.rollback()
            raise Exception(f"An error occurred while updating the work plan: {str(e)}")

    def get_work_plan_by_id(self, work_plan_id: int):
        """Retrieve a work plan by its ID, handling exceptions that might occur."""
        try:
            work_plan = (
                self.db_session.query(WorkPlan)
                .filter(WorkPlan.id == work_plan_id)
                .first()
            )
            if not work_plan:
                raise HTTPException(status_code=404, detail="Work plan not found")
            return work_plan
        except SQLAlchemyError as e:
            # Log the error for debugging purposes
            logging.error(f"Database error occurred: {e}")
            # Optionally, you can raise an HTTPException or your custom exception depending on how you want to handle it in your application.
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while fetching the work plan",
            )


    def fetch_employees_by_work_plan(
        self, workplan_code=None, initiator_name=None, activity_date=None
    ):
        try:
            query = self.db_session.query(Employee)

            if workplan_code:
                query = query.join(Employee.work_plans).filter(
                    WorkPlan.workplan_code == workplan_code
                )

            if initiator_name:
                name_parts = initiator_name.split()
                if len(name_parts) != 2:
                    raise ValueError(
                        "Initiator name must include both first and last names separated by a space."
                    )
                first_name, last_name = name_parts
                query = (
                    query.join(Employee.work_plans)
                    .join(User, WorkPlan.initiating_user_id == User.id)
                    .filter(
                        User.employee.has(first_name=first_name, last_name=last_name)
                    )
                )

            if activity_date:
                query = query.join(Employee.work_plans).filter(
                    WorkPlan.activity_date == activity_date
                )

            employees = query.filter(Employee.employee_email != None).all()
            return [EmployeeModel.from_orm(emp) for emp in employees]
        except ValueError as ve:
            logging.error(f"Input error: {ve}")
            raise Exception(f"Input error: {ve}")
        except SQLAlchemyError as e:
            logging.error(f"Database error occurred: {e}")
            raise Exception(f"Failed to fetch employees due to a database error: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise Exception(f"Failed to fetch employees due to an error: {e}")


    def get_active_work_plans(self):
        """Fetch all active work plans."""
        try:
            active_work_plans = (
                self.db_session.query(WorkPlan).filter(WorkPlan.is_active == True).all()
            )
            return active_work_plans
        except Exception as e:
            logging.error(f"Failed to fetch active work plans: {e}")
            raise Exception(f"Database error while fetching active work plans: {e}")


    def list_employees_without_work_plan_on_date(self, activity_date: date):
        try:
            # Use a subquery to find employees with work plans on the given date
            subquery = self.db_session.query(workplan_employee_association.c.employee_id).join(
                WorkPlan,
                workplan_employee_association.c.work_plan_id == WorkPlan.id
            ).filter(WorkPlan.activity_date == activity_date).subquery()

            # Query employees who are not in the subquery
            employees = self.db_session.query(
                Employee.id.label('employee_id'),
                Employee.staff_code,
                Employee.last_name,
                Employee.first_name,
                Employee.phone_number
            ).outerjoin(
                subquery, subquery.c.employee_id == Employee.id
            ).filter(subquery.c.employee_id == None).all()

            return [{"employee_id": emp.employee_id, "staff_code": emp.staff_code, "last_name": emp.last_name, "first_name": emp.first_name, "phone_number": emp.phone_number} for emp in employees]
        except SQLAlchemyError as e:
            self.logger.error(f"Database error occurred: {e}")
            return []
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return []


    def list_archived_work_plans(self, skip: int, limit: int):
        return (
            self.db_session.query(WorkPlan)
            .filter(WorkPlan.archived == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_work_plans_by_status(self, is_approved: bool, skip: int, limit: int):
        return (
            self.db_session.query(WorkPlan)
            .filter(WorkPlan.is_approved == is_approved)
            .offset(skip)
            .limit(limit)
            .all()
        )


    def fetch_approved_weekly_work_plans(self):
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday

        # Alias for employees to use in subqueries
        employee_alias = aliased(Employee)

        # Case statement for dynamically determining the implementing team
        implementing_team = case(
            (WorkPlan.initiating_srt_id == SRT.id, SRT.name),
            (WorkPlan.initiating_unit_id == Unit.id, Unit.name),
            (WorkPlan.initiating_department_id == Department.id, Department.name),
            (WorkPlan.initiating_thematic_area_id == ThematicArea.id, ThematicArea.name),
        else_="Unknown").label("implementing_team")


        # Subquery to get employee details associated with each work plan
        employee_details = (
            self.db_session.query(
                workplan_employee_association.c.work_plan_id.label("work_plan_id"),
                func.array_agg(employee_alias.id).label("employee_ids"),  # List of employee IDs
                func.string_agg(employee_alias.first_name + ' ' + employee_alias.last_name, ', ').label("employee_names"),  # Names
                func.count().label("employee_count")
            )
            .join(employee_alias, employee_alias.id == workplan_employee_association.c.employee_id)
            .group_by(workplan_employee_association.c.work_plan_id)
            .subquery()
        )


        # Adjust the query to ensure it's properly fetching full WorkPlan entities
        work_plans = (
            self.db_session.query(WorkPlan)
            .options(
                selectinload(WorkPlan.employees),
                selectinload(WorkPlan.locations)
            )
            .join(WorkPlanSource, isouter=True)
            .outerjoin(SRT)
            .outerjoin(Unit)
            .outerjoin(Department)
            .outerjoin(ThematicArea)
            .filter(
                WorkPlan.status == "Approved",
                WorkPlan.activity_date >= start_of_week,
                WorkPlan.activity_date <= end_of_week,
            )
            .all()
        )

        return [
            {
                "id": wp.id,
                "workplan_code": wp.workplan_code,
                "activity_title": wp.activity_title,
                "specific_task": wp.specific_task,
                "logistics_required": wp.logistics_required,
                "activity_date": wp.activity_date.isoformat(),
                "activity_time": wp.activity_start_time.isoformat() if wp.activity_start_time else None,
                "initiating_user_id": wp.initiating_user_id,
                "status": wp.status,
                "workplan_source_name": wp.workplan_source.name,
                "implementing_team": getattr(wp, 'implementing_team', None),  # Assuming 'implementing_team' is correctly integrated into the model or managed through additional query adjustments.
                "employee_ids":employee_details.c.employee_ids,
                "employee_ids":[emp.id for emp in wp.employees],
                "employee_names": [f"{emp.first_name} {emp.last_name}" for emp in wp.employees],
                "employee_count": len(wp.employees),
                "locations": [loc.name for loc in wp.locations],
            }
            for wp in work_plans
        ]


    def fetch_approved_work_plan_by_code_or_id(self, identifier: str):
        # Alias for Employee to use in subqueries
        employee_alias = aliased(Employee)

        # Subquery to get employee names and count
        employee_names = (
            self.db_session.query(
                WorkPlan.id.label("work_plan_id"),
                func.string_agg(
                    employee_alias.first_name + " " + employee_alias.last_name, ", "
                ).label("employee_names"),
                func.count(employee_alias.id).label("employee_count"),
            )
            .join(
                workplan_employee_association,
                workplan_employee_association.c.work_plan_id == WorkPlan.id,
            )
            .join(
                employee_alias,
                employee_alias.id == workplan_employee_association.c.employee_id,
            )
            .group_by(WorkPlan.id)
            .subquery()
        )

        # Determine if identifier is numeric (ID) or non-numeric (work plan code)
        if identifier.isdigit():
            # Fetch by ID
            work_plan_query = self.db_session.query(WorkPlan).filter(
                WorkPlan.id == int(identifier), WorkPlan.status == "Approved"
            )
        else:
            # Fetch by work plan code
            work_plan_query = self.db_session.query(WorkPlan).filter(
                WorkPlan.workplan_code == identifier, WorkPlan.status == "Approved"
            )

        # Join with the subquery to include employee names and counts
        work_plan = (
            work_plan_query.outerjoin(
                employee_names, employee_names.c.work_plan_id == WorkPlan.id
            )
            .add_columns(
                employee_names.c.employee_names, employee_names.c.employee_count
            )
            .first()
        )

        if work_plan:
            # Unpacking the tuple from the joined query
            wp, employee_names, employee_count = work_plan
            return {
                "id": wp.id,
                "workplan_code": wp.workplan_code,
                "activity_title": wp.activity_title,
                "specific_task": wp.specific_task,
                "logistics_required": wp.logistics_required,
                "activity_date": wp.activity_date.isoformat(),
                "initiating_user_id": wp.initiating_user_id,
                "status": wp.status,
                "employee_names": employee_names.split(", ") if employee_names else [],
                "employee_count": employee_count,
            }
        return None

    def fetch_approved_work_plan_by_entity(self, entity_type: str, entity_name: str):
        # Define aliases for Employee to use in subqueries
        employee_alias = aliased(Employee)

        # Subquery to get employee names and count
        employee_names = (
            self.db_session.query(
                WorkPlan.id.label("work_plan_id"),
                func.string_agg(
                    employee_alias.first_name + " " + employee_alias.last_name, ", "
                ).label("employee_names"),
                func.count(employee_alias.id).label("employee_count"),
            )
            .join(
                workplan_employee_association,
                workplan_employee_association.c.work_plan_id == WorkPlan.id,
            )
            .join(
                employee_alias,
                employee_alias.id == workplan_employee_association.c.employee_id,
            )
            .group_by(WorkPlan.id)
            .subquery()
        )

        # Prepare the base query with subquery joined
        base_query = (
            self.db_session.query(WorkPlan)
            .outerjoin(employee_names, employee_names.c.work_plan_id == WorkPlan.id)
            .add_columns(
                employee_names.c.employee_names, employee_names.c.employee_count
            )
            .filter(WorkPlan.status == "Approved")
        )

        # Filter based on the type of entity and its name
        if entity_type.lower() == "unit":
            base_query = base_query.join(Unit).filter(Unit.name == entity_name)
        elif entity_type.lower() == "srt":
            base_query = base_query.join(SRT).filter(SRT.name == entity_name)
        elif entity_type.lower() == "department":
            base_query = base_query.join(Department).filter(
                Department.name == entity_name
            )
        elif entity_type.lower() == "thematicarea":
            base_query = base_query.join(ThematicArea).filter(
                ThematicArea.name == entity_name
            )
        else:
            raise ValueError(
                "Invalid entity type provided. Must be one of: unit, srt, department, thematicarea."
            )

        # Fetch the first matching work plan
        work_plan = base_query.first()

        if work_plan:
            # Unpack the tuple from the joined query
            wp, employee_names, employee_count = work_plan
            return {
                "id": wp.id,
                "workplan_code": wp.workplan_code,
                "activity_title": wp.activity_title,
                "specific_task": wp.specific_task,
                "logistics_required": wp.logistics_required,
                "activity_date": wp.activity_date.isoformat(),
                "initiating_user_id": wp.initiating_user_id,
                "status": wp.status,
                "employee_names": employee_names.split(", ") if employee_names else [],
                "employee_count": employee_count,
            }
        return None

    def fetch_monthly_work_plan_summary(self, year: int, month: int):
        from sqlalchemy import extract

        # Ensure correct bounds for month and year, you might also want to validate these beforehand or use a library
        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12")
        if year < 1900 or year > 2100:  # Arbitrary year range for example
            raise ValueError("Year must be a reasonable value")

        # Calculate the start and end of the month
        start_date = date(year, month, 1)
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        # Query work plans within the month and aggregate information
        work_plans = (
            self.db_session.query(
                WorkPlan.status,
                func.count(WorkPlan.id).label("count"),
                func.string_agg(
                    Employee.first_name + " " + Employee.last_name, ", "
                ).label("employee_names"),
            )
            .join(
                workplan_employee_association,
                workplan_employee_association.c.work_plan_id == WorkPlan.id,
            )
            .join(Employee, Employee.id == workplan_employee_association.c.employee_id)
            .filter(WorkPlan.activity_date.between(start_date, end_date))
            .group_by(WorkPlan.status)
            .all()
        )

        # Transform results into a structured format
        summary = {"month": month, "year": year, "details": []}
        for status, count, employee_names in work_plans:
            summary["details"].append(
                {
                    "status": status,
                    "employee_count": count,
                    "employees": (
                        list(set(employee_names.split(", "))) if employee_names else []
                    ),
                }
            )

        return summary

    def fetch_workplans_by_date_range(
        self, start_date: date, end_date: date, status: Optional[str] = None
    ) -> List[dict]:
        """
        Fetches work plans scheduled within a specific date range, including details about the employees involved and optionally filtering by status.
        """
        # Alias for Employee to use in subqueries
        employee_alias = aliased(Employee)

        # Subquery to get employee names and count
        employee_names = (
            self.db_session.query(
                WorkPlan.id.label("work_plan_id"),
                func.string_agg(
                    employee_alias.first_name + " " + employee_alias.last_name, ", "
                ).label("employee_names"),
                func.count(employee_alias.id).label("employee_count"),
            )
            .join(
                workplan_employee_association,
                workplan_employee_association.c.work_plan_id == WorkPlan.id,
            )
            .join(
                employee_alias,
                employee_alias.id == workplan_employee_association.c.employee_id,
            )
            .group_by(WorkPlan.id)
            .subquery()
        )

        # Main query to fetch work plans including employee names and counts
        query = (
            self.db_session.query(
                WorkPlan.id,
                WorkPlan.workplan_code,
                WorkPlan.activity_title,
                WorkPlan.specific_task,
                WorkPlan.logistics_required,
                WorkPlan.activity_date,
                WorkPlan.initiating_user_id,
                WorkPlan.status,
                WorkPlanSource.name.label("workplan_source_name"),
                employee_names.c.employee_names,
                employee_names.c.employee_count,
                User.username.label("initiating_user_name"),
            )
            .outerjoin(employee_names, employee_names.c.work_plan_id == WorkPlan.id)
            .join(WorkPlan.initiating_user)
            .join(WorkPlan.workplan_source)
            .filter(
                WorkPlan.activity_date >= start_date, WorkPlan.activity_date <= end_date
            )
        )

        # Conditionally add status filter if provided
        if status:
            query = query.filter(WorkPlan.status == status)

        try:
            work_plans = query.order_by(WorkPlan.activity_date).all()
            return [
                {
                    "work_plan_id": wp.id,
                    "workplan_code": wp.workplan_code,
                    "activity_title": wp.activity_title,
                    "specific_task": wp.specific_task,
                    "logistics_required": wp.logistics_required,
                    "activity_date": wp.activity_date.isoformat(),
                    "initiating_user_name": wp.initiating_user_name,
                    "workplan_source_name": wp.workplan_source_name,
                    "status": wp.status,
                    "employee_names": (
                        wp.employee_names.split(", ") if wp.employee_names else []
                    ),
                    "employee_count": wp.employee_count,
                }
                for wp in work_plans
            ]
        except Exception as e:
            self.db_session.rollback()
            raise Exception(f"Error retrieving work plans: {str(e)}")

    def get_work_plans_by_logistics(self, logistics_requirement: str):
        # Use a subquery to aggregate employee names for each work plan
        employee_subquery = (
            self.db_session.query(
                workplan_employee_association.c.work_plan_id.label("work_plan_id"),
                func.array_agg(Employee.id).label("employee_ids"),
                func.array_agg(
                    func.concat(Employee.first_name, " ", Employee.last_name)
                ).label("employee_names"),
            )
            .join(Employee, Employee.id == workplan_employee_association.c.employee_id)
            .group_by(workplan_employee_association.c.work_plan_id)
            .subquery()
        )

        # Fetch work plans that match the given logistics requirement
        work_plans = (
            self.db_session.query(
                WorkPlan.id,
                WorkPlan.activity_title,
                WorkPlan.logistics_required,
                WorkPlanSource.id.label("source_id"),
                WorkPlanSource.name.label("source_name"),
                Site.id.label("site_id"),
                Site.name.label("site_name"),
                Location.id.label("location_id"),
                Location.name.label("location_name"),
                employee_subquery.c.employee_ids,
                employee_subquery.c.employee_names,
            )
            .join(WorkPlanSource)
            .outerjoin(
                employee_subquery, WorkPlan.id == employee_subquery.c.work_plan_id
            )
            .outerjoin(
                workplan_site_association,
                WorkPlan.id == workplan_site_association.c.work_plan_id,
            )
            .outerjoin(Site, Site.id == workplan_site_association.c.site_id)
            .outerjoin(
                workplan_location_association,
                WorkPlan.id == workplan_location_association.c.work_plan_id,
            )
            .outerjoin(
                Location, Location.id == workplan_location_association.c.location_id
            )
            .filter(WorkPlan.logistics_required == logistics_requirement)
            .all()
        )

        # Format the results into a structured list of dictionaries
        results = []
        for wp in work_plans:
            results.append(
                {
                    "id": wp.id,
                    "activity_title": wp.activity_title,
                    "logistics_required": wp.logistics_required,
                    "workplan_source": {"id": wp.source_id, "name": wp.source_name},
                    "sites": (
                        [{"id": wp.site_id, "name": wp.site_name}] if wp.site_id else []
                    ),
                    "locations": (
                        [{"id": wp.location_id, "name": wp.location_name}]
                        if wp.location_id
                        else []
                    ),
                    "employees": (
                        [
                            {"id": id, "name": name}
                            for id, name in zip(wp.employee_ids, wp.employee_names)
                        ]
                        if wp.employee_ids
                        else []
                    ),
                }
            )
        return results




"""

{
  "activity_title": "Test Module",
  "specific_task": "Test NMRS Module",
  "logistics_required": "SRT",
  "activity_date": "2024-05-03",
  "activity_start_time": "09:00",
  "activity_lead_id": 2,
  "initiating_unit_id": 1,
  "initiating_department_id": 0,
  "initiating_srt_id": 0,
  "initiating_thematic_area_id": 0,
  "workplan_source_id": 1,
  "employee_ids": [
    1,2,3
  ],
  "site_ids": [
    1
  ],
  "location_ids": [
    1
  ]
}   




Using the provided all_models.py, develop a function that allows a user to create a trip based on their tenancy_id. 
This function should assign one or more vehicles to a work plan, ensuring the number of employees in the work plan 
does not exceed the vehicle's seating capacity. If the number of employees exceeds the capacity, the excess employees 
should be allocated to another vehicle heading to the same destination. Conversely, if the vehicle has extra seats after 
accommodating a work plan's employees, it should be filled with employees from another team traveling to the same location. 
At all times, vehicles must not be overloaded beyond their seating capacity. Only vehicles and drivers that are available 
should be assigned to trips. While each trip is limited to one driver and one vehicle, a work plan may be linked to multiple 
trips if it involves several employees.

Create a function that will enable the user to assign available vehicles and drivers to the work plan one after the other based on the criteria previously mentioned.

"""

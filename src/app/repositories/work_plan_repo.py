from typing import List, Union
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, case, func, or_
from sqlalchemy.orm import Session, aliased
from sqlalchemy.orm import joinedload
from models.all_models import SRT, Department, Trip, Unit, User, WorkPlan, Site, Employee, Location, WorkPlanSource, workplan_employee_association, ThematicArea
from schemas.workplan_schemas import EmployeeModel, WorkPlanCreate
from datetime import date, datetime, timedelta
import logging
from auth.email import notify_initiator_about_work_plan, notify_work_plan_approval, notify_work_plan_creation, notify_work_plan_denial, notify_work_plan_reschedule

class WorkPlanRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def generate_work_plan_code(self, work_plan: WorkPlan) -> str:
        # This is just a placeholder
        return f"WP-{work_plan.id}-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    

    def generate_trip_code(self, trip: Trip) -> str:
        # This is just a placeholder
        return f"TRP-{Trip.id}-{datetime.utcnow().strftime('%Y%m%d%H%M')}"


    def _find_existing_group(self, work_plan_data: WorkPlanCreate):
        start_of_week = work_plan_data.activity_date - timedelta(days=work_plan_data.activity_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        query = self.db_session.query(WorkPlan).filter(
            #WorkPlan.initiating_user_id == work_plan_data.initiating_user_id,
            WorkPlan.workplan_source_id == work_plan_data.workplan_source_id,
            WorkPlan.activity_date.between(start_of_week, end_of_week)
        )

        # Check for associated employees
        query = query.filter(
            WorkPlan.employees.any(Employee.id.in_(work_plan_data.employee_ids))
        )

        filters = []
        if work_plan_data.initiating_unit_id:
            filters.append(WorkPlan.initiating_unit_id == work_plan_data.initiating_unit_id)
        if work_plan_data.initiating_department_id:
            filters.append(WorkPlan.initiating_department_id == work_plan_data.initiating_department_id)
        if work_plan_data.initiating_srt_id:
            filters.append(WorkPlan.initiating_srt_id == work_plan_data.initiating_srt_id)
        if work_plan_data.initiating_thematic_area_id:
            filters.append(WorkPlan.initiating_thematic_area_id == work_plan_data.initiating_thematic_area_id)
        
        if filters:
            query = query.filter(or_(*filters))

        earliest_work_plan = query.order_by(WorkPlan.date_created).first()
        return earliest_work_plan

    def _valid_id(self, id_value, model):
        return id_value if self.db_session.query(model).filter(model.id == id_value).count() > 0 else None

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
            WorkPlan.activity_date == work_plan_data.activity_date
        )

        # Check for associated employees
        existing_work_plan = existing_work_plan.filter(
            WorkPlan.employees.any(Employee.id.in_(work_plan_data.employee_ids))
        )
        return existing_work_plan.first()

    def check_employee_schedule_conflict(self, employee_ids, activity_date):
        """Check if any employee is already assigned to a work plan on the given date."""
        existing_work_plan = self.db_session.query(WorkPlan).join(WorkPlan.employees).filter(
            Employee.id.in_(employee_ids),
            WorkPlan.activity_date == activity_date
        ).first()
        return existing_work_plan
    

    def create_work_plan(self, work_plan_data: WorkPlanCreate):
        STATUS_PENDING = "Pending"
        try:
            # Check for non-empty lists of employee_ids, site_ids, and location_ids
            if not work_plan_data.employee_ids or all(id == 0 for id in work_plan_data.employee_ids):
                raise ValueError("At least one valid employee is required.")
            if not work_plan_data.site_ids or all(id == 0 for id in work_plan_data.site_ids):
                raise ValueError("At least one valid site is required.")
            if not work_plan_data.location_ids or all(id == 0 for id in work_plan_data.location_ids):
                raise ValueError("At least one valid location is required.")
        
            # Verify the existence of all entities referred by foreign keys
            initiator = self.db_session.query(User).filter(User.id == work_plan_data.initiating_user_id).first()
            if not initiator:
                raise HTTPException(status_code=404, detail="Initiating user not found")

            # Fetch the initiator's name and email
            initiator_name = f"{initiator.employee.first_name} {initiator.employee.last_name}" if initiator.employee else initiator.username
            initiator_email = initiator.email

            # Map workplan_source_id to the corresponding initiating ID field and validate
            source_id_to_field = {
                1: ('initiating_unit_id', Unit),
                2: ('initiating_department_id', Department),
                3: ('initiating_srt_id', SRT),
                4: ('initiating_thematic_area_id', ThematicArea)
            }
            if work_plan_data.workplan_source_id not in source_id_to_field:
                raise ValueError("Invalid workplan source ID.")

            field_name, field_class = source_id_to_field[work_plan_data.workplan_source_id]
            initiating_id = getattr(work_plan_data, field_name)
            if initiating_id is None or initiating_id == 0:
                raise ValueError(f"Required initiating ID for the selected workplan source is not provided or invalid.")
            
            # Validate activity_lead_id
            if not work_plan_data.activity_lead_id:
                raise ValueError("Activity lead is required.")
        
            # Validate foreign key IDs if provided
            initiating_unit_id = self._valid_id(work_plan_data.initiating_unit_id, Unit) if work_plan_data.initiating_unit_id else None
            initiating_department_id = self._valid_id(work_plan_data.initiating_department_id, Department) if work_plan_data.initiating_department_id else None
            initiating_srt_id = self._valid_id(work_plan_data.initiating_srt_id, SRT) if work_plan_data.initiating_srt_id else None
            initiating_thematic_area_id = self._valid_id(work_plan_data.initiating_thematic_area_id, ThematicArea) if work_plan_data.initiating_thematic_area_id else None

            if not self._valid_id(work_plan_data.workplan_source_id, WorkPlanSource):
                raise HTTPException(status_code=404, detail="Work plan source not found")

            # Check for an existing work plan with the same title, source, and date
            if self.check_existing_work_plan(work_plan_data):
                raise HTTPException(status_code=400, detail="A similar work plan already exists.")

            # Check for employee schedule conflicts
            schedule_conflict = self.check_employee_schedule_conflict(work_plan_data.employee_ids, work_plan_data.activity_date)
            if schedule_conflict:
                conflicting_employee_names = [employee.first_name for employee in schedule_conflict.employees if employee.id in work_plan_data.employee_ids]
                # raise HTTPException(
                #     status_code=400,
                #     detail="One or more employees are already assigned to another work plan on the chosen date:\n"
                #     + "\n ,".join(conflicting_employee_names)
                # )
                raise HTTPException(status_code=400, detail=f"One or more employees are already assigned to another work plan on the chosen date. {', '.join(conflicting_employee_names)}")
                # #raise HTTPException(status_code=400, detail=f"One or more employees are already assigned to another work plan on the chosen date.+"\n" {', '.join(conflicting_employee_names)}")
            #
            # #raise HTTPException(status_code=400, detail=f"One or more employees are already assigned to another work plan on the chosen date.+"\n" {', '.join(conflicting_employee_names)}") Find an existing group or create a new one based on the criteria
            existing_group = self._find_existing_group(work_plan_data)

            new_work_plan = WorkPlan(
                activity_title=work_plan_data.activity_title,
                specific_task=work_plan_data.specific_task,
                logistics_required=work_plan_data.logistics_required,
                activity_date=work_plan_data.activity_date,
                activity_start_time=work_plan_data.activity_start_time,
                initiating_user_id=work_plan_data.initiating_user_id,
                activity_lead_id=work_plan_data.activity_lead_id,
                initiating_unit_id=initiating_unit_id,
                initiating_srt_id=initiating_srt_id,
                initiating_department_id=initiating_department_id,
                initiating_thematic_area_id=initiating_thematic_area_id,
                workplan_source_id=work_plan_data.workplan_source_id,
                status=STATUS_PENDING,
                group_id=existing_group.id if existing_group else None
            )
            self.db_session.add(new_work_plan)
            self.db_session.flush()

            # If no existing group, set the group_id to its own ID
            if not existing_group:
                new_work_plan.group_id = new_work_plan.id
                self.db_session.commit()

            # Associate sites, employees, and locations
            new_work_plan.sites.extend(self.db_session.query(Site).filter(Site.id.in_(work_plan_data.site_ids)).all())
            new_work_plan.employees.extend(self.db_session.query(Employee).filter(Employee.id.in_(work_plan_data.employee_ids)).all())
            new_work_plan.locations.extend(self.db_session.query(Location).filter(Location.id.in_(work_plan_data.location_ids)).all())

            self.db_session.commit()

            # Prepare recipients list for the associated employees
            recipients = [(employee.first_name, employee.employee_email) for employee in new_work_plan.employees if employee.employee_email]
            if initiator_email not in [email for _, email in recipients]:
                recipients.append((initiator.employee.first_name if initiator.employee else initiator.username.split('@')[0], initiator_email))

            # Send email notification to all associated employees and the initiator
            notify_work_plan_creation(recipients, new_work_plan.activity_title, initiator_name, STATUS_PENDING)  # Include the work plan status

            # Send a separate email to the initiator to track the status
            notify_initiator_about_work_plan(initiator_email, initiator_name, new_work_plan.activity_title, STATUS_PENDING)

            return new_work_plan

        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def approve_work_plan(self, work_plan_id: int, approver_id: int):
        """Approve a work plan and set the approver."""
        STATUS_APPROVED ="Approved"
        db_work_plan = self.get_work_plan_by_id(work_plan_id)
        if db_work_plan is None:
            raise HTTPException(status_code=404, detail="Work plan not found")

        #Check if the plan has already been Approved
        if db_work_plan.is_approved:
            raise HTTPException(status_code=400, detail="Work plan already approved")

        #Reverse if the Plan was initially Re-Scheduled 
        if db_work_plan.is_rescheduled:
            db_work_plan.is_rescheduled = False
            db_work_plan.date_rescheduled = None

        #Reverse if the Plan was Initially Denied
        if db_work_plan.is_denied:
            db_work_plan.is_denied = False
            db_work_plan.date_denied = None

        #Reverse the reason back to null    
        if db_work_plan.reason is not None:
            db_work_plan.reason = None

        # Generate a unique code for the work plan
        work_plan_code = self.generate_work_plan_code(db_work_plan)
        if not db_work_plan.workplan_code:
            db_work_plan.workplan_code = work_plan_code

        # Set the work plan as approved and update the approver details
        db_work_plan.is_approved = True
        db_work_plan.approved_by = approver_id
        db_work_plan.date_approved = datetime.utcnow()
        db_work_plan.status = STATUS_APPROVED

        try:
            self.db_session.commit()

            # Prepare the list of recipients with first names and emails
            recipients = [(employee.first_name, employee.employee_email) for employee in db_work_plan.employees if employee.employee_email]
            
            # Send notification emails to all associated employees with status
            notify_work_plan_approval(
                recipients, 
                db_work_plan.activity_title, 
                db_work_plan.workplan_code, 
                db_work_plan.activity_date, 
                db_work_plan.activity_start_time,
                STATUS_APPROVED  # Assuming you're passing the current status of the work plan
            )
            return db_work_plan
        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Failed to approve work plan: {e}")
            raise HTTPException(status_code=500, detail="Failed to approve work plan")


    def deny_work_plan(self, work_plan_id: int, reason: str) -> WorkPlan:
        """
        Deny a work plan and record the reason. If the work plan was previously approved,
        reverse the approval.
        """
        STATUS_DENIED = "Denied"
        db_work_plan = self.get_work_plan_by_id(work_plan_id)
        if db_work_plan is None:
            raise HTTPException(status_code=404, detail="Work plan not found")

        if db_work_plan.is_denied:
            raise HTTPException(status_code=400, detail="Work plan already denied")

        # If the work plan was approved, set approval status to False and clear the approval date
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

            # Prepare notification details for all associated employees
            recipients = [(employee.first_name, employee.employee_email) for employee in db_work_plan.employees if employee.employee_email]
            notify_work_plan_denial(
                recipients,
                db_work_plan.activity_title, 
                db_work_plan.workplan_code, 
                reason,
                STATUS_DENIED
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
            if work_plan.status != 'Pending':
                raise HTTPException(status_code=400, detail="Work plan is not in a pending state and cannot be updated.")

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
            work_plan = self.db_session.query(WorkPlan).filter(WorkPlan.id == work_plan_id).first()
            if not work_plan:
                raise HTTPException(status_code=404, detail="Work plan not found")
            return work_plan
        except SQLAlchemyError as e:
            # Log the error for debugging purposes
            logging.error(f"Database error occurred: {e}")
            # Optionally, you can raise an HTTPException or your custom exception depending on how you want to handle it in your application.
            raise HTTPException(status_code=500, detail="Database error occurred while fetching the work plan")

    def reschedule_work_plan(self, work_plan_id: int, reason: str, new_date: datetime) -> Union[WorkPlan, dict]:
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
                    db_work_plan.date_approved = None
                    db_work_plan.approved_by = None

                # Reset Denial if the plan was previously Denied
                if db_work_plan.is_denied:
                    db_work_plan.is_denied = False
                    db_work_plan.date_denied = None

                try:
                    self.db_session.commit()
                    # Prepare the list of recipients with their first names and email addresses
                    recipients = [(emp.first_name, emp.employee_email) for emp in db_work_plan.employees if emp.employee_email]
                    # Send email notification
                    notify_work_plan_reschedule(
                        recipients,
                        db_work_plan.activity_title,
                        db_work_plan.workplan_code,
                        reason,
                        new_date.strftime("%Y-%m-%d")
                    )
                    return db_work_plan
                except Exception as e:
                    self.db_session.rollback()
                    logging.error(f"Failed to reschedule work plan: {e}")
                    raise HTTPException(status_code=500, detail=f"Failed to reschedule work plan due to an error: {e}")
            else:
                raise HTTPException(status_code=400, detail="Work plan has already been rescheduled")
        else:
            raise HTTPException(status_code=404, detail="Work plan not found")



    def fetch_employees_by_work_plan(self, workplan_code=None, initiator_name=None, activity_date=None):
        try:
            query = self.db_session.query(Employee)

            if workplan_code:
                query = query.join(Employee.work_plans).filter(WorkPlan.workplan_code == workplan_code)

            if initiator_name:
                name_parts = initiator_name.split()
                if len(name_parts) != 2:
                    raise ValueError("Initiator name must include both first and last names separated by a space.")
                first_name, last_name = name_parts
                query = query.join(Employee.work_plans).join(User, WorkPlan.initiating_user_id == User.id).filter(User.employee.has(first_name=first_name, last_name=last_name))

            if activity_date:
                query = query.join(Employee.work_plans).filter(WorkPlan.activity_date == activity_date)

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
            active_work_plans = self.db_session.query(WorkPlan).filter(WorkPlan.is_active == True).all()
            return active_work_plans
        except Exception as e:
            logging.error(f"Failed to fetch active work plans: {e}")
            raise Exception(f"Database error while fetching active work plans: {e}")


    def fetch_pending_work_plans_for_week(self):
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
            (WorkPlan.initiating_thematic_area_id == ThematicArea.id, ThematicArea.name),
            else_="Unknown"
        )

        # Subquery to get employee names associated with each work plan
        employee_names = self.db_session.query(
            WorkPlan.id.label("work_plan_id"),
            func.string_agg(employee_alias.first_name + ' ' + employee_alias.last_name, ', ').label("employee_names"),
            func.count(employee_alias.id).label("employee_count")  # Count of employees
        ).join(
            workplan_employee_association,
            workplan_employee_association.c.work_plan_id == WorkPlan.id
        ).join(
            employee_alias,
            employee_alias.id == workplan_employee_association.c.employee_id
        ).group_by(WorkPlan.id).subquery()

        # Main query to fetch work plans and associated data
        work_plans = self.db_session.query(
            WorkPlan.id,
            WorkPlan.activity_title,
            WorkPlan.activity_date,
            WorkPlan.status,  # Include status
            Location.name.label("location_name"),
            WorkPlanSource.name.label("workplan_source_name"),
            implementing_team.label("implementing_team"),
            employee_names.c.employee_names,
            employee_names.c.employee_count  # Include count of employees
        ).join(
            WorkPlan.locations
        ).join(
            WorkPlan.workplan_source
        ).outerjoin(
            SRT, WorkPlan.initiating_srt_id == SRT.id
        ).outerjoin(
            Unit, WorkPlan.initiating_unit_id == Unit.id
        ).outerjoin(
            Department, WorkPlan.initiating_department_id == Department.id
        ).outerjoin(
            ThematicArea, WorkPlan.initiating_thematic_area_id == ThematicArea.id
        ).outerjoin(
            employee_names, employee_names.c.work_plan_id == WorkPlan.id
        ).filter(
            WorkPlan.status == "Pending",
            WorkPlan.is_active==True,
            WorkPlan.activity_date >= start_of_week,
            WorkPlan.activity_date <= end_of_week
        ).group_by(
            WorkPlan.id,
            WorkPlan.activity_title,
            WorkPlan.activity_date,
            WorkPlan.status,
            Location.name,
            WorkPlanSource.name,
            implementing_team,
            employee_names.c.employee_names,
            employee_names.c.employee_count
        ).order_by(WorkPlan.group_id).all()

        return [{
            "activity_title": wp.activity_title,
            "activity_date": wp.activity_date.strftime('%Y-%m-%d'),
            # "status": wp.status,
            "location_name": wp.location_name,
            "workplan_source_name": wp.workplan_source_name,
            "implementing_team": wp.implementing_team,
            "employee_names": wp.employee_names,  # Comma-separated list of employee names
            "no_of_staff": wp.employee_count  # Number of employees associated with the work plan
        } for wp in work_plans]
    

    # def fetch_current_week_work_plans_with_status(self):
    #     today = date.today()
    #     start_of_week = today - timedelta(days=today.weekday())  # Monday
    #     end_of_week = start_of_week + timedelta(days=6)  # Sunday

    #     # Alias for employees to use in subqueries
    #     employee_alias = aliased(Employee)

    #     # Define the case statement for dynamically determining the implementing team
    #     implementing_team = case(
    #         (WorkPlan.initiating_srt_id == SRT.id, SRT.name),
    #         (WorkPlan.initiating_unit_id == Unit.id, Unit.name),
    #         (WorkPlan.initiating_department_id == Department.id, Department.name),
    #         (WorkPlan.initiating_thematic_area_id == ThematicArea.id, ThematicArea.name),
    #         else_="Unknown"
    #     )

    #     # Subquery to get employee names associated with each work plan
    #     employee_names = self.db_session.query(
    #         WorkPlan.id.label("work_plan_id"),
    #         func.string_agg(employee_alias.first_name + ' ' + employee_alias.last_name, ', ').label("employee_names"),
    #         func.count(employee_alias.id).label("employee_count")  # Count of employees
    #     ).join(
    #         workplan_employee_association,
    #         workplan_employee_association.c.work_plan_id == WorkPlan.id
    #     ).join(
    #         employee_alias,
    #         employee_alias.id == workplan_employee_association.c.employee_id
    #     ).group_by(WorkPlan.id).subquery()

    #     # Main query to fetch work plans and associated data
    #     work_plans = self.db_session.query(
    #         WorkPlan.id,
    #         WorkPlan.activity_title,
    #         WorkPlan.activity_date,
    #         WorkPlan.status,  # Include status
    #         Location.name.label("location_name"),
    #         WorkPlanSource.name.label("workplan_source_name"),
    #         implementing_team.label("implementing_team"),
    #         employee_names.c.employee_names,
    #         employee_names.c.employee_count  # Include count of employees
    #     ).join(
    #         WorkPlan.locations
    #     ).join(
    #         WorkPlan.workplan_source
    #     ).outerjoin(
    #         SRT, WorkPlan.initiating_srt_id == SRT.id
    #     ).outerjoin(
    #         Unit, WorkPlan.initiating_unit_id == Unit.id
    #     ).outerjoin(
    #         Department, WorkPlan.initiating_department_id == Department.id
    #     ).outerjoin(
    #         ThematicArea, WorkPlan.initiating_thematic_area_id == ThematicArea.id
    #     ).outerjoin(
    #         employee_names, employee_names.c.work_plan_id == WorkPlan.id
    #     ).filter(
    #         # WorkPlan.status == "Pending",
    #         WorkPlan.is_active==True,
    #         WorkPlan.activity_date >= start_of_week,
    #         WorkPlan.activity_date <= end_of_week
    #     ).group_by(
    #         WorkPlan.id,
    #         WorkPlan.activity_title,
    #         WorkPlan.activity_date,
    #         WorkPlan.status,
    #         Location.name,
    #         WorkPlanSource.name,
    #         implementing_team,
    #         employee_names.c.employee_names,
    #         employee_names.c.employee_count
    #     ).order_by(WorkPlan.group_id).all()

    #     return [{
    #         "activity_title": wp.activity_title,
    #         "activity_date": wp.activity_date.strftime('%Y-%m-%d'),
    #         "status": wp.status,
    #         "location_name": wp.location_name,
    #         "workplan_source_name": wp.workplan_source_name,
    #         "implementing_team": wp.implementing_team,
    #         "employee_names": wp.employee_names,  # Comma-separated list of employee names
    #         "no_of_staff": wp.employee_count  # Number of employees associated with the work plan
    #     } for wp in work_plans]

    def fetch_current_week_work_plans_with_status(self):
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
            (WorkPlan.initiating_thematic_area_id == ThematicArea.id, ThematicArea.name),
            else_="Unknown"
        )

        # Subquery to get employee names associated with each work plan
        employee_names = self.db_session.query(
            WorkPlan.id.label("work_plan_id"),
            func.string_agg(func.concat(employee_alias.first_name, ' ', employee_alias.last_name), ', ').label("employee_names")
        ).join(
            workplan_employee_association,
            workplan_employee_association.c.work_plan_id == WorkPlan.id
        ).join(
            employee_alias,
            employee_alias.id == workplan_employee_association.c.employee_id
        ).group_by(WorkPlan.id).subquery()

        # Main query to fetch work plans and associated data
        work_plans = self.db_session.query(
            WorkPlan.id,
            WorkPlan.activity_title,
            WorkPlan.activity_date,
            WorkPlan.status,
            Location.name.label("location_name"),
            WorkPlanSource.name.label("workplan_source_name"),
            implementing_team.label("implementing_team"),
            employee_names.c.employee_names
        ).join(
            WorkPlan.locations
        ).join(
            WorkPlan.workplan_source
        ).outerjoin(
            SRT, WorkPlan.initiating_srt_id == SRT.id
        ).outerjoin(
            Unit, WorkPlan.initiating_unit_id == Unit.id
        ).outerjoin(
            Department, WorkPlan.initiating_department_id == Department.id
        ).outerjoin(
            ThematicArea, WorkPlan.initiating_thematic_area_id == ThematicArea.id
        ).outerjoin(
            employee_names, employee_names.c.work_plan_id == WorkPlan.id
        ).filter(
            WorkPlan.is_active==True,
            WorkPlan.activity_date >= start_of_week,
            WorkPlan.activity_date <= end_of_week
        ).order_by(WorkPlan.group_id).all()

        return [{
            "activity_title": wp.activity_title,
            "activity_date": wp.activity_date.strftime('%Y-%m-%d'),
            "status": wp.status,
            "location_name": wp.location_name,
            "workplan_source_name": wp.workplan_source_name,
            "implementing_team": wp.implementing_team,
            "employee_names": wp.employee_names.split(', ') if wp.employee_names else [],  # Correctly splitting names into a list
            "no_of_staff": len(wp.employee_names.split(', ')) if wp.employee_names else 0
        } for wp in work_plans]


    def list_employees_without_work_plan_on_date(self, activity_date: datetime):
        return self.db_session.query(Employee).outerjoin(workplan_employee_association, and_(
            workplan_employee_association.c.employee_id == Employee.id,
            workplan_employee_association.c.work_plan_id == WorkPlan.id,
            WorkPlan.activity_date == activity_date
        )).filter(WorkPlan.id == None).all()

    def list_archived_work_plans(self, skip: int, limit: int):
        return self.db_session.query(WorkPlan).filter(WorkPlan.archived == True).offset(skip).limit(limit).all()

    def list_work_plans_by_status(self, is_approved: bool, skip: int, limit: int):
        return self.db_session.query(WorkPlan).filter(WorkPlan.is_approved == is_approved).offset(skip).limit(limit).all()


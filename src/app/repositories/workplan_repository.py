
# from typing import List, Optional, Union
# from fastapi import BackgroundTasks, HTTPException
# from sqlalchemy.exc import SQLAlchemyError
# from sqlalchemy import case, func, or_
# from sqlalchemy.orm import Session, aliased
# from sqlalchemy.orm import selectinload
# from models.all_models import (
#     SRT,
#     Department,
#     Trip,
#     Unit,
#     User,
#     WorkPlan,
#     Site,
#     Employee,
#     Location,
#     WorkPlanSource,
#     workplan_employee_association,
#     ThematicArea,
#     workplan_site_association,
#     workplan_location_association,
#     ActionEnum,
# )
# from schemas.workplan_schemas import EmployeeModel, WorkPlanCreate, WorkPlanUpdate
# from datetime import date, datetime, timedelta, timezone
# from logging_helpers import logging_helper
# from auth.email import (
#     notify_initiator_about_work_plan,
#     notify_work_plan_approval,
#     notify_work_plan_creation,
#     notify_work_plan_denial,
#     notify_work_plan_reschedule,
#     notify_work_plan_updates,
#     generate_message_id,
# )

# class WorkPlanRepository:
#     def __init__(self, db_session: Session):
#         self.db_session = db_session

#     def generate_work_plan_code(self, work_plan: WorkPlan) -> str:
#         # This is just a placeholder
#         try:
#             logging_helper.log_info(
#                 f"Workplan code successfully created for the Workpklan id:{work_plan.id}"
#             )
#             return f"WP-{work_plan.id}-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
#         except Exception as e:
#             logging_helper.log_error("Error Generating Workplan Code")
#             raise HTTPException(
#                 status_code=500, detail=f"Error Generating Workplan Code: {e}"
#             )

#     def generate_trip_code(self, trip: Trip) -> str:
#         try:
#             logging_helper.log_info(
#                 f"Workplan code successfully created for the Workplan id:{trip.id}"
#             )
#             return f"TP-{trip.id}-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
#         except Exception as e:
#             logging_helper.log_error("Error Generating Trip Code")
#             raise HTTPException(
#                 status_code=500, detail=f"Error Generating Trip Code: {e}"
#             )

#     def _find_existing_group(self, work_plan_data: WorkPlanCreate):
#         try:
#             start_of_week = work_plan_data.activity_date - timedelta(
#                 days=work_plan_data.activity_date.weekday()
#             )
#             end_of_week = start_of_week + timedelta(days=6)

#             query = self.db_session.query(WorkPlan).filter(
#                 WorkPlan.workplan_source_id == work_plan_data.workplan_source_id,
#                 WorkPlan.activity_date.between(start_of_week, end_of_week),
#             )

#             query = query.filter(
#                 WorkPlan.employees.any(Employee.id.in_(work_plan_data.employee_ids))
#             )

#             filters = []
#             if work_plan_data.initiating_unit_id:
#                 filters.append(
#                     WorkPlan.initiating_unit_id == work_plan_data.initiating_unit_id
#                 )
#             if work_plan_data.initiating_department_id:
#                 filters.append(
#                     WorkPlan.initiating_department_id
#                     == work_plan_data.initiating_department_id
#                 )
#             if work_plan_data.initiating_srt_id:
#                 filters.append(
#                     WorkPlan.initiating_srt_id == work_plan_data.initiating_srt_id
#                 )
#             if work_plan_data.initiating_thematic_area_id:
#                 filters.append(
#                     WorkPlan.initiating_thematic_area_id
#                     == work_plan_data.initiating_thematic_area_id
#                 )

#             if filters:
#                 query = query.filter(or_(*filters))

#             earliest_work_plan = query.order_by(WorkPlan.date_created).first()
#             logging_helper.log_info("Found a matching workplan Group for the Week")
#             return earliest_work_plan
#         except Exception as e:
#             logging_helper.log_error("Error finding an existing Workplan Group")
#             raise HTTPException(
#                 status_code=500, detail=f"Error finding an existing Workplan Group: {e}"
#             )

#     def _valid_id(self, id_value, model):
#         return (
#             id_value
#             if self.db_session.query(model).filter(model.id == id_value).count() > 0
#             else None
#         )

#     def check_existing_work_plan(self, work_plan_data: WorkPlanCreate):
#         try:
#             existing_work_plan = self.db_session.query(WorkPlan).filter(
#                 WorkPlan.activity_title == work_plan_data.activity_title,
#                 WorkPlan.workplan_source_id == work_plan_data.workplan_source_id,
#                 WorkPlan.activity_date == work_plan_data.activity_date,
#             )

#             existing_work_plan = existing_work_plan.filter(
#                 WorkPlan.employees.any(Employee.id.in_(work_plan_data.employee_ids))
#             )
#             return existing_work_plan.first()
#         except Exception as e:
#             logging_helper.log_error(
#                 "Error Checking for a workplan that matches the one being created."
#             )
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"Error Checking for a workplan that matches the one being created: {e}",
#             )

#     def check_employee_schedule_conflict(self, employee_ids, activity_date):
#         existing_work_plan = (
#             self.db_session.query(WorkPlan)
#             .join(WorkPlan.employees)
#             .filter(
#                 Employee.id.in_(employee_ids), WorkPlan.activity_date == activity_date
#             )
#             .first()
#         )
#         return existing_work_plan

#     def create_work_plan(
#         self, background_tasks: BackgroundTasks, work_plan_data: WorkPlanCreate
#     ):
#         STATUS_PENDING = "Pending"
#         try:
#             if not work_plan_data.employee_ids or all(
#                 id == 0 for id in work_plan_data.employee_ids
#             ):
#                 raise ValueError("At least one valid employee is required.")
#             if not work_plan_data.site_ids or all(
#                 id == 0 for id in work_plan_data.site_ids
#             ):
#                 raise ValueError("At least one valid site is required.")
#             if not work_plan_data.location_ids or all(
#                 id == 0 for id in work_plan_data.location_ids
#             ):
#                 raise ValueError("At least one valid location is required.")

#             initiator = (
#                 self.db_session.query(User)
#                 .filter(User.id == work_plan_data.initiating_user_id)
#                 .first()
#             )
#             if not initiator:
#                 logging_helper.log_error("Initiating user not provided by the user")
#                 raise HTTPException(status_code=404, detail="Initiating user not found")

#             over_two_weeks_ago = date.today() - timedelta(days=14)
#             employees_with_unsubmitted_reports = (
#                 self.db_session.query(Employee)
#                 .join(WorkPlan.employees)
#                 .filter(
#                     Employee.id.in_(work_plan_data.employee_ids),
#                     WorkPlan.activity_date < over_two_weeks_ago,
#                     WorkPlan.is_report_submitted.is_(False),
#                     WorkPlan.is_approved.is_(True),
#                 )
#                 .distinct()
#             )

#             if employees_with_unsubmitted_reports.count() > 0:
#                 employee_names = ", ".join(
#                     f"{emp.first_name} {emp.last_name}"
#                     for emp in employees_with_unsubmitted_reports
#                 )
#                 logging_helper.log_error(
#                     f"{employee_names}, who have not submitted their trip report(s) from over two weeks ago Trip embarked on, cannot be added to this workplan. Kindly drop them to Proceed"
#                 )
#                 raise HTTPException(
#                     status_code=400,
#                     detail=f"{employee_names}, who have not submitted their trip report(s) from over two weeks ago Trip embarked on, cannot be added to this workplan. Kindly drop them to Proceed",
#                 )

#             initiator_name = (
#                 f"{initiator.employee.first_name} {initiator.employee.last_name}"
#                 if initiator.employee
#                 else initiator.username
#             )
#             initiator_email = initiator.email

#             source_id_to_field = {
#                 1: ("initiating_unit_id", Unit),
#                 2: ("initiating_department_id", Department),
#                 3: ("initiating_srt_id", SRT),
#                 4: ("initiating_thematic_area_id", ThematicArea),
#             }
#             if work_plan_data.workplan_source_id not in source_id_to_field:
#                 raise ValueError("Invalid workplan source ID.")

#             field_name, field_class = source_id_to_field[
#                 work_plan_data.workplan_source_id
#             ]
#             initiating_id = getattr(work_plan_data, field_name)
#             if initiating_id is None or initiating_id == 0:
#                 logging_helper.log_error(
#                     f"Required initiating ID for the selected workplan source is not provided or invalid."
#                 )
#                 raise ValueError(
#                     f"Required initiating ID for the selected workplan source is not provided or invalid."
#                 )
#             if not work_plan_data.activity_lead_id:
#                 logging_helper.log_error("Activity lead was not provided by the user.")
#                 raise ValueError("Activity lead is required.")

#             initiating_unit_id = (
#                 self._valid_id(work_plan_data.initiating_unit_id, Unit)
#                 if work_plan_data.initiating_unit_id
#                 else None
#             )
#             initiating_department_id = (
#                 self._valid_id(work_plan_data.initiating_department_id, Department)
#                 if work_plan_data.initiating_department_id
#                 else None
#             )
#             initiating_srt_id = (
#                 self._valid_id(work_plan_data.initiating_srt_id, SRT)
#                 if work_plan_data.initiating_srt_id
#                 else None
#             )
#             initiating_thematic_area_id = (
#                 self._valid_id(work_plan_data.initiating_thematic_area_id, ThematicArea)
#                 if work_plan_data.initiating_thematic_area_id
#                 else None
#             )
#             if not self._valid_id(work_plan_data.workplan_source_id, WorkPlanSource):
#                 logging_helper.log_error("Work plan source not provided by the user")
#                 raise HTTPException(
#                     status_code=404, detail="Work plan source not found"
#                 )
#             if self.check_existing_work_plan(work_plan_data):
#                 logging_helper.log_error(
#                     "Fail to create the Workplan as a similar workplan already exists."
#                 )
#                 raise HTTPException(
#                     status_code=400, detail="A similar work plan already exists."
#                 )
#             schedule_conflict = self.check_employee_schedule_conflict(
#                 work_plan_data.employee_ids, work_plan_data.activity_date
#             )
#             if schedule_conflict:
#                 conflicting_employee_names = [
#                     employee.first_name
#                     for employee in schedule_conflict.employees
#                     if employee.id in work_plan_data.employee_ids
#                 ]
#                 logging_helper.log_error(
#                     f"One or more employees are already assigned to another work plan on the chosen date. {', '.join(conflicting_employee_names)}"
#                 )
#                 raise HTTPException(
#                     status_code=400,
#                     detail=f"One or more employees are already assigned to another work plan on the chosen date. {', '.join(conflicting_employee_names)}",
#                 )

#             existing_group = self._find_existing_group(work_plan_data)
#             new_work_plan = WorkPlan(
#                 activity_title=work_plan_data.activity_title,
#                 specific_task=work_plan_data.specific_task,
#                 logistics_required=work_plan_data.logistics_required,
#                 activity_date=work_plan_data.activity_date,
#                 tenancy_id=work_plan_data.tenancy_id,
#                 activity_start_time=work_plan_data.activity_start_time,
#                 initiating_user_id=work_plan_data.initiating_user_id,
#                 activity_lead_id=work_plan_data.activity_lead_id,
#                 initiating_unit_id=initiating_unit_id,
#                 initiating_srt_id=initiating_srt_id,
#                 initiating_department_id=initiating_department_id,
#                 initiating_thematic_area_id=initiating_thematic_area_id,
#                 workplan_source_id=work_plan_data.workplan_source_id,
#                 status=STATUS_PENDING,
#                 need_vehicle=work_plan_data.need_vehicle,
#                 group_id=existing_group.id if existing_group else None,
#             )
#             self.db_session.add(new_work_plan)
#             self.db_session.flush()

#             if not existing_group:
#                 new_work_plan.group_id = new_work_plan.id
#                 self.db_session.commit()
#             new_work_plan.sites.extend(
#                 self.db_session.query(Site)
#                 .filter(Site.id.in_(work_plan_data.site_ids))
#                 .all()
#             )
#             new_work_plan.employees.extend(
#                 self.db_session.query(Employee)
#                 .filter(Employee.id.in_(work_plan_data.employee_ids))
#                 .all()
#             )
#             new_work_plan.locations.extend(
#                 self.db_session.query(Location)
#                 .filter(Location.id.in_(work_plan_data.location_ids))
#                 .all()
#             )

#             self.db_session.commit()

#             recipients = [
#                 (employee.first_name, employee.employee_email)
#                 for employee in new_work_plan.employees
#                 if employee.employee_email
#             ]
#             if initiator_email not in [email for _, email in recipients]:
#                 recipients.append(
#                     (
#                         (
#                             initiator.employee.first_name
#                             if initiator.employee
#                             else initiator.username.split("@")[0]
#                         ),
#                         initiator_email,
#                     )
#                 )

#             message_id = generate_message_id()

#             background_tasks.add_task(
#                 notify_work_plan_creation,
#                 recipients,
#                 new_work_plan.activity_title,
#                 initiator_name,
#                 STATUS_PENDING,
#                 message_id=message_id,
#             )
#             background_tasks.add_task(
#                 notify_initiator_about_work_plan,
#                 initiator_email,
#                 initiator_name,
#                 new_work_plan.activity_title,
#                 STATUS_PENDING,
#                 message_id=message_id,
#             )
#             logging_helper.log_info(
#                 f"The workplan with id {new_work_plan.id} has been created successfully"
#             )
#             return new_work_plan

#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Database error: {e}")
#             raise HTTPException(status_code=500, detail=str(e))

#     def send_emails_in_background(
#         self, recipients, activity_title, initiator_name, status, message_id
#     ):
#         notify_work_plan_creation(
#             recipients, activity_title, initiator_name, status, message_id=message_id
#         )
#         initiator_email = next((email for _, email in recipients if email), None)
#         if initiator_email:
#             notify_initiator_about_work_plan(
#                 initiator_email,
#                 initiator_name,
#                 activity_title,
#                 status,
#                 message_id=message_id,
#             )

#     def update_work_plan(
#         self,
#         work_plan_id: int,
#         update_data: WorkPlanUpdate,
#         tenancy_id: Optional[int] = None,
#     ):
#         try:
#             if tenancy_id:
#                 work_plan = (
#                     self.db_session.query(WorkPlan)
#                     .filter(
#                         WorkPlan.id == work_plan_id, WorkPlan.tenancy_id == work_plan_id
#                     )
#                     .first()
#                 )
#                 if not work_plan:
#                     logging_helper.log_error(
#                         f"Work plan ID {work_plan_id} not found or does not belong to your state"
#                     )
#                     raise HTTPException(
#                         status_code=404,
#                         detail=f"Work plan ID {work_plan_id} not found or does not belong to your state",
#                     )
#             else:
#                 work_plan = (
#                     self.db_session.query(WorkPlan)
#                     .filter(WorkPlan.id == work_plan_id)
#                     .first()
#                 )
#                 if not work_plan:
#                     logging_helper.log_error(f"Work plan ID {work_plan_id} not found")
#                     raise HTTPException(
#                         status_code=404, detail=f"Work plan ID {work_plan_id} not found"
#                     )

#             if (
#                 update_data.workplan_source_id is None
#                 or update_data.workplan_source_id == 0
#             ):
#                 logging_helper.log_error("workplan_source_id was not provided.")
#                 raise ValueError("workplan_source_id cannot be zero.")

#             regroup_needed = False
#             changes_detected = {}

#             fields_to_check = [
#                 "activity_title",
#                 "specific_task",
#                 "logistics_required",
#                 "activity_date",
#                 "activity_start_time",
#                 "activity_lead_id",
#             ]
#             for field in fields_to_check:
#                 new_value = getattr(update_data, field, None)
#                 if new_value is not None and new_value != getattr(work_plan, field):
#                     changes_detected[field] = (getattr(work_plan, field), new_value)
#                     setattr(work_plan, field, new_value)
#                     regroup_needed = True

#             field_class_map = {
#                 "initiating_unit_id": Unit,
#                 "initiating_department_id": Department,
#                 "initiating_srt_id": SRT,
#                 "initiating_thematic_area_id": ThematicArea,
#             }

#             source_id_to_field = {
#                 1: "initiating_unit_id",
#                 2: "initiating_department_id",
#                 3: "initiating_srt_id",
#                 4: "initiating_thematic_area_id",
#             }
#             correct_field = source_id_to_field.get(update_data.workplan_source_id, None)
#             if correct_field:
#                 correct_id = getattr(update_data, correct_field, None)
#                 if correct_id is None or correct_id == 0:
#                     setattr(work_plan, correct_field, None)
#                 else:
#                     if not self._valid_id(correct_id, field_class_map[correct_field]):
#                         raise HTTPException(
#                             status_code=400, detail=f"Invalid {correct_field} provided."
#                         )
#                     setattr(work_plan, correct_field, correct_id)
#                 regroup_needed = True
#                 for field, clazz in field_class_map.items():
#                     if field != correct_field:
#                         setattr(work_plan, field, None)

#             if update_data.employee_ids:
#                 schedule_conflict = self.check_employee_schedule_conflict(
#                     update_data.employee_ids, update_data.activity_date
#                 )
#                 if schedule_conflict and schedule_conflict.id != work_plan_id:
#                     conflicting_employee_names = [
#                         employee.first_name
#                         for employee in schedule_conflict.employees
#                         if employee.id in update_data.employee_ids
#                     ]
#                     raise HTTPException(
#                         status_code=400,
#                         detail=f"One or more employees are already assigned to another work plan on the chosen date. {', '.join(conflicting_employee_names)}",
#                     )

#             if update_data.employee_ids is not None:
#                 new_employees = (
#                     self.db_session.query(Employee)
#                     .filter(Employee.id.in_(update_data.employee_ids))
#                     .all()
#                 )
#                 work_plan.employees = new_employees
#                 changes_detected["employees"] = [e.id for e in new_employees]

#             if update_data.site_ids is not None:
#                 new_sites = (
#                     self.db_session.query(Site)
#                     .filter(Site.id.in_(update_data.site_ids))
#                     .all()
#                 )
#                 work_plan.sites = new_sites
#                 changes_detected["sites"] = [s.id for s in new_sites]

#             if update_data.location_ids is not None:
#                 new_locations = (
#                     self.db_session.query(Location)
#                     .filter(Location.id.in_(update_data.location_ids))
#                     .all()
#                 )
#                 work_plan.locations = new_locations
#                 changes_detected["locations"] = [l.id for l in new_locations]

#             if regroup_needed:
#                 new_group = self._find_existing_group(work_plan)
#                 work_plan.group_id = new_group.id if new_group else work_plan.id

#             self.db_session.commit()

#             if changes_detected:
#                 recipients = [
#                     (emp.first_name, emp.employee_email) for emp in work_plan.employees
#                 ]
#                 notify_work_plan_updates(
#                     recipients, work_plan.activity_title, changes_detected
#                 )

#             return work_plan

#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Failed to update work plan: {e}")
#             raise HTTPException(status_code=500, detail=str(e))

#     def fetch_pending_work_plans_for_week(
#         self, tenancy_id: Optional[int] = None, employee_id: Optional[int] = None
#     ):
#         today = date.today()
#         start_of_week = today - timedelta(days=today.weekday())  # Monday
#         end_of_week = start_of_week + timedelta(days=6)  # Sunday

#         employee_alias = aliased(Employee)

#         implementing_team = case(
#             (WorkPlan.initiating_srt_id == SRT.id, SRT.name),
#             (WorkPlan.initiating_unit_id == Unit.id, Unit.name),
#             (WorkPlan.initiating_department_id == Department.id, Department.name),
#             (
#                 WorkPlan.initiating_thematic_area_id == ThematicArea.id,
#                 ThematicArea.name,
#             ),
#             else_="Unknown",
#         )

#         employee_names = (
#             self.db_session.query(
#                 WorkPlan.id.label("work_plan_id"),
#                 func.string_agg(
#                     employee_alias.first_name + " " + employee_alias.last_name, ", "
#                 ).label("employee_names"),
#                 func.count(employee_alias.id).label("employee_count"),
#             )
#             .join(
#                 workplan_employee_association,
#                 workplan_employee_association.c.work_plan_id == WorkPlan.id,
#             )
#             .join(
#                 employee_alias,
#                 employee_alias.id == workplan_employee_association.c.employee_id,
#             )
#             .group_by(WorkPlan.id)
#             .subquery()
#         )

#         work_plans = (
#             self.db_session.query(
#                 WorkPlan.id,
#                 WorkPlan.activity_title,
#                 WorkPlan.activity_date,
#                 WorkPlan.status,
#                 Location.name.label("location_name"),
#                 WorkPlanSource.name.label("workplan_source_name"),
#                 implementing_team.label("implementing_team"),
#                 employee_names.c.employee_names,
#                 employee_names.c.employee_count,
#                 WorkPlan.tenancy_id,
#             )
#             .join(WorkPlan.locations)
#             .join(WorkPlan.workplan_source)
#             .outerjoin(SRT, WorkPlan.initiating_srt_id == SRT.id)
#             .outerjoin(Unit, WorkPlan.initiating_unit_id == Unit.id)
#             .outerjoin(Department, WorkPlan.initiating_department_id == Department.id)
#             .outerjoin(
#                 ThematicArea, WorkPlan.initiating_thematic_area_id == ThematicArea.id
#             )
#             .outerjoin(employee_names, employee_names.c.work_plan_id == WorkPlan.id)
#             .filter(
#                 WorkPlan.status == "Pending",
#                 WorkPlan.is_active == True,
#                 WorkPlan.activity_date >= start_of_week,
#                 WorkPlan.activity_date <= end_of_week,
#             )
#         )

#         if tenancy_id:
#             work_plans = work_plans.filter(WorkPlan.tenancy_id == tenancy_id)

#         if employee_id:
#             work_plans = work_plans.join(
#                 workplan_employee_association,
#                 workplan_employee_association.c.work_plan_id == WorkPlan.id,
#             )
#             work_plans = work_plans.filter(
#                 workplan_employee_association.c.employee_id == employee_id
#             )

#         list_of_work_plans = (
#             work_plans.group_by(
#                 WorkPlan.id,
#                 WorkPlan.activity_title,
#                 WorkPlan.activity_date,
#                 WorkPlan.status,
#                 Location.name,
#                 WorkPlanSource.name,
#                 implementing_team,
#                 employee_names.c.employee_names,
#                 employee_names.c.employee_count,
#                 WorkPlan.tenancy_id,
#             )
#             .order_by(WorkPlan.group_id)
#             .all()
#         )

#         return [
#             {
#                 "workplan_id": wp.id,
#                 "activity_title": wp.activity_title,
#                 "activity_date": wp.activity_date.strftime("%Y-%m-%d"),
#                 "location_name": wp.location_name,
#                 "workplan_source_name": wp.workplan_source_name,
#                 "implementing_team": wp.implementing_team,
#                 "employee_names": [wp.employee_names],
#                 "no_of_staff": wp.employee_count,
#                 "tenancy_id": wp.tenancy_id,
#             }
#             for wp in list_of_work_plans
#         ]

#     def fetch_current_week_work_plans_with_status(
#         self,
#         start_of_week: date,
#         end_of_week: date,
#         vehicle_assigned: Optional[bool],
#         tenancy_id: Optional[int] = None,
#         employee_id: Optional[int] = None,
#     ):
#         try:
#             employee_alias = aliased(Employee)

#             implementing_team = case(
#                 (WorkPlan.initiating_srt_id == SRT.id, SRT.name),
#                 (WorkPlan.initiating_unit_id == Unit.id, Unit.name),
#                 (WorkPlan.initiating_department_id == Department.id, Department.name),
#                 (
#                     WorkPlan.initiating_thematic_area_id == ThematicArea.id,
#                     ThematicArea.name,
#                 ),
#                 else_="Unknown",
#             )

#             employee_details = (
#                 self.db_session.query(
#                     workplan_employee_association.c.work_plan_id.label("work_plan_id"),
#                     func.array_agg(employee_alias.id).label("employee_ids"),
#                     func.string_agg(
#                         employee_alias.first_name + " " + employee_alias.last_name, ", "
#                     ).label("employee_names"),
#                     func.count().label("employee_count"),
#                 )
#                 .join(
#                     employee_alias,
#                     employee_alias.id == workplan_employee_association.c.employee_id,
#                 )
#                 .group_by(workplan_employee_association.c.work_plan_id)
#                 .subquery()
#             )

#             work_plans_query = (
#                 self.db_session.query(
#                     WorkPlan.id,
#                     WorkPlan.workplan_code,
#                     WorkPlan.activity_title,
#                     WorkPlan.activity_date,
#                     WorkPlan.status,
#                     WorkPlan.vehicle_assigned,
#                     Location.name.label("location_name"),
#                     WorkPlanSource.name.label("workplan_source_name"),
#                     implementing_team.label("implementing_team"),
#                     WorkPlan.initiating_user_id,
#                     employee_details.c.employee_ids,
#                     employee_details.c.employee_names,
#                     employee_details.c.employee_count,
#                     WorkPlan.tenancy_id,
#                 )
#                 .join(WorkPlan.locations)
#                 .join(WorkPlan.workplan_source)
#                 .outerjoin(SRT, WorkPlan.initiating_srt_id == SRT.id)
#                 .outerjoin(Unit, WorkPlan.initiating_unit_id == Unit.id)
#                 .outerjoin(
#                     Department, WorkPlan.initiating_department_id == Department.id
#                 )
#                 .outerjoin(
#                     ThematicArea,
#                     WorkPlan.initiating_thematic_area_id == ThematicArea.id,
#                 )
#                 .outerjoin(
#                     employee_details, employee_details.c.work_plan_id == WorkPlan.id
#                 )
#                 .filter(
#                     WorkPlan.is_active == True,
#                     WorkPlan.activity_date >= start_of_week,
#                     WorkPlan.activity_date <= end_of_week,
#                 )
#             )
#             if vehicle_assigned:
#                 work_plans_query = work_plans_query.filter(WorkPlan.vehicle_assigned)
#             if tenancy_id:
#                 work_plans_query = work_plans_query.filter(
#                     WorkPlan.tenancy_id == tenancy_id
#                 )
#             if employee_id:
#                 work_plans_query = work_plans_query.filter(
#                     employee_details.c.employee_ids.any(employee_id)
#                 )

#             work_plans = work_plans_query.distinct(WorkPlan.id).all()

#             return [
#                 {
#                     "workplan_id": wp.id,
#                     "workplan_code": wp.workplan_code,
#                     "activity_title": wp.activity_title,
#                     "activity_date": wp.activity_date.strftime("%Y-%m-%d"),
#                     "status": wp.status,
#                     "vehicle_assigned": wp.vehicle_assigned,
#                     "location_name": wp.location_name,
#                     "workplan_source_name": wp.workplan_source_name,
#                     "implementing_team": wp.implementing_team,
#                     "initiating_user_id": wp.initiating_user_id,
#                     "employee_ids": wp.employee_ids,
#                     "employee_names": [wp.employee_names],
#                     "no_of_staff": wp.employee_count,
#                     "tenancy_id": wp.tenancy_id,
#                 }
#                 for wp in work_plans
#             ]

#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
#         except Exception as e:
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

#     def approve_work_plan(
#         self,
#         background_tasks: BackgroundTasks,
#         work_plan_id: int,
#         approver_id: int,
#         tenancy_id: Optional[int] = None,
#     ):

#         STATUS_APPROVED = "Approved"

#         if approver_id is None:
#             raise ValueError("Approver ID is required")

#         db_work_plan = self.get_work_plan_by_id(
#             work_plan_id=work_plan_id, tenancy_id=tenancy_id
#         )
#         if db_work_plan is None:
#             raise HTTPException(status_code=404, detail="Work plan not found")

#         if db_work_plan.is_approved:
#             raise HTTPException(status_code=400, detail="Work plan already approved")

#         if db_work_plan.is_rescheduled:
#             db_work_plan.is_rescheduled = False
#             db_work_plan.date_rescheduled = None

#         if db_work_plan.is_denied:
#             db_work_plan.is_denied = False
#             db_work_plan.date_denied = None

#         if db_work_plan.reason is not None:
#             db_work_plan.reason = None

#         work_plan_code = self.generate_work_plan_code(db_work_plan)
#         if not db_work_plan.workplan_code:
#             db_work_plan.workplan_code = work_plan_code

#         db_work_plan.approved_by = approver_id
#         db_work_plan.date_approved = datetime.now(timezone.utc)
#         db_work_plan.status = STATUS_APPROVED
#         db_work_plan.is_approved = True
#         work_plan_code = self.generate_work_plan_code(db_work_plan)
#         db_work_plan.workplan_code = work_plan_code or db_work_plan.workplan_code

#         try:
#             self.db_session.commit()
#             recipients = [
#                 (emp.first_name, emp.employee_email)
#                 for emp in db_work_plan.employees
#                 if emp.employee_email
#             ]

#             message_id = generate_message_id()

#             background_tasks.add_task(
#                 notify_work_plan_approval,
#                 recipients,
#                 db_work_plan.activity_title,
#                 db_work_plan.workplan_code,
#                 db_work_plan.activity_date,
#                 db_work_plan.activity_start_time,
#                 STATUS_APPROVED,
#                 message_id=message_id,
#             )
#             return {
#                 "Feedback": f"The Workplan with the ID {work_plan_id} has been Approved Successfully !!!"
#             }
#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Failed to approve work plan: {e}")
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"Failed to approve work plan due to an error: {e}",
#             )

#     def reschedule_work_plan(
#         self,
#         background_tasks: BackgroundTasks,
#         work_plan_id: int,
#         reason: str,
#         new_date: datetime,
#         tenancy_id: Optional[int] = None,
#     ) -> Union[WorkPlan, dict]:
#         STATUS_RESCHEDULED = "Re-Scheduled"

#         db_work_plan = self.get_work_plan_by_id(
#             work_plan_id=work_plan_id, tenancy_id=tenancy_id
#         )

#         if db_work_plan:
#             if not db_work_plan.is_rescheduled:
#                 db_work_plan.is_rescheduled = True
#                 db_work_plan.reason = reason
#                 db_work_plan.date_rescheduled = datetime.utcnow()
#                 db_work_plan.activity_date = new_date
#                 db_work_plan.status = STATUS_RESCHEDULED

#                 if db_work_plan.is_approved:
#                     db_work_plan.is_approved = False
#                     db_work_plan.date_approved = None
#                     db_work_plan.approved_by = None
#                     db_work_plan.workplan_code = None

#                 if db_work_plan.is_denied:
#                     db_work_plan.is_denied = False
#                     db_work_plan.date_denied = None

#                 try:
#                     self.db_session.commit()
#                     recipients = [
#                         (emp.first_name, emp.employee_email)
#                         for emp in db_work_plan.employees
#                         if emp.employee_email
#                     ]

#                     initiator_email = db_work_plan.initiating_user.email
#                     initiator_name = db_work_plan.initiating_user.employee.first_name

#                     recipients.append((initiator_name, initiator_email))

#                     message_id = generate_message_id()

#                     background_tasks.add_task(
#                         notify_work_plan_reschedule,
#                         recipients,
#                         db_work_plan.activity_title,
#                         db_work_plan.workplan_code,
#                         reason,
#                         new_date.strftime("%Y-%m-%d"),
#                         message_id=message_id,
#                     )

#                     return {
#                         "Feedback": f"The Workplan with the ID {work_plan_id} has been rescheduled Successfully on {new_date.strftime('%Y-%m-%d')} !!!"
#                     }

#                 except Exception as e:
#                     self.db_session.rollback()
#                     logging_helper.log_error(f"Failed to reschedule work plan: {e}")
#                     raise HTTPException(
#                         status_code=500,
#                         detail=f"Failed to reschedule work plan due to an error: {e}",
#                     )
#             else:
#                 raise HTTPException(
#                     status_code=400, detail="Work plan has already been rescheduled"
#                 )
#         else:
#             raise HTTPException(status_code=404, detail="Work plan not found")

#     def deny_work_plan(
#         self,
#         background_tasks: BackgroundTasks,
#         work_plan_id: int,
#         reason: str,
#         tenancy_id: Optional[int] = None,
#     ) -> WorkPlan:
#         STATUS_DENIED = "Denied"
#         db_work_plan = self.get_work_plan_by_id(
#             work_plan_id=work_plan_id, tenancy_id=tenancy_id
#         )
#         if db_work_plan is None:
#             raise HTTPException(status_code=404, detail="Work plan not found")

#         if db_work_plan.is_denied:
#             raise HTTPException(status_code=400, detail="Work plan already denied")

#         if db_work_plan.is_approved:
#             db_work_plan.is_approved = False
#             db_work_plan.date_approved = None
#             db_work_plan.approved_by = None

#         if db_work_plan.is_rescheduled:
#             db_work_plan.is_rescheduled = False
#             db_work_plan.date_rescheduled = None

#         db_work_plan.is_denied = True
#         db_work_plan.reason = reason
#         db_work_plan.date_denied = datetime.utcnow()
#         db_work_plan.status = STATUS_DENIED

#         try:
#             self.db_session.commit()

#             recipients = [
#                 (employee.first_name, employee.employee_email)
#                 for employee in db_work_plan.employees
#                 if employee.employee_email
#             ]

#             message_id = generate_message_id()

#             background_tasks.add_task(
#                 notify_work_plan_denial,
#                 recipients,
#                 db_work_plan.activity_title,
#                 db_work_plan.workplan_code,
#                 reason,
#                 STATUS_DENIED,
#                 message_id=message_id,
#             )

#             return {
#                 "Feedback": f"The Workplan with the ID {work_plan_id} has been Denied"
#             }
#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Failed to deny work plan: {e}")
#             raise HTTPException(status_code=500, detail="Failed to deny work plan")

#     def update_work_plan_if_pending(
#         self,
#         work_plan_id: int,
#         updates: dict,
#         tenancy_id: Optional[int] = None,
#         user_id: Optional[int] = None,
#     ):
#         try:
#             if tenancy_id and user_id:
#                 work_plan = (
#                     self.db_session.query(WorkPlan)
#                     .filter(
#                         WorkPlan.id == work_plan_id,
#                         WorkPlan.initiating_user_id == user_id,
#                     )
#                     .first()
#                 )
#                 if work_plan is None:
#                     raise HTTPException(
#                         status_code=404,
#                         detail="Work plan not found or was not created by you.",
#                     )

#             if tenancy_id:
#                 work_plan = self.get_work_plan_by_id(
#                     work_plan_id, tenancy_id=tenancy_id
#                 )
#                 if work_plan is None:
#                     raise HTTPException(
#                         status_code=404,
#                         detail="Work plan not found or does not belong to the state.",
#                     )

#             if work_plan.status != "Pending":
#                 raise HTTPException(
#                     status_code=400,
#                     detail="Work plan is not in a pending state and cannot be updated.",
#                 )

#             for key, value in updates.items():
#                 if hasattr(work_plan, key):
#                     setattr(work_plan, key, value)

#             self.db_session.commit()
#             return work_plan
#         except Exception as e:
#             self.db_session.rollback()
#             raise Exception(f"An error occurred while updating the work plan: {str(e)}")

#     def get_work_plan_by_id(
#         self,
#         work_plan_id: int,
#         tenancy_id: Optional[int] = None,
#         employee_id: Optional[int] = None,
#     ):
#         try:
#             work_plan = (self.db_session.query(WorkPlan)).filter(
#                 WorkPlan.id == work_plan_id
#             )

#             if tenancy_id:
#                 work_plan = work_plan.filter(WorkPlan.tenancy_id == tenancy_id)

#             if employee_id:
#                 work_plan = work_plan.join(
#                     workplan_employee_association,
#                     workplan_employee_association.c.work_plan_id == WorkPlan.id,
#                 )
#                 work_plan = work_plan.filter(
#                     workplan_employee_association.c.employee_id == employee_id
#                 )

#             work_plan = work_plan.first()

#             if not work_plan:
#                 raise HTTPException(status_code=404, detail="Work plan not found")
#             return work_plan
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Database error occurred: {e}")
#             raise HTTPException(
#                 status_code=500,
#                 detail="Database error occurred while fetching the work plan",
#             )

#     def fetch_employees_by_work_plan(
#         self,
#         workplan_code=None,
#         initiator_name=None,
#         activity_date=None,
#         tenancy_id: Optional[int] = None,
#     ):
#         try:
#             query = self.db_session.query(Employee)

#             if workplan_code:
#                 query = query.join(Employee.work_plans).filter(
#                     WorkPlan.workplan_code == workplan_code
#                 )

#             if initiator_name:
#                 name_parts = initiator_name.split()
#                 if len(name_parts) != 2:
#                     raise ValueError(
#                         "Initiator name must include both first and last names separated by a space."
#                     )
#                 first_name, last_name = name_parts
#                 query = (
#                     query.join(Employee.work_plans)
#                     .join(User, WorkPlan.initiating_user_id == User.id)
#                     .filter(
#                         User.employee.has(first_name=first_name, last_name=last_name)
#                     )
#                 )

#             if activity_date:
#                 query = query.join(Employee.work_plans).filter(
#                     WorkPlan.activity_date == activity_date
#                 )

#             if tenancy_id:
#                 query = query.filter(WorkPlan.tenancy_id == tenancy_id)

#             employees = query.filter(Employee.employee_email != None).all()
#             return [EmployeeModel.from_orm(emp) for emp in employees]
#         except ValueError as ve:
#             logging_helper.log_error(f"Input error: {ve}")
#             raise Exception(f"Input error: {ve}")
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Database error occurred: {e}")
#             raise Exception(f"Failed to fetch employees due to a database error: {e}")
#         except Exception as e:
#             logging_helper.log_error(f"An error occurred: {e}")
#             raise Exception(f"Failed to fetch employees due to an error: {e}")

#     def get_active_work_plans(self, tenancy_id: Optional[int] = None):
#         try:
#             active_work_plans = self.db_session.query(WorkPlan).filter(
#                 WorkPlan.is_active == True
#             )

#             if tenancy_id:
#                 active_work_plans = active_work_plans.filter(
#                     WorkPlan.tenancy_id == tenancy_id
#                 )

#             return active_work_plans
#             logging_helper.log_info(
#                 f"Weekly Active Workplans for the Tenancy with ID: {tenancy_id} was Successfully Fetched"
#             )
#         except Exception as e:
#             logging_helper.log_error(f"Failed to fetch active work plans: {e}")
#             raise Exception(f"Database error while fetching active work plans: {e}")

#     def list_employees_without_work_plan_on_date(
#         self, activity_date: date, tenancy_id: Optional[int] = None
#     ):
#         try:
#             subquery = (
#                 self.db_session.query(workplan_employee_association.c.employee_id)
#                 .join(
#                     WorkPlan,
#                     workplan_employee_association.c.work_plan_id == WorkPlan.id,
#                 )
#                 .filter(WorkPlan.activity_date == activity_date)
#                 .subquery()
#             )

#             employees = (
#                 self.db_session.query(
#                     Employee.id.label("employee_id"),
#                     Employee.staff_code,
#                     Employee.last_name,
#                     Employee.first_name,
#                     Employee.phone_number,
#                 )
#                 .outerjoin(subquery, subquery.c.employee_id == Employee.id)
#                 .filter(subquery.c.employee_id == None)
#             )

#             if tenancy_id:
#                 employees = employees.filter(Employee.tenancy_id == tenancy_id)

#             employees = employees.all()
#             employees_count = len(employees)
#             logging_helper.log_info(
#                 f"A total of {employees_count} Employees were not associated with a Workplan on {activity_date}"
#             )
#             return [
#                 {
#                     "employee_id": emp.employee_id,
#                     "staff_code": emp.staff_code,
#                     "last_name": emp.last_name,
#                     "first_name": emp.first_name,
#                     "phone_number": emp.phone_number,
#                 }
#                 for emp in employees
#             ]
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Database error occurred: {e}")
#             return []
#         except Exception as e:
#             logging_helper.log_error(f"An unexpected error occurred: {e}")
#             return []

#     def list_archived_work_plans(self, skip: int, limit: int):
#         try:
#             return (
#                 self.db_session.query(WorkPlan)
#                 .filter(WorkPlan.archived == True)
#                 .offset(skip)
#                 .limit(limit)
#                 .all()
#             )
#         except Exception as e:
#             logging_helper.log_error(f"Error Listing the Archived Workplans: {str(e)}")

#     def list_work_plans_by_status(self, is_approved: bool, skip: int, limit: int):
#         return (
#             self.db_session.query(WorkPlan)
#             .filter(WorkPlan.is_approved == is_approved)
#             .offset(skip)
#             .limit(limit)
#             .all()
#         )

#     def fetch_approved_weekly_work_plans(self, tenancy_id: Optional[int] = None):
#         today = date.today()
#         start_of_week = today - timedelta(days=today.weekday())  # Monday
#         end_of_week = start_of_week + timedelta(days=6)  # Sunday

#         employee_alias = aliased(Employee)

#         implementing_team = case(
#             (WorkPlan.initiating_srt_id == SRT.id, SRT.name),
#             (WorkPlan.initiating_unit_id == Unit.id, Unit.name),
#             (WorkPlan.initiating_department_id == Department.id, Department.name),
#             (
#                 WorkPlan.initiating_thematic_area_id == ThematicArea.id,
#                 ThematicArea.name,
#             ),
#             else_="Unknown",
#         ).label("implementing_team")

#         employee_details = (
#             self.db_session.query(
#                 workplan_employee_association.c.work_plan_id.label("work_plan_id"),
#                 func.array_agg(employee_alias.id).label("employee_ids"),
#                 func.string_agg(
#                     employee_alias.first_name + " " + employee_alias.last_name, ", "
#                 ).label("employee_names"),
#                 func.count().label("employee_count"),
#             )
#             .join(
#                 employee_alias,
#                 employee_alias.id == workplan_employee_association.c.employee_id,
#             )
#             .group_by(workplan_employee_association.c.work_plan_id)
#             .subquery()
#         )

#         work_plans = (
#             self.db_session.query(WorkPlan)
#             .options(selectinload(WorkPlan.employees), selectinload(WorkPlan.locations))
#             .join(WorkPlanSource, isouter=True)
#             .outerjoin(SRT)
#             .outerjoin(Unit)
#             .outerjoin(Department)
#             .outerjoin(ThematicArea)
#             .filter(
#                 WorkPlan.status == "Approved",
#                 WorkPlan.activity_date >= start_of_week,
#                 WorkPlan.activity_date <= end_of_week,
#             )
#         )

#         if tenancy_id:
#             work_plans = work_plans.filter(WorkPlan.tenancy_id == tenancy_id)

#         work_plans = work_plans.all()

#         return [
#             {
#                 "id": wp.id,
#                 "workplan_code": wp.workplan_code,
#                 "activity_title": wp.activity_title,
#                 "specific_task": wp.specific_task,
#                 "logistics_required": wp.logistics_required,
#                 "activity_date": wp.activity_date.isoformat(),
#                 "activity_time": (
#                     wp.activity_start_time.isoformat()
#                     if wp.activity_start_time
#                     else None
#                 ),
#                 "initiating_user_id": wp.initiating_user_id,
#                 "status": wp.status,
#                 "workplan_source_name": wp.workplan_source.name,
#                 "implementing_team": getattr(wp, "implementing_team", None),
#                 "employee_ids": [emp.id for emp in wp.employees],
#                 "employee_names": [
#                     f"{emp.first_name} {emp.last_name}" for emp in wp.employees
#                 ],
#                 "employee_count": len(wp.employees),
#                 "locations": [loc.name for loc in wp.locations],
#             }
#             for wp in work_plans
#         ]

#     def fetch_approved_work_plan_by_code_or_id(
#         self, identifier: str, tenancy_id: Optional[int] = None
#     ):
#         try:
#             employee_alias = aliased(Employee)

#             employee_names = (
#                 self.db_session.query(
#                     WorkPlan.id.label("work_plan_id"),
#                     func.string_agg(
#                         employee_alias.first_name + " " + employee_alias.last_name, ", "
#                     ).label("employee_names"),
#                     func.count(employee_alias.id).label("employee_count"),
#                 )
#                 .join(
#                     workplan_employee_association,
#                     workplan_employee_association.c.work_plan_id == WorkPlan.id,
#                 )
#                 .join(
#                     employee_alias,
#                     employee_alias.id == workplan_employee_association.c.employee_id,
#                 )
#                 .group_by(WorkPlan.id)
#                 .subquery()
#             )

#             if identifier.isdigit():
#                 work_plan_query = self.db_session.query(WorkPlan).filter(
#                     WorkPlan.id == int(identifier), WorkPlan.status == "Approved"
#                 )
#             else:
#                 work_plan_query = self.db_session.query(WorkPlan).filter(
#                     WorkPlan.workplan_code == identifier, WorkPlan.status == "Approved"
#                 )

#             if tenancy_id:
#                 work_plan_query = work_plan_query.filter(
#                     WorkPlan.tenancy_id == tenancy_id
#                 )

#             work_plan = (
#                 work_plan_query.outerjoin(
#                     employee_names, employee_names.c.work_plan_id == WorkPlan.id
#                 )
#                 .add_columns(
#                     employee_names.c.employee_names, employee_names.c.employee_count
#                 )
#                 .first()
#             )

#             if work_plan:
#                 wp, employee_names, employee_count = work_plan
#                 return {
#                     "id": wp.id,
#                     "workplan_code": wp.workplan_code,
#                     "activity_title": wp.activity_title,
#                     "specific_task": wp.specific_task,
#                     "logistics_required": wp.logistics_required,
#                     "activity_date": wp.activity_date.isoformat(),
#                     "initiating_user_id": wp.initiating_user_id,
#                     "status": wp.status,
#                     "employee_names": (
#                         employee_names.split(", ") if employee_names else []
#                     ),
#                     "employee_count": employee_count,
#                 }
#             return None
#         except Exception as e:
#             logging_helper.log_error(
#                 f"Error fetching approved workplan by identifier : {identifier}"
#             )
#             raise (f"Error fetching approved workplan by identifier : {identifier}")

#     def fetch_approved_work_plan_by_entity(
#         self, entity_type: str, entity_name: str, tenancy_id: Optional[int] = None
#     ):
#         employee_alias = aliased(Employee)

#         employee_names = (
#             self.db_session.query(
#                 WorkPlan.id.label("work_plan_id"),
#                 func.string_agg(
#                     employee_alias.first_name + " " + employee_alias.last_name, ", "
#                 ).label("employee_names"),
#                 func.count(employee_alias.id).label("employee_count"),
#             )
#             .join(
#                 workplan_employee_association,
#                 workplan_employee_association.c.work_plan_id == WorkPlan.id,
#             )
#             .join(
#                 employee_alias,
#                 employee_alias.id == workplan_employee_association.c.employee_id,
#             )
#             .group_by(WorkPlan.id)
#             .subquery()
#         )

#         base_query = (
#             self.db_session.query(WorkPlan)
#             .outerjoin(employee_names, employee_names.c.work_plan_id == WorkPlan.id)
#             .add_columns(
#                 employee_names.c.employee_names, employee_names.c.employee_count
#             )
#             .filter(WorkPlan.status == "Approved")
#         )

#         if entity_type.lower() == "unit":
#             base_query = base_query.join(Unit).filter(Unit.name == entity_name)
#         elif entity_type.lower() == "srt":
#             base_query = base_query.join(SRT).filter(SRT.name == entity_name)
#         elif entity_type.lower() == "department":
#             base_query = base_query.join(Department).filter(
#                 Department.name == entity_name
#             )
#         elif entity_type.lower() == "thematicarea":
#             base_query = base_query.join(ThematicArea).filter(
#                 ThematicArea.name == entity_name
#             )
#         else:
#             raise ValueError(
#                 "Invalid entity type provided. Must be one of: unit, srt, department, thematicarea."
#             )

#         if tenancy_id:
#             base_query = base_query.filter(WorkPlan.tenancy_id == tenancy_id)

#         work_plan = base_query.first()

#         if work_plan:
#             wp, employee_names, employee_count = work_plan
#             return {
#                 "id": wp.id,
#                 "workplan_code": wp.workplan_code,
#                 "activity_title": wp.activity_title,
#                 "specific_task": wp.specific_task,
#                 "logistics_required": wp.logistics_required,
#                 "activity_date": wp.activity_date.isoformat(),
#                 "initiating_user_id": wp.initiating_user_id,
#                 "status": wp.status,
#                 "employee_names": employee_names.split(", ") if employee_names else [],
#                 "employee_count": employee_count,
#             }
#         return None

#     def fetch_monthly_work_plan_summary(
#         self, year: int, month: int, tenancy_id: Optional[int] = None
#     ):
#         from sqlalchemy import extract

#         if not (1 <= month <= 12):
#             raise ValueError("Month must be between 1 and 12")
#         if year < 1900 or year > 2100:
#             raise ValueError("Year must be a reasonable value")

#         start_date = date(year, month, 1)
#         end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

#         work_plans = (
#             self.db_session.query(
#                 WorkPlan.status,
#                 func.count(WorkPlan.id).label("count"),
#                 func.string_agg(
#                     Employee.first_name + " " + Employee.last_name, ", "
#                 ).label("employee_names"),
#             )
#             .join(
#                 workplan_employee_association,
#                 workplan_employee_association.c.work_plan_id == WorkPlan.id,
#             )
#             .join(Employee, Employee.id == workplan_employee_association.c.employee_id)
#             .filter(WorkPlan.activity_date.between(start_date, end_date))
#         )

#         work_plans = work_plans.group_by(WorkPlan.status)

#         if tenancy_id:
#             work_plans = work_plans.filter(WorkPlan.tenancy_id == tenancy_id)

#         work_plans = work_plans.all()

#         summary = {"month": month, "year": year, "details": []}
#         for status, count, employee_names in work_plans:
#             summary["details"].append(
#                 {
#                     "status": status,
#                     "employee_count": count,
#                     "employees": (
#                         list(set(employee_names.split(", "))) if employee_names else []
#                     ),
#                 }
#             )
#         logging_helper.log_error("Successfully fetched the monthly workplan summary")
#         return summary

#     def fetch_workplans_by_date_range(
#         self,
#         start_date: date,
#         end_date: date,
#         status: Optional[str] = None,
#         tenancy_id: Optional[int] = None,
#     ) -> List[dict]:
#         employee_alias = aliased(Employee)

#         employee_names = (
#             self.db_session.query(
#                 WorkPlan.id.label("work_plan_id"),
#                 func.string_agg(
#                     employee_alias.first_name + " " + employee_alias.last_name, ", "
#                 ).label("employee_names"),
#                 func.count(employee_alias.id).label("employee_count"),
#             )
#             .join(
#                 workplan_employee_association,
#                 workplan_employee_association.c.work_plan_id == WorkPlan.id,
#             )
#             .join(
#                 employee_alias,
#                 employee_alias.id == workplan_employee_association.c.employee_id,
#             )
#             .group_by(WorkPlan.id)
#             .subquery()
#         )

#         query = (
#             self.db_session.query(
#                 WorkPlan.id,
#                 WorkPlan.workplan_code,
#                 WorkPlan.activity_title,
#                 WorkPlan.specific_task,
#                 WorkPlan.logistics_required,
#                 WorkPlan.activity_date,
#                 WorkPlan.initiating_user_id,
#                 WorkPlan.status,
#                 WorkPlanSource.name.label("workplan_source_name"),
#                 employee_names.c.employee_names,
#                 employee_names.c.employee_count,
#                 User.username.label("initiating_user_name"),
#             )
#             .outerjoin(employee_names, employee_names.c.work_plan_id == WorkPlan.id)
#             .join(WorkPlan.initiating_user)
#             .join(WorkPlan.workplan_source)
#             .filter(
#                 WorkPlan.activity_date >= start_date, WorkPlan.activity_date <= end_date
#             )
#         )

#         if tenancy_id:
#             query = query.filter(WorkPlan.tenancy_id == tenancy_id)

#         if status:
#             query = query.filter(WorkPlan.status == status)

#         try:
#             work_plans = query.order_by(WorkPlan.activity_date).all()
#             work_plan_count = len(work_plans)
#             logging_helper.log_info(
#                 f"Successfully fetched {work_plan_count} workplan(s) based on the date ranges: {start_date} and {end_date} with the status: {status}"
#             )
#             return [
#                 {
#                     "work_plan_id": wp.id,
#                     "workplan_code": wp.workplan_code,
#                     "activity_title": wp.activity_title,
#                     "specific_task": wp.specific_task,
#                     "logistics_required": wp.logistics_required,
#                     "activity_date": wp.activity_date.isoformat(),
#                     "initiating_user_name": wp.initiating_user_name,
#                     "workplan_source_name": wp.workplan_source_name,
#                     "status": wp.status,
#                     "employee_names": (
#                         wp.employee_names.split(", ") if wp.employee_names else []
#                     ),
#                     "employee_count": wp.employee_count,
#                 }
#                 for wp in work_plans
#             ]
#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(
#                 f"Error retrieving work plans based on the date range {start_date} and {end_date}: {str(e)}"
#             )
#             raise Exception(f"Error retrieving work plans: {str(e)}")

#     def get_work_plans_by_logistics(
#         self, logistics_requirement: str, tenancy_id: Optional[int] = None
#     ) -> List[dict]:
#         try:
#             employee_subquery = (
#                 self.db_session.query(
#                     workplan_employee_association.c.work_plan_id.label("work_plan_id"),
#                     func.array_agg(Employee.id).label("employee_ids"),
#                     func.array_agg(
#                         func.concat(Employee.first_name, " ", Employee.last_name)
#                     ).label("employee_names"),
#                 )
#                 .join(
#                     Employee, Employee.id == workplan_employee_association.c.employee_id
#                 )
#                 .group_by(workplan_employee_association.c.work_plan_id)
#                 .subquery()
#             )

#             query = (
#                 self.db_session.query(
#                     WorkPlan.id,
#                     WorkPlan.activity_title,
#                     WorkPlan.logistics_required,
#                     WorkPlanSource.id.label("source_id"),
#                     WorkPlanSource.name.label("source_name"),
#                     Site.id.label("site_id"),
#                     Site.name.label("site_name"),
#                     Location.id.label("location_id"),
#                     Location.name.label("location_name"),
#                     employee_subquery.c.employee_ids,
#                     employee_subquery.c.employee_names,
#                 )
#                 .join(WorkPlanSource)
#                 .outerjoin(
#                     employee_subquery, WorkPlan.id == employee_subquery.c.work_plan_id
#                 )
#                 .outerjoin(
#                     workplan_site_association,
#                     WorkPlan.id == workplan_site_association.c.work_plan_id,
#                 )
#                 .outerjoin(Site, Site.id == workplan_site_association.c.site_id)
#                 .outerjoin(
#                     workplan_location_association,
#                     WorkPlan.id == workplan_location_association.c.work_plan_id,
#                 )
#                 .outerjoin(
#                     Location, Location.id == workplan_location_association.c.location_id
#                 )
#                 .filter(WorkPlan.logistics_required == logistics_requirement)
#             )

#             if tenancy_id:
#                 query = query.filter(WorkPlan.tenancy_id == tenancy_id)

#             work_plans = query.distinct(WorkPlan.id).all()

#             results = []
#             workplan_count = len(work_plans)
#             for wp in work_plans:
#                 results.append(
#                     {
#                         "id": wp.id,
#                         "activity_title": wp.activity_title,
#                         "logistics_required": wp.logistics_required,
#                         "workplan_source": {"id": wp.source_id, "name": wp.source_name},
#                         "sites": (
#                             [{"id": wp.site_id, "name": wp.site_name}]
#                             if wp.site_id
#                             else []
#                         ),
#                         "locations": (
#                             [{"id": wp.location_id, "name": wp.location_name}]
#                             if wp.location_id
#                             else []
#                         ),
#                         "employees": (
#                             [
#                                 {"id": id, "name": name}
#                                 for id, name in zip(wp.employee_ids, wp.employee_names)
#                             ]
#                             if wp.employee_ids
#                             else []
#                         ),
#                     }
#                 )

#             logging_helper.log_info(
#                 f"Successfully fetched {workplan_count} workplans based on the logistics requirement: {logistics_requirement}"
#             )
#             return results
#         except Exception as e:
#             logging_helper.log_error(f"Error fetching workplans logistics: {str(e)}")
#             raise Exception(f"Error fetching work plans: {str(e)}")



from typing import List, Optional, Union
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import case, func, or_
from sqlalchemy.orm import Session, aliased
from sqlalchemy.orm import selectinload
from models.all_models import (
    SRT,
    Department,
    ScopeOfWork,
    ScopeOfWorkLineItem,
    Trip,
    Unit,
    User,
    WorkPlan,
    Site,
    Employee,
    Location,
    WorkPlanSource,
    workplan_employee_association,
    ThematicArea,
    workplan_site_association,
    workplan_location_association,
    ActionEnum,
)
from schemas.workplan_schemas import EmployeeModel, WorkPlanCreate, WorkPlanUpdate
from datetime import date, datetime, timedelta, timezone
from logging_helpers import logging_helper
from auth.email import (
    notify_initiator_about_work_plan,
    notify_work_plan_approval,
    notify_work_plan_creation,
    notify_work_plan_denial,
    notify_work_plan_reschedule,
    notify_work_plan_updates,
    generate_message_id,
)

class WorkPlanRepository:
    def __init__(self, db_session: Session):
        """
        Initialize the repository with the given database session.

        :param db_session: SQLAlchemy database session.
        """
        self.db_session = db_session

    def generate_work_plan_code(self, work_plan: WorkPlan) -> str:
        """
        Generate a unique work plan code.

        :param work_plan: The work plan instance.
        :return: The generated work plan code.
        """
        try:
            logging_helper.log_info(f"Workplan code successfully created for the Workplan id:{work_plan.id}")
            return f"WP-{work_plan.id}-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
        except Exception as e:
            logging_helper.log_error("Error Generating Workplan Code")
            raise HTTPException(status_code=500, detail=f"Error Generating Workplan Code: {e}")

    def generate_trip_code(self, trip: Trip) -> str:
        """
        Generate a unique trip code.

        :param trip: The trip instance.
        :return: The generated trip code.
        """
        try:
            logging_helper.log_info(f"Trip code successfully created for the Trip id:{trip.id}")
            return f"TP-{trip.id}-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
        except Exception as e:
            logging_helper.log_error("Error Generating Trip Code")
            raise HTTPException(status_code=500, detail=f"Error Generating Trip Code: {e}")

    def _find_existing_group(self, work_plan_data: WorkPlanCreate):
        """
        Find an existing group for the work plan based on the activity date and other criteria.

        :param work_plan_data: The work plan data.
        :return: The earliest work plan in the group or None.
        """
        try:
            start_of_week = work_plan_data.activity_date - timedelta(days=work_plan_data.activity_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)

            query = self.db_session.query(WorkPlan).filter(
                WorkPlan.workplan_source_id == work_plan_data.workplan_source_id,
                WorkPlan.activity_date.between(start_of_week, end_of_week),
            )

            query = query.filter(WorkPlan.employees.any(Employee.id.in_(work_plan_data.employee_ids)))

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
            logging_helper.log_info("Found a matching workplan Group for the Week")
            return earliest_work_plan
        except Exception as e:
            logging_helper.log_error("Error finding an existing Workplan Group")
            raise HTTPException(status_code=500, detail=f"Error finding an existing Workplan Group: {e}")

    def _valid_id(self, id_value, model):
        """
        Check if an ID value is valid for a given model.

        :param id_value: The ID value to check.
        :param model: The model class.
        :return: The ID value if valid, otherwise None.
        """
        return id_value if self.db_session.query(model).filter(model.id == id_value).count() > 0 else None

    def check_existing_work_plan(self, work_plan_data: WorkPlanCreate):
        """
        Check for an existing work plan that matches the given data.

        :param work_plan_data: The work plan data.
        :return: The existing work plan if found, otherwise None.
        """
        try:
            existing_work_plan = self.db_session.query(WorkPlan).filter(
                WorkPlan.activity_title == work_plan_data.activity_title,
                WorkPlan.workplan_source_id == work_plan_data.workplan_source_id,
                WorkPlan.activity_date == work_plan_data.activity_date,
            )

            existing_work_plan = existing_work_plan.filter(WorkPlan.employees.any(Employee.id.in_(work_plan_data.employee_ids)))
            return existing_work_plan.first()
        except Exception as e:
            logging_helper.log_error("Error Checking for a workplan that matches the one being created.")
            raise HTTPException(status_code=500, detail=f"Error Checking for a workplan that matches the one being created: {e}")

    def check_employee_schedule_conflict(self, employee_ids, activity_date):
        """
        Check for schedule conflicts for the given employees on a specific date.

        :param employee_ids: The list of employee IDs.
        :param activity_date: The activity date.
        :return: The existing work plan if a conflict is found, otherwise None.
        """
        existing_work_plan = self.db_session.query(WorkPlan).join(WorkPlan.employees).filter(
            Employee.id.in_(employee_ids), WorkPlan.activity_date == activity_date).first()
        return existing_work_plan


    def create_work_plan(self, background_tasks: BackgroundTasks, work_plan_data: WorkPlanCreate):
        STATUS_PENDING = "Pending"
        try:
            # Validate employee, site, and location IDs
            if not work_plan_data.employee_ids or all(id == 0 for id in work_plan_data.employee_ids):
                raise ValueError("At least one valid employee is required.")
            if not work_plan_data.site_ids or all(id == 0 for id in work_plan_data.site_ids):
                raise ValueError("At least one valid site is required.")
            if not work_plan_data.location_ids or all(id == 0 for id in work_plan_data.location_ids):
                raise ValueError("At least one valid location is required.")

            # Validate initiator
            initiator = self.db_session.query(User).filter(User.id == work_plan_data.initiating_user_id).first()
            if not initiator:
                logging_helper.log_error("Initiating user not provided by the user")
                raise HTTPException(status_code=404, detail="Initiating user not found")

            over_two_weeks_ago = date.today() - timedelta(days=14)
            employees_with_unsubmitted_reports = self.db_session.query(Employee).join(WorkPlan.employees).filter(
                Employee.id.in_(work_plan_data.employee_ids),
                WorkPlan.activity_date < over_two_weeks_ago,
                WorkPlan.is_report_submitted.is_(False),
                WorkPlan.is_approved.is_(True),
            ).distinct()

            if employees_with_unsubmitted_reports.count() > 0:
                employee_names = ", ".join(f"{emp.first_name} {emp.last_name}" for emp in employees_with_unsubmitted_reports)
                logging_helper.log_error(f"{employee_names}, who have not submitted their trip report(s) from over two weeks ago Trip embarked on, cannot be added to this workplan. Kindly drop them to Proceed")
                raise HTTPException(status_code=400, detail=f"{employee_names}, who have not submitted their trip report(s) from over two weeks ago Trip embarked on, cannot be added to this workplan. Kindly drop them to Proceed")

            initiator_name = f"{initiator.employee.first_name} {initiator.employee.last_name}" if initiator.employee else initiator.username
            initiator_email = initiator.email

            source_id_to_field = {
                1: ("initiating_unit_id", Unit),
                2: ("initiating_department_id", Department),
                3: ("initiating_srt_id", SRT),
                4: ("initiating_thematic_area_id", ThematicArea),
            }
            if work_plan_data.workplan_source_id not in source_id_to_field:
                raise ValueError("Invalid workplan source ID.")

            field_name, field_class = source_id_to_field[work_plan_data.workplan_source_id]
            initiating_id = getattr(work_plan_data, field_name)
            if initiating_id is None or initiating_id == 0:
                logging_helper.log_error(f"Required initiating ID for the selected workplan source is not provided or invalid.")
                raise ValueError(f"Required initiating ID for the selected workplan source is not provided or invalid.")
            if not work_plan_data.activity_lead_id:
                logging_helper.log_error("Activity lead was not provided by the user.")
                raise ValueError("Activity lead is required.")

            # Validate IDs
            initiating_unit_id = self._valid_id(work_plan_data.initiating_unit_id, Unit) if work_plan_data.initiating_unit_id else None
            initiating_department_id = self._valid_id(work_plan_data.initiating_department_id, Department) if work_plan_data.initiating_department_id else None
            initiating_srt_id = self._valid_id(work_plan_data.initiating_srt_id, SRT) if work_plan_data.initiating_srt_id else None
            initiating_thematic_area_id = self._valid_id(work_plan_data.initiating_thematic_area_id, ThematicArea) if work_plan_data.initiating_thematic_area_id else None
            if not self._valid_id(work_plan_data.workplan_source_id, WorkPlanSource):
                logging_helper.log_error("Work plan source not provided by the user")
                raise HTTPException(status_code=404, detail="Work plan source not found")
            if self.check_existing_work_plan(work_plan_data):
                logging_helper.log_error("Fail to create the Workplan as a similar workplan already exists.")
                raise HTTPException(status_code=400, detail="A similar work plan already exists.")
            schedule_conflict = self.check_employee_schedule_conflict(work_plan_data.employee_ids, work_plan_data.activity_date)
            if schedule_conflict:
                conflicting_employee_names = [employee.first_name for employee in schedule_conflict.employees if employee.id in work_plan_data.employee_ids]
                logging_helper.log_error(f"One or more employees are already assigned to another work plan on the chosen date. {', '.join(conflicting_employee_names)}")
                raise HTTPException(status_code=400, detail=f"One or more employees are already assigned to another work plan on the chosen date. {', '.join(conflicting_employee_names)}")

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
                vehicle_assigned=False,
                group_id=existing_group.id if existing_group else None,
            )
            self.db_session.add(new_work_plan)
            self.db_session.flush()

            if not existing_group:
                new_work_plan.group_id = new_work_plan.id
                self.db_session.commit()
            new_work_plan.sites.extend(self.db_session.query(Site).filter(Site.id.in_(work_plan_data.site_ids)).all())
            new_work_plan.employees.extend(self.db_session.query(Employee).filter(Employee.id.in_(work_plan_data.employee_ids)).all())
            new_work_plan.locations.extend(self.db_session.query(Location).filter(Location.id.in_(work_plan_data.location_ids)).all())

            # Add Scope of Work and Line Items
            scope_of_work_data = work_plan_data.scope_of_work
            new_scope_of_work = ScopeOfWork(
                description=scope_of_work_data.description,
                work_plan_id=new_work_plan.id
            )
            self.db_session.add(new_scope_of_work)
            self.db_session.flush()

            for line_item_data in scope_of_work_data.line_items:
                line_item_employees = self.db_session.query(Employee).filter(Employee.id.in_(line_item_data.employee_ids)).all()
                if not all(employee.id in work_plan_data.employee_ids for employee in line_item_employees):
                    raise HTTPException(status_code=400, detail="All employees in line items must be part of the employees associated with the work plan.")

                new_line_item = ScopeOfWorkLineItem(
                    description=line_item_data.description,
                    scope_of_work_id=new_scope_of_work.id,
                    employees=line_item_employees
                )
                self.db_session.add(new_line_item)

            self.db_session.commit()

            recipients = [(employee.first_name, employee.employee_email) for employee in new_work_plan.employees if employee.employee_email]
            if initiator_email not in [email for _, email in recipients]:
                recipients.append((initiator_name, initiator_email))

            message_id = generate_message_id()

            background_tasks.add_task(
                notify_work_plan_creation,
                recipients,
                new_work_plan.activity_title,
                initiator_name,
                STATUS_PENDING,
                message_id=message_id,
            )
            background_tasks.add_task(
                notify_initiator_about_work_plan,
                initiator_email,
                initiator_name,
                new_work_plan.activity_title,
                STATUS_PENDING,
                message_id=message_id,
            )
            logging_helper.log_info(f"The workplan with id {new_work_plan.id} has been created successfully")
            return new_work_plan

        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail=str(e))


    def send_emails_in_background(self, recipients, activity_title, initiator_name, status, message_id):
        """
        Send notification emails in the background.

        :param recipients: The list of recipients.
        :param activity_title: The activity title.
        :param initiator_name: The initiator's name.
        :param status: The status of the work plan.
        :param message_id: The message ID for tracking emails.
        """
        notify_work_plan_creation(recipients, activity_title, initiator_name, status, message_id=message_id)
        initiator_email = next((email for _, email in recipients if email), None)
        if initiator_email:
            notify_initiator_about_work_plan(initiator_email, initiator_name, activity_title, status, message_id=message_id)

    def update_work_plan(self, work_plan_id: int, update_data: WorkPlanUpdate, tenancy_id: Optional[int] = None):
        """
        Update an existing work plan.

        :param work_plan_id: The work plan ID.
        :param update_data: The update data.
        :param tenancy_id: The tenancy ID (optional).
        :return: The updated work plan.
        """
        try:
            if tenancy_id:
                work_plan = self.db_session.query(WorkPlan).filter(WorkPlan.id == work_plan_id, WorkPlan.tenancy_id == work_plan_id).first()
                if not work_plan:
                    logging_helper.log_error(f"Work plan ID {work_plan_id} not found or does not belong to your state")
                    raise HTTPException(status_code=404, detail=f"Work plan ID {work_plan_id} not found or does not belong to your state")
            else:
                work_plan = self.db_session.query(WorkPlan).filter(WorkPlan.id == work_plan_id).first()
                if not work_plan:
                    logging_helper.log_error(f"Work plan ID {work_plan_id} not found")
                    raise HTTPException(status_code=404, detail=f"Work plan ID {work_plan_id} not found")

            if update_data.workplan_source_id is None or update_data.workplan_source_id == 0:
                logging_helper.log_error("workplan_source_id was not provided.")
                raise ValueError("workplan_source_id cannot be zero.")

            regroup_needed = False
            changes_detected = {}

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

            field_class_map = {
                "initiating_unit_id": Unit,
                "initiating_department_id": Department,
                "initiating_srt_id": SRT,
                "initiating_thematic_area_id": ThematicArea,
            }

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
                        raise HTTPException(status_code=400, detail=f"Invalid {correct_field} provided.")
                    setattr(work_plan, correct_field, correct_id)
                regroup_needed = True
                for field, clazz in field_class_map.items():
                    if field != correct_field:
                        setattr(work_plan, field, None)

            if update_data.employee_ids:
                schedule_conflict = self.check_employee_schedule_conflict(update_data.employee_ids, update_data.activity_date)
                if schedule_conflict and schedule_conflict.id != work_plan_id:
                    conflicting_employee_names = [employee.first_name for employee in schedule_conflict.employees if employee.id in update_data.employee_ids]
                    raise HTTPException(status_code=400, detail=f"One or more employees are already assigned to another work plan on the chosen date. {', '.join(conflicting_employee_names)}")

            if update_data.employee_ids is not None:
                new_employees = self.db_session.query(Employee).filter(Employee.id.in_(update_data.employee_ids)).all()
                work_plan.employees = new_employees
                changes_detected["employees"] = [e.id for e in new_employees]

            if update_data.site_ids is not None:
                new_sites = self.db_session.query(Site).filter(Site.id.in_(update_data.site_ids)).all()
                work_plan.sites = new_sites
                changes_detected["sites"] = [s.id for s in new_sites]

            if update_data.location_ids is not None:
                new_locations = self.db_session.query(Location).filter(Location.id.in_(update_data.location_ids)).all()
                work_plan.locations = new_locations
                changes_detected["locations"] = [l.id for l in new_locations]

            if regroup_needed:
                new_group = self._find_existing_group(work_plan)
                work_plan.group_id = new_group.id if new_group else work_plan.id

            self.db_session.commit()

            if changes_detected:
                recipients = [(emp.first_name, emp.employee_email) for emp in work_plan.employees]
                notify_work_plan_updates(recipients, work_plan.activity_title, changes_detected)

            return work_plan

        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Failed to update work plan: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def fetch_pending_work_plans_for_week(self, tenancy_id: Optional[int] = None, employee_id: Optional[int] = None):
        """
        Fetch pending work plans for the current week.

        :param tenancy_id: The tenancy ID (optional).
        :param employee_id: The employee ID (optional).
        :return: A list of pending work plans for the current week.
        """
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday

        employee_alias = aliased(Employee)

        implementing_team = case(
            (WorkPlan.initiating_srt_id == SRT.id, SRT.name),
            (WorkPlan.initiating_unit_id == Unit.id, Unit.name),
            (WorkPlan.initiating_department_id == Department.id, Department.name),
            (WorkPlan.initiating_thematic_area_id == ThematicArea.id, ThematicArea.name),
            else_="Unknown",
        )

        employee_names = self.db_session.query(
            WorkPlan.id.label("work_plan_id"),
            func.string_agg(employee_alias.first_name + " " + employee_alias.last_name, ", ").label("employee_names"),
            func.count(employee_alias.id).label("employee_count"),
        ).join(
            workplan_employee_association,
            workplan_employee_association.c.work_plan_id == WorkPlan.id,
        ).join(
            employee_alias,
            employee_alias.id == workplan_employee_association.c.employee_id,
        ).group_by(WorkPlan.id).subquery()

        work_plans = self.db_session.query(
            WorkPlan.id,
            WorkPlan.activity_title,
            WorkPlan.activity_date,
            WorkPlan.status,
            Location.name.label("location_name"),
            WorkPlanSource.name.label("workplan_source_name"),
            implementing_team.label("implementing_team"),
            employee_names.c.employee_names,
            employee_names.c.employee_count,
            WorkPlan.tenancy_id,
        ).join(WorkPlan.locations).join(WorkPlan.workplan_source).outerjoin(SRT, WorkPlan.initiating_srt_id == SRT.id).outerjoin(Unit, WorkPlan.initiating_unit_id == Unit.id).outerjoin(Department, WorkPlan.initiating_department_id == Department.id).outerjoin(ThematicArea, WorkPlan.initiating_thematic_area_id == ThematicArea.id).outerjoin(employee_names, employee_names.c.work_plan_id == WorkPlan.id).filter(
            WorkPlan.status == "Pending",
            WorkPlan.is_active == True,
            WorkPlan.activity_date >= start_of_week,
            WorkPlan.activity_date <= end_of_week,
        )

        if tenancy_id:
            work_plans = work_plans.filter(WorkPlan.tenancy_id == tenancy_id)

        if employee_id:
            work_plans = work_plans.join(workplan_employee_association, workplan_employee_association.c.work_plan_id == WorkPlan.id)
            work_plans = work_plans.filter(workplan_employee_association.c.employee_id == employee_id)

        list_of_work_plans = work_plans.group_by(
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
        ).order_by(WorkPlan.group_id).all()

        return [
            {
                "workplan_id": wp.id,
                "activity_title": wp.activity_title,
                "activity_date": wp.activity_date.strftime("%Y-%m-%d"),
                "location_name": wp.location_name,
                "workplan_source_name": wp.workplan_source_name,
                "implementing_team": wp.implementing_team,
                "employee_names": [wp.employee_names],
                "no_of_staff": wp.employee_count,
                "tenancy_id": wp.tenancy_id,
            }
            for wp in list_of_work_plans
        ]

    def fetch_current_week_work_plans_with_status(self, start_of_week: date, end_of_week: date, vehicle_assigned: Optional[bool], tenancy_id: Optional[int] = None, employee_id: Optional[int] = None):
        """
        Fetch work plans for the current week with a specific status.

        :param start_of_week: The start date of the week.
        :param end_of_week: The end date of the week.
        :param vehicle_assigned: Whether the vehicle is assigned.
        :param tenancy_id: The tenancy ID (optional).
        :param employee_id: The employee ID (optional).
        :return: A list of work plans with the specified status.
        """
        try:
            employee_alias = aliased(Employee)

            implementing_team = case(
                (WorkPlan.initiating_srt_id == SRT.id, SRT.name),
                (WorkPlan.initiating_unit_id == Unit.id, Unit.name),
                (WorkPlan.initiating_department_id == Department.id, Department.name),
                (WorkPlan.initiating_thematic_area_id == ThematicArea.id, ThematicArea.name),
                else_="Unknown",
            )

            employee_details = self.db_session.query(
                workplan_employee_association.c.work_plan_id.label("work_plan_id"),
                func.array_agg(employee_alias.id).label("employee_ids"),
                func.string_agg(employee_alias.first_name + " " + employee_alias.last_name, ", ").label("employee_names"),
                func.count().label("employee_count"),
            ).join(
                employee_alias,
                employee_alias.id == workplan_employee_association.c.employee_id,
            ).group_by(workplan_employee_association.c.work_plan_id).subquery()

            work_plans_query = self.db_session.query(
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
            ).join(WorkPlan.locations).join(WorkPlan.workplan_source).outerjoin(SRT, WorkPlan.initiating_srt_id == SRT.id).outerjoin(Unit, WorkPlan.initiating_unit_id == Unit.id).outerjoin(Department, WorkPlan.initiating_department_id == Department.id).outerjoin(ThematicArea, WorkPlan.initiating_thematic_area_id == ThematicArea.id).outerjoin(employee_details, employee_details.c.work_plan_id == WorkPlan.id).filter(
                WorkPlan.is_active == True,
                WorkPlan.activity_date >= start_of_week,
                WorkPlan.activity_date <= end_of_week,
            )
            if vehicle_assigned:
                work_plans_query = work_plans_query.filter(WorkPlan.vehicle_assigned)
            if tenancy_id:
                work_plans_query = work_plans_query.filter(WorkPlan.tenancy_id == tenancy_id)
            if employee_id:
                work_plans_query = work_plans_query.filter(employee_details.c.employee_ids.any(employee_id))

            work_plans = work_plans_query.distinct(WorkPlan.id).all()

            return [
                {
                    "workplan_id": wp.id,
                    "workplan_code": wp.workplan_code,
                    "activity_title": wp.activity_title,
                    "activity_date": wp.activity_date.strftime("%Y-%m-%d"),
                    "status": wp.status,
                    "vehicle_assigned": wp.vehicle_assigned,
                    "location_name": wp.location_name,
                    "workplan_source_name": wp.workplan_source_name,
                    "implementing_team": wp.implementing_team,
                    "initiating_user_id": wp.initiating_user_id,
                    "employee_ids": wp.employee_ids,
                    "employee_names": [wp.employee_names],
                    "no_of_staff": wp.employee_count,
                    "tenancy_id": wp.tenancy_id,
                }
                for wp in work_plans
            ]

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    def approve_work_plan(self, background_tasks: BackgroundTasks, work_plan_id: int, approver_id: int, tenancy_id: Optional[int] = None):
        """
        Approve a work plan.

        :param background_tasks: The background tasks.
        :param work_plan_id: The work plan ID.
        :param approver_id: The approver's user ID.
        :param tenancy_id: The tenancy ID (optional).
        :return: A dictionary with feedback.
        """
        STATUS_APPROVED = "Approved"

        if approver_id is None:
            raise ValueError("Approver ID is required")

        db_work_plan = self.get_work_plan_by_id(work_plan_id=work_plan_id, tenancy_id=tenancy_id)
        if db_work_plan is None:
            raise HTTPException(status_code=404, detail="Work plan not found")

        if db_work_plan.is_approved:
            raise HTTPException(status_code=400, detail="Work plan already approved")

        if db_work_plan.is_rescheduled:
            db_work_plan.is_rescheduled = False
            db_work_plan.date_rescheduled = None

        if db_work_plan.is_denied:
            db_work_plan.is_denied = False
            db_work_plan.date_denied = None

        if db_work_plan.reason is not None:
            db_work_plan.reason = None

        work_plan_code = self.generate_work_plan_code(db_work_plan)
        if not db_work_plan.workplan_code:
            db_work_plan.workplan_code = work_plan_code

        db_work_plan.approved_by = approver_id
        db_work_plan.date_approved = datetime.now(timezone.utc)
        db_work_plan.status = STATUS_APPROVED
        db_work_plan.is_approved = True
        work_plan_code = self.generate_work_plan_code(db_work_plan)
        db_work_plan.workplan_code = work_plan_code or db_work_plan.workplan_code

        try:
            self.db_session.commit()
            recipients = [(emp.first_name, emp.employee_email) for emp in db_work_plan.employees if emp.employee_email]

            message_id = generate_message_id()

            background_tasks.add_task(
                notify_work_plan_approval,
                recipients,
                db_work_plan.activity_title,
                db_work_plan.workplan_code,
                db_work_plan.activity_date,
                db_work_plan.activity_start_time,
                STATUS_APPROVED,
                message_id=message_id,
            )
            return {"Feedback": f"The Workplan with the ID {work_plan_id} has been Approved Successfully !!!"}
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Failed to approve work plan: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to approve work plan due to an error: {e}")

    def reschedule_work_plan(self, background_tasks: BackgroundTasks, work_plan_id: int, reason: str, new_date: datetime, tenancy_id: Optional[int] = None) -> Union[WorkPlan, dict]:
        """
        Reschedule a work plan.

        :param background_tasks: The background tasks.
        :param work_plan_id: The work plan ID.
        :param reason: The reason for rescheduling.
        :param new_date: The new activity date.
        :param tenancy_id: The tenancy ID (optional).
        :return: The rescheduled work plan or a feedback dictionary.
        """
        STATUS_RESCHEDULED = "Re-Scheduled"

        db_work_plan = self.get_work_plan_by_id(work_plan_id=work_plan_id, tenancy_id=tenancy_id)

        if db_work_plan:
            if not db_work_plan.is_rescheduled:
                db_work_plan.is_rescheduled = True
                db_work_plan.reason = reason
                db_work_plan.date_rescheduled = datetime.utcnow()
                db_work_plan.activity_date = new_date
                db_work_plan.status = STATUS_RESCHEDULED

                if db_work_plan.is_approved:
                    db_work_plan.is_approved = False
                    db_work_plan.date_approved = None
                    db_work_plan.approved_by = None
                    db_work_plan.workplan_code = None

                if db_work_plan.is_denied:
                    db_work_plan.is_denied = False
                    db_work_plan.date_denied = None

                try:
                    self.db_session.commit()
                    recipients = [(emp.first_name, emp.employee_email) for emp in db_work_plan.employees if emp.employee_email]

                    initiator_email = db_work_plan.initiating_user.email
                    initiator_name = db_work_plan.initiating_user.employee.first_name

                    recipients.append((initiator_name, initiator_email))

                    message_id = generate_message_id()

                    background_tasks.add_task(
                        notify_work_plan_reschedule,
                        recipients,
                        db_work_plan.activity_title,
                        db_work_plan.workplan_code,
                        reason,
                        new_date.strftime("%Y-%m-%d"),
                        message_id=message_id,
                    )

                    return {"Feedback": f"The Workplan with the ID {work_plan_id} has been rescheduled Successfully on {new_date.strftime('%Y-%m-%d')} !!!"}

                except Exception as e:
                    self.db_session.rollback()
                    logging_helper.log_error(f"Failed to reschedule work plan: {e}")
                    raise HTTPException(status_code=500, detail=f"Failed to reschedule work plan due to an error: {e}")
            else:
                raise HTTPException(status_code=400, detail="Work plan has already been rescheduled")
        else:
            raise HTTPException(status_code=404, detail="Work plan not found")

    def deny_work_plan(self, background_tasks: BackgroundTasks, work_plan_id: int, reason: str, tenancy_id: Optional[int] = None) -> WorkPlan:
        """
        Deny a work plan.

        :param background_tasks: The background tasks.
        :param work_plan_id: The work plan ID.
        :param reason: The reason for denial.
        :param tenancy_id: The tenancy ID (optional).
        :return: The denied work plan.
        """
        STATUS_DENIED = "Denied"
        db_work_plan = self.get_work_plan_by_id(work_plan_id=work_plan_id, tenancy_id=tenancy_id)
        if db_work_plan is None:
            raise HTTPException(status_code=404, detail="Work plan not found")

        if db_work_plan.is_denied:
            raise HTTPException(status_code=400, detail="Work plan already denied")

        if db_work_plan.is_approved:
            db_work_plan.is_approved = False
            db_work_plan.date_approved = None
            db_work_plan.approved_by = None

        if db_work_plan.is_rescheduled:
            db_work_plan.is_rescheduled = False
            db_work_plan.date_rescheduled = None

        db_work_plan.is_denied = True
        db_work_plan.reason = reason
        db_work_plan.date_denied = datetime.utcnow()
        db_work_plan.status = STATUS_DENIED

        try:
            self.db_session.commit()

            recipients = [(employee.first_name, employee.employee_email) for employee in db_work_plan.employees if employee.employee_email]

            message_id = generate_message_id()

            background_tasks.add_task(
                notify_work_plan_denial,
                recipients,
                db_work_plan.activity_title,
                db_work_plan.workplan_code,
                reason,
                STATUS_DENIED,
                message_id=message_id,
            )

            return {"Feedback": f"The Workplan with the ID {work_plan_id} has been Denied"}
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Failed to deny work plan: {e}")
            raise HTTPException(status_code=500, detail="Failed to deny work plan")

    def update_work_plan_if_pending(self, work_plan_id: int, updates: dict, tenancy_id: Optional[int] = None, user_id: Optional[int] = None):
        """
        Update a pending work plan.

        :param work_plan_id: The work plan ID.
        :param updates: The updates to apply.
        :param tenancy_id: The tenancy ID (optional).
        :param user_id: The user's ID (optional).
        :return: The updated work plan.
        """
        try:
            if tenancy_id and user_id:
                work_plan = self.db_session.query(WorkPlan).filter(WorkPlan.id == work_plan_id, WorkPlan.initiating_user_id == user_id).first()
                if work_plan is None:
                    raise HTTPException(status_code=404, detail="Work plan not found or was not created by you.")

            if tenancy_id:
                work_plan = self.get_work_plan_by_id(work_plan_id, tenancy_id=tenancy_id)
                if work_plan is None:
                    raise HTTPException(status_code=404, detail="Work plan not found or does not belong to the state.")

            if work_plan.status != "Pending":
                raise HTTPException(status_code=400, detail="Work plan is not in a pending state and cannot be updated.")

            for key, value in updates.items():
                if hasattr(work_plan, key):
                    setattr(work_plan, key, value)

            self.db_session.commit()
            return work_plan
        except Exception as e:
            self.db_session.rollback()
            raise Exception(f"An error occurred while updating the work plan: {str(e)}")

    def get_work_plan_by_id(self, work_plan_id: int, tenancy_id: Optional[int] = None, employee_id: Optional[int] = None):
        """
        Get a work plan by ID.

        :param work_plan_id: The work plan ID.
        :param tenancy_id: The tenancy ID (optional).
        :param employee_id: The employee ID (optional).
        :return: The work plan.
        """
        try:
            work_plan = self.db_session.query(WorkPlan).filter(WorkPlan.id == work_plan_id)

            if tenancy_id:
                work_plan = work_plan.filter(WorkPlan.tenancy_id == tenancy_id)

            if employee_id:
                work_plan = work_plan.join(workplan_employee_association, workplan_employee_association.c.work_plan_id == WorkPlan.id)
                work_plan = work_plan.filter(workplan_employee_association.c.employee_id == employee_id)

            work_plan = work_plan.first()

            if not work_plan:
                raise HTTPException(status_code=404, detail="Work plan not found")
            return work_plan
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Database error occurred: {e}")
            raise HTTPException(status_code=500, detail="Database error occurred while fetching the work plan")

    def fetch_employees_by_work_plan(self, workplan_code=None, initiator_name=None, activity_date=None, tenancy_id: Optional[int] = None):
        """
        Fetch employees by work plan details.

        :param workplan_code: The work plan code.
        :param initiator_name: The initiator's name.
        :param activity_date: The activity date.
        :param tenancy_id: The tenancy ID (optional).
        :return: A list of employees.
        """
        try:
            query = self.db_session.query(Employee)

            if workplan_code:
                query = query.join(Employee.work_plans).filter(WorkPlan.workplan_code == workplan_code)

            if initiator_name:
                name_parts = initiator_name.split()
                if len(name_parts) != 2:
                    raise ValueError("Initiator name must include both first and last names separated by a space.")
                first_name, last_name = name_parts
                query = query.join(Employee.work_plans).join(User, WorkPlan.initiating_user_id == User.id).filter(
                    User.employee.has(first_name=first_name, last_name=last_name)
                )

            if activity_date:
                query = query.join(Employee.work_plans).filter(WorkPlan.activity_date == activity_date)

            if tenancy_id:
                query = query.filter(WorkPlan.tenancy_id == tenancy_id)

            employees = query.filter(Employee.employee_email != None).all()
            return [EmployeeModel.from_orm(emp) for emp in employees]
        except ValueError as ve:
            logging_helper.log_error(f"Input error: {ve}")
            raise Exception(f"Input error: {ve}")
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Database error occurred: {e}")
            raise Exception(f"Failed to fetch employees due to a database error: {e}")
        except Exception as e:
            logging_helper.log_error(f"An error occurred: {e}")
            raise Exception(f"Failed to fetch employees due to an error: {e}")

    def get_active_work_plans(self, tenancy_id: Optional[int] = None):
        """
        Get active work plans.

        :param tenancy_id: The tenancy ID (optional).
        :return: A list of active work plans.
        """
        try:
            active_work_plans = self.db_session.query(WorkPlan).filter(WorkPlan.is_active == True)

            if tenancy_id:
                active_work_plans = active_work_plans.filter(WorkPlan.tenancy_id == tenancy_id)

            return active_work_plans
            logging_helper.log_info(f"Weekly Active Workplans for the Tenancy with ID: {tenancy_id} was Successfully Fetched")
        except Exception as e:
            logging_helper.log_error(f"Failed to fetch active work plans: {e}")
            raise Exception(f"Database error while fetching active work plans: {e}")

    def list_employees_without_work_plan_on_date(self, activity_date: date, tenancy_id: Optional[int] = None):
        """
        List employees without a work plan on a specific date.

        :param activity_date: The activity date.
        :param tenancy_id: The tenancy ID (optional).
        :return: A list of employees without a work plan on the specified date.
        """
        try:
            subquery = self.db_session.query(workplan_employee_association.c.employee_id).join(WorkPlan, workplan_employee_association.c.work_plan_id == WorkPlan.id).filter(WorkPlan.activity_date == activity_date).subquery()

            employees = self.db_session.query(
                Employee.id.label("employee_id"),
                Employee.staff_code,
                Employee.last_name,
                Employee.first_name,
                Employee.phone_number,
            ).outerjoin(subquery, subquery.c.employee_id == Employee.id).filter(subquery.c.employee_id == None)

            if tenancy_id:
                employees = employees.filter(Employee.tenancy_id == tenancy_id)

            employees = employees.all()
            employees_count = len(employees)
            logging_helper.log_info(f"A total of {employees_count} Employees were not associated with a Workplan on {activity_date}")
            return [
                {
                    "employee_id": emp.employee_id,
                    "staff_code": emp.staff_code,
                    "last_name": emp.last_name,
                    "first_name": emp.first_name,
                    "phone_number": emp.phone_number,
                }
                for emp in employees
            ]
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Database error occurred: {e}")
            return []
        except Exception as e:
            logging_helper.log_error(f"An unexpected error occurred: {e}")
            return []

    def list_archived_work_plans(self, skip: int, limit: int):
        """
        List archived work plans.

        :param skip: The number of work plans to skip.
        :param limit: The number of work plans to return.
        :return: A list of archived work plans.
        """
        try:
            return self.db_session.query(WorkPlan).filter(WorkPlan.archived == True).offset(skip).limit(limit).all()
        except Exception as e:
            logging_helper.log_error(f"Error Listing the Archived Workplans: {str(e)}")

    def list_work_plans_by_status(self, is_approved: bool, skip: int, limit: int):
        """
        List work plans by approval status.

        :param is_approved: The approval status.
        :param skip: The number of work plans to skip.
        :param limit: The number of work plans to return.
        :return: A list of work plans with the specified approval status.
        """
        return self.db_session.query(WorkPlan).filter(WorkPlan.is_approved == is_approved).offset(skip).limit(limit).all()

    def fetch_approved_weekly_work_plans(self, tenancy_id: Optional[int] = None):
        """
        Fetch approved work plans for the current week.

        :param tenancy_id: The tenancy ID (optional).
        :return: A list of approved work plans for the current week.
        """
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday

        employee_alias = aliased(Employee)

        implementing_team = case(
            (WorkPlan.initiating_srt_id == SRT.id, SRT.name),
            (WorkPlan.initiating_unit_id == Unit.id, Unit.name),
            (WorkPlan.initiating_department_id == Department.id, Department.name),
            (WorkPlan.initiating_thematic_area_id == ThematicArea.id, ThematicArea.name),
            else_="Unknown",
        ).label("implementing_team")

        employee_details = self.db_session.query(
            workplan_employee_association.c.work_plan_id.label("work_plan_id"),
            func.array_agg(employee_alias.id).label("employee_ids"),
            func.string_agg(employee_alias.first_name + " " + employee_alias.last_name, ", ").label("employee_names"),
            func.count().label("employee_count"),
        ).join(
            employee_alias,
            employee_alias.id == workplan_employee_association.c.employee_id,
        ).group_by(workplan_employee_association.c.work_plan_id).subquery()

        work_plans = self.db_session.query(WorkPlan).options(selectinload(WorkPlan.employees), selectinload(WorkPlan.locations)).join(WorkPlanSource, isouter=True).outerjoin(SRT).outerjoin(Unit).outerjoin(Department).outerjoin(ThematicArea).filter(
            WorkPlan.status == "Approved",
            WorkPlan.activity_date >= start_of_week,
            WorkPlan.activity_date <= end_of_week,
        )

        if tenancy_id:
            work_plans = work_plans.filter(WorkPlan.tenancy_id == tenancy_id)

        work_plans = work_plans.all()

        return [
            {
                "id": wp.id,
                "workplan_code": wp.workplan_code,
                "activity_title": wp.activity_title,
                "specific_task": wp.specific_task,
                "logistics_required": wp.logistics_required,
                "activity_date": wp.activity_date.isoformat(),
                "activity_time": (wp.activity_start_time.isoformat() if wp.activity_start_time else None),
                "initiating_user_id": wp.initiating_user_id,
                "status": wp.status,
                "workplan_source_name": wp.workplan_source.name,
                "implementing_team": getattr(wp, "implementing_team", None),
                "employee_ids": [emp.id for emp in wp.employees],
                "employee_names": [f"{emp.first_name} {emp.last_name}" for emp in wp.employees],
                "employee_count": len(wp.employees),
                "locations": [loc.name for loc in wp.locations],
            }
            for wp in work_plans
        ]

    def fetch_approved_work_plan_by_code_or_id(self, identifier: str, tenancy_id: Optional[int] = None):
        """
        Fetch an approved work plan by code or ID.

        :param identifier: The work plan code or ID.
        :param tenancy_id: The tenancy ID (optional).
        :return: The approved work plan.
        """
        try:
            employee_alias = aliased(Employee)

            employee_names = self.db_session.query(
                WorkPlan.id.label("work_plan_id"),
                func.string_agg(employee_alias.first_name + " " + employee_alias.last_name, ", ").label("employee_names"),
                func.count(employee_alias.id).label("employee_count"),
            ).join(
                workplan_employee_association,
                workplan_employee_association.c.work_plan_id == WorkPlan.id,
            ).join(
                employee_alias,
                employee_alias.id == workplan_employee_association.c.employee_id,
            ).group_by(WorkPlan.id).subquery()

            if identifier.isdigit():
                work_plan_query = self.db_session.query(WorkPlan).filter(WorkPlan.id == int(identifier), WorkPlan.status == "Approved")
            else:
                work_plan_query = self.db_session.query(WorkPlan).filter(WorkPlan.workplan_code == identifier, WorkPlan.status == "Approved")

            if tenancy_id:
                work_plan_query = work_plan_query.filter(WorkPlan.tenancy_id == tenancy_id)

            work_plan = work_plan_query.outerjoin(employee_names, employee_names.c.work_plan_id == WorkPlan.id).add_columns(employee_names.c.employee_names, employee_names.c.employee_count).first()

            if work_plan:
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
                    "employee_names": (employee_names.split(", ") if employee_names else []),
                    "employee_count": employee_count,
                }
            return None
        except Exception as e:
            logging_helper.log_error(f"Error fetching approved workplan by identifier : {identifier}")
            raise (f"Error fetching approved workplan by identifier : {identifier}")

    def fetch_approved_work_plan_by_entity(self, entity_type: str, entity_name: str, tenancy_id: Optional[int] = None):
        """
        Fetch an approved work plan by entity type and name.

        :param entity_type: The entity type (unit, srt, department, thematicarea).
        :param entity_name: The entity name.
        :param tenancy_id: The tenancy ID (optional).
        :return: The approved work plan.
        """
        employee_alias = aliased(Employee)

        employee_names = self.db_session.query(
            WorkPlan.id.label("work_plan_id"),
            func.string_agg(employee_alias.first_name + " " + employee_alias.last_name, ", ").label("employee_names"),
            func.count(employee_alias.id).label("employee_count"),
        ).join(
            workplan_employee_association,
            workplan_employee_association.c.work_plan_id == WorkPlan.id,
        ).join(
            employee_alias,
            employee_alias.id == workplan_employee_association.c.employee_id,
        ).group_by(WorkPlan.id).subquery()

        base_query = self.db_session.query(WorkPlan).outerjoin(employee_names, employee_names.c.work_plan_id == WorkPlan.id).add_columns(employee_names.c.employee_names, employee_names.c.employee_count).filter(WorkPlan.status == "Approved")

        if entity_type.lower() == "unit":
            base_query = base_query.join(Unit).filter(Unit.name == entity_name)
        elif entity_type.lower() == "srt":
            base_query = base_query.join(SRT).filter(SRT.name == entity_name)
        elif entity_type.lower() == "department":
            base_query = base_query.join(Department).filter(Department.name == entity_name)
        elif entity_type.lower() == "thematicarea":
            base_query = base_query.join(ThematicArea).filter(ThematicArea.name == entity_name)
        else:
            raise ValueError("Invalid entity type provided. Must be one of: unit, srt, department, thematicarea.")

        if tenancy_id:
            base_query = base_query.filter(WorkPlan.tenancy_id == tenancy_id)

        work_plan = base_query.first()

        if work_plan:
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

    def fetch_monthly_work_plan_summary(self, year: int, month: int, tenancy_id: Optional[int] = None):
        """
        Fetch a summary of work plans for a specific month.

        :param year: The year.
        :param month: The month.
        :param tenancy_id: The tenancy ID (optional).
        :return: A summary of work plans for the specified month.
        """
        from sqlalchemy import extract

        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12")
        if year < 1900 or year > 2100:
            raise ValueError("Year must be a reasonable value")

        start_date = date(year, month, 1)
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        work_plans = self.db_session.query(
            WorkPlan.status,
            func.count(WorkPlan.id).label("count"),
            func.string_agg(Employee.first_name + " " + Employee.last_name, ", ").label("employee_names"),
        ).join(
            workplan_employee_association,
            workplan_employee_association.c.work_plan_id == WorkPlan.id,
        ).join(Employee, Employee.id == workplan_employee_association.c.employee_id).filter(WorkPlan.activity_date.between(start_date, end_date))

        work_plans = work_plans.group_by(WorkPlan.status)

        if tenancy_id:
            work_plans = work_plans.filter(WorkPlan.tenancy_id == tenancy_id)

        work_plans = work_plans.all()

        summary = {"month": month, "year": year, "details": []}
        for status, count, employee_names in work_plans:
            summary["details"].append(
                {
                    "status": status,
                    "employee_count": count,
                    "employees": (list(set(employee_names.split(", "))) if employee_names else []),
                }
            )
        logging_helper.log_error("Successfully fetched the monthly workplan summary")
        return summary

    def fetch_workplans_by_date_range(self, start_date: date, end_date: date, status: Optional[str] = None, tenancy_id: Optional[int] = None) -> List[dict]:
        """
        Fetch work plans by date range.

        :param start_date: The start date.
        :param end_date: The end date.
        :param status: The status of the work plan (optional).
        :param tenancy_id: The tenancy ID (optional).
        :return: A list of work plans within the specified date range.
        """
        employee_alias = aliased(Employee)

        employee_names = self.db_session.query(
            WorkPlan.id.label("work_plan_id"),
            func.string_agg(employee_alias.first_name + " " + employee_alias.last_name, ", ").label("employee_names"),
            func.count(employee_alias.id).label("employee_count"),
        ).join(
            workplan_employee_association,
            workplan_employee_association.c.work_plan_id == WorkPlan.id,
        ).join(
            employee_alias,
            employee_alias.id == workplan_employee_association.c.employee_id,
        ).group_by(WorkPlan.id).subquery()

        query = self.db_session.query(
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
        ).outerjoin(employee_names, employee_names.c.work_plan_id == WorkPlan.id).join(WorkPlan.initiating_user).join(WorkPlan.workplan_source).filter(
            WorkPlan.activity_date >= start_date, WorkPlan.activity_date <= end_date
        )

        if tenancy_id:
            query = query.filter(WorkPlan.tenancy_id == tenancy_id)

        if status:
            query = query.filter(WorkPlan.status == status)

        try:
            work_plans = query.order_by(WorkPlan.activity_date).all()
            work_plan_count = len(work_plans)
            logging_helper.log_info(f"Successfully fetched {work_plan_count} workplan(s) based on the date ranges: {start_date} and {end_date} with the status: {status}")
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
                    "employee_names": (wp.employee_names.split(", ") if wp.employee_names else []),
                    "employee_count": wp.employee_count,
                }
                for wp in work_plans
            ]
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error retrieving work plans based on the date range {start_date} and {end_date}: {str(e)}")
            raise Exception(f"Error retrieving work plans: {str(e)}")

    def get_work_plans_by_logistics(self, logistics_requirement: str, tenancy_id: Optional[int] = None) -> List[dict]:
        """
        Get work plans by logistics requirement.

        :param logistics_requirement: The logistics requirement.
        :param tenancy_id: The tenancy ID (optional).
        :return: A list of work plans with the specified logistics requirement.
        """
        try:
            employee_subquery = self.db_session.query(
                workplan_employee_association.c.work_plan_id.label("work_plan_id"),
                func.array_agg(Employee.id).label("employee_ids"),
                func.array_agg(func.concat(Employee.first_name, " ", Employee.last_name)).label("employee_names"),
            ).join(Employee, Employee.id == workplan_employee_association.c.employee_id).group_by(workplan_employee_association.c.work_plan_id).subquery()

            query = self.db_session.query(
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
            ).join(WorkPlanSource).outerjoin(employee_subquery, WorkPlan.id == employee_subquery.c.work_plan_id).outerjoin(workplan_site_association, WorkPlan.id == workplan_site_association.c.work_plan_id).outerjoin(Site, Site.id == workplan_site_association.c.site_id).outerjoin(workplan_location_association, WorkPlan.id == workplan_location_association.c.work_plan_id).outerjoin(Location, Location.id == workplan_location_association.c.location_id).filter(WorkPlan.logistics_required == logistics_requirement)

            if tenancy_id:
                query = query.filter(WorkPlan.tenancy_id == tenancy_id)

            work_plans = query.distinct(WorkPlan.id).all()

            results = []
            workplan_count = len(work_plans)
            for wp in work_plans:
                results.append(
                    {
                        "id": wp.id,
                        "activity_title": wp.activity_title,
                        "logistics_required": wp.logistics_required,
                        "workplan_source": {"id": wp.source_id, "name": wp.source_name},
                        "sites": ( [{"id": wp.site_id, "name": wp.site_name}] if wp.site_id else [] ),
                        "locations": ( [{"id": wp.location_id, "name": wp.location_name}] if wp.location_id else [] ),
                        "employees": ( [{"id": id, "name": name} for id, name in zip(wp.employee_ids, wp.employee_names)] if wp.employee_ids else [] ),
                    }
                )

            logging_helper.log_info(f"Successfully fetched {workplan_count} workplans based on the logistics requirement: {logistics_requirement}")
            return results
        except Exception as e:
            logging_helper.log_error(f"Error fetching workplans logistics: {str(e)}")
            raise Exception(f"Error fetching work plans: {str(e)}")

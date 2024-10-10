# from fastapi import HTTPException, status, BackgroundTasks
# from sqlalchemy.orm import Session, aliased
# from schemas.issue_schemas import IssueCreate, IssueUpdate, IssueLogClosure
# from models.all_models import IssueLog, Tenancy, IssueLogSource, IssueStatus, focal_person_issue_association, Employee, SRT, Unit, Department
# from sqlalchemy.exc import SQLAlchemyError
# from typing import Optional, List
# from auth.email import notify_employees_about_issue_logs, notify_employees_about_update_on_issue_logs, notify_employees_about_completed_issue_logs, notify_initiator_about_issue_logs, notify_initiator_about_completed_issue_logs
# from sqlalchemy import func, case
# from logging_helpers import logging_helper
# PENDING=1
# COMPLETED=2

# class IssueRepository:
#     def __init__(self, db_session:Session):
#         self.db_session = db_session

#     def create_issue_log(self, background_tasks:BackgroundTasks, issue_create_data:IssueCreate):
#         "Creates an issue using data from the Issue Data"

#         # Check for duplicate entry
#         issue_exist = self.db_session.query(IssueLog).filter(IssueLog.tenancy_id==issue_create_data.tenancy_id, IssueLog.date_reported==issue_create_data.date_reported, IssueLog.issue_description==issue_create_data.issue_description).first()
#         if issue_exist:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The issue your raising '{issue_create_data.issue_description}' has already been created")
        
#         # Check for description
#         if not issue_create_data.issue_description:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No issue description was provided")
        
#         # Fetch the name of the issue log source
#         issue_source_name = self.db_session.query(IssueLogSource).filter(IssueLogSource.id==issue_create_data.source_id).one_or_none()
#         if not issue_source_name:
#             raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue Log Source with Source ID {issue_create_data.source_id} was not found")
        
#         # Fetch the name of the Tenancy
#         issue_tenancy_name = self.db_session.query(Tenancy).filter(Tenancy.id==issue_create_data.tenancy_id).one_or_none()
#         if not issue_tenancy_name:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tenancy with Tenancy ID {issue_create_data.tenancy_id} was not found")
        
#         # Fetch the name of the 

#         issue = IssueLog(
#             issue=f"Issue identified from {issue_source_name.name} for {issue_tenancy_name.name} State",
#             issue_description=issue_create_data.issue_description,
#             key_recommendation=issue_create_data.key_recommendation,
#             date_reported=issue_create_data.date_reported,
#             time_line_date=issue_create_data.time_line_date,
#             reported_by_id=issue_create_data.reported_by_id,
#             thematic_area_id=issue_create_data.thematic_area_id,
#             site_id=issue_create_data.site_id,
#             source_id=issue_create_data.source_id,
#             status_id=PENDING,
#             meeting_id=issue_create_data.meeting_id,
#             srt_id=issue_create_data.srt_id,
#             unit_id=issue_create_data.unit_id,
#             department_id=issue_create_data.department_id,
#             tenancy_id=issue_create_data.tenancy_id
#         )
#         try:
#             self.db_session.add(issue)
#             self.db_session.flush()

#             issue.employees.extend(
#                 self.db_session.query(Employee)
#                 .filter(Employee.id.in_(issue_create_data.focal_persons))
#                 .all()
#             )
#             self.db_session.commit()
#             issue_ouput = {
#                 "issue_id":issue.id,
#                 "issue":issue.issue,
#                 "issue_description":issue.issue_description,
#                 "key_recommendation":issue.key_recommendation,
#                 "time_line_date":issue.time_line_date,
#                 "focal_person":issue.employees
#             }

#             issue_initiator = self.db_session.query(Employee).filter(Employee.id==issue_create_data.reported_by_id).first()
#             issue_initiator_name = f"{issue_initiator.first_name} {issue_initiator.last_name}"

#             recipients = [(employee.first_name, employee.employee_email)
#                 for employee in issue.employees
#                 if employee.employee_email]
            
#             focal_persons_names_data = [f'{employee.first_name} {employee.last_name}'
#                 for employee in issue.employees
#                 if employee.employee_email]
            
#             focal_persons_names = ', '.join(focal_persons_names_data[:-1]) + ' and ' + focal_persons_names_data[-1]
            
#             # Date Formatting
#             if issue_create_data.time_line_date:
#                 time_line_date = issue_create_data.time_line_date
#                 time_line_date = f"{self.get_day_with_suffix(time_line_date.day)} of {time_line_date.strftime('%B')} {time_line_date.year}"
            
#             # Prepare mail to send to the initiator for the issues    
#             background_tasks.add_task(notify_initiator_about_issue_logs, focal_persons_names, issue_initiator.first_name, issue_initiator.employee_email, issue.issue, issue_create_data.issue_description, issue.key_recommendation, time_line_date)

#             # Prepare mail to send to the resposible persons for the issues    
#             background_tasks.add_task(notify_employees_about_issue_logs, recipients, issue_initiator_name, issue.issue, issue_create_data.issue_description, issue.key_recommendation, time_line_date)

#             logging_helper.log_info(f"IssueLog {issue.issue_description} created successfully")
#             return issue_ouput
            
#         except SQLAlchemyError as err:
#             self.db_session.rollback()
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured while creating issuse {str(err)}")



#     def update_pending_issue_log(self, background_tasks:BackgroundTasks, issue_log_id:int, issue_update_data:IssueUpdate, tenancy_id:Optional[int]=None, reported_by_id:Optional[int]=None) -> IssueUpdate:
#         """
#         To Update an issue log that has not been completed
#         """

#         # Fetch Issue Log using the ID
#         issue_log = self.db_session.query(IssueLog).filter(IssueLog.id==issue_log_id)

#         # Filter for Tenancy if True
#         if tenancy_id:
#             issue_log = issue_log.filter(IssueLog.tenancy_id==tenancy_id)

#         # Filter for reported person
#         if reported_by_id:
#             issue_log = issue_log.filter(IssueLog.reported_by_id==reported_by_id)

#         # Retrieve first record if found
#         issue_log = issue_log.one_or_none()
#         if not issue_log:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue Log with ID {issue_log_id} was not found")
        
#         # Check if Issue Log has been completed
#         if issue_log.close_date is not None or issue_log.status_id!=1:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Issue Log with ID {issue_log_id} has already been completed by the focal person(s)")

#         # Fetch the name of the issue log source
#         issue_source_name = self.db_session.query(IssueLogSource).filter(IssueLogSource.id==issue_update_data.source_id).one_or_none()
#         if not issue_source_name:
#             raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue Log Source with Source ID {issue_update_data.source_id} was not found")
        
#         # Fetch the name of the Tenancy
#         issue_tenancy_name = self.db_session.query(Tenancy).filter(Tenancy.id==issue_log.tenancy_id).one_or_none()
#         if not issue_tenancy_name:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tenancy with Tenancy ID {issue_log.tenancy_id} was not found")
        
#         # Structure the Issue Update data to forma dictionary
#         update_issue_data = issue_update_data.model_dump(exclude_unset=True)
        
#         # Append issue_source_name to the issue_update_data dictionary
#         update_issue_data["issue"] = f"Issue identified in {issue_source_name.name} for {issue_tenancy_name.name} State",

#         for key, value in update_issue_data.items():
#             setattr(issue_log, key, value)

#         try:
#             # Commit changes to the database
#             self.db_session.flush()
#             self.db_session.refresh(issue_log)

#             issue_initiator = self.db_session.query(Employee).filter(Employee.id==issue_log.reported_by_id).first()
#             issue_initiator_name = f"{issue_initiator.first_name} {issue_initiator.last_name}"

#             recipients = [(employee.first_name, employee.employee_email)
#                 for employee in issue_log.employees
#                 if employee.employee_email]

#             # Date Formatting
#             if issue_update_data.time_line_date:
#                 time_line_date = issue_update_data.time_line_date
#                 time_line_date = f"{self.get_day_with_suffix(time_line_date.day)} of {time_line_date.strftime('%B')} {time_line_date.year}"

#             # Send Notification for update of Issue Log
#             background_tasks.add_task(notify_employees_about_update_on_issue_logs, recipients, issue_initiator_name, issue_log.issue, issue_update_data.issue_description, issue_update_data.key_recommendation, time_line_date)

#             logging_helper.log_info(f"IssueLog with ID {issue_log_id} Updated successfully")
#             return issue_log
        
#         except SQLAlchemyError as err:
#             self.db_session.rollback()
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error due to {str(err)}")    



#     def get_all_status_issue_log_by_id(self, issue_log_id:int, tenancy_id:Optional[int]=None, reported_by_id:Optional[int]=None)->Optional[IssueLog]:
#         """
#         To retrieve an issue log that belongs to the current user
#         """
        
#         # Alias for employees to use in subqueries
#         employee_alias = aliased(Employee)

#         # Define the case statement for dynamically determining the implementing team
#         implementing_team = case(
            
#                 (IssueLog.srt_id == SRT.id, SRT.name),
#                 (IssueLog.unit_id == Unit.id, Unit.name),
#                 (IssueLog.department_id == Department.id, Department.name),
            
#             else_="Unknown",
#         )

#         # Subquery to get employee details associated with issue log
#         focal_persons_details = (
#             self.db_session.query(
#                 focal_person_issue_association.c.issue_logs_id.label("issue_logs_id"),
#                 func.array_agg(employee_alias.id).label("employee_ids"),
#                 func.array_agg(employee_alias.first_name + ' ' + employee_alias.last_name).label("employee_names"),
#             )
#             .join(employee_alias, employee_alias.id == focal_person_issue_association.c.employee_id)
#             .group_by(focal_person_issue_association.c.issue_logs_id)
#             .subquery()
#         )

#         # Main query to fetch issue log and associated data
#         issue_logs_query = (
#             self.db_session.query(
#                 IssueLog.id,
#                 IssueLog.issue,
#                 IssueLog.issue_description,
#                 IssueLog.key_recommendation,
#                 IssueLog.date_reported,
#                 IssueLog.status_id,
#                 IssueStatus.status.label("issue_log_status_name"),
#                 IssueLogSource.name.label("issue_log_source_name"),
#                 implementing_team.label("implementing_team"),
#                 IssueLog.reported_by_id,
#                 (Employee.first_name + ' ' + Employee.last_name).label("reported_by_name"),
#                 focal_persons_details.c.employee_ids,
#                 focal_persons_details.c.employee_names,
#                 IssueLog.tenancy_id,
#                 Tenancy.name.label("tenancy_name")
#             )
#             .join(IssueLog.status)
#             .join(IssueLog.source)
#             .join(Tenancy, Tenancy.id==IssueLog.tenancy_id)
#             .join(Employee, IssueLog.reported_by_id ==Employee.id)
#             .outerjoin(SRT, IssueLog.srt_id == SRT.id)
#             .outerjoin(Unit, IssueLog.unit_id == Unit.id)
#             .outerjoin(Department, IssueLog.department_id == Department.id)
#             .outerjoin(focal_persons_details, focal_persons_details.c.issue_logs_id == IssueLog.id)
#             .filter(
#                 IssueLog.is_active == True, IssueLog.id==issue_log_id
#             )
#         )
        
#         # Filter for Tenancy if True
#         if tenancy_id:
#             issue_logs_query = issue_logs_query.filter(IssueLog.tenancy_id == tenancy_id)

#         # Filter for Reported By
#         if reported_by_id:
#             issue_logs_query = issue_logs_query.filter(focal_persons_details.c.employee_ids.any(reported_by_id))
        
#         # Retrieve the filtered 
#         try:
#             issue_log=issue_logs_query.one_or_none()
#             if issue_log:
#                 logging_helper.log_info(f"IssueLog with ID {issue_log_id} Fetched successfully")
#                 return [{
#                     "issue_log_id": issue_log.id,
#                     "issue": issue_log.issue,
#                     "issue_description": issue_log.issue_description,
#                     "key_recommendation": issue_log.key_recommendation,
#                     "date_reported": issue_log.date_reported,
#                     "status_id": issue_log.status_id,
#                     "status_name": issue_log.issue_log_status_name,
#                     "issue_log_source_name": issue_log.issue_log_source_name,
#                     "implementing_team": issue_log.implementing_team,
#                     "reported_by_id":issue_log.reported_by_id,
#                     "reported_by_name": issue_log.reported_by_name,
#                     "focal_person_ids": issue_log.employee_ids,
#                     "focal_person_names": issue_log.employee_names,
#                     "tenancy_id": issue_log.tenancy_id,
#                     "tenancy_name": issue_log.tenancy_name
#                 }]
#             else:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The IssueLog with ID {issue_log_id} is not found")

#         except SQLAlchemyError as err:
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching issue log dues to {str(err)}")
        


#     def get_all_status_all_issue_log(self, skip:int=0, limit:int=100, tenancy_id:Optional[int]=None, reported_by_id:Optional[int]=None)->List[IssueLog]:
#         """
#         To retrieve all issue log that belongs to the current user
#         """
#         try:
#             # Alias for employees to use in subqueries
#             employee_alias = aliased(Employee)

#             # Define the case statement for dynamically determining the implementing team
#             implementing_team = case(
                
#                     (IssueLog.srt_id == SRT.id, SRT.name),
#                     (IssueLog.unit_id == Unit.id, Unit.name),
#                     (IssueLog.department_id == Department.id, Department.name),
                
#                 else_="Unknown",
#             )

#            # Subquery to get employee details associated with issue log
#             focal_persons_details = (
#                 self.db_session.query(
#                     focal_person_issue_association.c.issue_logs_id.label("issue_logs_id"),
#                     func.array_agg(employee_alias.id).label("employee_ids"),
#                     func.array_agg(employee_alias.first_name + ' ' + employee_alias.last_name).label("employee_names"),
#                 )
#                 .join(employee_alias, employee_alias.id == focal_person_issue_association.c.employee_id)
#                 .group_by(focal_person_issue_association.c.issue_logs_id)
#                 .subquery()
#             )

#             # Main query to fetch issue log and associated data
#             issue_logs_query = (
#                 self.db_session.query(
#                     IssueLog.id,
#                     IssueLog.issue,
#                     IssueLog.issue_description,
#                     IssueLog.key_recommendation,
#                     IssueLog.date_reported,
#                     IssueLog.status_id,
#                     IssueStatus.status.label("issue_log_status_name"),
#                     IssueLogSource.name.label("issue_log_source_name"),
#                     implementing_team.label("implementing_team"),
#                     IssueLog.reported_by_id,
#                     (Employee.first_name + ' ' + Employee.last_name).label("reported_by_name"),
#                     focal_persons_details.c.employee_ids,
#                     focal_persons_details.c.employee_names,
#                     IssueLog.tenancy_id,
#                     Tenancy.name.label("tenancy_name")
#                 )
#                 .join(IssueLog.status)
#                 .join(IssueLog.source)
#                 .join(Tenancy, Tenancy.id==IssueLog.tenancy_id)
#                 .join(Employee, IssueLog.reported_by_id ==Employee.id)
#                 .outerjoin(SRT, IssueLog.srt_id == SRT.id)
#                 .outerjoin(Unit, IssueLog.unit_id == Unit.id)
#                 .outerjoin(Department, IssueLog.department_id == Department.id)
#                 .outerjoin(focal_persons_details, focal_persons_details.c.issue_logs_id == IssueLog.id)
#                 .filter(
#                     IssueLog.is_active == True
#                 )
#             )
            
#             # Filter for Tenancy if True
#             if tenancy_id:
#                 issue_logs_query = issue_logs_query.filter(IssueLog.tenancy_id == tenancy_id)

#             # Filter for Reported By
#             if reported_by_id:
#                 issue_logs_query = issue_logs_query.filter(focal_persons_details.c.employee_ids.any(reported_by_id))

#             # Perform pagination on the retrieved data 
#             issue_logs = issue_logs_query.distinct(IssueLog.id).limit(limit=limit).offset(offset=skip).all()

#             logging_helper.log_info(f"All Status IssueLog Fetched Successfully")
#             return [{
#                 "issue_log_id": issue.id,
#                 "issue": issue.issue,
#                 "issue_description": issue.issue_description,
#                 "key_recommendation": issue.key_recommendation,
#                 "date_reported": issue.date_reported,
#                 "status_id": issue.status_id,
#                 "status_name": issue.issue_log_status_name,
#                 "issue_log_source_name": issue.issue_log_source_name,
#                 "implementing_team": issue.implementing_team,
#                 "reported_by_id":issue.reported_by_id,
#                 "reported_by_name": issue.reported_by_name,
#                 "focal_person_ids": issue.employee_ids,
#                 "focal_person_names": issue.employee_names,
#                 "tenancy_id": issue.tenancy_id,
#                 "tenancy_name": issue.tenancy_name
#             } for issue in issue_logs]

#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
#         except Exception as e:
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


#     def get_pending_issue_log_by_id(self, issue_log_id:int, tenancy_id:Optional[int]=None, reported_by_id:Optional[int]=None)->Optional[IssueLog]:
#         """
#         To retrieve an issue log that belongs to the current user
#         """
        
#         # Alias for employees to use in subqueries
#         employee_alias = aliased(Employee)

#         # Define the case statement for dynamically determining the implementing team
#         implementing_team = case(
            
#                 (IssueLog.srt_id == SRT.id, SRT.name),
#                 (IssueLog.unit_id == Unit.id, Unit.name),
#                 (IssueLog.department_id == Department.id, Department.name),
            
#             else_="Unknown",
#         )

#         # Subquery to get employee details associated with issue log
#         focal_persons_details = (
#             self.db_session.query(
#                 focal_person_issue_association.c.issue_logs_id.label("issue_logs_id"),
#                 func.array_agg(employee_alias.id).label("employee_ids"),
#                 func.array_agg(employee_alias.first_name + ' ' + employee_alias.last_name).label("employee_names"),
#             )
#             .join(employee_alias, employee_alias.id == focal_person_issue_association.c.employee_id)
#             .group_by(focal_person_issue_association.c.issue_logs_id)
#             .subquery()
#         )

#         # Main query to fetch issue log and associated data
#         issue_logs_query = (
#             self.db_session.query(
#                 IssueLog.id,
#                 IssueLog.issue,
#                 IssueLog.issue_description,
#                 IssueLog.key_recommendation,
#                 IssueLog.date_reported,
#                 IssueLog.status_id,
#                 IssueStatus.status.label("issue_log_status_name"),
#                 IssueLogSource.name.label("issue_log_source_name"),
#                 implementing_team.label("implementing_team"),
#                 IssueLog.reported_by_id,
#                 (Employee.first_name + ' ' + Employee.last_name).label("reported_by_name"),
#                 focal_persons_details.c.employee_ids,
#                 focal_persons_details.c.employee_names,
#                 IssueLog.tenancy_id,
#                 Tenancy.name.label("tenancy_name")
#             )
#             .join(IssueLog.status)
#             .join(IssueLog.source)
#             .join(Tenancy, Tenancy.id==IssueLog.tenancy_id)
#             .join(Employee, IssueLog.reported_by_id ==Employee.id)
#             .outerjoin(SRT, IssueLog.srt_id == SRT.id)
#             .outerjoin(Unit, IssueLog.unit_id == Unit.id)
#             .outerjoin(Department, IssueLog.department_id == Department.id)
#             .outerjoin(focal_persons_details, focal_persons_details.c.issue_logs_id == IssueLog.id)
#             .filter(
#                 IssueLog.is_active == True, IssueLog.status_id==PENDING, IssueLog.id==issue_log_id
#             )
#         )
        
#         # Filter for Tenancy if True
#         if tenancy_id:
#             issue_logs_query = issue_logs_query.filter(IssueLog.tenancy_id == tenancy_id)

#         # Filter for Reported By
#         if reported_by_id:
#             issue_logs_query = issue_logs_query.filter(focal_persons_details.c.employee_ids.any(reported_by_id))
        
#         # Retrieve the filtered 
#         try:
#             issue_log=issue_logs_query.one_or_none()
#             if issue_log:
#                 logging_helper.log_info(f"IssueLog with ID {issue_log_id} Updated successfully")
#                 return [{
#                     "issue_log_id": issue_log.id,
#                     "issue": issue_log.issue,
#                     "issue_description": issue_log.issue_description,
#                     "key_recommendation": issue_log.key_recommendation,
#                     "date_reported": issue_log.date_reported,
#                     "status_id": issue_log.status_id,
#                     "status_name": issue_log.issue_log_status_name,
#                     "issue_log_source_name": issue_log.issue_log_source_name,
#                     "implementing_team": issue_log.implementing_team,
#                     "reported_by_id":issue_log.reported_by_id,
#                     "reported_by_name": issue_log.reported_by_name,
#                     "focal_person_ids": issue_log.employee_ids,
#                     "focal_person_names": issue_log.employee_names,
#                     "tenancy_id": issue_log.tenancy_id,
#                     "tenancy_name": issue_log.tenancy_name
#                 }]
#             else:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The IssueLog with ID {issue_log_id} is not found")

#         except SQLAlchemyError as err:
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching issue log dues to {str(err)}")


#     def get_pending_issue_log_all(self, skip:int=0, limit:int=100, tenancy_id:Optional[int]=None, reported_by_id:Optional[int]=None)->List[IssueLog]:
#         """
#         To retrieve all issue log that belongs to the current user
#         """
        
#         try:
#             # Alias for employees to use in subqueries
#             employee_alias = aliased(Employee)

#             # Define the case statement for dynamically determining the implementing team
#             implementing_team = case(
                
#                     (IssueLog.srt_id == SRT.id, SRT.name),
#                     (IssueLog.unit_id == Unit.id, Unit.name),
#                     (IssueLog.department_id == Department.id, Department.name),
                
#                 else_="Unknown",
#             )

#            # Subquery to get employee details associated with issue log
#             focal_persons_details = (
#                 self.db_session.query(
#                     focal_person_issue_association.c.issue_logs_id.label("issue_logs_id"),
#                     func.array_agg(employee_alias.id).label("employee_ids"),
#                     func.array_agg(employee_alias.first_name + ' ' + employee_alias.last_name).label("employee_names"),
#                 )
#                 .join(employee_alias, employee_alias.id == focal_person_issue_association.c.employee_id)
#                 .group_by(focal_person_issue_association.c.issue_logs_id)
#                 .subquery()
#             )

#             # Main query to fetch issue log and associated data
#             issue_logs_query = (
#                 self.db_session.query(
#                     IssueLog.id,
#                     IssueLog.issue,
#                     IssueLog.issue_description,
#                     IssueLog.key_recommendation,
#                     IssueLog.date_reported,
#                     IssueLog.status_id,
#                     IssueStatus.status.label("issue_log_status_name"),
#                     IssueLogSource.name.label("issue_log_source_name"),
#                     implementing_team.label("implementing_team"),
#                     IssueLog.reported_by_id,
#                     (Employee.first_name + ' ' + Employee.last_name).label("reported_by_name"),
#                     focal_persons_details.c.employee_ids,
#                     focal_persons_details.c.employee_names,
#                     IssueLog.tenancy_id,
#                     Tenancy.name.label("tenancy_name")
#                 )
#                 .join(IssueLog.status)
#                 .join(IssueLog.source)
#                 .join(Tenancy, Tenancy.id==IssueLog.tenancy_id)
#                 .join(Employee, IssueLog.reported_by_id ==Employee.id)
#                 .outerjoin(SRT, IssueLog.srt_id == SRT.id)
#                 .outerjoin(Unit, IssueLog.unit_id == Unit.id)
#                 .outerjoin(Department, IssueLog.department_id == Department.id)
#                 .outerjoin(focal_persons_details, focal_persons_details.c.issue_logs_id == IssueLog.id)
#                 .filter(
#                     IssueLog.is_active == True, IssueLog.status_id==PENDING
#                 )
#             )
            
#             # Filter for Tenancy if True
#             if tenancy_id:
#                 issue_logs_query = issue_logs_query.filter(IssueLog.tenancy_id == tenancy_id)

#             # Filter for Reported By
#             if reported_by_id:
#                 issue_logs_query = issue_logs_query.filter(focal_persons_details.c.employee_ids.any(reported_by_id))

#             # Perform pagination on the retrieved data 
#             issue_logs = issue_logs_query.distinct(IssueLog.id).limit(limit=limit).offset(offset=skip).all()

#             logging_helper.log_info(f"All Pending IssueLog Fetched Successfully")
#             return [{
#                 "issue_log_id": issue.id,
#                 "issue": issue.issue,
#                 "issue_description": issue.issue_description,
#                 "key_recommendation": issue.key_recommendation,
#                 "date_reported": issue.date_reported,
#                 "status_id": issue.status_id,
#                 "status_name": issue.issue_log_status_name,
#                 "issue_log_source_name": issue.issue_log_source_name,
#                 "implementing_team": issue.implementing_team,
#                 "reported_by_id":issue.reported_by_id,
#                 "reported_by_name": issue.reported_by_name,
#                 "focal_person_ids": issue.employee_ids,
#                 "focal_person_names": issue.employee_names,
#                 "tenancy_id": issue.tenancy_id,
#                 "tenancy_name": issue.tenancy_name
#             } for issue in issue_logs]

#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
#         except Exception as e:
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



#     def delete_issue_by_id(self, issue_log_id:int, tenancy_id:Optional[int]=None):
#         """
#         To delete a PENDING issus log by specifying the ID
#         """
#         issue_log = self.db_session.query(IssueLog).filter(IssueLog.id==issue_log_id, IssueLog.is_active==True)

#         # Filter for Tenancy if True
#         if tenancy_id:
#             issue_log = issue_log.filter(IssueLog.tenancy_id==tenancy_id)
#             if issue_log is None:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Issue Log with ID {issue_log_id} is not for this Tenancy")
            
#         issue_log = issue_log.first()
#         if not issue_log:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Issue Log with ID {issue_log_id} was not found")
        
#         try:
#             # Delete the specified issue log
#             self.db_session.delete(instance=issue_log)
#             # Commit changes to the databases
#             self.db_session.commit()

#             logging_helper.log_info(f"IssueLog with ID {issue_log_id} Hard Deleted Successfully")
#             return f'message: Issue Log with ID {issue_log_id} is deleted successfully'
#         except SQLAlchemyError as err:
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Deleting Issuese failed due to {str(err)} ")
        


#     def soft_delete_issue_by_id(self, issue_log_id:int, tenancy_id:Optional[int]=None):
#         """
#         To soft delete an issue log
#         """
#         issue_log = self.db_session.query(IssueLog).filter(IssueLog.id==issue_log_id)
        
#         # Filter for Tenancy is True
#         if tenancy_id:
#             issue_log = issue_log.filter(IssueLog.tenancy_id==tenancy_id)
#             if issue_log is None:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Issue Log with ID {issue_log_id} is not for this Tenancy")
        
#         # Pull the first record
#         issue_log = issue_log.first()
#         if not issue_log:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The issue log with ID {issue_log_id} is not found")

#         # Check if is already deleted
#         if issue_log.is_active==False:
#             raise(HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The Issue log with ID {issue_log_id} is already dictivated"))
        
#         try:
#             # Updates the is active column 
#             issue_log.is_active=False

#             # Commit changes to the databases
#             self.db_session.commit()

#             logging_helper.log_info(f"IssueLog with ID {issue_log_id} Soft Deleted Successfully")
#             return f"The Issue log with ID {issue_log_id} is soft deleted successfully"

#         except SQLAlchemyError as err:
#             self.db_session.rollback()
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error occured while soft-delete {str(err)}")



#     def restore_issue_by_id(self, issue_log_id:int, tenancy_id:Optional[int]=None):
#         """
#         To restore an issue log
#         """
#         issue_log = self.db_session.query(IssueLog).filter(IssueLog.id==issue_log_id)
        
#         # Filter for Tenancy is True
#         if tenancy_id:
#             issue_log = issue_log.filter(IssueLog.tenancy_id==tenancy_id)
#             if issue_log is None:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Issue Log with ID {issue_log_id} is not for this Tenancy")
        
#         # Pull the first record
#         issue_log = issue_log.first()
#         if not issue_log:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The issue log with ID {issue_log_id} is not found")

#         # Check if is already active
#         if issue_log.is_active==True:
#             raise(HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The Issue log with ID {issue_log_id} is already active"))
        
#         try:
#             # Updates the is active column 
#             issue_log.is_active=True

#             # Commit changes to the databases
#             self.db_session.commit()            

#             logging_helper.log_info(f"IssueLog with ID {issue_log_id} Restored Successfully")
#             return f"The Issue log with ID {issue_log_id} is re-activated successfully"

#         except SQLAlchemyError as err:
#             self.db_session.rollback()
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error occured while soft-delete {str(err)}")


#     def close_completed_issue_log(self, background_tasks:BackgroundTasks, issue_log_id:int, issue_close_data:IssueLogClosure, tenancy_id:Optional[int]=None):
#         """
#         To close out issue log by the focal persons
#         """
#         try:
#             issue_log = self.db_session.query(IssueLog).filter(IssueLog.id==issue_log_id)

#             # Filter for Tenancy if is True
#             if tenancy_id:
#                 issue_log = issue_log.filter(IssueLog.tenancy_id==tenancy_id)

#             # Retrieve the first data
#             issue_log = issue_log.one_or_none()
#             if not issue_log:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The issue log with ID {issue_log_id} is not found")
            
#             # Check if is already completed
#             if issue_log.close_date is not None:
#                 raise(HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The Issue log with ID {issue_log_id} is already completed"))

#             # Structure the Issue Closure data to form a dictionary
#             close_issue_data = issue_close_data.model_dump(exclude_unset=True)

#             for key, value in close_issue_data.items():
#                 setattr(issue_log, key, value)

#             # Update the status ID
#             issue_log.status_id=COMPLETED

#             # Commit changes to the database
#             self.db_session.commit()
#             self.db_session.refresh(issue_log)

#             issue_initiator = self.db_session.query(Employee).filter(Employee.id==issue_log.reported_by_id).first()
#             issue_initiator_name = f"{issue_initiator.first_name} {issue_initiator.last_name}"

#             recipients = [(employee.first_name, employee.employee_email)
#                 for employee in issue_log.employees
#                 if employee.employee_email]

#             # Date Formatting
#             closure_date = issue_close_data.close_date
#             closure_date = f"{self.get_day_with_suffix(day=closure_date.day)} of {closure_date.strftime('%B')} {closure_date.year}"


#             # Send Notification for closure of Issue Log
#             background_tasks.add_task(notify_initiator_about_completed_issue_logs, issue_initiator.first_name, issue_initiator.employee_email, issue_log.issue, issue_log.issue_description, issue_close_data.notes_on_closure, closure_date)

#             background_tasks.add_task(notify_employees_about_completed_issue_logs, recipients, issue_initiator_name, issue_log.issue, issue_log.issue_description, issue_close_data.notes_on_closure, closure_date)

#             logging_helper.log_info(f"IssueLog with ID {issue_log_id} Closed Successfully")
#             return f"The Issue log with ID {issue_log_id} has been completed successfully"

#         except Exception as e:
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



#     def get_day_with_suffix(self, day):
#         if 11 <= day <= 13:
#             return f"{day}th"
#         suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
#         return f"{day}{suffixes.get(day % 10, 'th')}"


from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session, aliased
from schemas.issue_schemas import IssueCreate, IssueUpdate, IssueLogClosure
from models.all_models import IssueLog, Tenancy, IssueLogSource, IssueStatus, focal_person_issue_association, Employee, SRT, Unit, Department
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
from auth.email import notify_employees_about_issue_logs, notify_employees_about_update_on_issue_logs, notify_employees_about_completed_issue_logs, notify_initiator_about_issue_logs, notify_initiator_about_completed_issue_logs
from sqlalchemy import func, case
from logging_helpers import logging_helper
from datetime import datetime
PENDING=1
COMPLETED=2

class IssueRepository:
    def __init__(self, db_session:Session):
        self.db_session = db_session

    def create_issue_log(self, background_tasks:BackgroundTasks, issue_create_data:IssueCreate):
        "Creates an issue using data from the Issue Data"

        # Check for duplicate entry
        issue_exist = self.db_session.query(IssueLog).filter(IssueLog.tenancy_id==issue_create_data.tenancy_id, IssueLog.issue_description==issue_create_data.issue_description).first()
        if issue_exist:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The issue your raising '{issue_create_data.issue_description}' has already been created")
        
        # Check for description
        if not issue_create_data.issue_description:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No issue description was provided")
        
        # Fetch the name of the issue log source
        issue_source_name = self.db_session.query(IssueLogSource).filter(IssueLogSource.id==issue_create_data.source_id).one_or_none()
        if not issue_source_name:
            raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue Log Source with Source ID {issue_create_data.source_id} was not found")
        
        # Fetch the name of the Tenancy
        issue_tenancy_name = self.db_session.query(Tenancy).filter(Tenancy.id==issue_create_data.tenancy_id).one_or_none()
        if not issue_tenancy_name:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tenancy with Tenancy ID {issue_create_data.tenancy_id} was not found")

        issue = IssueLog(
            issue=f"Issue identified from {issue_source_name.name} for {issue_tenancy_name.name} State",
            issue_description=issue_create_data.issue_description,
            key_recommendation=issue_create_data.key_recommendation,
            date_reported=datetime.now().date(), #Mapping the Current Date
            time_line_date=issue_create_data.time_line_date,
            reported_by_id=issue_create_data.reported_by_id,
            thematic_area_id=issue_create_data.thematic_area_id,
            site_id=issue_create_data.site_id,
            source_id=issue_create_data.source_id,
            status_id=PENDING,
            meeting_id=issue_create_data.meeting_id,
            srt_id=issue_create_data.srt_id,
            unit_id=issue_create_data.unit_id,
            department_id=issue_create_data.department_id,
            tenancy_id=issue_create_data.tenancy_id
        )
        try:
            self.db_session.add(issue)
            self.db_session.flush()

            issue.employees.extend(
                self.db_session.query(Employee)
                .filter(Employee.id.in_(issue_create_data.focal_persons))
                .all()
            )
            self.db_session.commit()
            issue_ouput = {
                "issue_id":issue.id,
                "issue":issue.issue,
                "issue_description":issue.issue_description,
                "key_recommendation":issue.key_recommendation,
                "time_line_date":issue.time_line_date,
                "focal_person":issue.employees
            }

            issue_initiator = self.db_session.query(Employee).filter(Employee.id==issue_create_data.reported_by_id).first()
            issue_initiator_name = f"{issue_initiator.first_name} {issue_initiator.last_name}"

            recipients = [(employee.first_name, employee.employee_email)
                for employee in issue.employees
                if employee.employee_email]
            
            focal_persons_names_data = [f'{employee.first_name} {employee.last_name}'
                for employee in issue.employees
                if employee.employee_email]
            
            focal_persons_names = ', '.join(focal_persons_names_data[:-1]) + ' and ' + focal_persons_names_data[-1]
            
            # Date Formatting
            if issue_create_data.time_line_date:
                time_line_date = issue_create_data.time_line_date
                time_line_date = f"{self.get_day_with_suffix(time_line_date.day)} of {time_line_date.strftime('%B')} {time_line_date.year}"
            
            # Prepare mail to send to the initiator for the issues    
            background_tasks.add_task(notify_initiator_about_issue_logs, focal_persons_names, issue_initiator.first_name, issue_initiator.employee_email, issue.issue, issue_create_data.issue_description, issue.key_recommendation, time_line_date)

            # Prepare mail to send to the resposible persons for the issues    
            background_tasks.add_task(notify_employees_about_issue_logs, recipients, issue_initiator_name, issue.issue, issue_create_data.issue_description, issue.key_recommendation, time_line_date)

            logging_helper.log_info(f"IssueLog {issue.issue_description} created successfully")
            return issue_ouput
            
        except SQLAlchemyError as err:
            self.db_session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured while creating issuse {str(err)}")



    def update_pending_issue_log(self, background_tasks:BackgroundTasks, issue_log_id:int, issue_update_data:IssueUpdate, tenancy_id:Optional[int]=None, reported_by_id:Optional[int]=None) -> IssueUpdate:
        """
        To Update an issue log that has not been completed
        """

        # Fetch Issue Log using the ID
        issue_log = self.db_session.query(IssueLog).filter(IssueLog.id==issue_log_id)

        # Filter for Tenancy if True
        if tenancy_id:
            issue_log = issue_log.filter(IssueLog.tenancy_id==tenancy_id)

        # Filter for reported person
        if reported_by_id:
            issue_log = issue_log.filter(IssueLog.reported_by_id==reported_by_id)

        # Retrieve first record if found
        issue_log = issue_log.one_or_none()
        if not issue_log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue Log with ID {issue_log_id} was not found")
        
        # Check if Issue Log has been completed
        if issue_log.close_date is not None or issue_log.status_id!=1:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Issue Log with ID {issue_log_id} has already been completed by the focal person(s)")

        # Fetch the name of the issue log source
        issue_source_name = self.db_session.query(IssueLogSource).filter(IssueLogSource.id==issue_update_data.source_id).one_or_none()
        if not issue_source_name:
            raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue Log Source with Source ID {issue_update_data.source_id} was not found")
        
        # Fetch the name of the Tenancy
        issue_tenancy_name = self.db_session.query(Tenancy).filter(Tenancy.id==issue_log.tenancy_id).one_or_none()
        if not issue_tenancy_name:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tenancy with Tenancy ID {issue_log.tenancy_id} was not found")
        
        # Structure the Issue Update data to forma dictionary
        update_issue_data = issue_update_data.model_dump(exclude_unset=True)
        
        # Append issue_source_name to the issue_update_data dictionary
        update_issue_data["issue"] = f"Issue identified in {issue_source_name.name} for {issue_tenancy_name.name} State",

        for key, value in update_issue_data.items():
            setattr(issue_log, key, value)

        try:
            # Commit changes to the database
            self.db_session.flush()
            self.db_session.refresh(issue_log)

            issue_initiator = self.db_session.query(Employee).filter(Employee.id==issue_log.reported_by_id).first()
            issue_initiator_name = f"{issue_initiator.first_name} {issue_initiator.last_name}"

            recipients = [(employee.first_name, employee.employee_email)
                for employee in issue_log.employees
                if employee.employee_email]

            # Date Formatting
            if issue_update_data.time_line_date:
                time_line_date = issue_update_data.time_line_date
                time_line_date = f"{self.get_day_with_suffix(time_line_date.day)} of {time_line_date.strftime('%B')} {time_line_date.year}"

            # Send Notification for update of Issue Log
            background_tasks.add_task(notify_employees_about_update_on_issue_logs, recipients, issue_initiator_name, issue_log.issue, issue_update_data.issue_description, issue_update_data.key_recommendation, time_line_date)

            logging_helper.log_info(f"IssueLog with ID {issue_log_id} Updated successfully")
            return issue_log
        
        except SQLAlchemyError as err:
            self.db_session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error due to {str(err)}")    



    def get_all_status_issue_log_by_id(self, issue_log_id:int, tenancy_id:Optional[int]=None, reported_by_id:Optional[int]=None)->Optional[IssueLog]:
        """
        To retrieve an issue log that belongs to the current user
        """
        
        # Alias for employees to use in subqueries
        employee_alias = aliased(Employee)

        # Define the case statement for dynamically determining the implementing team
        implementing_team = case(
            
                (IssueLog.srt_id == SRT.id, SRT.name),
                (IssueLog.unit_id == Unit.id, Unit.name),
                (IssueLog.department_id == Department.id, Department.name),
            
            else_="Unknown",
        )

        # Subquery to get employee details associated with issue log
        focal_persons_details = (
            self.db_session.query(
                focal_person_issue_association.c.issue_logs_id.label("issue_logs_id"),
                func.array_agg(employee_alias.id).label("employee_ids"),
                func.array_agg(employee_alias.first_name + ' ' + employee_alias.last_name).label("employee_names"),
            )
            .join(employee_alias, employee_alias.id == focal_person_issue_association.c.employee_id)
            .group_by(focal_person_issue_association.c.issue_logs_id)
            .subquery()
        )

        # Main query to fetch issue log and associated data
        issue_logs_query = (
            self.db_session.query(
                IssueLog.id,
                IssueLog.issue,
                IssueLog.issue_description,
                IssueLog.key_recommendation,
                IssueLog.date_reported,
                IssueLog.status_id,
                IssueStatus.status.label("issue_log_status_name"),
                IssueLogSource.name.label("issue_log_source_name"),
                implementing_team.label("implementing_team"),
                IssueLog.reported_by_id,
                (Employee.first_name + ' ' + Employee.last_name).label("reported_by_name"),
                focal_persons_details.c.employee_ids,
                focal_persons_details.c.employee_names,
                IssueLog.tenancy_id,
                Tenancy.name.label("tenancy_name")
            )
            .join(IssueLog.status)
            .join(IssueLog.source)
            .join(Tenancy, Tenancy.id==IssueLog.tenancy_id)
            .join(Employee, IssueLog.reported_by_id ==Employee.id)
            .outerjoin(SRT, IssueLog.srt_id == SRT.id)
            .outerjoin(Unit, IssueLog.unit_id == Unit.id)
            .outerjoin(Department, IssueLog.department_id == Department.id)
            .outerjoin(focal_persons_details, focal_persons_details.c.issue_logs_id == IssueLog.id)
            .filter(
                IssueLog.is_active == True, IssueLog.id==issue_log_id
            )
        )
        
        # Filter for Tenancy if True
        if tenancy_id:
            issue_logs_query = issue_logs_query.filter(IssueLog.tenancy_id == tenancy_id)

        # Filter for Reported By
        if reported_by_id:
            issue_logs_query = issue_logs_query.filter(focal_persons_details.c.employee_ids.any(reported_by_id))
        
        # Retrieve the filtered 
        try:
            issue_log=issue_logs_query.one_or_none()
            if issue_log:
                logging_helper.log_info(f"IssueLog with ID {issue_log_id} Fetched successfully")
                return [{
                    "issue_log_id": issue_log.id,
                    "issue": issue_log.issue,
                    "issue_description": issue_log.issue_description,
                    "key_recommendation": issue_log.key_recommendation,
                    "date_reported": issue_log.date_reported,
                    "issue_status":[{"status_id":issue_log.status_id, "status_name":issue_log.issue_log_status_name}],
                    "issue_log_source_name": issue_log.issue_log_source_name,
                    "implementing_team": issue_log.implementing_team,
                    "reported_by":[{"reported_by_id":issue_log.reported_by_id, "reported_by_name":issue_log.reported_by_name}],
                    "focal_person_ids": issue_log.employee_ids,
                    "focal_person_names": issue_log.employee_names,
                    "tenancy":[{"tenancy_id":issue_log.tenancy_id, "tenancy_name":issue_log.tenancy_name}]
                }]
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The IssueLog with ID {issue_log_id} is not found")

        except SQLAlchemyError as err:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching issue log dues to {str(err)}")
        


    def get_all_status_all_issue_log(self, skip:int=0, limit:int=100, tenancy_id:Optional[int]=None, reported_by_id:Optional[int]=None)->List[IssueLog]:
        """
        To retrieve all issue log that belongs to the current user
        """
        try:
            # Alias for employees to use in subqueries
            employee_alias = aliased(Employee)

            # Define the case statement for dynamically determining the implementing team
            implementing_team = case(
                
                    (IssueLog.srt_id == SRT.id, SRT.name),
                    (IssueLog.unit_id == Unit.id, Unit.name),
                    (IssueLog.department_id == Department.id, Department.name),
                
                else_="Unknown",
            )

           # Subquery to get employee details associated with issue log
            focal_persons_details = (
                self.db_session.query(
                    focal_person_issue_association.c.issue_logs_id.label("issue_logs_id"),
                    func.array_agg(employee_alias.id).label("employee_ids"),
                    func.array_agg(employee_alias.first_name + ' ' + employee_alias.last_name).label("employee_names"),
                )
                .join(employee_alias, employee_alias.id == focal_person_issue_association.c.employee_id)
                .group_by(focal_person_issue_association.c.issue_logs_id)
                .subquery()
            )

            # Main query to fetch issue log and associated data
            issue_logs_query = (
                self.db_session.query(
                    IssueLog.id,
                    IssueLog.issue,
                    IssueLog.issue_description,
                    IssueLog.key_recommendation,
                    IssueLog.date_reported,
                    IssueLog.status_id,
                    IssueStatus.status.label("issue_log_status_name"),
                    IssueLogSource.name.label("issue_log_source_name"),
                    implementing_team.label("implementing_team"),
                    IssueLog.reported_by_id,
                    (Employee.first_name + ' ' + Employee.last_name).label("reported_by_name"),
                    focal_persons_details.c.employee_ids,
                    focal_persons_details.c.employee_names,
                    IssueLog.tenancy_id,
                    Tenancy.name.label("tenancy_name")
                )
                .join(IssueLog.status)
                .join(IssueLog.source)
                .join(Tenancy, Tenancy.id==IssueLog.tenancy_id)
                .join(Employee, IssueLog.reported_by_id ==Employee.id)
                .outerjoin(SRT, IssueLog.srt_id == SRT.id)
                .outerjoin(Unit, IssueLog.unit_id == Unit.id)
                .outerjoin(Department, IssueLog.department_id == Department.id)
                .outerjoin(focal_persons_details, focal_persons_details.c.issue_logs_id == IssueLog.id)
                .filter(
                    IssueLog.is_active == True
                )
            )
            
            # Filter for Tenancy if True
            if tenancy_id:
                issue_logs_query = issue_logs_query.filter(IssueLog.tenancy_id == tenancy_id)

            # Filter for Reported By
            if reported_by_id:
                issue_logs_query = issue_logs_query.filter(focal_persons_details.c.employee_ids.any(reported_by_id))

            # Perform pagination on the retrieved data 
            issue_logs = issue_logs_query.distinct(IssueLog.id).limit(limit=limit).offset(offset=skip).all()

            logging_helper.log_info(f"All Status IssueLog Fetched Successfully")
            return [{
                "issue_log_id": issue.id,
                "issue": issue.issue,
                "issue_description": issue.issue_description,
                "key_recommendation": issue.key_recommendation,
                "date_reported": issue.date_reported,
                "issue_status":[{"status_id":issue.status_id, "status_name":issue.issue_log_status_name}],
                "issue_log_source_name": issue.issue_log_source_name,
                "implementing_team": issue.implementing_team,
                "reported_by":[{"reported_by_id":issue.reported_by_id, "reported_by_name":issue.reported_by_name}],
                "focal_person_ids": issue.employee_ids,
                "focal_person_names": issue.employee_names,
                "tenancy":[{"tenancy_id":issue.tenancy_id, "tenancy_name":issue.tenancy_name}]
            } for issue in issue_logs]

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


    def get_pending_issue_log_by_id(self, issue_log_id:int, tenancy_id:Optional[int]=None, reported_by_id:Optional[int]=None)->Optional[IssueLog]:
        """
        To retrieve an issue log that belongs to the current user
        """
        
        # Alias for employees to use in subqueries
        employee_alias = aliased(Employee)

        # Define the case statement for dynamically determining the implementing team
        implementing_team = case(
            
                (IssueLog.srt_id == SRT.id, SRT.name),
                (IssueLog.unit_id == Unit.id, Unit.name),
                (IssueLog.department_id == Department.id, Department.name),
            
            else_="Unknown",
        )

        # Subquery to get employee details associated with issue log
        focal_persons_details = (
            self.db_session.query(
                focal_person_issue_association.c.issue_logs_id.label("issue_logs_id"),
                func.array_agg(employee_alias.id).label("employee_ids"),
                func.array_agg(employee_alias.first_name + ' ' + employee_alias.last_name).label("employee_names"),
            )
            .join(employee_alias, employee_alias.id == focal_person_issue_association.c.employee_id)
            .group_by(focal_person_issue_association.c.issue_logs_id)
            .subquery()
        )

        # Main query to fetch issue log and associated data
        issue_logs_query = (
            self.db_session.query(
                IssueLog.id,
                IssueLog.issue,
                IssueLog.issue_description,
                IssueLog.key_recommendation,
                IssueLog.date_reported,
                IssueLog.status_id,
                IssueStatus.status.label("issue_log_status_name"),
                IssueLogSource.name.label("issue_log_source_name"),
                implementing_team.label("implementing_team"),
                IssueLog.reported_by_id,
                (Employee.first_name + ' ' + Employee.last_name).label("reported_by_name"),
                focal_persons_details.c.employee_ids,
                focal_persons_details.c.employee_names,
                IssueLog.tenancy_id,
                Tenancy.name.label("tenancy_name")
            )
            .join(IssueLog.status)
            .join(IssueLog.source)
            .join(Tenancy, Tenancy.id==IssueLog.tenancy_id)
            .join(Employee, IssueLog.reported_by_id ==Employee.id)
            .outerjoin(SRT, IssueLog.srt_id == SRT.id)
            .outerjoin(Unit, IssueLog.unit_id == Unit.id)
            .outerjoin(Department, IssueLog.department_id == Department.id)
            .outerjoin(focal_persons_details, focal_persons_details.c.issue_logs_id == IssueLog.id)
            .filter(
                IssueLog.is_active == True, IssueLog.status_id==PENDING, IssueLog.id==issue_log_id
            )
        )
        
        # Filter for Tenancy if True
        if tenancy_id:
            issue_logs_query = issue_logs_query.filter(IssueLog.tenancy_id == tenancy_id)

        # Filter for Reported By
        if reported_by_id:
            issue_logs_query = issue_logs_query.filter(focal_persons_details.c.employee_ids.any(reported_by_id))
        
        # Retrieve the filtered 
        try:
            issue_log=issue_logs_query.one_or_none()
            if issue_log:
                logging_helper.log_info(f"IssueLog with ID {issue_log_id} Updated successfully")
                return [{
                    "issue_log_id": issue_log.id,
                    "issue": issue_log.issue,
                    "issue_description": issue_log.issue_description,
                    "key_recommendation": issue_log.key_recommendation,
                    "date_reported": issue_log.date_reported,
                    "issue_status":[{"status_id":issue_log.status_id, "status_name":issue_log.issue_log_status_name}],
                    "issue_log_source_name": issue_log.issue_log_source_name,
                    "implementing_team": issue_log.implementing_team,
                    "reported_by":[{"reported_by_id":issue_log.reported_by_id, "reported_by_name":issue_log.reported_by_name}],
                    "focal_person_ids": issue_log.employee_ids,
                    "focal_person_names": issue_log.employee_names,
                    "tenancy":[{"tenancy_id":issue_log.tenancy_id, "tenancy_name":issue_log.tenancy_name}]
                }]
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The IssueLog with ID {issue_log_id} is not found")

        except SQLAlchemyError as err:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching issue log dues to {str(err)}")


    def get_pending_issue_log_all(self, skip:int=0, limit:int=100, tenancy_id:Optional[int]=None, reported_by_id:Optional[int]=None)->List[IssueLog]:
        """
        To retrieve all issue log that belongs to the current user
        """
        
        try:
            # Alias for employees to use in subqueries
            employee_alias = aliased(Employee)

            # Define the case statement for dynamically determining the implementing team
            implementing_team = case(
                
                    (IssueLog.srt_id == SRT.id, SRT.name),
                    (IssueLog.unit_id == Unit.id, Unit.name),
                    (IssueLog.department_id == Department.id, Department.name),
                
                else_="Unknown",
            )

           # Subquery to get employee details associated with issue log
            focal_persons_details = (
                self.db_session.query(
                    focal_person_issue_association.c.issue_logs_id.label("issue_logs_id"),
                    func.array_agg(employee_alias.id).label("employee_ids"),
                    func.array_agg(employee_alias.first_name + ' ' + employee_alias.last_name).label("employee_names"),
                )
                .join(employee_alias, employee_alias.id == focal_person_issue_association.c.employee_id)
                .group_by(focal_person_issue_association.c.issue_logs_id)
                .subquery()
            )

            # Main query to fetch issue log and associated data
            issue_logs_query = (
                self.db_session.query(
                    IssueLog.id,
                    IssueLog.issue,
                    IssueLog.issue_description,
                    IssueLog.key_recommendation,
                    IssueLog.date_reported,
                    IssueLog.status_id,
                    IssueStatus.status.label("issue_log_status_name"),
                    IssueLogSource.name.label("issue_log_source_name"),
                    implementing_team.label("implementing_team"),
                    IssueLog.reported_by_id,
                    (Employee.first_name + ' ' + Employee.last_name).label("reported_by_name"),
                    focal_persons_details.c.employee_ids,
                    focal_persons_details.c.employee_names,
                    IssueLog.tenancy_id,
                    Tenancy.name.label("tenancy_name")
                )
                .join(IssueLog.status)
                .join(IssueLog.source)
                .join(Tenancy, Tenancy.id==IssueLog.tenancy_id)
                .join(Employee, IssueLog.reported_by_id ==Employee.id)
                .outerjoin(SRT, IssueLog.srt_id == SRT.id)
                .outerjoin(Unit, IssueLog.unit_id == Unit.id)
                .outerjoin(Department, IssueLog.department_id == Department.id)
                .outerjoin(focal_persons_details, focal_persons_details.c.issue_logs_id == IssueLog.id)
                .filter(
                    IssueLog.is_active == True, IssueLog.status_id==PENDING
                )
            )
            
            # Filter for Tenancy if True
            if tenancy_id:
                issue_logs_query = issue_logs_query.filter(IssueLog.tenancy_id == tenancy_id)

            # Filter for Reported By
            if reported_by_id:
                issue_logs_query = issue_logs_query.filter(focal_persons_details.c.employee_ids.any(reported_by_id))

            

            # Perform pagination on the retrieved data 
            issue_logs = issue_logs_query.distinct(IssueLog.id).limit(limit=limit).offset(offset=skip).all()


            logging_helper.log_info(f"All Pending IssueLog Fetched Successfully")
            return [{
                "issue_log_id": issue.id,
                "issue": issue.issue,
                "issue_description": issue.issue_description,
                "key_recommendation": issue.key_recommendation,
                "date_reported": issue.date_reported,
                "issue_status":[{"status_id":issue.status_id, "status_name":issue.issue_log_status_name}],
                "issue_log_source_name": issue.issue_log_source_name,
                "implementing_team": issue.implementing_team,
                "reported_by":[{"reported_by_id":issue.reported_by_id, "reported_by_name":issue.reported_by_name}],
                "focal_person_ids": issue.employee_ids,
                "focal_person_names": issue.employee_names,
                "tenancy_id": issue.tenancy_id,
                "tenancy":[{"tenancy_id":issue.tenancy_id, "tenancy_name":issue.tenancy_name}]
            } for issue in issue_logs]

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



    def delete_issue_by_id(self, issue_log_id:int, tenancy_id:Optional[int]=None):
        """
        To delete a PENDING issus log by specifying the ID
        """
        issue_log = self.db_session.query(IssueLog).filter(IssueLog.id==issue_log_id, IssueLog.is_active==True)

        # Filter for Tenancy if True
        if tenancy_id:
            issue_log = issue_log.filter(IssueLog.tenancy_id==tenancy_id)
            if issue_log is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Issue Log with ID {issue_log_id} is not for this Tenancy")
            
        issue_log = issue_log.first()
        if not issue_log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Issue Log with ID {issue_log_id} was not found")
        
        try:
            # Delete the specified issue log
            self.db_session.delete(instance=issue_log)
            # Commit changes to the databases
            self.db_session.commit()

            logging_helper.log_info(f"IssueLog with ID {issue_log_id} Hard Deleted Successfully")
            return f'message: Issue Log with ID {issue_log_id} is deleted successfully'
        except SQLAlchemyError as err:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Deleting Issuese failed due to {str(err)} ")
        


    def soft_delete_issue_by_id(self, issue_log_id:int, tenancy_id:Optional[int]=None):
        """
        To soft delete an issue log
        """
        issue_log = self.db_session.query(IssueLog).filter(IssueLog.id==issue_log_id)
        
        # Filter for Tenancy is True
        if tenancy_id:
            issue_log = issue_log.filter(IssueLog.tenancy_id==tenancy_id)
            if issue_log is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Issue Log with ID {issue_log_id} is not for this Tenancy")
        
        # Pull the first record
        issue_log = issue_log.first()
        if not issue_log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The issue log with ID {issue_log_id} is not found")

        # Check if is already deleted
        if issue_log.is_active==False:
            raise(HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The Issue log with ID {issue_log_id} is already dictivated"))
        
        try:
            # Updates the is active column 
            issue_log.is_active=False

            # Commit changes to the databases
            self.db_session.commit()

            logging_helper.log_info(f"IssueLog with ID {issue_log_id} Soft Deleted Successfully")
            return f"The Issue log with ID {issue_log_id} is soft deleted successfully"

        except SQLAlchemyError as err:
            self.db_session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error occured while soft-delete {str(err)}")



    def restore_issue_by_id(self, issue_log_id:int, tenancy_id:Optional[int]=None):
        """
        To restore an issue log
        """
        issue_log = self.db_session.query(IssueLog).filter(IssueLog.id==issue_log_id)
        
        # Filter for Tenancy is True
        if tenancy_id:
            issue_log = issue_log.filter(IssueLog.tenancy_id==tenancy_id)
            if issue_log is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Issue Log with ID {issue_log_id} is not for this Tenancy")
        
        # Pull the first record
        issue_log = issue_log.first()
        if not issue_log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The issue log with ID {issue_log_id} is not found")

        # Check if is already active
        if issue_log.is_active==True:
            raise(HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The Issue log with ID {issue_log_id} is already active"))
        
        try:
            # Updates the is active column 
            issue_log.is_active=True

            # Commit changes to the databases
            self.db_session.commit()            

            logging_helper.log_info(f"IssueLog with ID {issue_log_id} Restored Successfully")
            return f"The Issue log with ID {issue_log_id} is re-activated successfully"

        except SQLAlchemyError as err:
            self.db_session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error occured while soft-delete {str(err)}")


    def close_completed_issue_log(self, background_tasks:BackgroundTasks, issue_log_id:int, issue_close_data:IssueLogClosure, tenancy_id:Optional[int]=None):
        """
        To close out issue log by the focal persons
        """
        try:
            issue_log = self.db_session.query(IssueLog).filter(IssueLog.id==issue_log_id)

            # Filter for Tenancy if is True
            if tenancy_id:
                issue_log = issue_log.filter(IssueLog.tenancy_id==tenancy_id)

            # Retrieve the first data
            issue_log = issue_log.one_or_none()
            if not issue_log:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The issue log with ID {issue_log_id} is not found")
            
            # Check if is already completed
            if issue_log.close_date is not None:
                raise(HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The Issue log with ID {issue_log_id} is already completed"))

            # Structure the Issue Closure data to form a dictionary
            close_issue_data = issue_close_data.model_dump(exclude_unset=True)

            for key, value in close_issue_data.items():
                setattr(issue_log, key, value)

            # Update the status ID
            issue_log.status_id=COMPLETED
            issue_log.close_date=datetime.now().date(), #Mapping the Current Date

            # Commit changes to the database
            self.db_session.commit()
            self.db_session.refresh(issue_log)

            issue_initiator = self.db_session.query(Employee).filter(Employee.id==issue_log.reported_by_id).first()
            issue_initiator_name = f"{issue_initiator.first_name} {issue_initiator.last_name}"

            recipients = [(employee.first_name, employee.employee_email)
                for employee in issue_log.employees
                if employee.employee_email]

            # Date Formatting
            closure_date = issue_log.close_date
            closure_date = f"{self.get_day_with_suffix(day=closure_date.day)} of {closure_date.strftime('%B')} {closure_date.year}"


            # Send Notification for closure of Issue Log
            background_tasks.add_task(notify_initiator_about_completed_issue_logs, issue_initiator.first_name, issue_initiator.employee_email, issue_log.issue, issue_log.issue_description, issue_close_data.notes_on_closure, closure_date)

            background_tasks.add_task(notify_employees_about_completed_issue_logs, recipients, issue_initiator_name, issue_log.issue, issue_log.issue_description, issue_close_data.notes_on_closure, closure_date)

            logging_helper.log_info(f"IssueLog with ID {issue_log_id} Closed Successfully")
            return f"The Issue log with ID {issue_log_id} has been completed successfully"

        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



    def get_day_with_suffix(self, day):
        if 11 <= day <= 13:
            return f"{day}th"
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        return f"{day}{suffixes.get(day % 10, 'th')}"
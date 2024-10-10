
# from fastapi import HTTPException, status, BackgroundTasks
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from typing import List, Optional, Dict
# from models.all_models import Assignment as AssignmentModel, Employee as EmployeeModel, Tenancy as TenancyModel, User as UserModel, ActionEnum, Task as TaskModel, task_employee_association
# from schemas.assignment_schemas import AssignmentCreate, AssignmentUpdate, AssignmentResponse, AssignmentWithEmployees
# from logging_helpers import logging_helper
# from datetime import date, datetime
# from auth.email import (
#     notify_assignment_creation,
#     notify_initiator_about_assignment,
#     generate_message_id
# )

# class AssignmentRepository:
#     def __init__(self, db_session: Session):
#         self.db_session = db_session

    
#     def create_assignment(
#         self, 
#         assignment: AssignmentCreate, 
#         user_id: Optional[int], 
#         background_tasks: BackgroundTasks
#     ) -> AssignmentModel:
#         try:
#             db_assignment = AssignmentModel(
#                 name=assignment.name,
#                 description=assignment.description,
#                 start_date=assignment.start_date,
#                 end_date=assignment.end_date,
#                 status=assignment.status,
#                 assignment_lead_id=assignment.assignment_lead_id,
#                 initiating_user_id=user_id
#             )
#             for tenancy_id in assignment.tenancy_ids:
#                 tenancy = self.db_session.query(TenancyModel).get(tenancy_id)
#                 if tenancy:
#                     db_assignment.tenancies.append(tenancy)
#             for employee_id in assignment.assigned_employee_ids:
#                 employee = self.db_session.query(EmployeeModel).get(employee_id)
#                 if not employee:
#                     raise Exception(f"Employee with ID {employee_id} does not exist.")
#                 db_assignment.responsible_employees.append(employee)
#             self.db_session.add(db_assignment)
#             self.db_session.commit()
#             self.db_session.refresh(db_assignment)

#             # Fetching the initiating user's full name
#             initiating_user = (
#                 self.db_session.query(EmployeeModel)
#                 .join(UserModel, UserModel.id == db_assignment.initiating_user_id)
#                 .filter(UserModel.id == db_assignment.initiating_user_id)
#                 .first()
#             )
#             if initiating_user:
#                 initiating_user_fullname = f"{initiating_user.first_name} {initiating_user.last_name}"
#                 db_assignment.initiating_user_fullname = initiating_user_fullname

#             logging_helper.log_info(f"Assignment {db_assignment.name} created successfully")

#             # Send email notifications
#             recipient_emails = [
#                 (employee.first_name, employee.employee_email)
#                 for employee in db_assignment.responsible_employees
#                 if employee.employee_email
#             ]

#             background_tasks.add_task(
#                 notify_assignment_creation,
#                 recipient_emails,
#                 db_assignment.name,
#                 initiating_user_fullname
#             )

#             background_tasks.add_task(
#                 notify_initiator_about_assignment,
#                 initiating_user.employee_email,
#                 initiating_user_fullname,
#                 db_assignment.name,
#                 db_assignment.status
#             )

#             return db_assignment
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error creating assignment: {e}")
#             raise Exception(f"Failed to create assignment: {str(e)}")


#     def update_assignment(self, assignment_id: int, assignment: AssignmentUpdate, user_id: Optional[int] = None) -> Optional[AssignmentModel]:
#         try:
#             db_assignment = self.db_session.query(AssignmentModel).filter(AssignmentModel.id == assignment_id).first()
#             if db_assignment is None:
#                 return None

#             # Update fields
#             for var, value in vars(assignment).items():
#                 if var not in ['tenancy_ids', 'assigned_employee_ids']:
#                     setattr(db_assignment, var, value) if value else None

#             # Update tenancies if they differ from existing ones
#             existing_tenancy_ids = {tenancy.id for tenancy in db_assignment.tenancies}
#             new_tenancy_ids = set(assignment.tenancy_ids)
#             if existing_tenancy_ids != new_tenancy_ids:
#                 db_assignment.tenancies = []
#                 for tenancy_id in new_tenancy_ids:
#                     tenancy = self.db_session.query(TenancyModel).get(tenancy_id)
#                     if tenancy:
#                         db_assignment.tenancies.append(tenancy)

#             # Update responsible employees if they differ from existing ones
#             existing_employee_ids = {employee.id for employee in db_assignment.responsible_employees}
#             new_employee_ids = set(assignment.assigned_employee_ids)
#             if existing_employee_ids != new_employee_ids:
#                 db_assignment.responsible_employees = []
#                 for employee_id in new_employee_ids:
#                     employee = self.db_session.query(EmployeeModel).get(employee_id)
#                     if not employee:
#                         raise Exception(f"Employee with ID {employee_id} does not exist.")
#                     db_assignment.responsible_employees.append(employee)

#             self.db_session.commit()
#             self.db_session.refresh(db_assignment)

#             # Fetching the initiating user's full name
#             initiating_user = (
#                 self.db_session.query(EmployeeModel)
#                 .join(UserModel, UserModel.id == db_assignment.initiating_user_id)
#                 .filter(UserModel.id == db_assignment.initiating_user_id)
#                 .first()
#             )
#             if initiating_user:
#                 initiating_user_fullname = f"{initiating_user.first_name} {initiating_user.last_name}"
#                 db_assignment.initiating_user_fullname = initiating_user_fullname

#             logging_helper.log_info(f"Assignment with ID {assignment_id} updated successfully")
#             return db_assignment
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error updating assignment with ID {assignment_id}: {e}")
#             raise Exception(f"Failed to update assignment: {str(e)}")

#     def delete_assignment(self, assignment_id: int, user_id: Optional[int] = None) -> Optional[AssignmentModel]:
#         try:
#             db_assignment = self.db_session.query(AssignmentModel).filter(AssignmentModel.id == assignment_id).first()
#             if db_assignment is None:
#                 raise Exception(f"The Assignment with the ID: {assignment_id} does not exist")
#             self.db_session.delete(db_assignment)
#             self.db_session.commit()
#             logging_helper.log_info(f"Assignment with ID {assignment_id} deleted successfully")
#             return db_assignment
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error deleting assignment with ID {assignment_id}: {e}")
#             raise Exception(f"Failed to delete assignment: {str(e)}")


#     def extend_assignment_due_date(self, assignment_id: int, new_end_date: date, user_id: Optional[int] = None) -> Optional[AssignmentModel]:
#         try:
#             db_assignment = self.db_session.query(AssignmentModel).filter(AssignmentModel.id == assignment_id).first()
#             if db_assignment is None:
#                 raise Exception(f"Assignment with ID {assignment_id} does not exist")
            
#             if new_end_date < db_assignment.end_date:
#                 raise Exception(f"New end date {new_end_date} cannot be earlier than the current end date {db_assignment.end_date}")

#             old_end_date = db_assignment.end_date
#             db_assignment.end_date = new_end_date
#             self.db_session.commit()
#             self.db_session.refresh(db_assignment)

#             # Fetching the initiating user's full name
#             initiating_user = (
#                 self.db_session.query(EmployeeModel)
#                 .join(UserModel, UserModel.id == db_assignment.initiating_user_id)
#                 .filter(UserModel.id == db_assignment.initiating_user_id)
#                 .first()
#             )
#             if initiating_user:
#                 initiating_user_fullname = f"{initiating_user.first_name} {initiating_user.last_name}"
#                 db_assignment.initiating_user_fullname = initiating_user_fullname

#             logging_helper.log_info(f"Assignment with ID {assignment_id} due date extended to {new_end_date}")

#             # Log audit information
#             changes = {"old_end_date": old_end_date, "new_end_date": new_end_date}
#             logging_helper.log_audit(
#                 self.db_session,
#                 user_id,
#                 ActionEnum.UPDATE,
#                 "Assignment",
#                 assignment_id,
#                 changes
#             )

#             return db_assignment
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error extending due date for assignment with ID {assignment_id}: {e}")
#             raise Exception(f"Failed to extend assignment due date: {str(e)}")


#     def substitute_employee(self, assignment_id: int, old_employee_id: int, new_employee_id: int, user_id: Optional[int] = None) -> Optional[AssignmentModel]:
#         try:
#             logging_helper.log_info("Accessing - Substitute Employee in Assignment - Endpoint")
#             db_assignment = self.db_session.query(AssignmentModel).filter(AssignmentModel.id == assignment_id).first()
#             if db_assignment is None:
#                 raise Exception(f"Assignment with ID {assignment_id} does not exist")

#             old_employee = self.db_session.query(EmployeeModel).get(old_employee_id)
#             new_employee = self.db_session.query(EmployeeModel).get(new_employee_id)
#             if not old_employee:
#                 raise Exception(f"Old employee with ID {old_employee_id} does not exist")
#             if not new_employee:
#                 raise Exception(f"New employee with ID {new_employee_id} does not exist")

#             if old_employee in db_assignment.responsible_employees:
#                 # Remove old employee from assignment
#                 db_assignment.responsible_employees.remove(old_employee)

#                 # Add new employee to assignment
#                 db_assignment.responsible_employees.append(new_employee)

#                 # Remove old employee from all tasks associated with this assignment
#                 tasks = self.db_session.query(TaskModel).filter(TaskModel.assignment_id == assignment_id).all()
#                 for task in tasks:
#                     if old_employee in task.employees:
#                         # Log the task and employee association before attempting to delete
#                         logging_helper.log_info(f"Removing old employee {old_employee_id} from task {task.id}")

#                         # Delete old employee association if it exists
#                         delete_stmt = task_employee_association.delete().where(
#                             (task_employee_association.c.task_id == task.id) &
#                             (task_employee_association.c.employee_id == old_employee_id)
#                         )
#                         delete_result = self.db_session.execute(delete_stmt)
#                         logging_helper.log_info(f"Delete result: {delete_result.rowcount} rows affected")

#                         # Add new employee association if they exist
#                         insert_stmt = task_employee_association.insert().values(task_id=task.id, employee_id=new_employee_id)
#                         self.db_session.execute(insert_stmt)

#                 self.db_session.commit()
#                 self.db_session.refresh(db_assignment)

#                 # Fetching the initiating user's full name
#                 initiating_user = (
#                     self.db_session.query(EmployeeModel)
#                     .join(UserModel, UserModel.id == db_assignment.initiating_user_id)
#                     .filter(UserModel.id == db_assignment.initiating_user_id)
#                     .first()
#                 )
#                 if initiating_user:
#                     initiating_user_fullname = f"{initiating_user.first_name} {initiating_user.last_name}"
#                     db_assignment.initiating_user_fullname = initiating_user_fullname

#                 logging_helper.log_info(f"Employee {old_employee_id} substituted with {new_employee_id} for assignment ID {assignment_id}")
#                 return db_assignment
#             else:
#                 logging_helper.log_error(f"Error substituting employee: Employee {old_employee_id} not found in assignment ID {assignment_id}")
#                 return None
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error substituting employee in assignment with ID {assignment_id}: {e}")
#             self.db_session.rollback()
#             raise Exception(f"Failed to substitute employee: {str(e)}")

        

#     def get_assignments(self, skip: int = 0, limit: int = 10) -> List[AssignmentResponse]:
#         try:
#             assignments = (
#                 self.db_session.query(AssignmentModel)
#                 .join(UserModel, UserModel.id == AssignmentModel.initiating_user_id)
#                 .join(EmployeeModel, EmployeeModel.id == UserModel.employee_id)
#                 .add_columns(
#                     AssignmentModel.id,
#                     AssignmentModel.name,
#                     AssignmentModel.description,
#                     AssignmentModel.start_date,
#                     AssignmentModel.end_date,
#                     AssignmentModel.status,
#                     AssignmentModel.assignment_lead_id,
#                     AssignmentModel.is_active,
#                     AssignmentModel.date_created,
#                     AssignmentModel.date_updated,
#                     AssignmentModel.date_deleted,
#                     EmployeeModel.first_name.label('initiating_user_first_name'),
#                     EmployeeModel.last_name.label('initiating_user_last_name')
#                 )
#                 .offset(skip)
#                 .limit(limit)
#                 .all()
#             )
#             logging_helper.log_info("Successfully fetched all assignments")

#             result = []
#             for assignment in assignments:
#                 initiating_user_fullname = f"{assignment.initiating_user_first_name} {assignment.initiating_user_last_name}"
#                 assignment_data = AssignmentResponse(
#                     id=assignment.id,
#                     name=assignment.name,
#                     description=assignment.description,
#                     start_date=assignment.start_date,
#                     end_date=assignment.end_date,
#                     status=assignment.status,
#                     assignment_lead_id=assignment.assignment_lead_id,
#                     initiating_user_fullname=initiating_user_fullname,
#                     is_active=assignment.is_active,
#                     date_created=assignment.date_created.date() if isinstance(assignment.date_created, datetime) else assignment.date_created,
#                     date_updated=assignment.date_updated.date() if assignment.date_updated and isinstance(assignment.date_updated, datetime) else assignment.date_updated,
#                     date_deleted=assignment.date_deleted.date() if assignment.date_deleted and isinstance(assignment.date_deleted, datetime) else assignment.date_deleted,
#                     tenancies=[tenancy.id for tenancy in self.db_session.query(TenancyModel).filter(TenancyModel.assignments.any(id=assignment.id)).all()],
#                     responsible_employees=[employee.id for employee in self.db_session.query(EmployeeModel).filter(EmployeeModel.assignments.any(id=assignment.id)).all()]
#                 )
#                 result.append(assignment_data)

#             return result
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error retrieving assignments: {e}")
#             raise Exception("Failed to fetch assignments")


#     def get_assignment(self, assignment_id: int) -> Optional[AssignmentResponse]:
#         try:
#             result = (
#                 self.db_session.query(
#                     AssignmentModel,
#                     EmployeeModel.first_name.label('initiating_user_first_name'),
#                     EmployeeModel.last_name.label('initiating_user_last_name')
#                 )
#                 .filter(AssignmentModel.id == assignment_id)
#                 .join(UserModel, UserModel.id == AssignmentModel.initiating_user_id)
#                 .join(EmployeeModel, EmployeeModel.id == UserModel.employee_id)
#                 .first()
#             )
#             if result:
#                 assignment, initiating_user_first_name, initiating_user_last_name = result
#                 logging_helper.log_info(f"Assignment with ID {assignment_id} retrieved successfully")
#                 initiating_user_fullname = f"{initiating_user_first_name} {initiating_user_last_name}"
#                 return AssignmentResponse(
#                     id=assignment.id,
#                     name=assignment.name,
#                     description=assignment.description,
#                     start_date=assignment.start_date,
#                     end_date=assignment.end_date,
#                     status=assignment.status,
#                     assignment_lead_id=assignment.assignment_lead_id,
#                     initiating_user_fullname=initiating_user_fullname,
#                     is_active=assignment.is_active,
#                     date_created=assignment.date_created.date() if isinstance(assignment.date_created, datetime) else assignment.date_created,
#                     date_updated=assignment.date_updated.date() if assignment.date_updated and isinstance(assignment.date_updated, datetime) else assignment.date_updated,
#                     date_deleted=assignment.date_deleted.date() if assignment.date_deleted and isinstance(assignment.date_deleted, datetime) else assignment.date_deleted,
#                     tenancies=[tenancy.id for tenancy in assignment.tenancies],
#                     responsible_employees=[employee.id for employee in assignment.responsible_employees]
#                 )
#             return None
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error retrieving assignment with ID {assignment_id}: {e}")
#             raise Exception(f"Failed to retrieve assignment: {str(e)}")



#     def get_employees_assigned_to_assignment(self, assignment_id: int) -> dict:
#         try:
#             result = (
#                 self.db_session.query(
#                     AssignmentModel,
#                     EmployeeModel.first_name.label('initiating_user_first_name'),
#                     EmployeeModel.last_name.label('initiating_user_last_name')
#                 )
#                 .filter(AssignmentModel.id == assignment_id)
#                 .join(UserModel, UserModel.id == AssignmentModel.initiating_user_id)
#                 .join(EmployeeModel, EmployeeModel.id == UserModel.employee_id)
#                 .first()
#             )
#             if not result:
#                 logging_helper.log_error(f"Assignment with ID {assignment_id} not found")
#                 return {"assignment": None, "employees": []}

#             assignment, initiating_user_first_name, initiating_user_last_name = result
#             employees = assignment.responsible_employees
#             logging_helper.log_info(f"Retrieved {len(employees)} employees for assignment ID {assignment_id}")

#             employee_details = [
#                 {
#                     "id": employee.id,
#                     "fullname": f"{employee.first_name} {employee.last_name}",
#                     "phone_number": employee.phone_number,
#                 } for employee in employees
#             ]
#             assignment_lead_fullname = None
#             if assignment.assignment_lead:
#                 assignment_lead_fullname = f"{assignment.assignment_lead.first_name} {assignment.assignment_lead.last_name}"

#             initiating_user_fullname = f"{initiating_user_first_name} {initiating_user_last_name}"

#             assignment_details = {
#                 "id": assignment.id,
#                 "name": assignment.name,
#                 "description": assignment.description,
#                 "start_date": assignment.start_date,
#                 "end_date": assignment.end_date,
#                 "status": assignment.status,
#                 "assignment_lead_id": assignment.assignment_lead_id,
#                 "initiating_user_fullname": initiating_user_fullname,
#                 "is_active": assignment.is_active,
#                 "date_created": assignment.date_created.date() if isinstance(assignment.date_created, datetime) else assignment.date_created,
#                 "date_updated": assignment.date_updated.date() if assignment.date_updated and isinstance(assignment.date_updated, datetime) else assignment.date_updated,
#                 "date_deleted": assignment.date_deleted.date() if assignment.date_deleted and isinstance(assignment.date_deleted, datetime) else assignment.date_deleted,
#                 "tenancies": [tenancy.id for tenancy in assignment.tenancies],
#                 "responsible_employees": [employee.id for employee in assignment.responsible_employees]
#             }

#             return {"assignment": assignment_details, "employees": employee_details}
#         except Exception as e:
#             logging_helper.log_error(f"Failed to fetch employees for assignment ID {assignment_id}: {e}")
#             raise Exception(f"Failed to fetch employees for assignment ID {assignment_id}: {str(e)}")


#     def get_assignments_hierarchy(self):
#         logging_helper.log_info("Fetching assignments hierarchy")
#         try:
#             assignments = self.db.query(AssignmentModel).all()
#             result = []
#             for assignment in assignments:
#                 assignment_data = {
#                     "id": assignment.id,
#                     "name": assignment.name,
#                     "description": assignment.description,
#                     "start_date": assignment.start_date.isoformat(),
#                     "end_date": assignment.end_date.isoformat() if assignment.end_date else None,
#                     "status": assignment.status,
#                     "comment": assignment.comment,
#                     "employees": [
#                         {
#                             "id": emp.id,
#                             "full_name": f"{emp.first_name} {emp.last_name}"
#                         } for emp in assignment.responsible_employees
#                     ],
#                     "milestones": [
#                         {
#                             "id": milestone.id,
#                             "name": milestone.name,
#                             "description": milestone.description,
#                             "due_date": milestone.due_date.isoformat(),
#                             "completion_date": milestone.completion_date.isoformat() if milestone.completion_date else None,
#                             "status": milestone.status,
#                             "comment": milestone.comment,
#                             "responsible_employee": {
#                                 "id": milestone.responsible_employee.id,
#                                 "full_name": f"{milestone.responsible_employee.first_name} {milestone.responsible_employee.last_name}"
#                             },
#                             "tasks": [
#                                 {
#                                     "id": task.id,
#                                     "description": task.description,
#                                     "due_date": task.due_date.isoformat() if task.due_date else None,
#                                     "status_id": task.status_id,
#                                     "comment": task.comment,
#                                     "employees": [
#                                         {
#                                             "id": emp.id,
#                                             "full_name": f"{emp.first_name} {emp.last_name}"
#                                         } for emp in task.employees
#                                     ]
#                                 } for task in milestone.tasks
#                             ]
#                         } for milestone in assignment.milestones
#                     ]
#                 }
#                 result.append(assignment_data)
#             return result
#         except Exception as e:
#             logging_helper.log_error(f"Failed to fetch assignments hierarchy: {str(e)}")
#             raise


#     def complete_assignment(self, assignment_id: int, user_id: Optional[int]) -> str:
#         try:
#             logging_helper.log_info(f"Completing assignment with ID: {assignment_id}")
#             db_assignment = self.db_session.query(AssignmentModel).filter(AssignmentModel.id == assignment_id).first()
#             if db_assignment is None:
#                 raise Exception(f"Assignment with ID {assignment_id} does not exist")

#             # Check if all milestones are completed
#             milestones = db_assignment.milestones
#             if not all(milestone.is_completed for milestone in milestones):
#                 raise Exception("Cannot complete assignment as not all milestones are completed")

#             if db_assignment.is_completed:
#                 raise Exception(f"Assignment with ID {assignment_id} is already completed")

#             db_assignment.is_completed = True
#             db_assignment.date_completed = datetime.utcnow()
#             self.db_session.commit()
#             logging_helper.log_info(f"Assignment with ID {assignment_id} marked as completed")
#             return f"Assignment with ID {assignment_id} has been completed successfully"
#         except Exception as e:
#             logging_helper.log_error(f"Failed to complete assignment with ID {assignment_id}: {str(e)}")
#             self.db_session.rollback()
#             raise Exception(f"Failed to complete assignment: {str(e)}")
        

#     def get_employees_for_assignment(self, assignment_id: int) -> Dict:
#         logging_helper.log_info(f"Fetching assignment details for assignment ID: {assignment_id}")
#         try:
#             assignment = self.db_session.query(AssignmentModel).filter(AssignmentModel.id == assignment_id).first()
#             if not assignment:
#                 logging_helper.log_error(f"Assignment not found with ID: {assignment_id}")
#                 raise Exception(f"Assignment not found with ID: {assignment_id}")

#             responsible_employees = assignment.responsible_employees
#             employee_details = [
#                 {
#                     "id": emp.id,
#                     "full_name": f"{emp.first_name} {emp.last_name}"
#                 }
#                 for emp in responsible_employees
#             ]

#             result = {
#                 "assignment_id": assignment.id,
#                 "responsible_employees": employee_details
#             }

#             logging_helper.log_info(f"Fetched assignment details successfully for assignment ID: {assignment_id}")
#             return result
#         except Exception as e:
#             logging_helper.log_error(f"Failed to fetch assignment details: {str(e)}")
#             raise Exception(f"Failed to fetch assignment details")


#     def add_employee_to_assignment(self, assignment_id: int, employee_id: int, user_id: Optional[int] = None) -> dict:
#         try:
#             logging_helper.log_info(f"Adding employee with ID {employee_id} to assignment ID {assignment_id}")
            
#             db_assignment = self.db_session.query(AssignmentModel).filter(AssignmentModel.id == assignment_id).first()
#             if not db_assignment:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Assignment with ID {assignment_id} does not exist")
            
#             employee = self.db_session.query(EmployeeModel).get(employee_id)
#             if not employee:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee with ID {employee_id} does not exist")
            
#             if employee in db_assignment.responsible_employees:
#                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Employee with ID {employee_id} is already assigned to assignment ID {assignment_id}")

#             db_assignment.responsible_employees.append(employee)
#             self.db_session.commit()

#             logging_helper.log_info(f"Employee with ID {employee_id} added to assignment ID {assignment_id}")
#             return {"message": f"The employee with ID: {employee_id} added to the Assignment with ID: {assignment_id} successfully"}
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error adding employee to assignment with ID {assignment_id}: {e}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to add employee to assignment: {str(e)}")



from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict
from models.all_models import Assignment as AssignmentModel, Employee as EmployeeModel, Tenancy as TenancyModel, User as UserModel, ActionEnum, Task as TaskModel, task_employee_association
from schemas.assignment_schemas import AssignmentCreate, AssignmentUpdate, AssignmentResponse, AssignmentWithEmployees
from logging_helpers import logging_helper
from datetime import date, datetime
from auth.email import (
    notify_assignment_creation,
    notify_initiator_about_assignment,
    generate_message_id
)

class AssignmentRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_assignment(
        self, 
        assignment: AssignmentCreate, 
        user_id: Optional[int], 
        background_tasks: BackgroundTasks
    ) -> AssignmentModel:
        """
        Creates a new assignment, adds it to the database, and sends email notifications.

        Args:
            assignment (AssignmentCreate): The data for creating the assignment.
            user_id (Optional[int]): The ID of the user initiating the assignment.
            background_tasks (BackgroundTasks): Background tasks for sending emails.

        Returns:
            AssignmentModel: The created assignment.

        Raises:
            Exception: If the assignment creation fails.
        """
        try:
            db_assignment = AssignmentModel(
                name=assignment.name,
                description=assignment.description,
                start_date=assignment.start_date,
                end_date=assignment.end_date,
                status=assignment.status,
                assignment_lead_id=assignment.assignment_lead_id,
                initiating_user_id=user_id
            )

            for tenancy_id in assignment.tenancy_ids:
                tenancy = self.db_session.query(TenancyModel).get(tenancy_id)
                if tenancy:
                    db_assignment.tenancies.append(tenancy)

            for employee_id in assignment.assigned_employee_ids:
                employee = self.db_session.query(EmployeeModel).get(employee_id)
                if not employee:
                    raise Exception(f"Employee with ID {employee_id} does not exist.")
                db_assignment.responsible_employees.append(employee)

            self.db_session.add(db_assignment)
            self.db_session.commit()
            self.db_session.refresh(db_assignment)

            # Fetching the initiating user's full name
            initiating_user = (
                self.db_session.query(EmployeeModel)
                .join(UserModel, UserModel.id == db_assignment.initiating_user_id)
                .filter(UserModel.id == db_assignment.initiating_user_id)
                .first()
            )
            if initiating_user:
                initiating_user_fullname = f"{initiating_user.first_name} {initiating_user.last_name}"
                db_assignment.initiating_user_fullname = initiating_user_fullname

            logging_helper.log_info(f"Assignment {db_assignment.name} created successfully")

            # Send email notifications
            recipient_emails = [
                (employee.first_name, employee.employee_email)
                for employee in db_assignment.responsible_employees
                if employee.employee_email
            ]

            background_tasks.add_task(
                notify_assignment_creation,
                recipient_emails,
                db_assignment.name,
                initiating_user_fullname
            )

            background_tasks.add_task(
                notify_initiator_about_assignment,
                initiating_user.employee_email,
                initiating_user_fullname,
                db_assignment.name,
                db_assignment.status
            )

            return db_assignment
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error creating assignment: {e}")
            raise Exception(f"Failed to create assignment: {str(e)}")

    def update_assignment(self, assignment_id: int, assignment: AssignmentUpdate, user_id: Optional[int] = None) -> Optional[AssignmentModel]:
        """
        Updates an existing assignment with the provided data.

        Args:
            assignment_id (int): The ID of the assignment to update.
            assignment (AssignmentUpdate): The updated data for the assignment.
            user_id (Optional[int]): The ID of the user initiating the update.

        Returns:
            Optional[AssignmentModel]: The updated assignment if found, None otherwise.

        Raises:
            Exception: If the assignment update fails.
        """
        try:
            db_assignment = self.db_session.query(AssignmentModel).filter(AssignmentModel.id == assignment_id).first()
            if db_assignment is None:
                return None

            # Update fields
            for var, value in vars(assignment).items():
                if var not in ['tenancy_ids', 'assigned_employee_ids']:
                    setattr(db_assignment, var, value) if value else None

            # Update tenancies if they differ from existing ones
            existing_tenancy_ids = {tenancy.id for tenancy in db_assignment.tenancies}
            new_tenancy_ids = set(assignment.tenancy_ids)
            if existing_tenancy_ids != new_tenancy_ids:
                db_assignment.tenancies = []
                for tenancy_id in new_tenancy_ids:
                    tenancy = self.db_session.query(TenancyModel).get(tenancy_id)
                    if tenancy:
                        db_assignment.tenancies.append(tenancy)

            # Update responsible employees if they differ from existing ones
            existing_employee_ids = {employee.id for employee in db_assignment.responsible_employees}
            new_employee_ids = set(assignment.assigned_employee_ids)
            if existing_employee_ids != new_employee_ids:
                db_assignment.responsible_employees = []
                for employee_id in new_employee_ids:
                    employee = self.db_session.query(EmployeeModel).get(employee_id)
                    if not employee:
                        raise Exception(f"Employee with ID {employee_id} does not exist.")
                    db_assignment.responsible_employees.append(employee)

            self.db_session.commit()
            self.db_session.refresh(db_assignment)

            # Fetching the initiating user's full name
            initiating_user = (
                self.db_session.query(EmployeeModel)
                .join(UserModel, UserModel.id == db_assignment.initiating_user_id)
                .filter(UserModel.id == db_assignment.initiating_user_id)
                .first()
            )
            if initiating_user:
                initiating_user_fullname = f"{initiating_user.first_name} {initiating_user.last_name}"
                db_assignment.initiating_user_fullname = initiating_user_fullname

            logging_helper.log_info(f"Assignment with ID {assignment_id} updated successfully")
            return db_assignment
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error updating assignment with ID {assignment_id}: {e}")
            raise Exception(f"Failed to update assignment: {str(e)}")

    def delete_assignment(self, assignment_id: int, user_id: Optional[int] = None) -> Optional[AssignmentModel]:
        """
        Deletes an assignment by its ID.

        Args:
            assignment_id (int): The ID of the assignment to delete.
            user_id (Optional[int]): The ID of the user initiating the deletion.

        Returns:
            Optional[AssignmentModel]: The deleted assignment if found, None otherwise.

        Raises:
            Exception: If the assignment deletion fails.
        """
        try:
            db_assignment = self.db_session.query(AssignmentModel).filter(AssignmentModel.id == assignment_id).first()
            if db_assignment is None:
                raise Exception(f"The Assignment with the ID: {assignment_id} does not exist")
            self.db_session.delete(db_assignment)
            self.db_session.commit()
            logging_helper.log_info(f"Assignment with ID {assignment_id} deleted successfully")
            return db_assignment
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error deleting assignment with ID {assignment_id}: {e}")
            raise Exception(f"Failed to delete assignment: {str(e)}")

    def extend_assignment_due_date(self, assignment_id: int, new_end_date: date, user_id: Optional[int] = None) -> Optional[AssignmentModel]:
        """
        Extends the due date of an assignment.

        Args:
            assignment_id (int): The ID of the assignment to extend.
            new_end_date (date): The new end date for the assignment.
            user_id (Optional[int]): The ID of the user initiating the extension.

        Returns:
            Optional[AssignmentModel]: The updated assignment if found, None otherwise.

        Raises:
            Exception: If the assignment extension fails.
        """
        try:
            db_assignment = self.db_session.query(AssignmentModel).filter(AssignmentModel.id == assignment_id).first()
            if db_assignment is None:
                raise Exception(f"Assignment with ID {assignment_id} does not exist")
            
            if new_end_date < db_assignment.end_date:
                raise Exception(f"New end date {new_end_date} cannot be earlier than the current end date {db_assignment.end_date}")

            old_end_date = db_assignment.end_date
            db_assignment.end_date = new_end_date
            self.db_session.commit()
            self.db_session.refresh(db_assignment)

            # Fetching the initiating user's full name
            initiating_user = (
                self.db_session.query(EmployeeModel)
                .join(UserModel, UserModel.id == db_assignment.initiating_user_id)
                .filter(UserModel.id == db_assignment.initiating_user_id)
                .first()
            )
            if initiating_user:
                initiating_user_fullname = f"{initiating_user.first_name} {initiating_user.last_name}"
                db_assignment.initiating_user_fullname = initiating_user_fullname

            logging_helper.log_info(f"Assignment with ID {assignment_id} due date extended to {new_end_date}")

            # Log audit information
            changes = {"old_end_date": old_end_date, "new_end_date": new_end_date}
            logging_helper.log_audit(
                self.db_session,
                user_id,
                ActionEnum.UPDATE,
                "Assignment",
                assignment_id,
                changes
            )

            return db_assignment
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error extending due date for assignment with ID {assignment_id}: {e}")
            raise Exception(f"Failed to extend assignment due date: {str(e)}")

    def substitute_employee(self, assignment_id: int, old_employee_id: int, new_employee_id: int, user_id: Optional[int] = None) -> Optional[AssignmentModel]:
        """
        Substitutes an old employee with a new employee in an assignment and updates the tasks associated with the assignment.

        Args:
            assignment_id (int): The ID of the assignment.
            old_employee_id (int): The ID of the old employee to be substituted.
            new_employee_id (int): The ID of the new employee to substitute.
            user_id (Optional[int]): The ID of the user initiating the substitution.

        Returns:
            Optional[AssignmentModel]: The updated assignment if found, None otherwise.

        Raises:
            Exception: If the substitution fails.
        """
        try:
            logging_helper.log_info("Accessing - Substitute Employee in Assignment - Endpoint")
            db_assignment = self.db_session.query(AssignmentModel).filter(AssignmentModel.id == assignment_id).first()
            if db_assignment is None:
                raise Exception(f"Assignment with ID {assignment_id} does not exist")

            old_employee = self.db_session.query(EmployeeModel).get(old_employee_id)
            new_employee = self.db_session.query(EmployeeModel).get(new_employee_id)
            if not old_employee:
                raise Exception(f"Old employee with ID {old_employee_id} does not exist")
            if not new_employee:
                raise Exception(f"New employee with ID {new_employee_id} does not exist")

            if old_employee in db_assignment.responsible_employees:
                # Remove old employee from assignment
                db_assignment.responsible_employees.remove(old_employee)

                # Add new employee to assignment
                db_assignment.responsible_employees.append(new_employee)

                # Remove old employee from all tasks associated with this assignment
                tasks = self.db_session.query(TaskModel).filter(TaskModel.assignment_id == assignment_id).all()
                for task in tasks:
                    if old_employee in task.employees:
                        # Log the task and employee association before attempting to delete
                        logging_helper.log_info(f"Removing old employee {old_employee_id} from task {task.id}")

                        # Delete old employee association if it exists
                        delete_stmt = task_employee_association.delete().where(
                            (task_employee_association.c.task_id == task.id) &
                            (task_employee_association.c.employee_id == old_employee_id)
                        )
                        delete_result = self.db_session.execute(delete_stmt)
                        logging_helper.log_info(f"Delete result: {delete_result.rowcount} rows affected")

                        # Add new employee association if they exist
                        insert_stmt = task_employee_association.insert().values(task_id=task.id, employee_id=new_employee_id)
                        self.db_session.execute(insert_stmt)

                self.db_session.commit()
                self.db_session.refresh(db_assignment)

                # Fetching the initiating user's full name
                initiating_user = (
                    self.db_session.query(EmployeeModel)
                    .join(UserModel, UserModel.id == db_assignment.initiating_user_id)
                    .filter(UserModel.id == db_assignment.initiating_user_id)
                    .first()
                )
                if initiating_user:
                    initiating_user_fullname = f"{initiating_user.first_name} {initiating_user.last_name}"
                    db_assignment.initiating_user_fullname = initiating_user_fullname

                logging_helper.log_info(f"Employee {old_employee_id} substituted with {new_employee_id} for assignment ID {assignment_id}")
                return db_assignment
            else:
                logging_helper.log_error(f"Error substituting employee: Employee {old_employee_id} not found in assignment ID {assignment_id}")
                return None
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error substituting employee in assignment with ID {assignment_id}: {e}")
            self.db_session.rollback()
            raise Exception(f"Failed to substitute employee: {str(e)}")

    def get_assignments(self, skip: int = 0, limit: int = 10) -> List[AssignmentResponse]:
        """
        Retrieves a list of assignments with pagination.

        Args:
            skip (int): The number of records to skip.
            limit (int): The maximum number of records to return.

        Returns:
            List[AssignmentResponse]: A list of assignments.

        Raises:
            Exception: If fetching the assignments fails.
        """
        try:
            assignments = (
                self.db_session.query(AssignmentModel)
                .join(UserModel, UserModel.id == AssignmentModel.initiating_user_id)
                .join(EmployeeModel, EmployeeModel.id == UserModel.employee_id)
                .add_columns(
                    AssignmentModel.id,
                    AssignmentModel.name,
                    AssignmentModel.description,
                    AssignmentModel.start_date,
                    AssignmentModel.end_date,
                    AssignmentModel.status,
                    AssignmentModel.assignment_lead_id,
                    AssignmentModel.is_active,
                    AssignmentModel.date_created,
                    AssignmentModel.date_updated,
                    AssignmentModel.date_deleted,
                    EmployeeModel.first_name.label('initiating_user_first_name'),
                    EmployeeModel.last_name.label('initiating_user_last_name')
                )
                .offset(skip)
                .limit(limit)
                .all()
            )
            logging_helper.log_info("Successfully fetched all assignments")

            result = []
            for assignment in assignments:
                initiating_user_fullname = f"{assignment.initiating_user_first_name} {assignment.initiating_user_last_name}"
                assignment_data = AssignmentResponse(
                    id=assignment.id,
                    name=assignment.name,
                    description=assignment.description,
                    start_date=assignment.start_date,
                    end_date=assignment.end_date,
                    status=assignment.status,
                    assignment_lead_id=assignment.assignment_lead_id,
                    initiating_user_fullname=initiating_user_fullname,
                    is_active=assignment.is_active,
                    date_created=assignment.date_created.date() if isinstance(assignment.date_created, datetime) else assignment.date_created,
                    date_updated=assignment.date_updated.date() if assignment.date_updated and isinstance(assignment.date_updated, datetime) else assignment.date_updated,
                    date_deleted=assignment.date_deleted.date() if assignment.date_deleted and isinstance(assignment.date_deleted, datetime) else assignment.date_deleted,
                    tenancies=[tenancy.id for tenancy in self.db_session.query(TenancyModel).filter(TenancyModel.assignments.any(id=assignment.id)).all()],
                    responsible_employees=[employee.id for employee in self.db_session.query(EmployeeModel).filter(EmployeeModel.assignments.any(id=assignment.id)).all()]
                )
                result.append(assignment_data)

            return result
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error retrieving assignments: {e}")
            raise Exception("Failed to fetch assignments")

    def get_assignment(self, assignment_id: int) -> Optional[AssignmentResponse]:
        """
        Retrieves a single assignment by its ID.

        Args:
            assignment_id (int): The ID of the assignment to retrieve.

        Returns:
            Optional[AssignmentResponse]: The assignment if found, None otherwise.

        Raises:
            Exception: If fetching the assignment fails.
        """
        try:
            result = (
                self.db_session.query(
                    AssignmentModel,
                    EmployeeModel.first_name.label('initiating_user_first_name'),
                    EmployeeModel.last_name.label('initiating_user_last_name')
                )
                .filter(AssignmentModel.id == assignment_id)
                .join(UserModel, UserModel.id == AssignmentModel.initiating_user_id)
                .join(EmployeeModel, EmployeeModel.id == UserModel.employee_id)
                .first()
            )
            if result:
                assignment, initiating_user_first_name, initiating_user_last_name = result
                logging_helper.log_info(f"Assignment with ID {assignment_id} retrieved successfully")
                initiating_user_fullname = f"{initiating_user_first_name} {initiating_user_last_name}"
                return AssignmentResponse(
                    id=assignment.id,
                    name=assignment.name,
                    description=assignment.description,
                    start_date=assignment.start_date,
                    end_date=assignment.end_date,
                    status=assignment.status,
                    assignment_lead_id=assignment.assignment_lead_id,
                    initiating_user_fullname=initiating_user_fullname,
                    is_active=assignment.is_active,
                    date_created=assignment.date_created.date() if isinstance(assignment.date_created, datetime) else assignment.date_created,
                    date_updated=assignment.date_updated.date() if assignment.date_updated and isinstance(assignment.date_updated, datetime) else assignment.date_updated,
                    date_deleted=assignment.date_deleted.date() if assignment.date_deleted and isinstance(assignment.date_deleted, datetime) else assignment.date_deleted,
                    tenancies=[tenancy.id for tenancy in assignment.tenancies],
                    responsible_employees=[employee.id for employee in assignment.responsible_employees]
                )
            return None
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error retrieving assignment with ID {assignment_id}: {e}")
            raise Exception(f"Failed to retrieve assignment: {str(e)}")

    def get_employees_assigned_to_assignment(self, assignment_id: int) -> dict:
        """
        Retrieves the employees assigned to an assignment.

        Args:
            assignment_id (int): The ID of the assignment.

        Returns:
            dict: A dictionary containing assignment details and the assigned employees.

        Raises:
            Exception: If fetching the employees fails.
        """
        try:
            result = (
                self.db_session.query(
                    AssignmentModel,
                    EmployeeModel.first_name.label('initiating_user_first_name'),
                    EmployeeModel.last_name.label('initiating_user_last_name')
                )
                .filter(AssignmentModel.id == assignment_id)
                .join(UserModel, UserModel.id == AssignmentModel.initiating_user_id)
                .join(EmployeeModel, EmployeeModel.id == UserModel.employee_id)
                .first()
            )
            if not result:
                logging_helper.log_error(f"Assignment with ID {assignment_id} not found")
                return {"assignment": None, "employees": []}

            assignment, initiating_user_first_name, initiating_user_last_name = result
            employees = assignment.responsible_employees
            logging_helper.log_info(f"Retrieved {len(employees)} employees for assignment ID {assignment_id}")

            employee_details = [
                {
                    "id": employee.id,
                    "fullname": f"{employee.first_name} {employee.last_name}",
                    "phone_number": employee.phone_number,
                } for employee in employees
            ]
            assignment_lead_fullname = None
            if assignment.assignment_lead:
                assignment_lead_fullname = f"{assignment.assignment_lead.first_name} {assignment.assignment_lead.last_name}"

            initiating_user_fullname = f"{initiating_user_first_name} {initiating_user_last_name}"

            assignment_details = {
                "id": assignment.id,
                "name": assignment.name,
                "description": assignment.description,
                "start_date": assignment.start_date,
                "end_date": assignment.end_date,
                "status": assignment.status,
                "assignment_lead_id": assignment.assignment_lead_id,
                "initiating_user_fullname": initiating_user_fullname,
                "is_active": assignment.is_active,
                "date_created": assignment.date_created.date() if isinstance(assignment.date_created, datetime) else assignment.date_created,
                "date_updated": assignment.date_updated.date() if assignment.date_updated and isinstance(assignment.date_updated, datetime) else assignment.date_updated,
                "date_deleted": assignment.date_deleted.date() if assignment.date_deleted and isinstance(assignment.date_deleted, datetime) else assignment.date_deleted,
                "tenancies": [tenancy.id for tenancy in assignment.tenancies],
                "responsible_employees": [employee.id for employee in assignment.responsible_employees]
            }

            return {"assignment": assignment_details, "employees": employee_details}
        except Exception as e:
            logging_helper.log_error(f"Failed to fetch employees for assignment ID {assignment_id}: {e}")
            raise Exception(f"Failed to fetch employees for assignment ID {assignment_id}: {str(e)}")

    def get_assignments_hierarchy(self):
        """
        Retrieves the hierarchy of assignments, including milestones, tasks, and employees.

        Returns:
            list: A list of assignments with their hierarchy details.

        Raises:
            Exception: If fetching the hierarchy fails.
        """
        logging_helper.log_info("Fetching assignments hierarchy")
        try:
            assignments = self.db.query(AssignmentModel).all()
            result = []
            for assignment in assignments:
                assignment_data = {
                    "id": assignment.id,
                    "name": assignment.name,
                    "description": assignment.description,
                    "start_date": assignment.start_date.isoformat(),
                    "end_date": assignment.end_date.isoformat() if assignment.end_date else None,
                    "status": assignment.status,
                    "comment": assignment.comment,
                    "employees": [
                        {
                            "id": emp.id,
                            "full_name": f"{emp.first_name} {emp.last_name}"
                        } for emp in assignment.responsible_employees
                    ],
                    "milestones": [
                        {
                            "id": milestone.id,
                            "name": milestone.name,
                            "description": milestone.description,
                            "due_date": milestone.due_date.isoformat(),
                            "completion_date": milestone.completion_date.isoformat() if milestone.completion_date else None,
                            "status": milestone.status,
                            "comment": milestone.comment,
                            "responsible_employee": {
                                "id": milestone.responsible_employee.id,
                                "full_name": f"{milestone.responsible_employee.first_name} {milestone.responsible_employee.last_name}"
                            },
                            "tasks": [
                                {
                                    "id": task.id,
                                    "description": task.description,
                                    "due_date": task.due_date.isoformat() if task.due_date else None,
                                    "status_id": task.status_id,
                                    "comment": task.comment,
                                    "employees": [
                                        {
                                            "id": emp.id,
                                            "full_name": f"{emp.first_name} {emp.last_name}"
                                        } for emp in task.employees
                                    ]
                                } for task in milestone.tasks
                            ]
                        } for milestone in assignment.milestones
                    ]
                }
                result.append(assignment_data)
            return result
        except Exception as e:
            logging_helper.log_error(f"Failed to fetch assignments hierarchy: {str(e)}")
            raise


    def complete_assignment(self, assignment_id: int, user_id: Optional[int]) -> str:
        """
        Marks an assignment as completed if all milestones are completed.

        Args:
            assignment_id (int): The ID of the assignment to complete.
            user_id (Optional[int]): The ID of the user initiating the completion.

        Returns:
            str: A success message.

        Raises:
            Exception: If the assignment completion fails.
        """
        try:
            logging_helper.log_info(f"Completing assignment with ID: {assignment_id}")
            db_assignment = self.db_session.query(AssignmentModel).filter(AssignmentModel.id == assignment_id).first()
            if db_assignment is None:
                raise Exception(f"Assignment with ID {assignment_id} does not exist")

            # Check if all milestones are completed
            milestones = db_assignment.milestones
            if not all(milestone.is_completed for milestone in milestones):
                raise Exception("Cannot complete assignment as not all milestones are completed")

            if db_assignment.is_completed:
                raise Exception(f"Assignment with ID {assignment_id} is already completed")

            db_assignment.is_completed = True
            db_assignment.date_completed = datetime.utcnow()
            self.db_session.commit()
            logging_helper.log_info(f"Assignment with ID {assignment_id} marked as completed")
            return f"Assignment with ID {assignment_id} has been completed successfully"
        except Exception as e:
            logging_helper.log_error(f"Failed to complete assignment with ID {assignment_id}: {str(e)}")
            self.db_session.rollback()
            raise Exception(f"Failed to complete assignment: {str(e)}")


    def get_employees_for_assignment(self, assignment_id: int) -> Dict:
        """
        Retrieves the details of an assignment along with its responsible employees.

        Args:
            assignment_id (int): The ID of the assignment.

        Returns:
            Dict: A dictionary containing the assignment details and responsible employees.

        Raises:
            Exception: If fetching the details fails.
        """
        logging_helper.log_info(f"Fetching assignment details for assignment ID: {assignment_id}")
        try:
            assignment = self.db_session.query(AssignmentModel).filter(AssignmentModel.id == assignment_id).first()
            if not assignment:
                logging_helper.log_error(f"Assignment not found with ID: {assignment_id}")
                raise Exception(f"Assignment not found with ID: {assignment_id}")

            responsible_employees = assignment.responsible_employees
            employee_details = [
                {
                    "id": emp.id,
                    "full_name": f"{emp.first_name} {emp.last_name}"
                }
                for emp in responsible_employees
            ]

            result = {
                "assignment_id": assignment.id,
                "responsible_employees": employee_details
            }

            logging_helper.log_info(f"Fetched assignment details successfully for assignment ID: {assignment_id}")
            return result
        except Exception as e:
            logging_helper.log_error(f"Failed to fetch assignment details: {str(e)}")
            raise Exception(f"Failed to fetch assignment details")


    def add_employee_to_assignment(self, assignment_id: int, employee_id: int, user_id: Optional[int] = None) -> dict:
        """
        Adds an employee to an assignment.

        Args:
            assignment_id (int): The ID of the assignment.
            employee_id (int): The ID of the employee to add.
            user_id (Optional[int]): The ID of the user initiating the addition.

        Returns:
            dict: A success message.

        Raises:
            HTTPException: If the assignment or employee does not exist or if the employee is already assigned.
        """
        try:
            logging_helper.log_info(f"Adding employee with ID {employee_id} to assignment ID {assignment_id}")
            
            db_assignment = self.db_session.query(AssignmentModel).filter(AssignmentModel.id == assignment_id).first()
            if not db_assignment:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Assignment with ID {assignment_id} does not exist")
            
            employee = self.db_session.query(EmployeeModel).get(employee_id)
            if not employee:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee with ID {employee_id} does not exist")
            
            if employee in db_assignment.responsible_employees:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Employee with ID {employee_id} is already assigned to assignment ID {assignment_id}")

            db_assignment.responsible_employees.append(employee)
            self.db_session.commit()

            logging_helper.log_info(f"Employee with ID {employee_id} added to assignment ID {assignment_id}")
            return {"message": f"The employee with ID: {employee_id} added to the Assignment with ID: {assignment_id} successfully"}
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error adding employee to assignment with ID {assignment_id}: {e}")
            self.db_session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to add employee to assignment: {str(e)}")

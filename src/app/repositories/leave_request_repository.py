from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.all_models import LeaveRequest, Employee, Project
from datetime import date
from logging_helpers import logging_helper
from auth.email import send_email, notify_stage_email, generate_message_id

class LeaveRequestRepository:
    def __init__(self, db_session: Session):
        """
        Initialize the LeaveRequestRepository with a database session.

        Args:
            db_session (Session): SQLAlchemy session object.
        """
        self.db_session = db_session

    def get_hr_or_finance_staff(self, staff_type: str):
        """
        Retrieve the list of HR or Finance staff based on the specified type.

        Args:
            staff_type (str): The type of staff to retrieve ("HR" or "Finance").

        Returns:
            list[dict]: A list of dictionaries containing the full name, email, and phone number of the specified staff.

        Raises:
            ValueError: If an invalid staff_type is provided.
        """
        valid_staff_types = {
            "HR": "is_hr",
            "Finance": "is_finance",
        }

        if staff_type not in valid_staff_types:
            raise ValueError("Invalid staff type. Choose either 'HR' or 'Finance'.")

        try:
            staff_list = self.db_session.query(Employee).filter(getattr(Employee, valid_staff_types[staff_type]) == True).all()
            return [{"full_name": f"{staff.first_name} {staff.last_name}", "email": staff.employee_email, "phone_number": staff.phone_number} for staff in staff_list]

        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error occurred while retrieving {staff_type} staff: {e}")
            raise ValueError(f"An error occurred while retrieving the {staff_type} staff.")

    def assign_employee_to_special_responsibility(self, employee_id: int, responsibility: str, project_id: Optional[int] = None):
        """
        Assign an employee to a specific responsibility such as HR staff, Finance staff, Internal Auditor, Budget Holder, or Compliance staff.
        If assigning as a Budget Holder, the associated project must be specified.

        Args:
            employee_id (int): The ID of the employee to update.
            responsibility (str): The responsibility to assign to the employee. Options are "HR", "Finance", "Internal Auditor", "Budget Holder", or "Compliance".
            project_id (Optional[int]): The ID of the project to assign the employee as a budget holder.

        Returns:
            Employee: The updated Employee object if successful.

        Raises:
            ValueError: If an invalid responsibility is provided, if the employee is not found, or if assigning budget holder without a project.
            SQLAlchemyError: If there is an issue with the database operation.
        """
        valid_responsibilities = {
            "CEO":"is_ceo",
            "HR": "is_hr",
            "Finance": "is_finance",
            "Internal Auditor": "is_internal_auditor",
            "Budget Holder": "is_budget_holder",
            "Compliance": "is_compliance"
        }

        if responsibility not in valid_responsibilities:
            raise ValueError("Invalid responsibility. Choose either 'CEO', 'HR', 'Finance', 'Internal Auditor', 'Budget Holder', or 'Compliance'.")

        try:
            # Retrieve the employee
            employee = self.db_session.query(Employee).get(employee_id)
            if not employee:
                raise ValueError(f"Employee with ID {employee_id} not found.")

            if responsibility == "Budget Holder":
                if not project_id:
                    raise ValueError("Project ID must be provided when assigning a budget holder.")
                # Check if the project exists and assign the employee as budget holder
                project = self.db_session.query(Project).get(project_id)
                if not project:
                    raise ValueError(f"Project with ID {project_id} not found.")
                
                # Unassign any existing budget holder for this project
                current_budget_holder = self.db_session.query(Employee).filter(Employee.is_budget_holder == True, Employee.project_id == project_id).first()
                if current_budget_holder:
                    current_budget_holder.is_budget_holder = False

                # Assign the employee as the budget holder for the specified project
                employee.is_budget_holder = True
                employee.project_id = project_id

            else:
                # Reset all responsibility flags and set the specified responsibility flag to True
                for key in valid_responsibilities.values():
                    setattr(employee, key, False)
                setattr(employee, valid_responsibilities[responsibility], True)

            self.db_session.commit()
            self.db_session.refresh(employee)

            return employee

        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error occurred while assigning responsibility: {e}")
            raise ValueError(f"An error occurred while assigning the responsibility: {e}")


    def create_leave_request(self, employee_id: int, leave_data: dict):
        """
        Create a new leave request for an employee.

        Args:
            employee_id (int): The ID of the employee requesting leave.
            leave_data (dict): Dictionary containing the start date, end date, reason for leave, reliever ID, HR staff ID, and leave type ID.

        Returns:
            LeaveRequest: The newly created LeaveRequest object.

        Raises:
            SQLAlchemyError: If there is an issue with database operations.
            ValueError: If the leave duration exceeds the employee's leave entitlement.
        """
        try:
            # Extract fields specific to the LeaveRequest model
            leave_request_data = {
                'employee_id': employee_id,
                'start_date': leave_data.get('start_date'),
                'end_date': leave_data.get('end_date'),
                'reason': leave_data.get('reason'),
                'leave_type_id': leave_data.get('leave_type_id'),
                'status': 'Pending HR Approval',
                'hr_approval': False,
                'reliever_supervisor_approval': False,
                'finance_approval': False,
            }

            # Create a new leave request record
            new_leave_request = LeaveRequest(**leave_request_data)
            self.db_session.add(new_leave_request)
            self.db_session.commit()
            self.db_session.refresh(new_leave_request)

            # Notify the specified HR staff about the new leave request
            hr_staff_id = leave_data.get('hr_staff_id')
            if hr_staff_id:
                hr_staff = self.db_session.query(Employee).get(hr_staff_id)
                if hr_staff:
                    message_id = generate_message_id()
                    notify_stage_email(hr_staff.employee_email, "Leave Request Created", new_leave_request, hr_staff.employee_email, "HR Verification", message_id)

            logging_helper.log_info(f"Leave request created successfully for employee ID {employee_id}.")
            return new_leave_request

        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error occurred while creating leave request: {e}")
            self.db_session.rollback()
            raise
        except ValueError as e:
            logging_helper.log_error(f"Validation error: {e}")
            raise





    def get_leave_requests_by_employee(self, employee_id: int):
        """
        Retrieve all leave requests made by a specific employee.

        Args:
            employee_id (int): The ID of the employee.

        Returns:
            list[LeaveRequest]: A list of LeaveRequest objects.

        Raises:
            SQLAlchemyError: If there is an issue with database operations.
        """
        try:
            leave_requests = self.db_session.query(LeaveRequest).filter(LeaveRequest.employee_id == employee_id).all()
            logging_helper.log_info(f"Retrieved {len(leave_requests)} leave requests for employee ID {employee_id}.")
            return leave_requests
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error occurred while retrieving leave requests for employee ID {employee_id}: {e}")
            raise

    def update_leave_request_status(self, leave_request_id: int, status: str, approver_id: int):
        """
        Update the status of a leave request and notify the appropriate person.

        Args:
            leave_request_id (int): The ID of the leave request.
            status (str): The new status of the leave request (e.g., "HR Approved", "Reliever Approved", "Supervisor Approved", "Finance Approved", "CEO Approved").
            approver_id (int): The ID of the approver (HR staff, Reliever, Supervisor, etc.).

        Returns:
            LeaveRequest: The updated LeaveRequest object.

        Raises:
            SQLAlchemyError: If there is an issue with database operations.
        """
        try:
            leave_request = self.db_session.query(LeaveRequest).get(leave_request_id)
            if not leave_request:
                raise ValueError(f"Leave request with ID {leave_request_id} not found.")

            leave_request.status = status

            # Determine the next step based on the current status
            next_step_email = None
            next_stage = None
            message_id = generate_message_id()

            if status == "HR Approved":
                next_step_email = leave_request.reliever.employee_email
                next_stage = "Reliever Approval"
            elif status == "Reliever Approved":
                next_step_email = leave_request.employee.supervisor.employee_email
                next_stage = "Supervisor Approval"
            elif status == "Supervisor Approved":
                next_step_email = leave_request.financial_check_by.employee_email
                next_stage = "Finance Check"
            elif status == "Finance Approved":
                next_step_email = leave_request.employee.ceo.employee_email
                next_stage = "CEO Approval"
            elif status == "CEO Approved":
                next_step_email = leave_request.hr_verification_by.employee_email
                next_stage = "Archiving by HR"

            if next_step_email:
                notify_stage_email(next_step_email, f"Leave Request {next_stage}", leave_request.employee, leave_request.start_date, leave_request.end_date, next_stage, message_id)

            self.db_session.commit()
            self.db_session.refresh(leave_request)

            logging_helper.log_info(f"Leave request ID {leave_request_id} status updated to {status}.")
            return leave_request

        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error occurred while updating leave request status: {e}")
            self.db_session.rollback()
            raise

    def delete_leave_request(self, leave_request_id: int):
        """
        Delete a leave request from the database.

        Args:
            leave_request_id (int): The ID of the leave request to be deleted.

        Returns:
            bool: True if the leave request was successfully deleted, otherwise False.

        Raises:
            SQLAlchemyError: If there is an issue with database operations.
        """
        try:
            leave_request = self.db_session.query(LeaveRequest).get(leave_request_id)
            if not leave_request:
                raise ValueError(f"Leave request with ID {leave_request_id} not found.")

            self.db_session.delete(leave_request)
            self.db_session.commit()

            logging_helper.log_info(f"Leave request ID {leave_request_id} was deleted successfully.")
            return True

        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error occurred while deleting leave request: {e}")
            self.db_session.rollback()
            raise

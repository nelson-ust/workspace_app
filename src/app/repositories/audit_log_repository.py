# # repository/audit_log_repository.py
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from typing import List
# from models.all_models import AuditLog, User, Employee
# from logging_helpers import logging_helper
# from datetime import datetime
# from models.all_models import ActionEnum

# class AuditLogRepository:
#     def __init__(self, db_session: Session):
#         self.db_session = db_session

#     def get_audit_logs(self, skip: int = 0, limit: int = 100, user_id: int = None) -> List[dict]:
#         """
#         Fetch all audit logs with optional pagination, including user's full name, email, and phone number.
#         """
#         try:
#             audit_logs = (
#                 self.db_session.query(
#                     AuditLog,
#                     User.username.label("username"),
#                     User.email.label("email"),
#                     Employee.first_name.label("first_name"),
#                     Employee.last_name.label("last_name"),
#                     Employee.phone_number.label("phone_number"),
#                 )
#                 .join(User, AuditLog.user_id == User.id)
#                 .join(Employee, User.employee_id == Employee.id).order_by(AuditLog.date_created.desc())
#                 .offset(skip)
#                 .limit(limit)
#                 .all()
#             )

#             result = []
#             for audit_log, username, email, first_name, last_name, phone_number in audit_logs:
#                 result.append({
#                     "id": audit_log.id,
#                     "user_id": audit_log.user_id,
#                     "username": username,
#                     "email": email,
#                     "full_name": f"{first_name} {last_name}",
#                     "phone_number": phone_number,
#                     "action": audit_log.action,
#                     "model": audit_log.model,
#                     "model_id": audit_log.model_id,
#                     "changes": audit_log.changes,
#                     "date_created": audit_log.date_created,
#                 })

#             logging_helper.log_info("Successfully fetched all audit logs")
#             logging_helper.log_audit(self.db_session, user_id, ActionEnum.READ, "AuditLog", None, "get_audit_logs")
#             return result
#         except SQLAlchemyError as err:
#             logging_helper.log_error(f"Error retrieving audit logs: {err}")
#             raise Exception(f"Failed to retrieve audit logs: {str(err)}")

#     def get_audit_logs_by_date_range(self, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100, user_id: int = None) -> List[dict]:
#         """
#         Fetch audit logs by date range with optional pagination, including user's full name, email, and phone number.
#         """
#         try:
#             audit_logs = (
#                 self.db_session.query(
#                     AuditLog,
#                     User.username.label("username"),
#                     User.email.label("email"),
#                     Employee.first_name.label("first_name"),
#                     Employee.last_name.label("last_name"),
#                     Employee.phone_number.label("phone_number"),
#                 )
#                 .join(User, AuditLog.user_id == User.id)
#                 .join(Employee, User.employee_id == Employee.id)
#                 .filter(AuditLog.date_created >= start_date, AuditLog.date_created <= end_date).order_by(AuditLog.date_created.desc())
#                 .offset(skip)
#                 .limit(limit)
#                 .all()
                
#             )

#             result = []
#             for audit_log, username, email, first_name, last_name, phone_number in audit_logs:
#                 result.append({
#                     "id": audit_log.id,
#                     "user_id": audit_log.user_id,
#                     "username": username,
#                     "email": email,
#                     "full_name": f"{first_name} {last_name}",
#                     "phone_number": phone_number,
#                     "action": audit_log.action,
#                     "model": audit_log.model,
#                     "model_id": audit_log.model_id,
#                     "changes": audit_log.changes,
#                     "date_created": audit_log.date_created,
#                 })

#             logging_helper.log_info("Successfully fetched audit logs by date range")
#             logging_helper.log_audit(self.db_session, user_id, ActionEnum.READ, "AuditLog", None, f"get_audit_logs_by_date_range: {start_date} - {end_date}")
#             return result
#         except SQLAlchemyError as err:
#             logging_helper.log_error(f"Error retrieving audit logs by date range: {err}")
#             raise Exception(f"Failed to retrieve audit logs by date range: {str(err)}")




from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from models.all_models import AuditLog, User, Employee
from logging_helpers import logging_helper
from datetime import datetime
from models.all_models import ActionEnum

class AuditLogRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_audit_logs(self, skip: int = 0, limit: int = 100, user_id: int = None) -> List[dict]:
        """
        Fetch all audit logs with optional pagination, including user's full name, email, and phone number.
        
        Args:
            skip (int): The number of records to skip for pagination.
            limit (int): The maximum number of records to return for pagination.
            user_id (int, optional): The ID of the user performing the action.

        Returns:
            List[dict]: A list of audit log entries with user details.
        """
        try:
            # Query to fetch audit logs along with user and employee details
            audit_logs = (
                self.db_session.query(
                    AuditLog,
                    User.username.label("username"),
                    User.email.label("email"),
                    Employee.first_name.label("first_name"),
                    Employee.last_name.label("last_name"),
                    Employee.phone_number.label("phone_number"),
                )
                .join(User, AuditLog.user_id == User.id)
                .join(Employee, User.employee_id == Employee.id)
                .order_by(AuditLog.date_created.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )

            # Constructing the result list
            result = []
            for audit_log, username, email, first_name, last_name, phone_number in audit_logs:
                result.append({
                    "id": audit_log.id,
                    "user_id": audit_log.user_id,
                    "username": username,
                    "email": email,
                    "full_name": f"{first_name} {last_name}",
                    "phone_number": phone_number,
                    "action": audit_log.action,
                    "model": audit_log.model,
                    "model_id": audit_log.model_id,
                    "changes": audit_log.changes,
                    "date_created": audit_log.date_created,
                })

            logging_helper.log_info("Successfully fetched all audit logs")
            logging_helper.log_audit(self.db_session, user_id, ActionEnum.READ, "AuditLog", None, "get_audit_logs")
            return result
        except SQLAlchemyError as err:
            logging_helper.log_error(f"Error retrieving audit logs: {err}")
            raise Exception(f"Failed to retrieve audit logs: {str(err)}")

    def get_audit_logs_by_date_range(self, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100, user_id: int = None) -> List[dict]:
        """
        Fetch audit logs by date range with optional pagination, including user's full name, email, and phone number.
        
        Args:
            start_date (datetime): The start date for filtering audit logs.
            end_date (datetime): The end date for filtering audit logs.
            skip (int): The number of records to skip for pagination.
            limit (int): The maximum number of records to return for pagination.
            user_id (int, optional): The ID of the user performing the action.

        Returns:
            List[dict]: A list of audit log entries within the specified date range with user details.
        """
        try:
            # Query to fetch audit logs within the date range along with user and employee details
            audit_logs = (
                self.db_session.query(
                    AuditLog,
                    User.username.label("username"),
                    User.email.label("email"),
                    Employee.first_name.label("first_name"),
                    Employee.last_name.label("last_name"),
                    Employee.phone_number.label("phone_number"),
                )
                .join(User, AuditLog.user_id == User.id)
                .join(Employee, User.employee_id == Employee.id)
                .filter(AuditLog.date_created >= start_date, AuditLog.date_created <= end_date)
                .order_by(AuditLog.date_created.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )

            # Constructing the result list
            result = []
            for audit_log, username, email, first_name, last_name, phone_number in audit_logs:
                result.append({
                    "id": audit_log.id,
                    "user_id": audit_log.user_id,
                    "username": username,
                    "email": email,
                    "full_name": f"{first_name} {last_name}",
                    "phone_number": phone_number,
                    "action": audit_log.action,
                    "model": audit_log.model,
                    "model_id": audit_log.model_id,
                    "changes": audit_log.changes,
                    "date_created": audit_log.date_created,
                })

            logging_helper.log_info("Successfully fetched audit logs by date range")
            logging_helper.log_audit(self.db_session, user_id, ActionEnum.READ, "AuditLog", None, f"get_audit_logs_by_date_range: {start_date} - {end_date}")
            return result
        except SQLAlchemyError as err:
            logging_helper.log_error(f"Error retrieving audit logs by date range: {err}")
            raise Exception(f"Failed to retrieve audit logs by date range: {str(err)}")

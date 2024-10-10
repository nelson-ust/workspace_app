# logging_helpers.py

import logging
# import json
from logging_config import async_log
from sqlalchemy.orm import Session
from models.all_models import AuditLog, ActionEnum

class LoggingHelper:
    @async_log(level=logging.INFO)
    def log_info(self, message: str):
        return message
    
    @async_log(level=logging.ERROR)
    def log_error(self, message: str):
        return message

    def log_audit(self, db_session: Session, user_id: int, action: ActionEnum, model: str, model_id: int, changes: dict = None):
        """
        Logs an audit entry for the given action.
        """
        # If model_id is None, provide a default value, e.g., 0
        if model_id is None:
            model_id = 0  # We can choose a more appropriate default value later.

        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            model=model,
            model_id=model_id,
            changes=str(changes) if changes else None,
        )
        db_session.add(audit_log)
        db_session.commit()

logging_helper = LoggingHelper()




# import logging
# # import json
# from logging_config import async_log
# from sqlalchemy.orm import Session
# from models.all_models import AuditLog, ActionEnum

# class LoggingHelper:
#     @async_log(level=logging.INFO)
#     def log_info(self, message: str):
#         return message
    
#     @async_log(level=logging.ERROR)
#     def log_error(self, message: str):
#         return message

#     def log_audit(self, db_session: Session, user_id: int, action: ActionEnum, model: str, model_id: int, changes: dict = None):
#         """
#         Logs an audit entry for the given action.
#         """
#         # If model_id is None, provide a default value, e.g., 0
#         if model_id is None:
#             model_id = 0  # We can choose a more appropriate default value later.

#         audit_log = AuditLog(
#             user_id=user_id,
#             action=action,
#             model=model,
#             model_id=model_id,
#             changes=json.dumps(changes) if changes else None,
#         )
#         db_session.add(audit_log)
#         db_session.commit()

# logging_helper = LoggingHelper()

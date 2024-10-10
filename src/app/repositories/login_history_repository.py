# repository/login_history_repository.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.all_models import LoginHistory, User, Employee
from logging_helpers import logging_helper

class LoginHistoryRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    #def get_login_history(self, user_id: int = None, skip: int = 0, limit: int = 100):
    def get_login_history(self, skip: int = 0, limit: int = 100):
        try:
            query = (
                self.db_session.query(
                    LoginHistory,
                    User.username.label("username"),
                    User.email.label("email"),
                    Employee.first_name.label("first_name"),
                    Employee.last_name.label("last_name")
                )
                .join(User, LoginHistory.user_id == User.id)
                .join(Employee, User.employee_id == Employee.id)
                .order_by(LoginHistory.date_created.desc())
            )
            
            # if user_id:
            #     query = query.filter(LoginHistory.user_id == user_id)
            
            login_histories = query.offset(skip).limit(limit).all()

            result = []
            for login_history, username,email, first_name, last_name in login_histories:
                result.append({
                    "id": login_history.id,
                    "user_id": login_history.user_id,
                    "username": username,
                    "email": email,
                    "full_name": f"{first_name} {last_name}",
                    "login_time": login_history.login_time,
                    "logout_time": login_history.logout_time,
                    "ip_address": login_history.ip_address,
                    "user_agent": login_history.user_agent,
                })

            logging_helper.log_info("Successfully Fetched Login History from the Database")
            return result
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching Login History: {str(e)}")
            raise Exception(f"Error fetching Login History: {str(e)}")


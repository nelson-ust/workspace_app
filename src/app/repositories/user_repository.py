from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from passlib.context import CryptContext
from typing import List, Optional
from sqlalchemy.orm import joinedload, aliased
from datetime import datetime, timedelta

from repositories.base_repository import BaseRepository
from models.all_models import Employee, Project, Tenancy, User, UserRole, users_roles, LoginHistory, InvalidToken, project_employee_association
from schemas.user_schemas import UserCreate, UserUpdate
import secrets
from config import ACCESS_TOKEN_EXPIRE_MINUTES  # Import the constant

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        try:
            return self.db.query(User).all()
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise

    def create_user(self, db: Session, user_create: UserCreate):
        # Verify employee exists
        employee = (
            self.db.query(Employee)
            .filter(Employee.id == user_create.employee_id)
            .first()
        )
        if not employee:
            raise Exception(f"Employee with ID {user_create.employee_id} not found")
        db_user = self.db.query(User).filter(User.email == user_create.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        # Proceed with user creation
        hashed_password = self.get_password_hash(user_create.password)
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
            employee_id=user_create.employee_id,
            tenancy_id=user_create.tenancy_id,
        )
        db.add(db_user)
        try:
            db.commit()
            db.refresh(db_user)
            return db_user
        except Exception as e:
            db.rollback()
            raise e

    def update_user(self, user_id: int, user: UserUpdate) -> Optional[User]:
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None
        for var, value in vars(user).items():
            setattr(db_user, var, value) if value else None
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int) -> Optional[int]:
        db_user = self.get_user_by_id(user_id)
        if db_user:
            try:
                self.db.delete(db_user)
                self.db.commit()
                return user_id
            except SQLAlchemyError as e:
                self.db.rollback()
                raise HTTPException(status_code=500, detail=str(e))

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def assign_roles(self, user_id: int, role_ids: List[int]):
        """
        Assigns roles to a user by user_id and role_ids.
        """
        # Fetch the user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User with ID {user_id} not found"
            )

        # Fetch the roles based on role_ids
        roles = self.db.query(UserRole).filter(UserRole.id.in_(role_ids)).all()
        if len(roles) != len(role_ids):
            raise HTTPException(status_code=404, detail="One or more roles not found")

        # Assign the roles to the user
        user.roles = roles

        try:
            self.db.commit()
            return {"detail": "Roles successfully assigned"}
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to assign roles: {e}")

    def get_user_with_roles_by_id(self, user_id: int) -> Optional[User]:
        return (
            self.db.query(User)
            .options(joinedload(User.roles))
            .filter(User.id == user_id)
            .first()
        )

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Fetch a user by their email address.

        :param email: Email address of the user to fetch
        :return: User object if found,Otherwise None
        """
        return self.db.query(User).filter(User.email == email,User.is_active==True).first()


    def get_user_details_by_email(self, email: str):
        # Fetch the user and their roles separately and then combine them in Python
        user = (
            self.db.query(
                User.id.label("id"),
                User.username.label("username"),
                User.email.label("email"),
                User.is_active.label("is_active"),
                User.employee_id.label("employee_id"),
                User.tenancy_id.label("tenancy_id"),
                Employee.first_name.label("first_name"),
                Employee.last_name.label("last_name"),
                Employee.unit_id.label("unit_id"),  # Added unit_id
                Employee.department_id.label("department_id"),  # Added department_id
                Tenancy.name.label("tenancy_name"),
            )
            .outerjoin(Employee, User.employee_id == Employee.id)
            .outerjoin(Tenancy, User.tenancy_id == Tenancy.id)
            .filter(User.email == email, User.is_active == True)
            .first()
        )

        if user:
            roles = (
                self.db.query(
                    UserRole.id.label("role_id"), UserRole.name.label("role_name")
                )
                .join(users_roles, UserRole.id == users_roles.c.role_id)
                .filter(users_roles.c.user_id == user.id)
                .all()
            )

            roles_data = [
                {"id": role.role_id, "name": role.role_name} for role in roles
            ]

            # Fetch the projects the user/employee is mapped to
            projects = (
                self.db.query(
                    Project.id.label("project_id"),
                    Project.name.label("project_name"),
                    Project.description.label("project_description"),
                    Project.start_date.label("start_date"),
                    Project.end_date.label("end_date"),
                )
                .join(project_employee_association, Project.id == project_employee_association.c.project_id)
                .filter(project_employee_association.c.employee_id == user.employee_id)
                .all()
            )

            projects_data = [
                {
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "project_description": project.project_description,
                    "start_date": project.start_date,
                    "end_date": project.end_date,
                }
                for project in projects
            ]

            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "employee_id": user.employee_id,
                "tenancy_id": user.tenancy_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "unit_id": user.unit_id,  # Include unit_id
                "department_id": user.department_id,  # Include department_id
                "tenancy_name": user.tenancy_name,
                "roles": roles_data,
                "projects": projects_data,  # Include projects data
            }
            return user_data
        return None


    def create_password_reset_token(self, email: str):
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        reset_token = secrets.token_urlsafe()
        expiration_time = datetime.utcnow() + timedelta(
            hours=2
        )  # Token expires in 2 hours
        user.reset_token = reset_token
        user.reset_token_expires = expiration_time
        try:
            self.db.commit()
            return {"reset_token": reset_token, "email": user.email}
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))


    def verify_password_reset_token(self, token: str) -> bool:
        user = (
            self.db.query(User)
            .filter(
                User.reset_token == token, User.reset_token_expires > datetime.utcnow()
            )
            .first()
        )
        if not user:
            return False
        return True

    def reset_password(self, token: str, new_password: str):
        user = (
            self.db.query(User)
            .filter(
                User.reset_token == token, User.reset_token_expires > datetime.utcnow()
            )
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=404, detail="Invalid or expired reset token"
            )
        user.hashed_password = pwd_context.hash(new_password)
        user.reset_token = None  # Invalidate the token after use
        user.reset_token_expires = None
        try:
            self.db.commit()
            return user
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Failed to reset password: {e}"
            )


    def logout_user(self, user_id: int, token: str):
        try:
            # Update logout time in LoginHistory
            login_history = self.db.query(LoginHistory).filter(LoginHistory.user_id == user_id, LoginHistory.logout_time.is_(None)).first()
            if login_history:
                login_history.logout_time = datetime.utcnow()
                self.db.commit()
            
            # Add the token to InvalidToken table to invalidate it
            invalid_token = InvalidToken(token=token, expiry_date=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), user_id=user_id)
            self.db.add(invalid_token)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to logout: {e}")
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to logout: {e}")

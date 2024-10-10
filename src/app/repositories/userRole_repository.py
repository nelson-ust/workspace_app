# # repositories/userRole_repository.py
# from fastapi import HTTPException
# from psycopg2 import IntegrityError
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from typing import List, Optional
# from models.all_models import UserRole
# from schemas.userRole_schemas import UserRoleCreate, UserRoleUpdate
# from repositories.base_repository import BaseRepository
# import logging

# class UserRoleRepository(BaseRepository[UserRole, UserRoleCreate, UserRoleUpdate]):
#     def __init__(self, db_session: Session):
#         super().__init__(UserRole, db_session)

#     def get_roles(self, skip: int = 0, limit: int = 100) -> List[UserRole]:
#         try:
#             return super().get_all(skip=skip, limit=limit)
#         except SQLAlchemyError as e:
#             logging.error(f"Database error when retrieving roles: {str(e)}")
#             raise HTTPException(status_code=500, detail="Failed to retrieve roles due to database error")

#     def get_role_by_id(self, role_id: int) -> Optional[UserRole]:
#         try:
#             role = super().get_by_id(role_id)
#             if not role:
#                 raise HTTPException(status_code=404, detail="Role not found")
#             return role
#         except SQLAlchemyError as e:
#             logging.error(f"Database error when retrieving role by ID {role_id}: {str(e)}")
#             raise HTTPException(status_code=500, detail="Failed to retrieve role due to database error")

#     def create_role(self, role_data: UserRoleCreate) -> UserRole:
#         existing_role = self.db_session.query(UserRole).filter_by(name=role_data.name).first()
#         if existing_role:
#             raise HTTPException(status_code=400, detail=f"Role '{role_data.name}' already exists.")

#         try:
#             return super().create(role_data)
#         except IntegrityError:
#             self.db_session.rollback()
#             raise HTTPException(status_code=409, detail="Role with the same name already exists")
#         except SQLAlchemyError as e:
#             logging.error(f"Database error during role creation: {str(e)}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail="Failed to create role due to database error")
#         except Exception as e:
#             logging.error(f"Unexpected error: {str(e)}")
#             raise

#     def update_role(self, role_id: int, role_update: UserRoleUpdate) -> Optional[UserRole]:
#         db_role = self.get_role_by_id(role_id)
#         if not db_role:
#             raise HTTPException(status_code=404, detail="Role not found")

#         try:
#             return super().update(db_role, role_update)
#         except SQLAlchemyError as e:
#             logging.error(f"Database error during role update: {str(e)}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail="Failed to update role due to database error")
#         except Exception as e:
#             logging.error(f"Error updating userRole with ID {role_id}: {str(e)}")
#             raise

#     def soft_delete_role(self, role_id: int) -> Optional[UserRole]:
#         db_role = self.get_role_by_id(role_id)
#         if not db_role:
#             raise HTTPException(status_code=404, detail="Role not found")
#         if not db_role.is_active:
#             raise HTTPException(status_code=400, detail="Role already deleted")

#         try:
#             db_role.is_active = False
#             self.db_session.commit()
#             return db_role
#         except SQLAlchemyError as e:
#             logging.error(f"Database error during role deletion: {str(e)}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail="Failed to delete role due to database error")

#     def restore_role(self, role_id: int) -> Optional[UserRole]:
#         db_role = self.get_role_by_id(role_id)
#         if not db_role:
#             raise HTTPException(status_code=404, detail="Role not found")
#         if db_role.is_active:
#             raise HTTPException(status_code=400, detail="Role is not deleted")

#         try:
#             db_role.is_active = True
#             self.db_session.commit()
#             return db_role
#         except SQLAlchemyError as e:
#             logging.error(f"Database error during role restoration: {str(e)}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail="Failed to restore role due to database error")




# repositories/userRole_repository.py
from fastapi import HTTPException
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from models.all_models import UserRole
from schemas.userRole_schemas import UserRoleCreate, UserRoleUpdate
from repositories.base_repository import BaseRepository
import logging

class UserRoleRepository(BaseRepository[UserRole, UserRoleCreate, UserRoleUpdate]):
    def __init__(self, db_session: Session):
        super().__init__(UserRole, db_session)

    def get_roles(self, skip: int = 0, limit: int = 100) -> List[UserRole]:
        try:
            roles = self.db_session.query(UserRole).filter(UserRole.is_active==True).all()
            return roles
        except SQLAlchemyError as e:
            logging.error(f"Database error when retrieving roles: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve roles due to database error")
        

    def get_role_by_id(self, role_id: int) -> Optional[UserRole]:
        try:
            role = self.db_session.query(UserRole).filter(UserRole.id==role_id, UserRole.is_active==True).first()
            if not role:
                raise HTTPException(status_code=404, detail="Role not found")
            return role
        except SQLAlchemyError as e:
            logging.error(f"Database error when retrieving role by ID {role_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve role due to database error")


    def create_role(self, role_data: UserRoleCreate) -> UserRole:
        existing_role = self.db_session.query(UserRole).filter_by(name=role_data.name).first()
        if existing_role:
            raise HTTPException(status_code=400, detail=f"Role '{role_data.name}' already exists.")

        try:
            return super().create(role_data)
        except IntegrityError:
            self.db_session.rollback()
            raise HTTPException(status_code=409, detail="Role with the same name already exists")
        except SQLAlchemyError as e:
            logging.error(f"Database error during role creation: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail="Failed to create role due to database error")
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            raise


    def update_role(self, role_id: int, role_update: UserRoleUpdate) -> Optional[UserRole]:
        db_role = self.get_role_by_id(role_id)
        if not db_role:
            raise HTTPException(status_code=404, detail="Role not found")
        try:
            db_role.name=role_update.name
            self.db_session.commit()
            self.db_session.refresh(db_role)
            return f"message : The UserRole with ID {role_id} updated succesfully"
        except SQLAlchemyError as e:
            logging.error(f"Database error during role update: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail="Failed to update role due to database error")
        except Exception as e:
            logging.error(f"Error updating userRole with ID {role_id}: {str(e)}")
            raise

    def soft_delete_role(self, role_id: int) -> Optional[UserRole]:
        db_role = self.db_session.query(UserRole).filter(UserRole.id==role_id).first()
        if not db_role:
            raise HTTPException(status_code=404, detail="Role not found")
        if not db_role.is_active:
            raise HTTPException(status_code=400, detail="Role already deleted")
        try:
            db_role.is_active = False
            self.db_session.commit()
            self.db_session.refresh(db_role)
            return role_id
        except SQLAlchemyError as e:
            logging.error(f"Database error during role deletion: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete role due to database error")


    def restore_role(self, role_id: int) -> Optional[UserRole]:
        db_role = self.db_session.query(UserRole).filter(UserRole.id==role_id).first()
        if not db_role:
            raise HTTPException(status_code=404, detail="Role not found")
        if db_role.is_active:
            raise HTTPException(status_code=400, detail="Role is already active")

        try:
            db_role.is_active = True
            self.db_session.commit()
            self.db_session.refresh(db_role)
            return role_id
        except SQLAlchemyError as e:
            logging.error(f"Database error during role restoration: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail="Failed to restore role due to database error")

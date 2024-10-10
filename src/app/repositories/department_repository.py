
# # repositories/department_repository.py
# import datetime
# from psycopg2 import IntegrityError
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from typing import List, Optional
# from fastapi import HTTPException
# from models.all_models import Department
# from schemas.department_schemas import DepartmentCreate, DepartmentUpdate
# from repositories.base_repository import BaseRepository
# import logging
# from logging_helpers import logging_helper

# class DepartmentRepository(BaseRepository[Department, DepartmentCreate, DepartmentUpdate]):
#     def __init__(self, db_session: Session):
#         super().__init__(Department, db_session)

#     def get_departments(self, skip: int = 0, limit: int = 100) -> List[Department]:
#         try:
#             return super().get_all(skip=skip, limit=limit)
#             logging_helper.log_info("Sucessfully fetched all the departments")
            
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Database error when retrieving departments: {e}")
#             raise HTTPException(status_code=500, detail="Failed to retrieve departments due to a database error")

#     def get_department_by_id(self, department_id: int) -> Optional[Department]:
#         try:
#             department = super().get_by_id(department_id)
#             if not department:
#                 logging_helper.log_error(f"Department with ID:{department_id} not found")
#                 raise HTTPException(status_code=404, detail="Department not found")
#             return department
#             logging_helper.log_info(f"Sucessfully fetched the department with ID: {department_id}")
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Database error when retrieving department with ID {department_id}: {e}")
#             raise HTTPException(status_code=500, detail="Failed to retrieve department due to a database error")


#     def create_department(self, department_data: DepartmentCreate) -> Department:
#         """
#         Creates a new Department from the provided schema data. Checks for duplicate names to prevent IntegrityError.
#         """
#         existing_department =self.db_session.query(Department).filter_by(name=department_data.name).first()
#         if existing_department :
#             logging_helper.log_info(f"Department with name '{department_data.name}' already exists.")
#             raise HTTPException(status_code=400, detail=f"A department with name '{department_data.name}' already exists.")
#         try:
#             return super().create(department_data)
#             logging_helper.log_info(f"Successfully Created the Department with name : {department_data.name}!!!")
#         except IntegrityError:
#             self.db_session.rollback()
#             raise HTTPException(status_code=409, detail="Department with the same name already exists")
#         except SQLAlchemyError as e:
#             logging_helper.log_info(f"Database error during department creation: {e}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail="Failed to create department due to a database error")
#         except Exception as e:
#             logging_helper.log_error(f"Error Creating Department with name {department_data.name}: {str(e)}")
#             raise

#     def update_department(self, department_id: int, department_update: DepartmentUpdate) -> Optional[Department]:
#         db_department= self.get_by_id(department_id)
#         if not db_department:
#             logging_helper.log_error(f"No Department found with ID {department_id}.")
#             raise HTTPException(status_code=404, detail=f"No work plan source found with ID {department_id}.")

#         if department_update.name:
#             #Check if the ne new Department name exists in  other record
#             existing_department = self.db_session.query(Department).filter(
#                 Department.name == department_update.name,
#                 Department.id !=department_id
#             ).first()
#             if existing_department:
#                 logging_helper.log_error(f"Department with name '{department_update.name}' already exists.")
#                 raise HTTPException(status_code=400, detail=F"Department with name '{department_update.name}' already exists. ")
#         try:
#             updated_department = self.update(db_department, department_update)
#             return updated_department
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error updating Department with ID {department_id} : {str(e)}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Failed to update Department due to a database error.")
#         except Exception as e:
#             logging_helper.log_error(f"Unexpected error: {str(e)}")
#             self.db_session.rollback() 
#             raise HTTPException(status_code=500, detail=f"An expected error occured while updating the Department.")   


#     def delete_department(self, department_id: int, hard_delete: bool = False) -> None:
#         """
#         Deletes a department by ID. Can perform a hard delete or a soft delete.
#         """
#         try:
#             department = self.db_session.query(Department).filter(Department.id==department_id)
#             if not department:
#                 logging_helper.log_info(f"Departmet with the ID: {department_id} not found")
#                 raise HTTPException(status_code=404, detail="Department not found")

#             if hard_delete:
#                 self.delete_hard(department_id)
#             else:
#                 self.soft_delete(department_id)
#             self.db_session.commit()  # Ensure commit only after successful operations
#         except IntegrityError as e:
#             self.db_session.rollback()  # Proper rollback in case of integrity issues
#             logging_helper.log_error(f"Integrity error during department deletion: {e}")
#             raise HTTPException(status_code=400, detail="Department cannot be deleted due to dependency constraints")
#         except SQLAlchemyError as e:
#             self.db_session.rollback()  # Rollback for any other SQL related errors
#             logging_helper.log_error(f"SQLAlchemy error during department deletion: {e}")
#             raise HTTPException(status_code=500, detail="Failed to delete department due to a database error")
#         except Exception as e:
#             self.db_session.rollback()  # Rollback for any other unexpected errors
#             logging_helper.log_error(f"Unexpected error during department deletion: {e}")
#             raise HTTPException(status_code=500, detail="An unexpected error occurred")


#     # def soft_delete_department(self, department_id: int):
#     #     """
#     #     Soft deletes a department by setting its is_active flag to False.
#     #     Checks if the department exists and is not already soft-deleted.
#     #     """
#     #     db_department = self.db_session.query(Department).filter(Department.id == department_id).first()
#     #     if not db_department:
#     #         logging.error(f"Department with ID {department_id} not found.")
#     #         raise HTTPException(status_code=404, detail="Department not found")

#     #     if not db_department.is_active:
#     #         logging.info(f"Department with ID {department_id} is already deactivated.")
#     #         raise HTTPException(status_code=400, detail="Department already deactivated")

#     #     try:
#     #         db_department.is_active = False
#     #         db_department.date_deleted = datetime.datetime.utcnow()
#     #         self.db_session.commit()
#     #         self.db_session.refresh(db_department)
#     #         logging.info(f"Department with ID {department_id} was successfully soft-deleted.")
#     #         # No return statement needed for 204 No Content
#     #     except SQLAlchemyError as e:
#     #         self.db_session.rollback()
#     #         logging.error(f"Database error occurred while soft-deleting the department: {e}")
#     #         raise HTTPException(status_code=500, detail="Failed to soft delete department due to a database error.")
#     #     except Exception as e:
#     #         self.db_session.rollback()
#     #         logging.error(f"Unexpected error during the soft-delete operation: {e}")
#     #         raise HTTPException(status_code=500, detail="An unexpected error occurred during the soft-delete operation.")


#     def soft_delete_department(self, department_id: int):
#         """
#         Soft deletes a department by setting its is_active flag to False.
#         Checks if the department exists and is not already soft-deleted.
#         """
#         db_department = self.get_by_id(department_id)
#         if not db_department:
#             logging_helper.log_error(f"Department with ID {department_id} not found.")
#             raise HTTPException(status_code=404, detail="Department not found")

#         if not db_department.is_active:
#             logging_helper.log_info(f"Department with ID {department_id} is already deactivated.")
#             raise HTTPException(status_code=400, detail="Department already deactivated")

#         try:
#             # Call the soft_delete method from the BaseRepository class
#             return super().soft_delete(department_id)
#         except HTTPException as http_exc:
#             # Re-raise the HTTPException to maintain the API error handling consistency
#             raise http_exc
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Database error occurred while soft-deleting the department: {e}")
#             raise HTTPException(status_code=500, detail="Failed to soft delete department due to a database error.")
#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Unexpected error during the soft-delete operation: {e}")
#             raise HTTPException(status_code=500, detail="An unexpected error occurred during the soft-delete operation.")

#     def restore_department(self, department_id: int) -> Optional[Department]:
#         """
#         Restores a soft-deleted department by setting its is_active flag to True.
#         """
#         #Fetch the Department, including those that might be soft-deleted (if applicable)
#         db_department = self.db_session.query(Department).filter(Department.id==department_id).first()
#         if db_department is None:
#             logging_helper.log_info(f"Departement with ID {department_id} not found in the Database.")
#             raise HTTPException(status_code=404, detail="Department not found.")
        
#         if db_department.is_active:
#             logging_helper.log_info(f"Department with ID {department_id} is already active")
#             raise HTTPException(status_code=400, detail="Department is already active")
#         try:
#             db_department.is_active=True
#             self.db_session.commit()
#             logging_helper.log_info(f"Department with ID {department_id} reactivated.")
#             return db_department
#         except SQLAlchemyError as e:
#             logging.error(f"Database error when trying to reactivate Department with ID {department_id}: {str(e)}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail="Database error during reactivation. ")
        
#         except Exception as e:
#             logging_helper.log_error(f"Unexpected error when trying to reactivate the Department with ID {department_id}: {str(e)}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail="Unexpected error during reactivation")




# repositories/department_repository.py
import datetime
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from fastapi import HTTPException
from models.all_models import Department
from schemas.department_schemas import DepartmentCreate, DepartmentUpdate
from repositories.base_repository import BaseRepository
import logging
from logging_helpers import logging_helper

class DepartmentRepository(BaseRepository[Department, DepartmentCreate, DepartmentUpdate]):
    def __init__(self, db_session: Session):
        super().__init__(Department, db_session)

    def get_departments(self, skip: int = 0, limit: int = 100, department_id:Optional[int]=None) -> List[Department]:
        try:
            departments = self.db_session.query(Department).filter(Department.is_active==True)
            if department_id:
                departments = departments.filter(Department.id == department_id)
            departments = departments.offset(offset=skip).limit(limit=limit).all()
            return departments
            
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Database error when retrieving departments: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve departments due to a database error")


    def get_department_by_id(self, department_id: int, dept_id:Optional[int]=None) -> Optional[Department]:
        try:
            department = self.db_session.query(Department).filter(Department.id==department_id, Department.is_active==True)
            if dept_id:
                department = department.filter(Department.id == dept_id).first()
            if not department:
                logging_helper.log_error(f"Department with ID:{department_id} not found")
                raise HTTPException(status_code=404, detail="Department not found")
            return department
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Database error when retrieving department with ID {department_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve department due to a database error")


    def create_department(self, department_data: DepartmentCreate) -> Department:
        """
        Creates a new Department from the provided schema data. Checks for duplicate names to prevent IntegrityError.
        """
        existing_department =self.db_session.query(Department).filter_by(name=department_data.name).first()
        if existing_department :
            logging_helper.log_info(f"Department with name '{department_data.name}' already exists.")
            raise HTTPException(status_code=400, detail=f"A department with name '{department_data.name}' already exists.")
        try:
            return super().create(department_data)
        except IntegrityError:
            self.db_session.rollback()
            raise HTTPException(status_code=409, detail="Department with the same name already exists")
        except SQLAlchemyError as e:
            logging_helper.log_info(f"Database error during department creation: {e}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail="Failed to create department due to a database error")
        except Exception as e:
            logging_helper.log_error(f"Error Creating Department with name {department_data.name}: {str(e)}")
            raise


    def update_department(self, department_id: int, department_update: DepartmentUpdate) -> Optional[Department]:
        db_department= self.db_session.query(Department).filter(Department.id==department_id, Department.is_active==True).first()

        if not db_department:
            logging_helper.log_error(f"No Department found with ID {department_id}.")
            raise HTTPException(status_code=404, detail=f"No work plan source found with ID {department_id}.")

        if department_update.name:
            #Check if the ne new Department name exists in  other record
            existing_department = self.db_session.query(Department).filter(
                Department.name == department_update.name,
                Department.id !=department_id
            ).first()
            if existing_department:
                logging_helper.log_error(f"Department with name '{department_update.name}' already exists.")
                raise HTTPException(status_code=400, detail=F"Department with name '{department_update.name}' already exists. ")
        try:
            db_department.name = department_update.name
            self.db_session.commit()
            self.db_session.refresh(db_department)
            
            return {"message : The Department updated succesfully"}
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error updating Department with ID {department_id} : {str(e)}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update Department due to a database error.")
        except Exception as e:
            logging_helper.log_error(f"Unexpected error: {str(e)}")
            self.db_session.rollback() 
            raise HTTPException(status_code=500, detail=f"An expected error occured while updating the Department.")   


    def delete_department(self, department_id: int, hard_delete: bool = False) -> None:
        """
        Deletes a department by ID. Can perform a hard delete or a soft delete.
        """
        try:
            department = self.db_session.query(Department).filter(Department.id==department_id)
            if not department:
                logging_helper.log_info(f"Departmet with the ID: {department_id} not found")
                raise HTTPException(status_code=404, detail="Department not found")

            if hard_delete:
                self.delete_hard(department_id)
            else:
                self.soft_delete(department_id)
            self.db_session.commit()  # Ensure commit only after successful operations
        except IntegrityError as e:
            self.db_session.rollback()  # Proper rollback in case of integrity issues
            logging_helper.log_error(f"Integrity error during department deletion: {e}")
            raise HTTPException(status_code=400, detail="Department cannot be deleted due to dependency constraints")
        except SQLAlchemyError as e:
            self.db_session.rollback()  # Rollback for any other SQL related errors
            logging_helper.log_error(f"SQLAlchemy error during department deletion: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete department due to a database error")
        except Exception as e:
            self.db_session.rollback()  # Rollback for any other unexpected errors
            logging_helper.log_error(f"Unexpected error during department deletion: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")


    def soft_delete_department(self, department_id: int):
        """
        Soft deletes a department by setting its is_active flag to False.
        Checks if the department exists and is not already soft-deleted.
        """
        db_department = self.db_session.query(Department).filter(Department.id==department_id).first()
        if not db_department:
            logging_helper.log_error(f"Department with ID {department_id} not found.")
            raise HTTPException(status_code=404, detail="Department not found")

        if not db_department.is_active:
            logging_helper.log_info(f"Department with ID {department_id} is already deactivated.")
            raise HTTPException(status_code=400, detail="Department already deactivated")

        try:
            # Call the soft_delete method from the BaseRepository class
            db_department.is_active=False
            self.db_session.commit()
            self.db_session.refresh(db_department)
            logging_helper.log_info(f"Department with ID {department_id} soft-deleted.")
            return {"Message": "Department soft deleted successfully"}
        except HTTPException as http_exc:
            # Re-raise the HTTPException to maintain the API error handling consistency
            raise http_exc
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Database error occurred while soft-deleting the department: {e}")
            raise HTTPException(status_code=500, detail="Failed to soft delete department due to a database error.")
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Unexpected error during the soft-delete operation: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred during the soft-delete operation.")


    def restore_department(self, department_id: int) -> Optional[Department]:
        """
        Restores a soft-deleted department by setting its is_active flag to True.
        """
        #Fetch the Department, including those that might be soft-deleted (if applicable)
        db_department = self.db_session.query(Department).filter(Department.id==department_id).first()
        if db_department is None:
            logging_helper.log_info(f"Departement with ID {department_id} not found in the Database.")
            raise HTTPException(status_code=404, detail="Department not found.")
        
        if db_department.is_active:
            logging_helper.log_info(f"Department with ID {department_id} is already active")
            raise HTTPException(status_code=400, detail="Department is already active")
        try:
            db_department.is_active=True
            self.db_session.commit()
            logging_helper.log_info(f"Department with ID {department_id} reactivated.")
            return {"Message": "Department restored successfully"}
        except SQLAlchemyError as e:
            logging.error(f"Database error when trying to reactivate Department with ID {department_id}: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail="Database error during reactivation. ")
        
        except Exception as e:
            logging_helper.log_error(f"Unexpected error when trying to reactivate the Department with ID {department_id}: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail="Unexpected error during reactivation")
# # repositories/designation_repository.py
# from sqlalchemy.orm import Session
# from typing import List, Optional
# from sqlalchemy.exc import SQLAlchemyError, IntegrityError
# from fastapi import HTTPException
# from models.all_models import Designation
# from schemas.designation_schemas import DesignationCreate, DesignationUpdate
# from repositories.base_repository import BaseRepository
# from db.database import get_db  # This function manages the DB session
# import logging
# from logging_helpers import logging_helper

# class DesignationRepository(BaseRepository[Designation, DesignationCreate, DesignationUpdate]):
#     def __init__(self, db_session: Session):
#         super().__init__(model=Designation, db_session=db_session)

#     def create_designation(self, designation_data: DesignationCreate) -> Designation:
#         """
#         Creates a new designation from the provided schema data, ensuring no duplicate names.
#         """
#         existing_designation = self.db_session.query(Designation).filter_by(name=designation_data.name).first()
#         if existing_designation:
#             logging_helper.log_info(f"Designation with name '{designation_data.name}' already exists.")
#             raise HTTPException(status_code=400, detail=f"Designation with name '{designation_data.name}' already exists.")

#         try:
#             return super().create(designation_data)
#         except IntegrityError as e:
#             logging_helper.log_error(f"Unique constraint error: {str(e)}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=400, detail="Failed to create designation due to a duplicate name.")
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error creating new designation: {str(e)}")
#             self.db_session.rollback()
#             raise
#         except Exception as e:
#             logging_helper.log_error(f"Unexpected error: {str(e)}")
#             raise

#     def get_all_designations(self, skip: int = 0, limit: int = 100) -> List[Designation]:
#         try:
#             return self.get_all(skip=skip, limit=limit)
#             logging_helper.log_info("Successfully Retrived all Designations")
#         except SQLAlchemyError as e:
#             logging.error(f"Error retrieving all designations: {str(e)}")
#             raise

#     def update_designation(self, designation_id: int, designation_update: DesignationUpdate) -> Optional[Designation]:
#         db_designation = self.get_by_id(designation_id)
#         if not db_designation:
#             logging_helper.log_info(f"Designation not found with ID {designation_id}")
#             raise HTTPException(status_code=404, detail=f"Designation not found with ID {designation_id}")

#         if designation_update.name:
#             existing_designation = self.db_session.query(Designation).filter(
#                 Designation.name == designation_update.name,
#                 Designation.id != designation_id
#             ).first()
#             if existing_designation:
#                 logging_helper.log_info(f"Designation with name '{designation_update.name}' already exists.")
#                 raise HTTPException(status_code=400, detail=f"Designation with name '{designation_update.name}' already exists.")

#         try:
#             return self.update(db_designation, designation_update)
#         except IntegrityError as e:
#             logging_helper.log_error(f"Unique constraint error: {str(e)}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=400, detail="Failed to update designation due to a duplicate name.")
#         except SQLAlchemyError as e:
#             logging.error(f"Error updating designation with ID {designation_id}: {str(e)}")
#             raise

#     def soft_delete_designation(self, designation_id: int) -> Optional[Designation]:
#         """
#         Soft deletes a designation by marking it as inactive. Ensures the designation exists before deleting.
#         """
#         db_designation = self.get_by_id(designation_id)
#         if not db_designation:
#             raise HTTPException(status_code=404, detail="Designation not found")
#         if not db_designation.is_active:
#             raise HTTPException(status_code=400, detail="Designation already deleted")

#         try:
#             db_designation.is_active = False
#             self.db_session.commit()
#             return db_designation
#         except SQLAlchemyError as e:
#             logging.error(f"Error soft deleting designation: {str(e)}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail="Failed to soft delete designation due to database error")

#     def restore_designation(self, designation_id: int) -> Optional[Designation]:
#         """
#         Restores a soft deleted designation by marking it as active. Ensures the designation exists and is currently inactive before restoring.
#         """
#         db_designation = self.get_by_id(designation_id)
#         if not db_designation:
#             raise HTTPException(status_code=404, detail="Designation not found")
#         if db_designation.is_active:
#             raise HTTPException(status_code=400, detail="Designation is not deleted and cannot be restored")

#         try:
#             db_designation.is_active = True
#             self.db_session.commit()
#             return db_designation
#         except SQLAlchemyError as e:
#             logging_helper.log_error (f"Error restoring designation: {str(e)}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail="Failed to restore designation due to database error")



# repositories/designation_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
from models.all_models import Designation
from schemas.designation_schemas import DesignationCreate, DesignationUpdate
from repositories.base_repository import BaseRepository
from db.database import get_db  # This function manages the DB session
import logging
from logging_helpers import logging_helper

class DesignationRepository(BaseRepository[Designation, DesignationCreate, DesignationUpdate]):
    def __init__(self, db_session: Session):
        super().__init__(model=Designation, db_session=db_session)

    def create_designation(self, designation_data: DesignationCreate) -> Designation:
        """
        Creates a new designation from the provided schema data, ensuring no duplicate names.
        """
        existing_designation = self.db_session.query(Designation).filter_by(name=designation_data.name).first()
        if existing_designation:
            logging_helper.log_info(f"Designation with name '{designation_data.name}' already exists.")
            raise HTTPException(status_code=400, detail=f"Designation with name '{designation_data.name}' already exists.")

        try:
            return super().create(designation_data)
        except IntegrityError as e:
            logging_helper.log_error(f"Unique constraint error: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(status_code=400, detail="Failed to create designation due to a duplicate name.")
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error creating new designation: {str(e)}")
            self.db_session.rollback()
            raise
        except Exception as e:
            logging_helper.log_error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=404, detail=f"Designations not created")


    def get_all_designations(self, skip: int = 0, limit: int = 100) -> List[Designation]:
        try:
            designations = self.db_session.query(Designation).filter(Designation.is_active==True).offset(offset=skip).limit(limit=limit).all()
            return designations
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving all designations: {str(e)}")
            raise HTTPException(status_code=404, detail=f"Designations not found")
        

    def get_designation_by_id(self, designation_id: int) -> Optional[Designation]:
        try:
            designation = self.db_session.query(Designation).filter(Designation.is_active==True, Designation.id==designation_id).first()
            return designation
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise HTTPException(status_code=400, detail=f"{str(e)}")


    def update_designation(self, designation_id: int, designation_update: DesignationUpdate) -> Optional[Designation]:
        db_designation = self.db_session.query(Designation).filter(Designation.id == designation_id, Designation.is_active==True).first()
        if not db_designation:
            logging_helper.log_info(f"Designation not found with ID {designation_id}")
            raise HTTPException(status_code=404, detail=f"Designation not found with ID {designation_id}")

        if designation_update.name:
            existing_designation = self.db_session.query(Designation).filter(
                Designation.name == designation_update.name,
                Designation.id != designation_id
            ).first()
            if existing_designation:
                logging_helper.log_info(f"Designation with name '{designation_update.name}' already exists.")
                raise HTTPException(status_code=400, detail=f"Designation with name '{designation_update.name}' already exists.")

        try:
            db_designation.name=designation_update.name
            self.db_session.commit()
            self.db_session.refresh(db_designation)
            return {"Message : The Designation name updated successfully"}
        except IntegrityError as e:
            logging_helper.log_error(f"Unique constraint error: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(status_code=400, detail="Failed to update designation due to a duplicate name.")
        except SQLAlchemyError as e:
            logging.error(f"Error updating designation with ID {designation_id}: {str(e)}")
            raise HTTPException(status_code=404, detail=f"Error due to {str(e)}")


    def soft_delete_designation(self, designation_id: int) -> Optional[Designation]:
        """
        Soft deletes a designation by marking it as inactive. Ensures the designation exists before deleting.
        """
        db_designation = self.db_session.query(Designation).filter(Designation.id == designation_id).first()
        if not db_designation:
            raise HTTPException(status_code=404, detail="Designation not found")
        if not db_designation.is_active:
            raise HTTPException(status_code=400, detail="Designation already deleted")
        try:
            db_designation.is_active = False
            self.db_session.commit()
            self.db_session.refresh(db_designation)
            return f"Message : The Designation with ID {designation_id} soft deleted successfully"
        except SQLAlchemyError as e:
            logging.error(f"Error soft deleting designation: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail="Failed to soft delete designation due to database error")


    def restore_designation(self, designation_id: int) -> Optional[Designation]:
        """
        Restores a soft deleted designation by marking it as active. Ensures the designation exists and is currently inactive before restoring.
        """
        db_designation = self.db_session.query(Designation).filter(Designation.id == designation_id).first()
        if not db_designation:
            raise HTTPException(status_code=404, detail="Designation not found")
        if db_designation.is_active:
            raise HTTPException(status_code=400, detail="Designation is already active")

        try:
            db_designation.is_active = True
            self.db_session.commit()
            self.db_session.refresh(db_designation)
            return f"Message : The Designation with ID {designation_id} restored successfully"
        except SQLAlchemyError as e:
            logging_helper.log_error (f"Error restoring designation: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail="Failed to restore designation due to database error")

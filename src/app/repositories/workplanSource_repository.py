# #repositories/workplansource_repository.py
# from typing import List
# from sqlalchemy.exc import IntegrityError, SQLAlchemyError
# from fastapi import HTTPException
# from sqlalchemy.orm import Session
# #from db.database import get_db
# from repositories.base_repository import BaseRepository
# from models.all_models import WorkPlanSource as WorkPlanSource_Model
# from schemas.workplanSource_schemas import WorkPlanSourceCreate,  WorkPlanSourceUpdate
# import logging

# class WorkPlanSourceRepository(BaseRepository[WorkPlanSource_Model, WorkPlanSourceCreate, WorkPlanSourceUpdate]):

#     def __init__(self, db_session: Session):
#         super().__init__(model=WorkPlanSource_Model, db_session=db_session)


#     def get_work_plan_source_by_id(self,workplan_source_id:int)->WorkPlanSource_Model:
#         try:
#             return self.get_by_id(workplan_source_id)
#         except SQLAlchemyError as e:
#             logging.error(f"Error retriving Workplan source with id '{workplan_source_id}': {str(e)}")
#             raise
#         except Exception as e:
#             logging.error(f"Unexpected error: {str(e)}")
    
#     def get_all_work_plan_sources(self, skip: int = 0, limit: int = 100)->List[WorkPlanSource_Model]:
#         try:
#             return self.get_all(skip=skip, limit=limit)
#         except SQLAlchemyError as e:
#             logging.error(f"Error retrieving all designations: {str(e)}")
#             raise
#         except Exception as e:
#             logging.error(f"Unexpected error: {str(e)}")
#             raise

   
#     def create_work_plan_source(self, work_plan_type_data: WorkPlanSourceCreate) -> WorkPlanSource_Model:
#         """
#         Creates a new work plan source from the provided schema data. Checks for duplicate names to prevent IntegrityError.
#         """
#         existing_work_plan_source = self.db_session.query(WorkPlanSource_Model).filter_by(name=work_plan_type_data.name).first()
#         if existing_work_plan_source:
#             logging.error(f"Work plan source with name '{work_plan_type_data.name}' already exists.")
#             raise HTTPException(status_code=400, detail=f"Work plan source with name '{work_plan_type_data.name}' already exists.")
        
#         try:
#             return self.create(work_plan_type_data)
#         except SQLAlchemyError as e:
#             logging.error(f"Error creating new work plan source: {str(e)}")
#             raise HTTPException(status_code=500, detail="Failed to create new work plan source due to a database error.")
#         except Exception as e:
#             logging.error(f"Unexpected error: {str(e)}")
#             raise HTTPException(status_code=500, detail="An unexpected error occurred while creating a new work plan source.")


#     def update_work_plan_source(self, work_plan_source_id: int, work_plan_source_update: WorkPlanSourceUpdate) -> WorkPlanSource_Model:
#         """
#         Updates a work plan source given its ID and the updated data. Checks for potential name conflicts and existence before updating.
#         """
#         db_workplan_source = self.get_by_id(work_plan_source_id)
#         if not db_workplan_source:
#             logging.error(f"No work plan source found with ID {work_plan_source_id}.")
#             raise HTTPException(status_code=404, detail=f"No work plan source found with ID {work_plan_source_id}.")

#         if work_plan_source_update.name:
#             # Check if the new name already exists in other records
#             existing_work_plan_source = self.db_session.query(WorkPlanSource_Model).filter(
#                 WorkPlanSource_Model.name == work_plan_source_update.name,
#                 WorkPlanSource_Model.id != work_plan_source_id
#             ).first()
#             if existing_work_plan_source:
#                 logging.error(f"Work plan source with name '{work_plan_source_update.name}' already exists.")
#                 raise HTTPException(status_code=400, detail=f"Work plan source with name '{work_plan_source_update.name}' already exists.")

#         try:
#             updated_work_plan_source = self.update(db_workplan_source, work_plan_source_update)
#             return updated_work_plan_source
#         except SQLAlchemyError as e:
#             logging.error(f"Error updating work plan source with ID {work_plan_source_id}: {str(e)}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Failed to update work plan source due to a database error.")
#         except Exception as e:
#             logging.error(f"Unexpected error: {str(e)}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the work plan source.")

#     def delete_work_plan_source(self, work_plan_source_id: int) -> WorkPlanSource_Model:
#         try:
#             return self.soft_delete(work_plan_source_id)
#         except SQLAlchemyError as e:
#             logging.error(f"Error soft deleting designation with ID {work_plan_source_id}: {str(e)}")
#             raise
#         except Exception as e:
#             logging.error(f"Unexpected error: {str(e)}")
#             raise
    

#     def reactivate_work_plan_source(self, work_plan_source_id: int):
#         """
#         Attempts to reactivate a work plan source by ID.
#         """
#         # Fetching the work plan source, including those that might be soft-deleted (if applicable)
#         db_workplan_source = self.db_session.query(WorkPlanSource_Model).filter(WorkPlanSource_Model.id == work_plan_source_id).first()

#         if db_workplan_source is None:
#             logging.error(f"Work plan source with ID {work_plan_source_id} not found in the database.")
#             raise HTTPException(status_code=404, detail="Work plan source not found.")

#         if db_workplan_source.is_active:
#             logging.info(f"Work plan source with ID {work_plan_source_id} is already active.")
#             raise HTTPException(status_code=400, detail="Work plan source is already active.")

#         try:
#             db_workplan_source.is_active = True
#             self.db_session.commit()
#             logging.info(f"Work plan source with ID {work_plan_source_id} reactivated.")
#             return db_workplan_source
#         except SQLAlchemyError as e:
#             logging.error(f"Database error when trying to reactivate work plan source with ID {work_plan_source_id}: {str(e)}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail="Database error during reactivation.")
#         except Exception as e:
#             logging.error(f"Unexpected error during reactivation of work plan source with ID {work_plan_source_id}: {e}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail="Unexpected error during reactivation.")



#repositories/workplansource_repository.py
from typing import List
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException
from sqlalchemy.orm import Session
#from db.database import get_db
from repositories.base_repository import BaseRepository
from models.all_models import WorkPlanSource as WorkPlanSource_Model
from schemas.workplanSource_schemas import WorkPlanSourceCreate,  WorkPlanSourceUpdate
import logging
from logging_helpers import logging_helper

class WorkPlanSourceRepository(BaseRepository[WorkPlanSource_Model, WorkPlanSourceCreate, WorkPlanSourceUpdate]):

    def __init__(self, db_session: Session):
        super().__init__(model=WorkPlanSource_Model, db_session=db_session)


    def get_work_plan_source_by_id(self,workplan_source_id:int)->WorkPlanSource_Model:
        try:
            return self.get_by_id(workplan_source_id)
        except SQLAlchemyError as e:
            logging.error(f"Error retriving Workplan source with id '{workplan_source_id}': {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
    

    def get_all_work_plan_sources(self)->List[WorkPlanSource_Model]:
        try:
            workplans = self.db_session.query(WorkPlanSource_Model).filter(WorkPlanSource_Model.is_active==True).all()
            return workplans
        except Exception as e:
            logging.error(f"Error retrieving all designations: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error fetching workplan sources")

   
    def create_work_plan_source(self, work_plan_type_data: WorkPlanSourceCreate) -> WorkPlanSource_Model:
        """
        Creates a new work plan source from the provided schema data. Checks for duplicate names to prevent IntegrityError.
        """
        existing_work_plan_source = self.db_session.query(WorkPlanSource_Model).filter_by(name=work_plan_type_data.name).first()
        if existing_work_plan_source:
            logging.error(f"Work plan source with name '{work_plan_type_data.name}' already exists.")
            raise HTTPException(status_code=400, detail=f"Work plan source with name '{work_plan_type_data.name}' already exists.")
        
        try:
            return self.create(work_plan_type_data)
        except SQLAlchemyError as e:
            logging.error(f"Error creating new work plan source: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create new work plan source due to a database error.")
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred while creating a new work plan source.")


    def update_work_plan_source(self, work_plan_source_id: int, work_plan_source_update: WorkPlanSourceUpdate) -> WorkPlanSource_Model:
        """
        Updates a work plan source given its ID and the updated data. Checks for potential name conflicts and existence before updating.
        """
        db_workplan_source = self.get_by_id(work_plan_source_id)
        if not db_workplan_source:
            logging.error(f"No work plan source found with ID {work_plan_source_id}.")
            raise HTTPException(status_code=404, detail=f"No work plan source found with ID {work_plan_source_id}.")

        if work_plan_source_update.name:
            # Check if the new name already exists in other records
            existing_work_plan_source = self.db_session.query(WorkPlanSource_Model).filter(
                WorkPlanSource_Model.name == work_plan_source_update.name,
                WorkPlanSource_Model.id != work_plan_source_id
            ).first()
            if existing_work_plan_source:
                logging.error(f"Work plan source with name '{work_plan_source_update.name}' already exists.")
                raise HTTPException(status_code=400, detail=f"Work plan source with name '{work_plan_source_update.name}' already exists.")

        try:
            db_workplan_source.name = work_plan_source_update.name
            self.db_session.commit()
            self.db_session.refresh(db_workplan_source)
            return {"Workplan Source updated successfully"}
        except SQLAlchemyError as e:
            logging.error(f"Error updating work plan source with ID {work_plan_source_id}: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update work plan source due to a database error.")
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred while updating the work plan source. {str(e)}")


    def delete_work_plan_source(self, work_plan_source_id: int) -> WorkPlanSource_Model:
        try:
            db_workplan_source = self.db_session.query(WorkPlanSource_Model).filter(WorkPlanSource_Model.id == work_plan_source_id).first()
            if not db_workplan_source:
                logging_helper.log_error(f"WorkplanSource with ID {work_plan_source_id} not found.")
                raise HTTPException(status_code=404, detail="WorkplanSource not found")

            if not db_workplan_source.is_active:
                logging_helper.log_info(f"WorkplanSource with ID {work_plan_source_id} is already deactivated.")
                raise HTTPException(status_code=400, detail="WorkplanSource already deactivated")

            db_workplan_source.is_active = False
            self.db_session.commit()
            self.db_session.refresh(db_workplan_source)
            return {"message : WorkplanSource deactivated successfully"}
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error {str(e)}")
    

    def reactivate_work_plan_source(self, work_plan_source_id: int):
        """
        Attempts to reactivate a work plan source by ID.
        """
        # Fetching the work plan source, including those that might be soft-deleted (if applicable)
        db_workplan_source = self.db_session.query(WorkPlanSource_Model).filter(WorkPlanSource_Model.id == work_plan_source_id).first()

        if db_workplan_source is None:
            logging.error(f"Work plan source with ID {work_plan_source_id} not found in the database.")
            raise HTTPException(status_code=404, detail="Work plan source not found.")

        if db_workplan_source.is_active:
            logging.info(f"Work plan source with ID {work_plan_source_id} is already active.")
            raise HTTPException(status_code=400, detail="Work plan source is already active.")

        try:
            db_workplan_source.is_active = True
            self.db_session.commit()
            logging.info(f"Work plan source with ID {work_plan_source_id} reactivated.")
            return {"message : WorkplanSource reactivated successfully"}
        except SQLAlchemyError as e:
            logging.error(f"Database error when trying to reactivate work plan source with ID {work_plan_source_id}: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail="Database error during reactivation.")
        except Exception as e:
            logging.error(f"Unexpected error during reactivation of work plan source with ID {work_plan_source_id}: {e}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail="Unexpected error during reactivation.")

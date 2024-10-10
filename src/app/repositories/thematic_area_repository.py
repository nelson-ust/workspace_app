# #repositories/thematicarea_repository.py
# from typing import List, Optional
# from sqlalchemy.exc import IntegrityError, SQLAlchemyError
# from fastapi import HTTPException, status
# from sqlalchemy.orm import Session
# from repositories.base_repository import BaseRepository
# from models.all_models import ThematicArea as ThematicArea_Model
# from schemas.thematic_area_schemas import ThematicAreaCreate,  ThematicAreaUpdate
# import logging


# class ThematicAreaRepository(BaseRepository[ThematicArea_Model, ThematicAreaCreate, ThematicAreaUpdate]):

#     def __init__(self, db_session: Session):
#         super().__init__(model=ThematicArea_Model, db_session=db_session)


#     def create_thematic_area(self, thematic_area_type_data: ThematicAreaCreate) -> ThematicArea_Model:
#         """
#         Creates a Thematic Area from the provided schema data. Checks for duplicate names to prevent IntegrityError.
#         """
#         existing_Thematic_Area = self.db_session.query(ThematicArea_Model).filter(ThematicArea_Model.name==thematic_area_type_data.name).first()
#         if existing_Thematic_Area:
#             logging.error(f"Thematic area with name '{thematic_area_type_data.name}' already exists.")
#             raise HTTPException(status_code=400, detail=f"Thematic area with name '{thematic_area_type_data.name}' already exists.")
        
#         try:
#             new_thematic_area = self.create(thematic_area_type_data)
#             return new_thematic_area
#         except SQLAlchemyError as e:
#             logging.error(f"Error creating new work plan source: {str(e)}")
#             raise HTTPException(status_code=500, detail="Failed to create new Thematic area due to a database error.")
#         except Exception as e:
#             logging.error(f"Unexpected error: {str(e)}")
#             raise HTTPException(status_code=500, detail="An unexpected error occurred while creating a new Thematic area.")


#     def get_thematic_area_by_id(self, thematic_area_id:int)->ThematicArea_Model:
#         try:
#             #check for existence
#             thematic_exist = self.db_session.query(ThematicArea_Model).filter(ThematicArea_Model.id==thematic_area_id, ThematicArea_Model.is_active==True).first()
#             if not thematic_exist:
#                 raise HTTPException(status_code=400, detail=f"Thematic area with ID {thematic_area_id} does not exist.")
            
#             thematic_area = self.get_by_id(id=thematic_area_id, is_active=True)
#             return thematic_area
#         except SQLAlchemyError as e:
#             logging.error(f"Error retriving Thematic Area with id '{thematic_area_id}': {str(e)}")
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{str(e)}")
    

#     def get_all_thematic_area(self, skip:int =0, limit:int =100)->List[ThematicArea_Model]:
#         try:
#             thematic_areas = self.get_all(skip=skip, limit=limit, is_active=True)

#             return thematic_areas
#         except SQLAlchemyError as e:
#             logging.error(f"Error retrieving all Thematic Area: {str(e)}")
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{str(e)}")


#     def update_thematic_area(self, thematic_area_id: int, thematic_area_update: ThematicAreaUpdate) -> Optional[ThematicArea_Model]:
#         """
#         Updates a Thematic Area given its ID and the updated data. Checks for potential name conflicts and existence before updating.
#         """
#         db_thematic_area = self.get_by_id(id=thematic_area_id, is_active=True)
#         if not db_thematic_area:
#             logging.error(f"Error fetching Thematic Area {thematic_area_id}.")
#             raise HTTPException(status_code=404, detail=f"No Thematic area found with ID {thematic_area_id}.")

#         #Check for Name Conflicts
#         existing_Thematic_Area = self.db_session.query(ThematicArea_Model).filter(ThematicArea_Model.name==thematic_area_update.name).first()
#         if existing_Thematic_Area:
#             logging.error(f"Thematic area with name '{thematic_area_update.name}' already exists.")
#             raise HTTPException(status_code=400, detail=f"Thematic area with name '{thematic_area_update.name}' already exists.")

#         try:
#             updated_thematic_area = self.update(db_obj=db_thematic_area, obj_in=thematic_area_update)
#             return updated_thematic_area
        
#         except SQLAlchemyError as e:
#             logging.error(f"Error updating thematic area with ID {thematic_area_id}: {str(e)}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Failed to update thematic area due to a database error.")
        

#     def delete_thematic_area(self, thematic_area_id, hard_delete: bool = True, tenancy_id: Optional[int] = None) -> Optional[ThematicArea_Model]:
#         """
#         Deletes or soft deletes a Thematic Area by ID based on the hard_delete flag.
#         """
#         try:
#             thematic_area = self.get_by_id(id=thematic_area_id, is_active=True)
#             if not thematic_area:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Thematic Area with ID {thematic_area_id} does not exist')  
            
#             if hard_delete:
#                 return self.delete_hard(thematic_area_id)
#             else:
#                 return self.soft_delete(thematic_area_id)
#         except SQLAlchemyError as e:
#             logging.error(f"Error deleting Thematic Area: {e}")
#             raise HTTPException(status_code=500, detail="Failed to delete Thematic Area")



#     def soft_delete_thematic_area(self, thematic_area_id: int ) -> Optional [ThematicArea_Model]:
#         """
#         Soft delete  a Thematic Area given its ID and the updated data. 
#         """
#         soft_thematic_area = self.get_by_id(id=thematic_area_id)
#         if not soft_thematic_area:
#             raise HTTPException(status_code=404, detail=f"Thematic area with ID {thematic_area_id} not found")
    
#         if not soft_thematic_area.is_active:
#             raise HTTPException(status_code=400, detail=f"Thematic Area with ID {thematic_area_id} already deactivated")

#         try:
#             soft_thematic_area.is_active = False
#             self.db_session.commit()
#             return soft_thematic_area
#         except SQLAlchemyError as e:
#             logging.error(f"Error soft deleting Thematic Area: {e}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail="Failed to soft delete Thematic Area")



#     def reactivate_deleted_thematic_area(self, thematic_area_id: int) -> Optional [ThematicArea_Model]:
#         """
#         Attempts to reactivate a Thematic Area by ID.
#         """
#         # Fetching theThematic Area, including those that might be soft-deleted (if applicable)
#         db_thematic_area = self.db_session.query(ThematicArea_Model).filter(ThematicArea_Model.id == thematic_area_id).first()

#         if not db_thematic_area:
#             logging.error(f"Thematic Area with ID {thematic_area_id} not found in the database.")
#             raise HTTPException(status_code=404, detail="Thematic Area not found.")

#         if db_thematic_area.is_active:
#             logging.info(f"Thematic Area with ID {thematic_area_id} is already active.")
#             raise HTTPException(status_code=400, detail="Thematic Area is already active.")

#         try:
#             db_thematic_area.is_active = True
#             self.db_session.commit()
#             logging.info(f"Thematic Area with ID {thematic_area_id} reactivated.")
#             return db_thematic_area
#         except SQLAlchemyError as e:
#             logging.error(f"Database error when trying to reactivate Thematic Area with ID {thematic_area_id}: {str(e)}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail="Database error during reactivation.")
    


  

#repositories/thematicarea_repository.py
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from repositories.base_repository import BaseRepository
from models.all_models import ThematicArea as ThematicArea_Model
from schemas.thematic_area_schemas import ThematicAreaCreate,  ThematicAreaUpdate
import logging


class ThematicAreaRepository(BaseRepository[ThematicArea_Model, ThematicAreaCreate, ThematicAreaUpdate]):

    def __init__(self, db_session: Session):
        super().__init__(model=ThematicArea_Model, db_session=db_session)


    def create_thematic_area(self, thematic_area_type_data: ThematicAreaCreate) -> ThematicArea_Model:
        """
        Creates a Thematic Area from the provided schema data. Checks for duplicate names to prevent IntegrityError.
        """
        existing_Thematic_Area = self.db_session.query(ThematicArea_Model).filter(ThematicArea_Model.name==thematic_area_type_data.name).first()
        if existing_Thematic_Area:
            logging.error(f"Thematic area with name '{thematic_area_type_data.name}' already exists.")
            raise HTTPException(status_code=400, detail=f"Thematic area with name '{thematic_area_type_data.name}' already exists.")
        
        try:
            new_thematic_area = self.create(thematic_area_type_data)
            return new_thematic_area
        except SQLAlchemyError as e:
            logging.error(f"Error creating new work plan source: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create new Thematic area due to a database error.")
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred while creating a new Thematic area.")


    def get_thematic_area_by_id(self, thematic_area_id:int)->ThematicArea_Model:
        try:
            #check for existence
            thematic_area = self.db_session.query(ThematicArea_Model).filter(ThematicArea_Model.id==thematic_area_id, ThematicArea_Model.is_active==True).first()
            if not thematic_area:
                raise HTTPException(status_code=400, detail=f"Thematic area with ID {thematic_area_id} does not exist.")
            
            return thematic_area
        except SQLAlchemyError as e:
            logging.error(f"Error retriving Thematic Area with id '{thematic_area_id}': {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{str(e)}")
    

    def get_all_thematic_area(self)->List[ThematicArea_Model]:
        try:
            thematic_areas = self.db_session.query(ThematicArea_Model).filter(ThematicArea_Model.is_active==True).all()

            return thematic_areas
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving all Thematic Area: {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{str(e)}")


    def update_thematic_area(self, thematic_area_id: int, thematic_area_update: ThematicAreaUpdate) -> Optional[ThematicArea_Model]:
        """
        Updates a Thematic Area given its ID and the updated data. Checks for potential name conflicts and existence before updating.
        """
        db_thematic_area = self.db_session.query(ThematicArea_Model).filter(ThematicArea_Model.id==thematic_area_id, ThematicArea_Model.is_active==True).first()
        if not db_thematic_area:
            logging.error(f"Error fetching Thematic Area {thematic_area_id}.")
            raise HTTPException(status_code=404, detail=f"No Thematic area found with ID {thematic_area_id}.")

        #Check for Name Conflicts
        if db_thematic_area.name==thematic_area_update.name:
            logging.error(f"Thematic area with name '{thematic_area_update.name}' already exists.")
            raise HTTPException(status_code=400, detail=f"Thematic area with name '{thematic_area_update.name}' already exists.")

        try:
            db_thematic_area.name = thematic_area_update.name
            self.db_session.commit()
            self.db_session.refresh(db_thematic_area
                                    )
            return {"message": f"Thematic Area with name {db_thematic_area.name} Updated successfully"}
        
        except SQLAlchemyError as e:
            logging.error(f"Error updating thematic area with ID {thematic_area_id}: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update thematic area due to a database error.")
        

    def delete_thematic_area(self, thematic_area_id, hard_delete: bool = True, tenancy_id: Optional[int] = None) -> Optional[ThematicArea_Model]:
        """
        Deletes or soft deletes a Thematic Area by ID based on the hard_delete flag.
        """
        try:
            thematic_area = self.get_by_id(id=thematic_area_id, is_active=True)
            if not thematic_area:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Thematic Area with ID {thematic_area_id} does not exist')  
            
            if hard_delete:
                return self.delete_hard(thematic_area_id)
            else:
                return self.soft_delete(thematic_area_id)
        except SQLAlchemyError as e:
            logging.error(f"Error deleting Thematic Area: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete Thematic Area")



    def soft_delete_thematic_area(self, thematic_area_id: int ) -> Optional [ThematicArea_Model]:
        """
        Soft delete  a Thematic Area given its ID and the updated data. 
        """
        db_thematic_area = self.db_session.query(ThematicArea_Model).filter(ThematicArea_Model.id == thematic_area_id).first()
        if not db_thematic_area:
            raise HTTPException(status_code=404, detail=f"Thematic area with ID {thematic_area_id} not found")
    
        if not db_thematic_area.is_active:
            raise HTTPException(status_code=400, detail=f"Thematic Area with ID {thematic_area_id} already deactivated")

        try:
            db_thematic_area.is_active = False
            self.db_session.commit()
            return {"message": f"Thematic Area with name {db_thematic_area.name} deactivated successfully"}
        except SQLAlchemyError as e:
            logging.error(f"Error soft deleting Thematic Area: {e}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail="Failed to soft delete Thematic Area")



    def reactivate_deleted_thematic_area(self, thematic_area_id: int) -> Optional [ThematicArea_Model]:
        """
        Attempts to reactivate a Thematic Area by ID.
        """
        # Fetching theThematic Area, including those that might be soft-deleted (if applicable)
        db_thematic_area = self.db_session.query(ThematicArea_Model).filter(ThematicArea_Model.id == thematic_area_id).first()

        if not db_thematic_area:
            logging.error(f"Thematic Area with ID {thematic_area_id} not found in the database.")
            raise HTTPException(status_code=404, detail="Thematic Area not found.")

        if db_thematic_area.is_active:
            logging.info(f"Thematic Area with ID {thematic_area_id} is already active.")
            raise HTTPException(status_code=400, detail="Thematic Area is already active.")

        try:
            db_thematic_area.is_active = True
            self.db_session.commit()
            logging.info(f"Thematic Area with ID {thematic_area_id} reactivated.")
            return {"message": f"Thematic Area with name {db_thematic_area.name} activated successfully"}
        except SQLAlchemyError as e:
            logging.error(f"Database error when trying to reactivate Thematic Area with ID {thematic_area_id}: {str(e)}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail="Database error during reactivation.")
    


  

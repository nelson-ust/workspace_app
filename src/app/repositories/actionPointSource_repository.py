# # repositories/actionpointsource_repository.py
# from fastapi import HTTPException, status
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from typing import List, Optional
# from models.all_models import ActionPointSource
# from schemas.actionPointSource_schemas import ActionPointSourceCreate, ActionPointSourceUpdate
# from repositories.base_repository import BaseRepository
# import logging
# from logging_helpers import logging_helper


# class ActionPointSourceRepository(BaseRepository[ActionPointSource, ActionPointSourceCreate, ActionPointSourceUpdate]):
#     def __init__(self, db_session: Session):
#         super().__init__(ActionPointSource, db_session)

#     def create_actionpointsource(self, actionpointsource_data: ActionPointSourceCreate) -> ActionPointSource:
#         """
#         Creates a new actionpointsource ensuring that the name is unique within the ActionPointSource table.
#         """
#         existing_actionpointsource = self.db_session.query(ActionPointSource).filter(ActionPointSource.name==actionpointsource_data.name).first()
#         if existing_actionpointsource:
#             logging_helper.log_error(f"An actionpointsource with the name {actionpointsource_data.name} already exists")
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An actionpointsource with the name {actionpointsource_data.name} already exists")
        
#         try:
#             return self.create(actionpointsource_data)
#         except SQLAlchemyError as err:
#             logging_helper.log_error(f"Database error during actionpointsource creation: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
    
#     def update_actionpointsource(self, actionpointsource_id: int,  actionpointsource_data: ActionPointSourceUpdate) -> Optional[ActionPointSource]:
#         """
#         Updates an existing actionpointsource_id.
#         """

#         db_actionpointsource = self.db_session.query(ActionPointSource).filter(ActionPointSource.is_active==True, ActionPointSource.id==actionpointsource_id).first()
#         if not db_actionpointsource:
#             logging_helper.log_error(f"An actionpointsource with the id {actionpointsource_id} does not exist")
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"An actionpointsource with the id {actionpointsource_id} does not exist")
        
#         if actionpointsource_data.name and (actionpointsource_data.name == db_actionpointsource.name):
#             logging_helper.log_error(f'actionpointsource with "{actionpointsource_data.name}" already exists')
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'actionpointsource with "{actionpointsource_data.name}" already exists')
        
#         try:
#             db_actionpointsource.name=actionpointsource_data.name
#             self.db_session.commit()
#             self.db_session.refresh(db_actionpointsource)
#             return {"message : ActionPointSource Updated Successfully"}
#         except SQLAlchemyError as err:
#             logging_helper.log_error(f"Database error during actionpointsource update: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update actionpointsource due to a database error")
            

#     def get_all_actionpointsource(self) -> List[ActionPointSource]:
#         """
#         Retrieves all actionpointsource records with optional pagination.
#         """
#         try:
#             action_point_sources = self.db_session.query(ActionPointSource).filter(ActionPointSource.is_active==True).all()
#             logging_helper.log_info("Successfully fetched all the actionpoint sources")
#             return action_point_sources
#         except SQLAlchemyError as err:
#             logging_helper.log_error(f"Error retrieving actionpointsource: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve actionpointsource")
        

#     def get_actionpointsource_by_id(self, actionpointsource_id: int) -> ActionPointSource:
#         """
#         Retrieves a actionpointsource by its ID.
#         """
#         try:
#             action_point_source = self.db_session.query(ActionPointSource).filter(ActionPointSource.is_active==True, ActionPointSource.id==actionpointsource_id).first()
#             logging_helper.log_info(f"Sucessfully fetched the actionpoint source for the id: {actionpointsource_id}")
#             return action_point_source

#         except SQLAlchemyError as err:
#             logging.error(f"Error retrieving actionpointsource: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve actionpointsource")


#     def delete_actionpointsource(self, actionpointsource_id: int, hard_delete: bool = True) ->Optional[ActionPointSource]:
#         """
#         Deletes or soft deletes a actionpointsource by ID based on the hard_delete flag.
#         """

#         try:
#             actionpointsource = self.get_actionpointsource_by_id(actionpointsource_id)
#             if not actionpointsource:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'actionpointsource {actionpointsource_id} not found')
            
#             if hard_delete:
#                 self.delete_hard(actionpointsource_id)
#                 logging_helper.log_info(f"Sucessfully Hard Deleted the ActionPoint Source with ID: {actionpointsource_id}")
#             else:
#                 logging_helper.log_info(f"Sucessfully deleted ActionPoint Source With ID: {actionpointsource_id} ")
#                 return self.soft_delete(actionpointsource_id)
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error deleting actionpointsource: {e}")
#             raise HTTPException(status_code=500, detail="Failed to delete actionpointsource")


#     def soft_delete_actionpointsource(self, actionpointsource_id):
#         """
#         Soft deletes a actionpointsource by setting its is_active flag to False.
#         """
#         actionpointsource = self.db_session.query(ActionPointSource).filter(ActionPointSource.id==actionpointsource_id).first()
#         if not actionpointsource:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'actionpointsource {actionpointsource_id} not found')
        
#         if not actionpointsource.is_active:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"actionpointsource {actionpointsource_id} has already been deactivated")
        
#         try:
#             actionpointsource.is_active = False
#             self.db_session.commit()
#             return {"detail": f"Actionpointsource with id {actionpointsource_id} has been deactivated successfully"}
#         except SQLAlchemyError as err:
#             logging.error(f"Error soft deleting actionpointsource: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to soft delete actionpointsource")


#     def restore(self, actionpointsource_id: int) -> Optional[ActionPointSource]:
#         """
#         Restores a soft-deleted actionpointsource by setting its is_active flag to True.
#         """

#         actionpointsource = self.db_session.query(ActionPointSource).filter(ActionPointSource.id==actionpointsource_id).first()
#         if not actionpointsource:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'actionpointsource {actionpointsource_id} not found')
        
#         if actionpointsource.is_active:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"actionpointsource with id {actionpointsource_id} is already active")
        
#         try:
#             actionpointsource.is_active = True
#             self.db_session.commit()
#             return {"detail": f"Actionpointsource with id {actionpointsource_id} has been activated successfully"}
#         except SQLAlchemyError as err:
#             logging.error(f"Error soft deleting actionpointsource: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to restore soft deleted actionpointsource")



# repositories/actionpointsource_repository.py

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from models.all_models import ActionPointSource
from schemas.actionPointSource_schemas import ActionPointSourceCreate, ActionPointSourceUpdate
from repositories.base_repository import BaseRepository
from logging_helpers import logging_helper

class ActionPointSourceRepository(BaseRepository[ActionPointSource, ActionPointSourceCreate, ActionPointSourceUpdate]):
    def __init__(self, db_session: Session):
        super().__init__(ActionPointSource, db_session)

    def create_actionpointsource(self, actionpointsource_data: ActionPointSourceCreate) -> ActionPointSource:
        """
        Creates a new ActionPointSource ensuring that the name is unique within the ActionPointSource table.
        
        Parameters:
            actionpointsource_data (ActionPointSourceCreate): The data required to create a new ActionPointSource.
        
        Returns:
            ActionPointSource: The newly created ActionPointSource object.
        
        Raises:
            HTTPException: If an ActionPointSource with the same name already exists or if a database error occurs.
        """
        # Check if an ActionPointSource with the same name already exists
        existing_actionpointsource = self.db_session.query(ActionPointSource).filter(ActionPointSource.name == actionpointsource_data.name).first()
        if existing_actionpointsource:
            logging_helper.log_error(f"An ActionPointSource with the name {actionpointsource_data.name} already exists")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An ActionPointSource with the name {actionpointsource_data.name} already exists")
        
        try:
            # Create the new ActionPointSource
            return self.create(actionpointsource_data)
        except SQLAlchemyError as err:
            logging_helper.log_error(f"Database error during ActionPointSource creation: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update_actionpointsource(self, actionpointsource_id: int, actionpointsource_data: ActionPointSourceUpdate) -> Optional[ActionPointSource]:
        """
        Updates an existing ActionPointSource.
        
        Parameters:
            actionpointsource_id (int): The ID of the ActionPointSource to update.
            actionpointsource_data (ActionPointSourceUpdate): The updated data for the ActionPointSource.
        
        Returns:
            ActionPointSource: The updated ActionPointSource object if successful.
        
        Raises:
            HTTPException: If the ActionPointSource does not exist, if a name conflict occurs, or if a database error occurs.
        """
        # Fetch the existing ActionPointSource by ID
        db_actionpointsource = self.db_session.query(ActionPointSource).filter(ActionPointSource.is_active == True, ActionPointSource.id == actionpointsource_id).first()
        if not db_actionpointsource:
            logging_helper.log_error(f"An ActionPointSource with the id {actionpointsource_id} does not exist")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"An ActionPointSource with the id {actionpointsource_id} does not exist")
        
        # Check for name conflict
        if actionpointsource_data.name and (actionpointsource_data.name == db_actionpointsource.name):
            logging_helper.log_error(f'ActionPointSource with "{actionpointsource_data.name}" already exists')
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'ActionPointSource with "{actionpointsource_data.name}" already exists')
        
        try:
            # Update the ActionPointSource name
            db_actionpointsource.name = actionpointsource_data.name
            self.db_session.commit()
            self.db_session.refresh(db_actionpointsource)
            return {"message": "ActionPointSource Updated Successfully"}
        except SQLAlchemyError as err:
            logging_helper.log_error(f"Database error during ActionPointSource update: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update ActionPointSource due to a database error")

    def get_all_actionpointsource(self) -> List[ActionPointSource]:
        """
        Retrieves all ActionPointSource records.
        
        Returns:
            List[ActionPointSource]: A list of all active ActionPointSource objects.
        
        Raises:
            HTTPException: If a database error occurs.
        """
        try:
            # Fetch all active ActionPointSource records
            action_point_sources = self.db_session.query(ActionPointSource).filter(ActionPointSource.is_active == True).all()
            logging_helper.log_info("Successfully fetched all ActionPointSources")
            return action_point_sources
        except SQLAlchemyError as err:
            logging_helper.log_error(f"Error retrieving ActionPointSources: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve ActionPointSources")

    def get_actionpointsource_by_id(self, actionpointsource_id: int) -> ActionPointSource:
        """
        Retrieves an ActionPointSource by its ID.
        
        Parameters:
            actionpointsource_id (int): The ID of the ActionPointSource to retrieve.
        
        Returns:
            ActionPointSource: The ActionPointSource object if found.
        
        Raises:
            HTTPException: If a database error occurs.
        """
        try:
            # Fetch the ActionPointSource by ID
            action_point_source = self.db_session.query(ActionPointSource).filter(ActionPointSource.is_active == True, ActionPointSource.id == actionpointsource_id).first()
            logging_helper.log_info(f"Successfully fetched the ActionPointSource for the id: {actionpointsource_id}")
            return action_point_source
        except SQLAlchemyError as err:
            logging_helper.log_error(f"Error retrieving ActionPointSource: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve ActionPointSource")

    def delete_actionpointsource(self, actionpointsource_id: int, hard_delete: bool = True) -> Optional[ActionPointSource]:
        """
        Deletes or soft deletes an ActionPointSource by ID based on the hard_delete flag.
        
        Parameters:
            actionpointsource_id (int): The ID of the ActionPointSource to delete.
            hard_delete (bool): If True, perform a hard delete. If False, perform a soft delete.
        
        Returns:
            Optional[ActionPointSource]: The deleted or deactivated ActionPointSource object.
        
        Raises:
            HTTPException: If the ActionPointSource does not exist or if a database error occurs.
        """
        try:
            # Fetch the ActionPointSource by ID
            actionpointsource = self.get_actionpointsource_by_id(actionpointsource_id)
            if not actionpointsource:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'ActionPointSource {actionpointsource_id} not found')
            
            if hard_delete:
                # Perform a hard delete
                self.delete_hard(actionpointsource_id)
                logging_helper.log_info(f"Successfully hard deleted the ActionPointSource with ID: {actionpointsource_id}")
            else:
                # Perform a soft delete
                logging_helper.log_info(f"Successfully deleted ActionPointSource with ID: {actionpointsource_id}")
                return self.soft_delete(actionpointsource_id)
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error deleting ActionPointSource: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete ActionPointSource")

    def soft_delete_actionpointsource(self, actionpointsource_id):
        """
        Soft deletes an ActionPointSource by setting its is_active flag to False.
        
        Parameters:
            actionpointsource_id (int): The ID of the ActionPointSource to soft delete.
        
        Returns:
            dict: A message indicating the successful deactivation of the ActionPointSource.
        
        Raises:
            HTTPException: If the ActionPointSource does not exist, is already deactivated, or if a database error occurs.
        """
        # Fetch the ActionPointSource by ID
        actionpointsource = self.db_session.query(ActionPointSource).filter(ActionPointSource.id == actionpointsource_id).first()
        if not actionpointsource:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'ActionPointSource {actionpointsource_id} not found')
        
        if not actionpointsource.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"ActionPointSource {actionpointsource_id} has already been deactivated")
        
        try:
            # Set the is_active flag to False for soft delete
            actionpointsource.is_active = False
            self.db_session.commit()
            return {"detail": f"ActionPointSource with id {actionpointsource_id} has been deactivated successfully"}
        except SQLAlchemyError as err:
            logging_helper.log_error(f"Error soft deleting ActionPointSource: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to soft delete ActionPointSource")

    def restore(self, actionpointsource_id: int) -> Optional[ActionPointSource]:
        """
        Restores a soft-deleted ActionPointSource by setting its is_active flag to True.
        
        Parameters:
            actionpointsource_id (int): The ID of the ActionPointSource to restore.
        
        Returns:
            dict: A message indicating the successful activation of the ActionPointSource.
        
        Raises:
            HTTPException: If the ActionPointSource does not exist, is already active, or if a database error occurs.
        """
        # Fetch the ActionPointSource by ID
        actionpointsource = self.db_session.query(ActionPointSource).filter(ActionPointSource.id == actionpointsource_id).first()
        if not actionpointsource:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'ActionPointSource {actionpointsource_id} not found')
        
        if actionpointsource.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"ActionPointSource with id {actionpointsource_id} is already active")
        
        try:
            # Set the is_active flag to True to restore the Soft Deleted Action Point Source
            actionpointsource.is_active = True
            self.db_session.commit()
            return {"detail": f"ActionPointSource with id {actionpointsource_id} has been activated successfully"}
        except SQLAlchemyError as err:
            logging_helper.log_error(f"Error restoring ActionPointSource: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to restore soft-deleted ActionPointSource")

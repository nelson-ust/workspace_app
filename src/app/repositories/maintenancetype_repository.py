# # repositories/location_repository.py

# from fastapi import HTTPException, status
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from typing import List, Optional, Type
# from models.all_models import MaintenanceType
# from schemas.maintenancetype_schemas import MaintenanceCreate, MaintenanceUpdate
# from repositories.base_repository import BaseRepository
# import logging

# class MaintenanceTypeRepository(BaseRepository[MaintenanceType, MaintenanceCreate, MaintenanceUpdate]):
#     def __init__(self, db_session: Session):
#         super().__init__(MaintenanceType, db_session)

#     def create_maintenancetype(self, maintenancetype_data: MaintenanceCreate) -> MaintenanceType:
#         """
#         Creates a new maintenancetype ensuring that the name is unique within the maintenancetype table.
#         """
#         existing_maintenancetype = self.db_session.query(MaintenanceType).filter(MaintenanceType.name==maintenancetype_data.name).first()
#         if existing_maintenancetype:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"A maintenancetype with the name {maintenancetype_data.name} already exists")
        
#         try:
#             return self.create(maintenancetype_data)
#         except SQLAlchemyError as err:
#             logging.error(f"Database error during maintenancetype creation: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#     def update_maintenancetype(self, maintenancetype_id: int,  maintenancetype_data: MaintenanceUpdate) -> Optional[MaintenanceType]:
#         """
#         Updates an existing maintenancetype.
#         """

#         db_maintenancetype = self.get_by_id(maintenancetype_id)
#         if not db_maintenancetype:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"A maintenancetype with the id {maintenancetype_id} does not exist")
        
#         if maintenancetype_data.name and (maintenancetype_data.name == db_maintenancetype.name):
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'maintenancetype with "{maintenancetype_data.name}" already exists')
        
#         try:
#             return self.update(db_maintenancetype, maintenancetype_data)
#         except SQLAlchemyError as err:
#             logging.error(f"Database error during location update: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update maintenancetype due to a database error")
            


#     def get_all_maintenancetype(self, skip:int =0, limit:int =100) -> List[MaintenanceType]:
#         """
#         Retrieves all maintenancetype records with optional pagination.
#         """
#         try:
#             return self.get_all(skip=skip, limit=limit)
#         except SQLAlchemyError as err:
#             logging.error(f"Error retrieving maintenancetype: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve maintenancetype")
        

#     def get_maintenance_by_id(self, maintenancetype_id: int) -> MaintenanceType:
#         """
#         Retrieves a maintenancetype by its ID.
#         """
#         try:
#             return self.get_by_id(maintenancetype_id)

#         except SQLAlchemyError as err:
#             logging.error(f"Error retrieving locations: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve maintenancetype")


#     def delete_maintenancetype(self, maintenancetype_id: int, hard_delete: bool = True) ->Optional[MaintenanceType]:
#         """
#         Deletes or soft deletes a maintenancetype by ID based on the hard_delete flag.
#         """

#         try:
#             maintenancetype = self.get_maintenance_by_id(maintenancetype_id)
#             if not maintenancetype:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'maintenancetype {maintenancetype_id} not found')
            
#             if hard_delete:
#                 self.delete_hard(maintenancetype_id)
#             else:
#                 return self.soft_delete(maintenancetype_id)
#         except SQLAlchemyError as e:
#             logging.error(f"Error deleting location: {e}")
#             raise HTTPException(status_code=500, detail="Failed to delete maintenancetype")


#     def soft_delete_maintenancetype(self, maintenancetype_id):
#         """
#         Soft deletes a maintenancetype by setting its is_active flag to False.
#         """

#         maintenancetype = self.get_maintenance_by_id(maintenancetype_id)
#         if not maintenancetype:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'maintenancetype {maintenancetype_id} not found')
        
#         if not maintenancetype.is_active:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"maintenancetype {maintenancetype} has already been deactivated")
        
#         try:
#             maintenancetype.is_active = False
#             self.db_session.commit()
#             return maintenancetype
#         except SQLAlchemyError as err:
#             logging.error(f"Error soft deleting maintenancetype: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to soft delete maintenancetype")


#     def restore(self, maintenancetype_id: int) -> Optional[MaintenanceType]:
#         """
#         Restores a soft-deleted maintenancetype by setting its is_active flag to True.
#         """

#         maintenancetype = self.get_all_by_id(maintenancetype_id)
#         if not maintenancetype:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'maintenancetype {maintenancetype_id} not found')
        
#         if maintenancetype.is_active:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"maintenancetype with id {maintenancetype.id} is already active")
        
#         try:
#             maintenancetype.is_active = True
#             self.db_session.commit()
#             return maintenancetype
#         except SQLAlchemyError as err:
#             logging.error(f"Error soft deleting maintenancetype: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to restore soft deleted maintenancetype")




# repositories/location_repository.py

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from models.all_models import MaintenanceType
from schemas.maintenancetype_schemas import MaintenanceCreate, MaintenanceUpdate
from repositories.base_repository import BaseRepository
import logging

class MaintenanceTypeRepository(BaseRepository[MaintenanceType, MaintenanceCreate, MaintenanceUpdate]):
    def __init__(self, db_session: Session):
        super().__init__(MaintenanceType, db_session)

    def create_maintenancetype(self, maintenancetype_data: MaintenanceCreate) -> MaintenanceType:
        """
        Creates a new maintenancetype ensuring that the name is unique within the maintenancetype table.
        """
        existing_maintenancetype = self.db_session.query(MaintenanceType).filter(MaintenanceType.name==maintenancetype_data.name).first()
        if existing_maintenancetype:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"A maintenancetype with the name {maintenancetype_data.name} already exists")
        
        try:
            return self.create(maintenancetype_data)
        except SQLAlchemyError as err:
            logging.error(f"Database error during maintenancetype creation: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update_maintenancetype(self, maintenancetype_id: int,  maintenancetype_data: MaintenanceUpdate) -> Optional[MaintenanceType]:
        """
        Updates an existing maintenancetype.
        """

        db_maintenancetype = self.db_session.query(MaintenanceType).filter(MaintenanceType.is_active==True, MaintenanceType.id==maintenancetype_id).first()
        if not db_maintenancetype:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"A maintenancetype with the id {maintenancetype_id} does not exist")
        
        if maintenancetype_data.name and (maintenancetype_data.name == db_maintenancetype.name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'maintenancetype with "{maintenancetype_data.name}" already exists')
        
        try:
            db_maintenancetype.name = maintenancetype_data.name
            self.db_session.commit()
            self.db_session.refresh(db_maintenancetype
                                    )
            return {"message : Vehicle Maintenance Type Updated Successfully"}
        except SQLAlchemyError as err:
            logging.error(f"Database error during location update: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update maintenancetype due to a database error")
            


    def get_all_maintenancetype(self) -> List[MaintenanceType]:
        """
        Retrieves all maintenancetype records with optional pagination.
        """
        try:
            maintenance_types = self.db_session.query(MaintenanceType).filter(MaintenanceType.is_active==True).all()
            return maintenance_types
        except SQLAlchemyError as err:
            logging.error(f"Error retrieving maintenancetype: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve maintenancetype")
        

    def get_maintenance_by_id(self, maintenancetype_id: int) -> MaintenanceType:
        """
        Retrieves a maintenancetype by its ID.
        """
        try:
            maintenance_type = self.db_session.query(MaintenanceType).filter(MaintenanceType.is_active==True, MaintenanceType.id==maintenancetype_id).first()
            return maintenance_type

        except SQLAlchemyError as err:
            logging.error(f"Error retrieving locations: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve maintenancetype")


    def delete_maintenancetype(self, maintenancetype_id: int, hard_delete: bool = True) ->Optional[MaintenanceType]:
        """
        Deletes or soft deletes a maintenancetype by ID based on the hard_delete flag.
        """

        try:
            maintenancetype = self.get_maintenance_by_id(maintenancetype_id)
            if not maintenancetype:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'maintenancetype {maintenancetype_id} not found')
            
            if hard_delete:
                self.delete_hard(maintenancetype_id)
            else:
                return self.soft_delete(maintenancetype_id)
        except SQLAlchemyError as e:
            logging.error(f"Error deleting location: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete maintenancetype")


    def soft_delete_maintenancetype(self, maintenancetype_id):
        """
        Soft deletes a maintenancetype by setting its is_active flag to False.
        """

        maintenancetype = self.db_session.query(MaintenanceType).filter(MaintenanceType.id==maintenancetype_id).first()
        if not maintenancetype:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'maintenancetype {maintenancetype_id} not found')
        
        if not maintenancetype.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"maintenancetype {maintenancetype_id} has already been deactivated")
        
        try:
            maintenancetype.is_active = False
            self.db_session.commit()
            return {"message : Vehicle Maintenance Type deactivated successfully"}
        except SQLAlchemyError as err:
            logging.error(f"Error soft deleting maintenancetype: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to soft delete maintenancetype")


    def restore(self, maintenancetype_id: int) -> Optional[MaintenanceType]:
        """
        Restores a soft-deleted maintenancetype by setting its is_active flag to True.
        """
        maintenancetype = self.db_session.query(MaintenanceType).filter(MaintenanceType.id==maintenancetype_id).first()
        if not maintenancetype:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'maintenancetype {maintenancetype_id} not found')
        
        if maintenancetype.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"maintenancetype with id {maintenancetype.id} is already active")
        
        try:
            maintenancetype.is_active = True
            self.db_session.commit()
            return {"message : Vehicle Maintenance Type activated successfully"}
        except SQLAlchemyError as err:
            logging.error(f"Error soft deleting maintenancetype: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to restore soft deleted maintenancetype")
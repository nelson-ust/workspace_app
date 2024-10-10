# repositories/public_holiday_type_repository.py

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from models.all_models import HolidayType
from schemas.holiday_type_schemas import HolidayTypeCreate, HolidayTypeUpdate
from repositories.base_repository import BaseRepository
import logging


class HolidayTypeRepository(BaseRepository[HolidayType, HolidayTypeCreate, HolidayTypeUpdate]):
    def __init__(self, db_session: Session):
        super().__init__(HolidayType, db_session)

    def create_holiday_type(self, holiday_type_data: HolidayTypeCreate) -> HolidayType:
        """
        Creates a new holiday_type ensuring that the name is unique within the holiday_type table.
        """
        existing_holiday_type = self.db_session.query(HolidayType).filter(HolidayType.name == holiday_type_data.name).first()
        if existing_holiday_type:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"A holiday type with the name {holiday_type_data.name} already exists")
        
        try:
            return self.create(holiday_type_data)
        except SQLAlchemyError as err:
            logging.error(f"Database error during holiday type creation: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create holiday type due to a database error")
   
    
    def update_holiday_type(self, holiday_type_id: int, holiday_type_data: HolidayTypeUpdate) -> Optional[HolidayType]:
        """
        Updates an existing holiday type.
        """
        db_holiday_type = self.db_session.query(HolidayType).filter(HolidayType.id == holiday_type_id, HolidayType.is_active == True).first()
        if not db_holiday_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"A holiday type with the ID {holiday_type_id} does not exist")
        
        if holiday_type_data.name and (holiday_type_data.name == db_holiday_type.name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Holiday type with the name "{holiday_type_data.name}" already exists')
        
        try:
            db_holiday_type.name = holiday_type_data.name
            db_holiday_type.description = holiday_type_data.description
            self.db_session.commit()
            self.db_session.refresh(db_holiday_type)

            return db_holiday_type
        except SQLAlchemyError as err:
            logging.error(f"Database error during holiday type update: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update holiday type due to a database error")
            


    def get_all_holiday_types(self) -> List[HolidayType]:
        """
        Retrieves all holiday type records with optional pagination.
        """
        try:
            holiday_types = self.db_session.query(HolidayType).filter(HolidayType.is_active == True).all()
            return holiday_types
        except SQLAlchemyError as err:
            logging.error(f"Error retrieving holiday types: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve holiday types")
        

    def get_holiday_type_by_id(self, holiday_type_id: int) -> HolidayType:
        """
        Retrieves a holiday type by its ID.
        """
        try:
            holiday_type = self.db_session.query(HolidayType).filter(HolidayType.is_active == True, HolidayType.id == holiday_type_id).first()
            if not holiday_type:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Holiday type with ID {holiday_type_id} not found")
            return holiday_type

        except SQLAlchemyError as err:
            logging.error(f"Error retrieving holiday type: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve holiday type")


    def delete_holiday_type(self, holiday_type_id: int, hard_delete: bool = True) -> Optional[HolidayType]:
        """
        Deletes or soft deletes a holiday type by ID based on the hard_delete flag.
        """
        try:
            holiday_type = self.db_session.query(HolidayType).filter(HolidayType.id == holiday_type_id).first()
            if not holiday_type:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Holiday type with ID {holiday_type_id} not found')
            
            if hard_delete:
                self.delete_hard(holiday_type_id)
            else:
                return self.soft_delete(holiday_type_id)
        except SQLAlchemyError as e:
            logging.error(f"Error deleting holiday type: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete holiday type")


    def soft_delete_holiday_type(self, holiday_type_id: int) -> Optional[HolidayType]:
        """
        Soft deletes a holiday type by setting its is_active flag to False.
        """
        holiday_type = self.db_session.query(HolidayType).filter(HolidayType.id == holiday_type_id).first()
        if not holiday_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Holiday type with ID {holiday_type_id} not found')
        
        if not holiday_type.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Holiday type with ID {holiday_type_id} has already been deactivated")
        
        try:
            holiday_type.is_active = False
            self.db_session.commit()
            return holiday_type
        except SQLAlchemyError as err:
            logging.error(f"Error soft deleting holiday type: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to soft delete holiday type")


    def restore(self, holiday_type_id: int) -> Optional[HolidayType]:
        """
        Restores a soft-deleted holiday type by setting its is_active flag to True.
        """
        holiday_type = self.db_session.query(HolidayType).filter(HolidayType.id == holiday_type_id).first()
        if not holiday_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Holiday type with ID {holiday_type_id} not found')
        
        if holiday_type.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Holiday type with ID {holiday_type.id} is already active")
        
        try:
            holiday_type.is_active = True
            self.db_session.commit()
            return holiday_type
        except SQLAlchemyError as err:
            logging.error(f"Error restoring holiday type: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to restore holiday type")

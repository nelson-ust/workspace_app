from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from models.all_models import EmployeeType
from schemas.employee_type_schemas import EmployeeTypeCreate, EmployeeTypeUpdate
from repositories.base_repository import BaseRepository
import logging


class EmployeeTypeRepository(BaseRepository[EmployeeType, EmployeeTypeCreate, EmployeeTypeUpdate]):
    def __init__(self, db_session: Session):
        super().__init__(EmployeeType, db_session)

    def create_employee_type(self, employee_type_data: EmployeeTypeCreate) -> EmployeeType:
        """
        Creates a new employee type ensuring that the name is unique within the employee_type table.
        """
        existing_employee_type = self.db_session.query(EmployeeType).filter(EmployeeType.name == employee_type_data.name).first()
        if existing_employee_type:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An employee type with the name {employee_type_data.name} already exists")
        
        try:
            return self.create(employee_type_data)
        except SQLAlchemyError as err:
            logging.error(f"Database error during employee type creation: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create employee type due to a database error")
   
    
    def update_employee_type(self, employee_type_id: int, employee_type_data: EmployeeTypeUpdate) -> Optional[EmployeeType]:
        """
        Updates an existing employee type.
        """
        db_employee_type = self.db_session.query(EmployeeType).filter(EmployeeType.id == employee_type_id, EmployeeType.is_active == True).first()
        if not db_employee_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"An employee type with the ID {employee_type_id} does not exist")
        
        if employee_type_data.name and (employee_type_data.name == db_employee_type.name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Employee type with the name "{employee_type_data.name}" already exists')
        
        try:
            db_employee_type.name = employee_type_data.name
            db_employee_type.description = employee_type_data.description
            self.db_session.commit()
            self.db_session.refresh(db_employee_type)

            return db_employee_type
        except SQLAlchemyError as err:
            logging.error(f"Database error during employee type update: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update employee type due to a database error")


    def get_all_employee_types(self) -> List[EmployeeType]:
        """
        Retrieves all employee type records.
        """
        try:
            employee_types = self.db_session.query(EmployeeType).filter(EmployeeType.is_active == True).all()
            return employee_types
        except SQLAlchemyError as err:
            logging.error(f"Error retrieving employee types: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve employee types")
        

    def get_employee_type_by_id(self, employee_type_id: int) -> EmployeeType:
        """
        Retrieves an employee type by its ID.
        """
        try:
            employee_type = self.db_session.query(EmployeeType).filter(EmployeeType.is_active == True, EmployeeType.id == employee_type_id).first()
            if not employee_type:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee type with ID {employee_type_id} not found")
            return employee_type

        except SQLAlchemyError as err:
            logging.error(f"Error retrieving employee type: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve employee type")


    def delete_employee_type(self, employee_type_id: int, hard_delete: bool = True) -> Optional[EmployeeType]:
        """
        Deletes or soft deletes an employee type by ID based on the hard_delete flag.
        """
        try:
            employee_type = self.db_session.query(EmployeeType).filter(EmployeeType.id == employee_type_id).first()
            if not employee_type:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Employee type with ID {employee_type_id} not found')
            
            if hard_delete:
                self.delete_hard(employee_type_id)
            else:
                return self.soft_delete(employee_type_id)
        except SQLAlchemyError as e:
            logging.error(f"Error deleting employee type: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete employee type")


    def soft_delete_employee_type(self, employee_type_id: int) -> Optional[EmployeeType]:
        """
        Soft deletes an employee type by setting its is_active flag to False.
        """
        employee_type = self.db_session.query(EmployeeType).filter(EmployeeType.id == employee_type_id).first()
        if not employee_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Employee type with ID {employee_type_id} not found')
        
        if not employee_type.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Employee type with ID {employee_type_id} has already been deactivated")
        
        try:
            employee_type.is_active = False
            self.db_session.commit()
            return employee_type
        except SQLAlchemyError as err:
            logging.error(f"Error soft deleting employee type: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to soft delete employee type")


    def restore(self, employee_type_id: int) -> Optional[EmployeeType]:
        """
        Restores a soft-deleted employee type by setting its is_active flag to True.
        """
        employee_type = self.db_session.query(EmployeeType).filter(EmployeeType.id == employee_type_id).first()
        if not employee_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Employee type with ID {employee_type_id} not found')
        
        if employee_type.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Employee type with ID {employee_type.id} is already active")
        
        try:
            employee_type.is_active = True
            self.db_session.commit()
            return employee_type
        except SQLAlchemyError as err:
            logging.error(f"Error restoring employee type: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to restore employee type")

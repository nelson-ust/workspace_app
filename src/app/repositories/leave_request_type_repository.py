from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.all_models import LeaveType
from fastapi import HTTPException
from logging_helpers import logging_helper

class LeaveRequestTypeRepository:
    def __init__(self, db_session: Session):
        """
        Initialize the LeaveRequestTypeRepository with a database session.

        Args:
            db_session (Session): SQLAlchemy session object.
        """
        self.db_session = db_session

    def create_leave_type(self, name: str, description: str) -> LeaveType:
        """
        Create a new leave type in the database.

        Args:
            name (str): The name of the leave type.
            description (str): A description of the leave type.

        Returns:
            LeaveType: The newly created LeaveType object.
        """
        try:
            new_leave_type = LeaveType(name=name, description=description)
            self.db_session.add(new_leave_type)
            self.db_session.commit()
            self.db_session.refresh(new_leave_type)
            logging_helper.log_info(f"Leave type '{name}' created successfully.")
            return new_leave_type
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error occurred while creating leave type: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def get_all_leave_types(self) -> list[LeaveType]:
        """
        Retrieve all leave types from the database.

        Returns:
            list[LeaveType]: A list of all LeaveType objects.
        """
        try:
            leave_types = self.db_session.query(LeaveType).all()
            logging_helper.log_info(f"Retrieved {len(leave_types)} leave types from the database.")
            return leave_types
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error occurred while retrieving leave types: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def get_leave_type_by_id(self, leave_type_id: int) -> LeaveType:
        """
        Retrieve a specific leave type by its ID.

        Args:
            leave_type_id (int): The ID of the leave type.

        Returns:
            LeaveType: The LeaveType object with the specified ID, or None if not found.
        """
        try:
            leave_type = self.db_session.query(LeaveType).get(leave_type_id)
            if not leave_type:
                logging_helper.log_info(f"Leave type with ID {leave_type_id} not found.")
                raise HTTPException(status_code=404, detail="Leave type not found.")
            return leave_type
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error occurred while retrieving leave type: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def delete_leave_type(self, leave_type_id: int) -> bool:
        """
        Delete a leave type from the database.

        Args:
            leave_type_id (int): The ID of the leave type to delete.

        Returns:
            bool: True if the leave type was successfully deleted, False otherwise.
        """
        try:
            leave_type = self.db_session.query(LeaveType).get(leave_type_id)
            if leave_type:
                self.db_session.delete(leave_type)
                self.db_session.commit()
                logging_helper.log_info(f"Leave type with ID {leave_type_id} has been deleted.")
                return True
            else:
                logging_helper.log_info(f"Leave type with ID {leave_type_id} not found.")
                return False
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error occurred while deleting leave type: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def update_leave_type(self, leave_type_id: int, name: str, description: str) -> LeaveType:
        """
        Update a leave type in the database.

        Args:
            leave_type_id (int): The ID of the leave type to update.
            name (str): The new name of the leave type.
            description (str): The new description of the leave type.

        Returns:
            LeaveType: The updated LeaveType object, or None if not found.
        """
        try:
            leave_type = self.db_session.query(LeaveType).get(leave_type_id)
            if leave_type:
                leave_type.name = name
                leave_type.description = description
                self.db_session.commit()
                self.db_session.refresh(leave_type)
                logging_helper.log_info(f"Leave type with ID {leave_type_id} has been updated.")
                return leave_type
            else:
                logging_helper.log_info(f"Leave type with ID {leave_type_id} not found.")
                return None
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error occurred while updating leave type: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

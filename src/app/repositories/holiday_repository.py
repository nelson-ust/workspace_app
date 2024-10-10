# import datetime
# from typing import Optional, List
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from models.all_models import PublicHoliday, Employee
# from fastapi import HTTPException
# from auth.email import send_email
# from logging_helpers import logging_helper
# from auth.email import notify_holiday_creation  # Import the function from email.py


# class HolidayRepository:
#     def __init__(self, db_session: Session):
#         """
#         Initialize the HolidayRepository with a database session.
        
#         Args:
#             db_session (Session): SQLAlchemy session object.
#         """
#         self.db_session = db_session


#     def create_holiday(self, holiday_data: dict) -> PublicHoliday:
#         """
#         Create a new holiday record in the database and send an email notification to all employees with the CEO in copy.

#         Args:
#             holiday_data (dict): Dictionary containing the holiday data to be inserted.

#         Returns:
#             PublicHoliday: The newly created PublicHoliday object.

#         Raises:
#             HTTPException: If there is any error during the process.
#         """
#         try:
#             # Check if a holiday with the same date already exists
#             existing_holiday = self.db_session.query(PublicHoliday).filter(
#                 PublicHoliday.date == holiday_data.get('date'),
#                 PublicHoliday.is_active == True
#             ).first()

#             if existing_holiday:
#                 raise HTTPException(
#                     status_code=400,
#                     detail=f"A holiday with the date {holiday_data.get('date').date()} already exists."
#                 )

#             # Create a new holiday record
#             new_holiday = PublicHoliday(**holiday_data)
#             self.db_session.add(new_holiday)
#             self.db_session.commit()
#             self.db_session.refresh(new_holiday)

#             # Fetch all employees and the CEO
#             employees = self.db_session.query(Employee).filter(Employee.is_active == True).all()
#             ceo = self.db_session.query(Employee).filter(Employee.is_ceo == True, Employee.is_active == True).first()

#             if not ceo:
#                 raise HTTPException(status_code=404, detail="CEO not found in the database.")

#             ceo_email = ceo.employee_email

#             # Prepare the list of recipient emails
#             email_recipients = [employee.employee_email for employee in employees]

#             # Call the email notification function
#             notify_holiday_creation(
#                 recipients=email_recipients,
#                 holiday_name=new_holiday.name,
#                 holiday_date=new_holiday.date,
#                 holiday_description=new_holiday.description,
#                 ceo_email=ceo_email
#             )
            
#             return new_holiday

#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error occurred while creating holiday: {e}")
#             raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
#         except HTTPException as he:
#             logging_helper.log_error(f"Validation error: {he.detail}")
#             raise
#         except Exception as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Unexpected error: {e}")
#             raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


#     def get_all_holidays(self) -> List[PublicHoliday]:
#         """
#         Retrieve all holiday records from the database.
        
#         Returns:
#             list[PublicHoliday]: A list of all PublicHoliday objects.

#         Raises:
#             HTTPException: If there is any error during the process.
#         """
#         try:
#             holidays = self.db_session.query(PublicHoliday).filter(PublicHoliday.is_active == True).all()
#             logging_helper.log_info(f"Retrieved {len(holidays)} holidays from the database.")
#             return holidays
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error occurred while retrieving holidays: {e}")
#             raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

#     def delete_holiday(self, holiday_id: int) -> bool:
#         """
#         Delete a holiday record from the database.
        
#         Args:
#             holiday_id (int): The ID of the holiday to be deleted.
        
#         Returns:
#             bool: True if the holiday was successfully deleted, False otherwise.
        
#         Raises:
#             HTTPException: If there is any error during the process.
#         """
#         try:
#             holiday = self.db_session.query(PublicHoliday).filter(PublicHoliday.id == holiday_id, PublicHoliday.is_active == True).first()
#             if holiday:
#                 holiday.is_active = False  # Soft delete the holiday
#                 holiday.date_deleted = datetime.datetime.utcnow()  # Set the deletion date
#                 self.db_session.commit()
#                 logging_helper.log_info(f"Holiday with ID {holiday_id} has been soft-deleted.")
#                 return True
#             else:
#                 logging_helper.log_info(f"Holiday with ID {holiday_id} not found.")
#                 return False
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error occurred while deleting holiday: {e}")
#             raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

#     def update_holiday(self, holiday_id: int, update_data: dict) -> Optional[PublicHoliday]:
#         """
#         Update a holiday record in the database.
        
#         Args:
#             holiday_id (int): The ID of the holiday to be updated.
#             update_data (dict): Dictionary containing the fields to update.
        
#         Returns:
#             PublicHoliday: The updated PublicHoliday object, or None if not found.
        
#         Raises:
#             HTTPException: If there is any error during the process.
#         """
#         try:
#             holiday = self.db_session.query(PublicHoliday).filter(PublicHoliday.id == holiday_id, PublicHoliday.is_active == True).first()
#             if holiday:
#                 for key, value in update_data.items():
#                     setattr(holiday, key, value)
#                 holiday.date_updated = datetime.datetime.utcnow()  # Update the last updated date
#                 self.db_session.commit()
#                 self.db_session.refresh(holiday)
#                 logging_helper.log_info(f"Holiday with ID {holiday_id} has been updated.")
#                 return holiday
#             else:
#                 logging_helper.log_info(f"Holiday with ID {holiday_id} not found.")
#                 return None
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error occurred while updating holiday: {e}")
#             raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



#repositories/holiday_repository.py
import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.all_models import PublicHoliday, Employee
from fastapi import HTTPException
from logging_helpers import logging_helper

class HolidayRepository:
    def __init__(self, db_session: Session):
        """
        Initialize the HolidayRepository with a database session.
        
        Args:
            db_session (Session): SQLAlchemy session object.
        """
        self.db_session = db_session

    def create_holiday(self, holiday_data: dict) -> PublicHoliday:
        """
        Create a new holiday record in the database.

        Args:
            holiday_data (dict): Dictionary containing the holiday data to be inserted.

        Returns:
            PublicHoliday: The newly created PublicHoliday object.

        Raises:
            HTTPException: If there is any error during the process.
        """
        try:
            # Check if a holiday with the same date already exists
            existing_holiday = self.db_session.query(PublicHoliday).filter(
                PublicHoliday.date == holiday_data.get('date'),
                PublicHoliday.is_active == True
            ).first()

            if existing_holiday:
                raise HTTPException(
                    status_code=400,
                    detail=f"A holiday with the date {holiday_data.get('date').date()} already exists."
                )

            # Create a new holiday record
            new_holiday = PublicHoliday(**holiday_data)
            self.db_session.add(new_holiday)
            self.db_session.commit()
            self.db_session.refresh(new_holiday)

            logging_helper.log_info(f"Created a new holiday with ID {new_holiday.id}.")
            return new_holiday

        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error occurred while creating holiday: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

    def get_all_holidays(self) -> List[PublicHoliday]:
        """
        Retrieve all holiday records from the database.
        
        Returns:
            list[PublicHoliday]: A list of all PublicHoliday objects.

        Raises:
            HTTPException: If there is any error during the process.
        """
        try:
            holidays = self.db_session.query(PublicHoliday).filter(PublicHoliday.is_active == True).all()
            logging_helper.log_info(f"Retrieved {len(holidays)} holidays from the database.")
            return holidays
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error occurred while retrieving holidays: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def delete_holiday(self, holiday_id: int) -> bool:
        """
        Delete a holiday record from the database.
        
        Args:
            holiday_id (int): The ID of the holiday to be deleted.
        
        Returns:
            bool: True if the holiday was successfully deleted, False otherwise.
        
        Raises:
            HTTPException: If there is any error during the process.
        """
        try:
            holiday = self.db_session.query(PublicHoliday).filter(PublicHoliday.id == holiday_id, PublicHoliday.is_active == True).first()
            if holiday:
                holiday.is_active = False  # Soft delete the holiday
                holiday.date_deleted = datetime.datetime.utcnow()  # Set the deletion date
                self.db_session.commit()
                logging_helper.log_info(f"Holiday with ID {holiday_id} has been soft-deleted.")
                return True
            else:
                logging_helper.log_info(f"Holiday with ID {holiday_id} not found.")
                return False
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error occurred while deleting holiday: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def update_holiday(self, holiday_id: int, update_data: dict) -> Optional[PublicHoliday]:
        """
        Update a holiday record in the database.
        
        Args:
            holiday_id (int): The ID of the holiday to be updated.
            update_data (dict): Dictionary containing the fields to update.
        
        Returns:
            PublicHoliday: The updated PublicHoliday object, or None if not found.
        
        Raises:
            HTTPException: If there is any error during the process.
        """
        try:
            holiday = self.db_session.query(PublicHoliday).filter(PublicHoliday.id == holiday_id, PublicHoliday.is_active == True).first()
            if holiday:
                for key, value in update_data.items():
                    setattr(holiday, key, value)
                holiday.date_updated = datetime.datetime.utcnow()  # Update the last updated date
                self.db_session.commit()
                self.db_session.refresh(holiday)
                logging_helper.log_info(f"Holiday with ID {holiday_id} has been updated.")
                return holiday
            else:
                logging_helper.log_info(f"Holiday with ID {holiday_id} not found.")
                return None
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error occurred while updating holiday: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def get_employees_and_ceo(self):
        """
        Fetch all active employees with employee_type_id of 1 and the CEO.

        Returns:
            tuple: A tuple containing a list of employees and the CEO object.
        """
        try:
            employees = self.db_session.query(Employee).filter(Employee.is_active == True, Employee.employee_type_id == 1).all()
            ceo = self.db_session.query(Employee).filter(Employee.is_ceo == True, Employee.is_active == True).first()

            if not ceo:
                raise HTTPException(status_code=404, detail="CEO not found in the database.")
            
            return employees, ceo

        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error occurred while fetching employees and CEO: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

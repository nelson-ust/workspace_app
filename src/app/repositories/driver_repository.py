
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from db.query_builder import QueryBuilder
from schemas.driver_schemas import DriverCreate, DriverRead, DriverUpdate
from models.all_models import Driver, Tenancy, User, Employee
from repositories.base_repository import BaseRepository
from sqlalchemy.exc import SQLAlchemyError
from typing import Any, Dict, Optional, List
import logging
from logging_helpers import logging_helper
from datetime import date, datetime


class DriverRepository(BaseRepository[Driver, DriverCreate, DriverUpdate]):

    def __init__(self, db_session: Session):
        super().__init__(Driver, db_session)

    def create_driver(self, driver_data: DriverCreate) -> Driver:
        """
        Creates a new Driver ensuring that the licence_plate is unique within the Driver table.
        """
        driver_existence = (
            self.db_session.query(Driver)
            .filter(Driver.licence_number == driver_data.licence_number)
            .first()
        )
        if driver_existence:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The Driver with the licence_number {driver_data.licence_number} already exists ",
            )

        try:
            return self.create(driver_data)
        except Exception as err:
            logging_helper.log_error(
                message=f"Database Error during Vehicle creation {err}"
            )


    def get_all_driver(self, skip: int = 0, limit: int = 100) -> List[DriverRead]:
        """
        Retrieves all Driver that are active with optional pagination.
        """
        try:
            drivers = self.db_session.query(Driver).filter(
                Driver.is_active == True
            ).options(
                joinedload(Driver.user).joinedload(User.employee)
            ).offset(skip).limit(limit).all()

            # Include the full names of the drivers
            driver_list = [
                DriverRead(
                    id=driver.id,
                    user_id=driver.user_id,
                    licence_number=driver.licence_number,
                    licence_exp_date=driver.licence_exp_date,
                    tenancy_id=driver.tenancy_id,
                    is_available=driver.is_available,
                    full_name=f"{driver.user.employee.first_name} {driver.user.employee.last_name}" if driver.user and driver.user.employee else "N/A"
                )
                for driver in drivers
            ]
            return driver_list
        except Exception as err:
            logging_helper.log_error(message=f"Failed to retrieve Driver records")

    def get_all_driver_for_tenancy(
        self, tenancy_id: int, skip: int = 0, limit: int = 100
    ) -> List[DriverRead]:
        """
        Retrieves all Driver that are active with optional pagination.
        """
        tenancy_exist = (
            self.db_session.query(Tenancy).filter(Tenancy.id == tenancy_id).first()
        )
        if not tenancy_exist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The Tenancy ID {tenancy_id} does not exist",
            )

        try:
            drivers = self.db_session.query(Driver).filter(
                Driver.tenancy_id == tenancy_id, Driver.is_active == True
            ).options(
                joinedload(Driver.user).joinedload(User.employee)
            ).offset(skip).limit(limit).all()

            # Include the full names of the drivers
            driver_list = [
                DriverRead(
                    id=driver.id,
                    user_id=driver.user_id,
                    licence_number=driver.licence_number,
                    licence_exp_date=driver.licence_exp_date,
                    tenancy_id=driver.tenancy_id,
                    is_available=driver.is_available,
                    full_name=f"{driver.user.employee.first_name} {driver.user.employee.last_name}" if driver.user and driver.user.employee else "N/A"
                )
                for driver in drivers
            ]
            return driver_list
        except Exception as err:
            logging_helper.log_error(message=f"Failed to retrieve Driver records")


    def get_driver_by_id(self, driver_id) -> Optional[DriverRead]:
        """
        Retrieves a Driver by its ID.
        """
        try:
            driver = self.db_session.query(Driver).filter(
                Driver.id == driver_id, Driver.is_active == True
            ).options(
                joinedload(Driver.user).joinedload(User.employee)
            ).first()

            if not driver:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Driver with ID {driver_id} not found.",
                )

            driver_data = DriverRead(
                id=driver.id,
                user_id=driver.user_id,
                licence_number=driver.licence_number,
                licence_exp_date=driver.licence_exp_date,
                tenancy_id=driver.tenancy_id,
                is_available=driver.is_available,
                full_name=f"{driver.user.employee.first_name} {driver.user.employee.last_name}" if driver.user and driver.user.employee else "N/A"
            )
            return driver_data
        except Exception as err:
            logging_helper.log_error(message=f"Failed to retrieve Driver record")


    def get_driver_by_id_for_tenancy(self, driver_id, tenancy_id) -> Optional[DriverRead]:
        """
        Retrieves a Driver by its ID for a specific tenancy.
        """
        try:
            driver = self.db_session.query(Driver).filter(
                Driver.id == driver_id, Driver.tenancy_id == tenancy_id, Driver.is_active == True
            ).options(
                joinedload(Driver.user).joinedload(User.employee)
            ).first()

            if not driver:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Driver with ID {driver_id} not found in the specified tenancy.",
                )

            driver_data = DriverRead(
                id=driver.id,
                user_id=driver.user_id,
                licence_number=driver.licence_number,
                licence_exp_date=driver.licence_exp_date,
                tenancy_id=driver.tenancy_id,
                is_available=driver.is_available,
                full_name=f"{driver.user.employee.first_name} {driver.user.employee.last_name}" if driver.user and driver.user.employee else "N/A"
            )
            return driver_data
        except HTTPException as err:
            logging_helper.log_error(message=f"Failed to retrieve Driver record")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


    def get_driver_by_licence_number(
        self, licence_number: str, tenancy_id: Optional[int] = None
    ) -> Optional[DriverRead]:
        """
        Retrieves a Driver using unique licence_number.
        """
        try:
            driver = self.db_session.query(Driver)
            if tenancy_id:
                driver = driver.filter(
                    Driver.is_active == True,
                    Driver.licence_number == licence_number,
                    Driver.tenancy_id == tenancy_id,
                ).first()
            else:
                driver = driver.filter(
                    Driver.is_active == True, Driver.licence_number == licence_number
                ).first()

            if driver:
                driver_data = DriverRead(
                    id=driver.id,
                    user_id=driver.user_id,
                    licence_number=driver.licence_number,
                    licence_exp_date=driver.licence_exp_date,
                    tenancy_id=driver.tenancy_id,
                    is_available=driver.is_available,
                    full_name=f"{driver.user.employee.first_name} {driver.user.employee.last_name}" if driver.user and driver.user.employee else "N/A"
                )
                return driver_data
            return None
        except Exception as err:
            logging_helper.log_error(message=f"Failed to retrieve Driver record")

    def get_driver_by_licence_expiration_date(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[str] = None,
        tenancy_id: Optional[int] = None,
    ) -> List[DriverRead]:
        """
        Retrieves Drivers records for licence expiration tracking.
        """
        try:
            driver_exp = self.db_session.query(Driver)
            if not tenancy_id:
                driver_exp = driver_exp.filter(
                    Driver.is_active == True,
                    Driver.licence_exp_date.between(start_date, end_date),
                ).all()
            else:
                driver_exp = driver_exp.filter(
                    Driver.tenancy_id == tenancy_id,
                    Driver.is_active == True,
                    Driver.licence_exp_date.between(start_date, end_date),
                ).all()

            driver_list = [
                DriverRead(
                    id=driver.id,
                    user_id=driver.user_id,
                    licence_number=driver.licence_number,
                    licence_exp_date=driver.licence_exp_date,
                    tenancy_id=driver.tenancy_id,
                    is_available=driver.is_available,
                    full_name=f"{driver.user.employee.first_name} {driver.user.employee.last_name}" if driver.user and driver.user.employee else "N/A"
                )
                for driver in driver_exp
            ]
            return driver_list
        except Exception as err:
            logging_helper.log_error(message=f"Failed to retrieve Driver record {str(err)}")

            
    def update_driver(
        self,
        driver_id: int,
        driver_data: DriverUpdate,
        tenancy_id: Optional[int] = None,
    ) -> Driver:
        """
        Updates an existing Driver.
        """
        try:
            if tenancy_id:
                driver = self.db_session.query(
                    Driver).filter(Driver.tenancy_id==tenancy_id, Driver.id==driver_id
                ).first()
                if not driver:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The driver with id {driver_id} does not exist or not in your state",
                    )
            else:
                driver = self.db_session.query(
                    Driver).filter(Driver.id==driver_id
                ).first()
                if not driver:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The driver with id {driver_id} does not exist or not in your state",
                    )
            # Structure the Driver Update data to forma dictionary
            update_driver_data = driver_data.model_dump(exclude_unset=True)

            for key, value in update_driver_data.items():
                setattr(driver, key, value)

            self.db_session.commit()
            self.db_session.refresh(driver)

            return {f"detail : The driver with ID {driver.id} updated successfully"}

        except SQLAlchemyError as err:
            logging.error(f"Database Error during Driver Update {err}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Check the update Driver route {str(err)}",
            )


    def delete_hard_driver(
        self, driver_id: int, hard_delete: bool = True, tenancy_id: Optional[int] = None
    ) -> Optional[Driver]:
        """
        Deletes a Driver by ID based on the hard_delete flag.
        """
        try:
            if tenancy_id:
                db_driver = self.get_driver_by_id_for_tenancy(
                    driver_id=driver_id, tenancy_id=tenancy_id
                )
                if not db_driver:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The driver with id {driver_id} does not exist or not in your state",
                    )
            else:
                db_driver = self.get_driver_by_id(driver_id=driver_id)
                if not db_driver:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The driver with id {driver_id} does not exist",
                    )

            if hard_delete:
                return self.delete_hard(driver_id)
            else:
                return self.soft_delete(driver_id)

        except Exception as err:
            logging_helper.log_error(message=f"{str(err)}")
            

    def soft_delete_driver(
        self, driver_id: int, tenancy_id: Optional[int] = None
    ) -> Driver:
        """
        Soft deletes a driver by setting its is_active flag to False.
        """
        if tenancy_id:
            driver = self.db_session.query(
                Driver).filter(Driver.tenancy_id==tenancy_id, Driver.id==driver_id
            ).first()
            if not driver:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"The driver with id {driver_id} does not exist or not in your state",
                )
        else:
            driver = self.db_session.query(
                Driver).filter(Driver.id==driver_id
            ).first()
            if not driver:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"The driver with id {driver_id} does not exist",
                )
            
        if not driver.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Driver {driver_id} is already deactivated",
            )
        
        try:
            driver.is_active = False
            return driver
        except SQLAlchemyError as err:
            logging.error(f"Error soft deleting Driver: {err}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to soft delete Driver",
            )

    def restore_driver(self, driver_id: int, tenancy_id: Optional[int] = None):
        """
        Soft restoring a driver by setting its is_active flag to True.
        """
        if tenancy_id:
            driver = self.db_session.query(
                Driver).filter(Driver.tenancy_id==tenancy_id, Driver.id==driver_id
            ).first()
            if not driver:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"The driver with id {driver_id} does not exist or not in your state",
                )
        else:
            driver = self.db_session.query(
                Driver).filter(Driver.id==driver_id
            ).first()
            if not driver:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"The driver with id {driver_id} does not exist",
                )
            
        if driver.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Driver {driver_id} is already active",
            )

        try:
            driver.is_active = True
            return driver
        except SQLAlchemyError as err:
            logging.error(f"Error restoring Driver: {err}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to restore Driver",
            )


    def custom_query(self, filters: Optional[Dict[str, Any]] = None, order_by: Optional[List[str]] = None, 
                     limit: Optional[int] = None, offset: Optional[int] = None, join_tables: Optional[List[str]] = None) -> List[Driver]:
        try:
            logging_helper.log_info("Starting custom query.")
            query_builder = QueryBuilder(self.db_session, Driver)

            # Map join_tables to actual models
            join_models = []
            if join_tables:
                for table_name in join_tables:
                    if table_name == "User":
                        join_models.append(User)
                    elif table_name == "Employee":
                        join_models.append(Employee)
                    # Add more models as needed

            query_builder = query_builder.join(join_models) if join_models else query_builder
            query_builder = query_builder.filter(filters) if filters else query_builder
            query_builder = query_builder.order_by(order_by) if order_by else query_builder
            query_builder = query_builder.limit(limit) if limit else query_builder
            query_builder = query_builder.offset(offset) if offset else query_builder

            drivers = query_builder.build()
            logging_helper.log_info(f"Custom query executed successfully: {drivers}")
            return drivers
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Database error during custom query: {str(e)}")
            raise
        except Exception as e:
            logging_helper.log_error(f"Error during custom query: {str(e)}")
            raise



    def update_driver_availability(self, driver_id: int, is_available: bool) -> Optional[DriverRead]:
        """
        Updates the availability status of a driver.
        """
        try:
            driver = self.db_session.query(Driver).filter(Driver.id == driver_id).options(
                joinedload(Driver.user).joinedload(User.employee)
            ).first()

            if not driver:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Driver with ID {driver_id} not found.")

            driver.is_available = is_available
            self.db_session.commit()

            driver_data = DriverRead(
                id=driver.id,
                user_id=driver.user_id,
                licence_number=driver.licence_number,
                licence_exp_date=driver.licence_exp_date,
                tenancy_id=driver.tenancy_id,
                is_available=driver.is_available,
                full_name=f"{driver.user.employee.first_name} {driver.user.employee.last_name}" if driver.user and driver.user.employee else "N/A"
            )
            return driver_data
        except SQLAlchemyError as err:
            self.db_session.rollback()
            logging_helper.log_error(f"Error updating driver availability: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error updating driver availability: {err}")
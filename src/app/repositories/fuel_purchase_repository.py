import datetime
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from schemas.fuel_purchase_schemas import FuelPurchaseCreate, FuelPurchaseUpdate
from models.all_models import FuelPurchase, Tenancy, Vehicle
from repositories.base_repository import BaseRepository
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from datetime import date
import logging, os, shutil
from sqlalchemy.exc import SQLAlchemyError, NoResultFound, MultipleResultsFound


class FuelPurchaseRepository(
    BaseRepository[FuelPurchase, FuelPurchaseCreate, FuelPurchaseUpdate]
):
    def __init__(self, db_session: Session):
        super().__init__(FuelPurchase, db_session)



    def fuel_purchase_create(
        self,
        vehicle_id: int,
        driver_id: int,
        quantity: float,
        unit_cost: float,
        purchase_date: date,
        tenancy_id: Optional[int],
        file: UploadFile,
    ):
        try:
            # Validate quantity and unit_cost to be positive floats
            if not isinstance(quantity, float) or quantity <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The quantity must be a positive float.",
                )

            if not isinstance(unit_cost, float) or unit_cost <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The unit cost must be a positive float.",
                )

            # Check if fuel purchase already exists
            fuelPurchase = (
                self.db_session.query(FuelPurchase)
                .filter(
                    FuelPurchase.purchase_date == purchase_date,
                    FuelPurchase.vehicle_id == vehicle_id,
                )
                .first()
            )
            if fuelPurchase:
                vehicle = self.db_session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"The fuel has already been purchased for this vehicle with name: {vehicle.name} and plate number: {vehicle.licence_plate} today  - {datetime.datetime.now().date()}",
                )

            # Check if tenancy exists
            tenancy_existence = (
                self.db_session.query(Tenancy)
                .filter(Tenancy.id == tenancy_id, Tenancy.is_active == True)
                .first()
            )
            if not tenancy_existence:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The Tenancy ID supplied does not exist.",
                )

            # Ensure the directory for storing files exists
            file_directory = "./fuel_purchase_documents"
            os.makedirs(file_directory, exist_ok=True)

            # Save the file
            file_location = f"{file_directory}/{file.filename}"

            # Convert file types to .png extension
            if not file.filename.endswith(".png"):
                base_name, extension = os.path.splitext(file.filename)
                new_extension = ".png"
                new_filename = base_name + new_extension
                file_location = f"{file_directory}/{new_filename}"

            with open(file_location, "wb") as file_object:
                shutil.copyfileobj(file.file, file_object)
            file.file.close()

            # Create fuel purchase record
            fuel_purchase = FuelPurchase(
                vehicle_id=vehicle_id,
                driver_id=driver_id,
                quantity=quantity,
                unit_cost=unit_cost,
                total_cost=float(quantity * unit_cost),
                purchase_date=purchase_date,
                tenancy_id=tenancy_id,
                file_path=file_location,
            )
            self.db_session.add(fuel_purchase)
            self.db_session.commit()
            return fuel_purchase

        except SQLAlchemyError as err:
            logging.error(f"Creation of fuel purchase failed: {err}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating fuel purchase: {str(err)}",
            )

    def get_all_fuel_purchase(
        self,
        skip: int = 0,
        limit: int = 100,
        tenancy_id: Optional[int] = None,
        driver_id: Optional[int] = None,
    ) -> FuelPurchase:
        try:
            ##For Admin, Chief Driver and Tenant Admin to map all Fuel Purchase for the state
            if tenancy_id and not driver_id:
                fuel_purchase = (
                    self.db_session.query(FuelPurchase)
                    .filter(
                        FuelPurchase.is_active == True,
                        FuelPurchase.tenancy_id == tenancy_id,
                    )
                    .offset(offset=skip)
                    .limit(limit=limit)
                    .all()
                )
                return fuel_purchase

            ##For Driver mapping only the Fuel Purchase of the Logged in Driver
            elif tenancy_id and driver_id:
                fuel_purchase = (
                    self.db_session.query(FuelPurchase)
                    .filter(
                        FuelPurchase.is_active == True,
                        FuelPurchase.tenancy_id == tenancy_id,
                        FuelPurchase.driver_id == driver_id,
                    )
                    .offset(offset=skip)
                    .limit(limit=limit)
                    .all()
                )
                return fuel_purchase

            ##For Super Admin mapping all the Fuel Purchase for the 3 States
            else:
                fuel_purchase = (
                    self.db_session.query(FuelPurchase)
                    .filter(FuelPurchase.is_active == True)
                    .offset(offset=skip)
                    .limit(limit=limit)
                    .all()
                )
                return fuel_purchase
        except SQLAlchemyError as err:
            logging.error(f"Error fetching all the FuelPurchase.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"There is error due to {str(err)}",
            )

    def get_fuel_purchase_by_id(
        self,
        fuel_purchase_id: int,
        tenancy_id: Optional[int] = None,
        driver_id: Optional[int] = None,
    ) -> FuelPurchase:
        """
        Retrieves a Fuel Purchase by its ID.
        """
        try:
            ##For Admin, Chief Driver and Tenant Admin to map all Fuel Purchase for the state
            if tenancy_id and not driver_id:
                fuel_purchase = (
                    self.db_session.query(FuelPurchase)
                    .filter(
                        FuelPurchase.is_active == True,
                        FuelPurchase.tenancy_id == tenancy_id,
                        FuelPurchase.id == fuel_purchase_id,
                    )
                    .first()
                )
                if not fuel_purchase:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The FuelPurchase ID {fuel_purchase_id} supplied does not exist or not in your state",
                    )
                return fuel_purchase

            ##For Driver mapping only the Fuel Purchase of the Logged in Driver
            elif tenancy_id and driver_id:
                fuel_purchase = (
                    self.db_session.query(FuelPurchase)
                    .filter(
                        FuelPurchase.is_active == True,
                        FuelPurchase.tenancy_id == tenancy_id,
                        FuelPurchase.driver_id == driver_id,
                        FuelPurchase.id == fuel_purchase_id,
                    )
                    .first()
                )
                if not fuel_purchase:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The FuelPurchase ID {fuel_purchase_id} supplied does not exist or does not belong to you",
                    )
                return fuel_purchase

            ##For Super Admin mapping all the Fuel Purchase for the 3 States
            else:
                fuel_purchase = (
                    self.db_session.query(FuelPurchase)
                    .filter(
                        FuelPurchase.is_active == True,
                        FuelPurchase.id == fuel_purchase_id,
                    )
                    .first()
                )
                if not fuel_purchase:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The FuelPurchase ID {fuel_purchase_id} supplied does not exist",
                    )
                return fuel_purchase
        except SQLAlchemyError as err:
            logging.error(f"Error fetching the specific fuel_purchase")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"There is error due to {str(err)}",
            )

    def update_fuel_purchase(
        self,
        fuel_purchase_id: int,
        fuel_purchase_data: FuelPurchaseUpdate,
        tenancy_id: Optional[int] = None,
        driver_id: Optional[int] = None,
    ) -> FuelPurchase:
        """
        Updates an existing FuelPurchase.
        """
        try:
            ##For Admin, Chief Driver and Tenant Admin to map all Fuel Purchase for the state
            if tenancy_id and not driver_id:
                fuel_purchase = self.get_fuel_purchase_by_id(
                    fuel_purchase_id=fuel_purchase_id, tenancy_id=tenancy_id
                )
                if not fuel_purchase:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The FuelPurchase ID {fuel_purchase_id} supplied does not exist or not in your state",
                    )

            ##For Driver mapping only the Fuel Purchase of the Logged in Driver
            elif tenancy_id and driver_id:
                fuel_purchase = self.get_fuel_purchase_by_id(
                    fuel_purchase_id=fuel_purchase_id,
                    tenancy_id=tenancy_id,
                    driver_id=driver_id,
                )
                if not fuel_purchase:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The FuelPurchase ID {fuel_purchase_id} supplied does not exist",
                    )

            ##For Super Admin mapping all the Fuel Purchase for the 3 States
            else:
                fuel_purchase = self.get_fuel_purchase_by_id(
                    fuel_purchase_id=fuel_purchase_id
                )
                if not fuel_purchase:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The FuelPurchase ID {fuel_purchase_id} supplied does not exist",
                    )

            update_fuel_purchase = self.update(
                db_obj=fuel_purchase, obj_in=fuel_purchase_data
            )
            return update_fuel_purchase
        except SQLAlchemyError as err:
            logging.error(f"Error fetching the specific FuelPurchase.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"There is error due to {str(err)}",
            )

    def delete_hard_fuel_purchase(
        self,
        fuel_purchase_id: int,
        tenancy_id: Optional[int] = None,
        driver_id: Optional[int] = None,
    ):
        try:
            ##For Admin, Chief Driver and Tenant Admin to map all Fuel Purchase for the state
            if tenancy_id and not driver_id:
                fuel_purchase = self.get_fuel_purchase_by_id(
                    fuel_purchase_id=fuel_purchase_id, tenancy_id=tenancy_id
                )
                if not fuel_purchase:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The FuelPurchase ID {fuel_purchase_id} supplied does not exist or not in your state",
                    )

            ##For Driver mapping only the Fuel Purchase of the Logged in Driver
            elif tenancy_id and driver_id:
                fuel_purchase = self.get_fuel_purchase_by_id(
                    fuel_purchase_id=fuel_purchase_id,
                    tenancy_id=tenancy_id,
                    driver_id=driver_id,
                )
                if not fuel_purchase:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The FuelPurchase ID {fuel_purchase_id} supplied does not exist or does not belong to you",
                    )

            ##For Super Admin mapping all the Fuel Purchase for the 3 States
            else:
                fuel_purchase = (
                    self.db_session.query(FuelPurchase)
                    .filter(
                        FuelPurchase.is_active == True,
                        FuelPurchase.id == fuel_purchase_id,
                    )
                    .first()
                )
                if not fuel_purchase:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The FuelPurchase ID {fuel_purchase_id} supplied does not exist",
                    )

            self.db_session.delete(fuel_purchase)
            self.db_session.commit()
            return fuel_purchase_id
        except SQLAlchemyError as err:
            logging.error(f"Error hard deleting the specific FuelPurchase.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"There is error deleting FuelPurchase due to {str(err)}",
            )

    def soft_delete_fuel_purchase(
        self,
        fuel_purchase_id: int,
        tenancy_id: Optional[int] = None,
        driver_id: Optional[int] = None,
    ):
        try:
            ##For Admin, Chief Driver and Tenant Admin to map all Fuel Purchase for the state
            if tenancy_id and not driver_id:
                fuel_purchase = (
                    self.db_session.query(FuelPurchase)
                    .filter(
                        FuelPurchase.tenancy_id == tenancy_id,
                        FuelPurchase.id == fuel_purchase_id,
                    )
                    .first()
                )
                if not fuel_purchase:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The FuelPurchase ID {fuel_purchase_id} supplied does not exist or not in your state",
                    )

            ##For Driver mapping only the Fuel Purchase of the Logged in Driver
            elif tenancy_id and driver_id:
                fuel_purchase = (
                    self.db_session.query(FuelPurchase)
                    .filter(
                        FuelPurchase.tenancy_id == tenancy_id,
                        FuelPurchase.driver_id == driver_id,
                        FuelPurchase.id == fuel_purchase_id,
                    )
                    .first()
                )
                if not fuel_purchase:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The FuelPurchase ID {fuel_purchase_id} supplied does not exist or does not belong to you",
                    )

            ##For Super Admin mapping all the Fuel Purchase for the 3 States
            else:
                fuel_purchase = (
                    self.db_session.query(FuelPurchase)
                    .filter(FuelPurchase.id == fuel_purchase_id)
                    .first()
                )
                if not fuel_purchase:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The FuelPurchase ID {fuel_purchase_id} supplied does not exist",
                    )

            if not fuel_purchase.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"The FuelPurchase with ID {fuel_purchase_id} is already deactivated !!!",
                )

            self.soft_delete(id=fuel_purchase_id)
            return {
                f"message : The FuelPurchase with FuelPurchase ID {fuel_purchase_id} has been deactivated successfully!!!"
            }
        except SQLAlchemyError as err:
            logging.error(f"Error hard deleting the specific FuelPurchase.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"There is error deleting FuelPurchase due to {str(err)}",
            )

    def restore_fuel_purchase(
        self,
        fuel_purchase_id: int,
        tenancy_id: Optional[int] = None,
        driver_id: Optional[int] = None,
    ) -> FuelPurchase:
        try:
            ##For Admin, Chief Driver and Tenant Admin to map all Fuel Purchase for the state
            if tenancy_id and not driver_id:
                fuel_purchase = (
                    self.db_session.query(FuelPurchase)
                    .filter(
                        FuelPurchase.tenancy_id == tenancy_id,
                        FuelPurchase.id == fuel_purchase_id,
                    )
                    .first()
                )
                if not fuel_purchase:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The FuelPurchase ID {fuel_purchase_id} supplied does not exist or not in your state",
                    )

            ##For Driver mapping only the Fuel Purchase of the Logged in Driver
            elif tenancy_id and driver_id:
                fuel_purchase = (
                    self.db_session.query(FuelPurchase)
                    .filter(
                        FuelPurchase.tenancy_id == tenancy_id,
                        FuelPurchase.driver_id == driver_id,
                        FuelPurchase.id == fuel_purchase_id,
                    )
                    .first()
                )
                if not fuel_purchase:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The FuelPurchase ID {fuel_purchase_id} supplied does not exist or does not belong to you",
                    )

            ##For Super Admin mapping all the Fuel Purchase for the 3 States
            else:
                fuel_purchase = (
                    self.db_session.query(FuelPurchase)
                    .filter(FuelPurchase.id == fuel_purchase_id)
                    .first()
                )
                if not fuel_purchase:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"The FuelPurchase ID {fuel_purchase_id} supplied does not exist",
                    )

            if fuel_purchase.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"The FuelPurchase with ID {fuel_purchase_id} is already active !!!",
                )

            fuel_purchase.is_active = True
            self.db_session.commit()
            return fuel_purchase
        except SQLAlchemyError as err:
            logging.error(f"Error hard deleting the specific FuelPurchase.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"There is error deleting FuelPurchase due to {str(err)}",
            )


    def get_fuel_purchase_file_path(self, fuel_purchase_id: int) -> str:
        """Retrieve the file path for a given FuelPurchase ID."""
        try:
            # Fetch the FuelPurchase to verify its existence
            fuel_purchase = self.db_session.query(FuelPurchase).filter(FuelPurchase.id == fuel_purchase_id).one_or_none()
            if not fuel_purchase:
                raise ValueError("FuelPurchase not found")

            if not fuel_purchase.file_path:
                raise ValueError("File path for the FuelPurchase is not available.")

            return fuel_purchase.file_path

        except NoResultFound:
            raise Exception("No FuelPurchase found with the given ID.")
        except MultipleResultsFound:
            raise Exception("Multiple entries found. Data inconsistency detected.")
        except Exception as e:
            logging.error(f"An error occurred while retrieving the file path: {str(e)}")
            raise Exception(f"An error occurred while retrieving the file path: {str(e)}")


from sqlalchemy.orm import Session
from models.all_models import TripSpecialLocation
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from logging_helpers import logging_helper

class TripSpecialLocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_trip_special_location_by_id(self, id: int) -> TripSpecialLocation:
        """
        Retrieve a TripSpecialLocation by its ID.
        
        :param id: ID of the TripSpecialLocation
        :return: TripSpecialLocation object if found, else None
        """
        try:
            logging_helper.log_info(f"Fetching TripSpecialLocation with ID: {id}")
            result = self.db.query(TripSpecialLocation).filter(TripSpecialLocation.id == id).first()
            logging_helper.log_info(f"Successfully fetched TripSpecialLocation with ID: {id}")
            return result
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching TripSpecialLocation with ID: {id} - {str(e)}")
            self.db.rollback()
            raise e

    def get_all_trip_special_locations(self, tenancy_ids: List[int]) -> List[TripSpecialLocation]:
        """
        Retrieve all TripSpecialLocations for the given tenancy IDs.
        
        :param tenancy_ids: List of tenancy IDs
        :return: List of TripSpecialLocation objects
        """
        try:
            logging_helper.log_info(f"Fetching all TripSpecialLocations for tenancy IDs: {tenancy_ids}")
            result = self.db.query(TripSpecialLocation).filter(TripSpecialLocation.tenancy_id.in_(tenancy_ids)).all()
            logging_helper.log_info(f"Successfully fetched all TripSpecialLocations for tenancy IDs: {tenancy_ids}")
            return result
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching TripSpecialLocations for tenancy IDs {tenancy_ids} - {str(e)}")
            self.db.rollback()
            raise e

    def create_trip_special_location(self, name: str, description: str, latitude: float, longitude: float, tenancy_id: int) -> dict:#TripSpecialLocation:
        """
        Create a new TripSpecialLocation.
        
        :param name: Name of the TripSpecialLocation
        :param description: Description of the TripSpecialLocation
        :param latitude: Latitude of the TripSpecialLocation
        :param longitude: Longitude of the TripSpecialLocation
        :param tenancy_id: ID of the associated Tenancy
        :return: The created TripSpecialLocation object
        """
        if not (-90 <= latitude <= 90):
            logging_helper.log_error(f"Invalid latitude value: {latitude}")
            raise ValueError("Latitude must be between -90 and 90.")
        if not (-180 <= longitude <= 180):
            logging_helper.log_error(f"Invalid longitude value: {longitude}")
            raise ValueError("Longitude must be between -180 and 180.")


        try:
             # Check if a TripSpecialLocation with the same name and tenancy_id already exists
            existing_location = self.db.query(TripSpecialLocation).filter_by(name=name, tenancy_id=tenancy_id).first()
            if existing_location:
                logging_helper.log_error(f"TripSpecialLocation with name: {name} and tenancy_id: {tenancy_id} already exists.")
                raise ValueError(f"TripSpecialLocation with name: {name} and tenancy_id: {tenancy_id} already exists.")
            
            
            logging_helper.log_info(f"Creating TripSpecialLocation with name: {name}")
            trip_special_location = TripSpecialLocation(
                name=name,
                description=description,
                latitude=latitude,
                longitude=longitude,
                tenancy_id=tenancy_id
            )
            self.db.add(trip_special_location)
            self.db.commit()
            self.db.refresh(trip_special_location)
            logging_helper.log_info(f"Successfully created TripSpecialLocation with name: {name}")
            return {'message':f'Trip Special Location with ID:{trip_special_location.id} Created Successfully!!!'}
        except SQLAlchemyError as e:
            logging_helper.log_error(f"SQLAlchemy error while creating TripSpecialLocation with name: {name} - {str(e)}")
            self.db.rollback()
            raise e
        except Exception as e:
            logging_helper.log_error(f"Unexpected error while creating TripSpecialLocation with name: {name} - {str(e)}")
            self.db.rollback()
            raise e


    def update_trip_special_location(self, id: int, name: str = None, description: str = None, latitude: float = None, longitude: float = None, tenancy_id: int = None) -> TripSpecialLocation:
        """
        Update an existing TripSpecialLocation.
        
        :param id: ID of the TripSpecialLocation to be updated
        :param name: New name (optional)
        :param description: New description (optional)
        :param latitude: New latitude (optional)
        :param longitude: New longitude (optional)
        :param tenancy_id: New tenancy ID (optional)
        :return: The updated TripSpecialLocation object
        """
        try:
            logging_helper.log_info(f"Updating TripSpecialLocation with ID: {id}")
            trip_special_location = self.get_trip_special_location_by_id(id)
            if trip_special_location:
                if name is not None:
                    trip_special_location.name = name
                if description is not None:
                    trip_special_location.description = description
                if latitude is not None:
                    if not (-90 <= latitude <= 90):
                        logging_helper.log_error(f"Invalid latitude value: {latitude}")
                        raise ValueError("Latitude must be between -90 and 90.")
                    trip_special_location.latitude = latitude
                if longitude is not None:
                    if not (-180 <= longitude <= 180):
                        logging_helper.log_error(f"Invalid longitude value: {longitude}")
                        raise ValueError("Longitude must be between -180 and 180.")
                    trip_special_location.longitude = longitude
                if tenancy_id is not None:
                    trip_special_location.tenancy_id = tenancy_id
                self.db.commit()
                self.db.refresh(trip_special_location)
                logging_helper.log_info(f"Successfully updated TripSpecialLocation with ID: {id}")
            return trip_special_location
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error updating TripSpecialLocation with ID: {id} - {str(e)}")
            self.db.rollback()
            raise e
        except Exception as e:
            logging_helper.log_error(f"Unexpected error while updating TripSpecialLocation with ID: {id} - {str(e)}")
            self.db.rollback()
            raise e


    def delete_trip_special_location(self, id: int) -> bool:
        """
        Delete a TripSpecialLocation by its ID.
        
        :param id: ID of the TripSpecialLocation to be deleted
        :return: True if deletion was successful, else False
        """
        try:
            logging_helper.log_info(f"Deleting TripSpecialLocation with ID: {id}")
            trip_special_location = self.get_trip_special_location_by_id(id)
            if trip_special_location:
                self.db.delete(trip_special_location)
                self.db.commit()
                logging_helper.log_info(f"Successfully deleted TripSpecialLocation with ID: {id}")
                return True
            logging_helper.log_info(f"TripSpecialLocation with ID: {id} not found for deletion")
            return False
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error deleting TripSpecialLocation with ID: {id} - {str(e)}")
            self.db.rollback()
            raise e
        except Exception as e:
            logging_helper.log_error(f"Unexpected error while deleting TripSpecialLocation with ID: {id} - {str(e)}")
            self.db.rollback()
            raise e

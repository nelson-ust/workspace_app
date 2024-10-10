
# # repositories/location_repository.py
# from fastapi import HTTPException
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from typing import List, Optional
# from models.all_models import Location, Tenancy  # Ensure imports are correct
# from schemas.location_schemas import LocationCreate, LocationUpdate
# from repositories.base_repository import BaseRepository
# import logging

# class LocationRepository(BaseRepository[Location, LocationCreate, LocationUpdate]):
#     def __init__(self, db_session: Session):
#         super().__init__(Location, db_session)

#     def create_location(self, location_data: LocationCreate) -> Location:
#         """
#         Creates a new location ensuring that the name is unique within the tenancy.
#         """
#         existing_location = self.db_session.query(Location).filter(Location.name == location_data.name, Location.tenancy_id == location_data.tenancy_id).first()
#         if existing_location:
#             raise HTTPException(status_code=400, detail=f"A location with name '{location_data.name}' already exists in this tenancy.")

#         tenancy = self.db_session.query(Tenancy).filter(Tenancy.id == location_data.tenancy_id).first()
#         if not tenancy:
#             raise HTTPException(status_code=400, detail=f"Tenancy ID {location_data.tenancy_id} does not exist.")

#         try:
#             return self.create(location_data)
#         except SQLAlchemyError as e:
#             logging.error(f"Database error during location creation: {e}")
#             raise HTTPException(status_code=500, detail="Database error during location creation")

#     def update_location(self, location_id: int, location_data: LocationUpdate) -> Optional[Location]:
#         """
#         Updates an existing location ensuring that the name is unique within the tenancy.
#         """
#         db_location = self.get_location_by_id(location_id)
#         if not db_location:
#             raise HTTPException(status_code=404, detail="Location not found")

#         if location_data.name and (location_data.name != db_location.name):
#             existing_location = self.db_session.query(Location).filter(Location.name == location_data.name, Location.tenancy_id == db_location.tenancy_id, Location.id != location_id).first()
#             if existing_location:
#                 raise HTTPException(status_code=400, detail=f"A location with name '{location_data.name}' already exists in this tenancy.")

#         try:
#             return self.update(db_location, location_data)
#         except SQLAlchemyError as e:
#             logging.error(f"Database error during location update: {e}")
#             raise HTTPException(status_code=500, detail="Failed to update location due to a database error")

#     # Other methods remain unchanged for brevity

#     # def get_all_locations(self, skip: int = 0, limit: int = 100) -> List[Location]:
#     #     """
#     #     Retrieves all location records with optional pagination.
#     #     """
#     #     try:
#     #         return self.get_all(skip=skip, limit=limit)
#     #     except SQLAlchemyError as e:
#     #         logging.error(f"Error retrieving locations: {e}")
#     #         raise HTTPException(status_code=500, detail="Failed to retrieve locations")

#     # def get_location_by_id(self, location_id: int) -> Optional[Location]:
#     #     """
#     #     Retrieves a location by its ID.
#     #     """
#     #     try:
#     #         return self.get_by_id(location_id)
#     #     except SQLAlchemyError as e:
#     #         logging.error(f"Error retrieving location by ID: {e}")
#     #         raise HTTPException(status_code=500, detail="Failed to retrieve location")

#     # def delete_location(self, location_id: int, hard_delete: bool = False) -> Optional[Location]:
#     #     """
#     #     Deletes or soft deletes a location by ID based on the hard_delete flag.
#     #     """
#     #     try:
#     #         location = self.get_location_by_id(location_id)
#     #         if not location:
#     #             raise HTTPException(status_code=404, detail="Location not found")

#     #         if hard_delete:
#     #             self.delete_hard(location_id)
#     #         else:
#     #             return self.soft_delete(location_id)
#     #     except SQLAlchemyError as e:
#     #         logging.error(f"Error deleting location: {e}")
#     #         raise HTTPException(status_code=500, detail="Failed to delete location")

#     # def soft_delete(self, location_id: int) -> Optional[Location]:
#     #     """
#     #     Soft deletes a location by setting its is_active flag to False.
#     #     """
#     #     location = self.get_location_by_id(location_id)
#     #     if not location:
#     #         raise HTTPException(status_code=404, detail="Location not found")

#     #     if not location.is_active:
#     #         raise HTTPException(status_code=400, detail="Location already deactivated")

#     #     try:
#     #         location.is_active = False
#     #         self.db_session.commit()
#     #         return location
#     #     except SQLAlchemyError as e:
#     #         logging.error(f"Error soft deleting location: {e}")
#     #         self.db_session.rollback()
#     #         raise HTTPException(status_code=500, detail="Failed to soft delete location")

#     # def restore(self, location_id: int) -> Optional[Location]:
#     #     """
#     #     Restores a soft-deleted location by setting its is_active flag to True.
#     #     """
#     #     location = self.get_location_by_id(location_id)
#     #     if not location:
#     #         raise HTTPException(status_code=404, detail="Location not found")

#     #     if location.is_active:
#     #         raise HTTPException(status_code=400, detail="Location is already active")

#     #     try:
#     #         location.is_active = True
#     #         self.db_session.commit()
#     #         return location
#     #     except SQLAlchemyError as e:
#     #         logging.error(f"Error restoring location: {e}")
#     #         self.db_session.rollback()
#     #         raise HTTPException(status_code=500, detail="Failed to restore location")
        
#     # def delete_location(self, location_id: int) -> None:
#     #     """
#     #     Deletes a location record by ID.
#     #     """
#     #     try:
#     #         self.delete_hard(location_id)
#     #     except SQLAlchemyError as e:
#     #         self.db_session.rollback()
#     #         logging.error(f"Database error occurred: {e}")
#     #         raise

#     # def soft_delete(self, location_id: int) -> Optional[Location]:
#     #     """
#     #     Soft delete a location by setting its is_active flag to False.
#     #     """
#     #     location = self.get_by_id(location_id)
#     #     if location:
#     #         location.is_active = False
#     #         self.db_session.commit()
#     #         return location
#     #     return None

#     # def restore(self, location_id: int) -> Optional[Location]:
#     #     """
#     #     Restore a soft-deleted location by setting its is_active flag to True.
#     #     """
#     #     location = self.db_session.query(Location).filter(Location.id == location_id, Location.is_active == False).first()
#     #     if location:
#     #         location.is_active = True
#     #         self.db_session.commit()
#     #         return location
#     #     return None


#     def get_all_locations(self, skip: int = 0, limit: int = 100) -> List[Location]:
#         """
#         Retrieves all location records with optional pagination.
#         """
#         try:
#             return self.get_all(skip=skip, limit=limit)
#         except SQLAlchemyError as e:
#             logging.error(f"Error retrieving locations: {e}")
#             raise HTTPException(status_code=500, detail="Failed to retrieve locations")

#     def get_location_by_id(self, location_id: int) -> Optional[Location]:
#         """
#         Retrieves a location by its ID.
#         """
#         try:
#             return self.get_by_id(location_id)
#         except SQLAlchemyError as e:
#             logging.error(f"Error retrieving location by ID: {e}")
#             raise HTTPException(status_code=500, detail="Failed to retrieve location")

#     def delete_location(self, location_id: int, hard_delete: bool = False) -> Optional[Location]:
#         """
#         Deletes or soft deletes a location by ID based on the hard_delete flag.
#         """
#         try:
#             location = self.get_location_by_id(location_id)
#             if not location:
#                 raise HTTPException(status_code=404, detail="Location not found")

#             if hard_delete:
#                 self.delete_hard(location_id)
#             else:
#                 return self.soft_delete(location_id)
#         except SQLAlchemyError as e:
#             logging.error(f"Error deleting location: {e}")
#             raise HTTPException(status_code=500, detail="Failed to delete location")

#     def soft_delete(self, location_id: int) -> Optional[Location]:
#         """
#         Soft deletes a location by setting its is_active flag to False.
#         """
#         location = self.get_location_by_id(location_id)
#         if not location:
#             raise HTTPException(status_code=404, detail="Location not found")

#         if not location.is_active:
#             raise HTTPException(status_code=400, detail="Location already deactivated")

#         try:
#             location.is_active = False
#             self.db_session.commit()
#             return location
#         except SQLAlchemyError as e:
#             logging.error(f"Error soft deleting location: {e}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail="Failed to soft delete location")

#     def restore(self, location_id: int) -> Optional[Location]:
#         """
#         Restores a soft-deleted location by setting its is_active flag to True.
#         """
#         location = self.get_all_by_id(location_id)
#         # location = self.db_session.query(Location).filter(Location.id==location_id).first()
#         if not location:
#             raise HTTPException(status_code=404, detail="Location not found")

#         if location.is_active:
#             raise HTTPException(status_code=400, detail="Location is already active")

#         try:
#             location.is_active = True
#             self.db_session.commit()
#             return location
#         except SQLAlchemyError as e:
#             logging.error(f"Error restoring location: {e}")
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail="Failed to restore location")




# repositories/location_repository.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from models.all_models import Location, Tenancy  # Ensure imports are correct
from schemas.location_schemas import LocationCreate, LocationUpdate
from repositories.base_repository import BaseRepository
import logging

class LocationRepository(BaseRepository[Location, LocationCreate, LocationUpdate]):
    def __init__(self, db_session: Session):
        super().__init__(Location, db_session)

    def create_location(self, location_data: LocationCreate) -> Location:
        """
        Creates a new location ensuring that the name is unique within the tenancy.
        """
        existing_location = self.db_session.query(Location).filter(Location.name == location_data.name, Location.tenancy_id == location_data.tenancy_id).first()
        if existing_location:
            raise HTTPException(status_code=400, detail=f"A location with name '{location_data.name}' already exists in this tenancy.")

        tenancy = self.db_session.query(Tenancy).filter(Tenancy.id == location_data.tenancy_id).first()
        if not tenancy:
            raise HTTPException(status_code=400, detail=f"Tenancy ID {location_data.tenancy_id} does not exist.")

        try:
            return self.create(location_data)
        except SQLAlchemyError as e:
            logging.error(f"Database error during location creation: {e}")
            raise HTTPException(status_code=500, detail="Database error during location creation")


    def update_location(self, location_id: int, location_data: LocationUpdate) -> Optional[Location]:
        """
        Updates an existing location ensuring that the name is unique within the tenancy.
        """
        db_location = self.get_location_by_id(location_id)
        if not db_location:
            raise HTTPException(status_code=404, detail="Location not found")

        if location_data.name and (location_data.name != db_location.name):
            existing_location = self.db_session.query(Location).filter(Location.name == location_data.name, Location.tenancy_id == db_location.tenancy_id, Location.id != location_id).first()
            if existing_location:
                raise HTTPException(status_code=400, detail=f"A location with name '{location_data.name}' already exists in this tenancy.")

        try:
            db_location.name=location_data.name
            self.db_session.commit()
            self.db_session.refresh(db_location)
            return {"message : The Location Details updated successfully"}
        except SQLAlchemyError as e:
            logging.error(f"Database error during location update: {e}")
            raise HTTPException(status_code=500, detail="Failed to update location due to a database error")


    def get_all_locations(self, skip: int = 0, limit: int = 100, tenancy_id:Optional[int]=None) -> List[Location]:
        """
        Retrieves all location records with optional pagination.
        """
        try:
            locations = self.db_session.query(Location).filter(Location.is_active==True)
            if tenancy_id:
                locations = locations.filter(Location.tenancy_id==tenancy_id)
            locations = locations.all()
            return locations
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving locations: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve locations")


    def get_location_by_id(self, location_id: int, tenancy_id:Optional[int]=None) -> Optional[Location]:
        """
        Retrieves a location by its ID.
        """
        try:
            location = self.db_session.query(Location).filter(Location.is_active==True, Location.id==location_id)
            if tenancy_id:
                location = location.filter(Location.tenancy_id==tenancy_id)

            location = location.first()
            return location
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving location by ID: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve location")


    def delete_location(self, location_id: int, hard_delete: bool = False) -> Optional[Location]:
        """
        Deletes or soft deletes a location by ID based on the hard_delete flag.
        """
        try:
            location = self.get_location_by_id(location_id)
            if not location:
                raise HTTPException(status_code=404, detail="Location not found")

            if hard_delete:
                self.delete_hard(location_id)
            else:
                return self.soft_delete(location_id)
        except SQLAlchemyError as e:
            logging.error(f"Error deleting location: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete location")


    def soft_delete(self, location_id: int) -> Optional[Location]:
        """
        Soft deletes a location by setting its is_active flag to False.
        """
        location = self.db_session.query(Location).filter(Location.id==location_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")

        if not location.is_active:
            raise HTTPException(status_code=400, detail="Location already deactivated")

        try:
            location.is_active = False
            self.db_session.commit()
            return {"detail": "Location deactivated successfully"}
        except SQLAlchemyError as e:
            logging.error(f"Error soft deleting location: {e}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail="Failed to soft delete location")


    def restore(self, location_id: int) -> Optional[Location]:
        """
        Restores a soft-deleted location by setting its is_active flag to True.
        """
        location = self.db_session.query(Location).filter(Location.id==location_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")

        if location.is_active:
            raise HTTPException(status_code=400, detail="Location is already active")

        try:
            location.is_active = True
            self.db_session.commit()
            return {"detail": "Location activated successfully"}
        except SQLAlchemyError as e:
            logging.error(f"Error restoring location: {e}")
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail="Failed to restore location")
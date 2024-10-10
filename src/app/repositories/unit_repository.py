# #repositories/unit_repository.py
# #from fastapi import HTTPException
# from fastapi import HTTPException
# from sqlalchemy import and_, select
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from sqlalchemy.orm import joinedload

# from typing import Any, Dict, List, Optional
# from models.all_models import Department, Unit  # Adjust the import path as necessary
# from schemas.unit_schemas import UnitCreate, UnitUpdate  # Adjust import paths as necessary
# from repositories.base_repository import BaseRepository

# class UnitRepository(BaseRepository[Unit, UnitCreate, UnitUpdate]):
#     def __init__(self, db_session: Session):
#         super().__init__(Unit, db_session)

#     def get_units(self, skip: int = 0, limit: int = 100) -> List[Unit]:
#         try:
#             return super().get_all(skip=skip, limit=limit)
#         except SQLAlchemyError as e:
#             print(f"Database error occurred: {e}")
#             raise

#     def get_unit_by_id(self, unit_id: int) -> Optional[Unit]:
#         try:
#             return super().get_by_id(unit_id)
#         except SQLAlchemyError as e:
#             print(f"Database error occurred: {e}")
#             raise
        
#     def check_unit_name_exists(self, name: str) -> bool:
#         return self.db_session.query(self.model).filter(self.model.name == name).first() is not None


#     def create_unit(self, unit_data: UnitCreate) -> Unit:
#         """
#         Creates a new unit record.
#         """
#         department = self.db_session.query(Department).filter(Department.id == unit_data.department_id).first()
#         if not department:
#             raise HTTPException(status_code=400,details=f"Department ID {unit_data.department_id} does not exist.")
#         try:
#             # Correctly calling .dict() to convert Pydantic model to dictionary
#             return super().create(unit_data)
#         except SQLAlchemyError as e:
#             self.db_session.rollback()  # Ensure transaction is rolled back on error
#             print(f"Database error occurred: {e}")
#             raise HTTPException(status_code=500, detail=f"Database error during Unit creation: {str(e)}")
      
#     def update_unit(self, unit_id: int, unit: UnitUpdate) -> Optional[Unit]:
#         db_unit = self.get_unit_by_id(unit_id)
#         if not db_unit:
#             return None
#         try:
#             return super().update(db_unit, unit)
#         except SQLAlchemyError as e:
#             print(f"Database error occurred: {e}")
#             raise

#     def delete_unit(self, unit_id: int, hard_delete: bool = False) -> Optional[Unit]:
#         try:
#             if hard_delete:
#                 super().delete_hard(unit_id)
#             else:
#                 return super().soft_delete(unit_id)
#         except SQLAlchemyError as e:
#             print(f"Database error occurred: {e}")
#             raise

#     def restore_unit(self, unit_id: int) -> Optional[Unit]:
#         try:
#             return super().restore(unit_id)
#         except SQLAlchemyError as e:
#             print(f"Database error occurred: {e}")
#             raise
    
        
#     # def get_units_by_department_name(self, department_name: str):
#     #     join_conditions = [
#     #         (Unit, Department, Unit.department_id == Department.id)
#     #     ]
#     #     filters = Department.name == department_name
#     #     columns = [Unit.id.label('id'), Unit.name.label('name'), Department.id.label('department_id'), Department.name.label('department_name')]

#     #     try:
#     #         units_info = self.get_multi_join(join_conditions=join_conditions, filters=filters, columns=columns)
#     #         if not units_info:
#     #             raise HTTPException(status_code=404, detail="No units found for the specified department.")
        
#     #         # Adjusted the mapping here
#     #         return [
#     #             {"id": unit.id, "name": unit.name, "department_id": unit.department_id}
#     #             for unit in units_info
#     #         ]
#     #     except SQLAlchemyError as e:
#     #         self.db_session.rollback()
#     #         print(f"Database error occurred: {e}")
#     #         raise HTTPException(status_code=500, detail="Database error")

#     def get_units_by_department_name(self, department_name: str):
#         try:
#             # Perform the join and filter operation directly
#             units_info = self.db_session.query(
#                 Unit.id.label('id'), 
#                 Unit.name.label('name'), 
#                 Department.id.label('department_id'), 
#                 Department.name.label('department_name')
#             ).join(Department, Unit.department_id == Department.id) \
#             .filter(Department.name == department_name) \
#             .all()

#             if not units_info:
#                 raise HTTPException(status_code=404, detail="No units found for the specified department.")

#             # Map the results to a dictionary
#             return [
#                 {
#                     "id": unit.id, 
#                     "name": unit.name, 
#                     "department_id": unit.department_id, 
#                     "department_name": unit.department_name
#                 } for unit in units_info
#             ]
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             print(f"Database error occurred: {e}")
#             raise HTTPException(status_code=500, detail="Database error")




#repositories/unit_repository.py
#from fastapi import HTTPException
from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from typing import Any, Dict, List, Optional
from models.all_models import Department, Unit  # Adjust the import path as necessary
from schemas.unit_schemas import UnitCreate, UnitUpdate  # Adjust import paths as necessary
from repositories.base_repository import BaseRepository
from logging_helpers import logging_helper

class UnitRepository(BaseRepository[Unit, UnitCreate, UnitUpdate]):
    def __init__(self, db_session: Session):
        super().__init__(Unit, db_session)

    def get_units(self, skip: int = 0, limit: int = 100, unit_id:Optional[int]=None) -> List[Unit]:
        try:
            units = self.db_session.query(Unit).filter(Unit.is_active==True)
            if unit_id:
                units=units.filter(Unit.id==unit_id)
            units=units.offset(offset=skip).limit(limit=limit).all()
            return units
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"Database error during getting Unit: {str(e)}")


    def get_unit_by_id(self, unit_id: int, unit_identity:Optional[int]=None) -> Optional[Unit]:
        try:
            unit = self.db_session.query(Unit).filter(Unit.is_active==True, Unit.id==unit_id)
            if unit_identity:
                unit=unit.filter(Unit.id==unit_identity)

            unit = unit.first()
            return unit
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"Database error during getting Unit: {str(e)}")
        

    def check_unit_name_exists(self, name: str) -> bool:
        return self.db_session.query(self.model).filter(self.model.name == name).first() is not None


    def create_unit(self, unit_data: UnitCreate) -> Unit:
        """
        Creates a new unit record.
        """
        department = self.db_session.query(Department).filter(Department.id == unit_data.department_id).first()
        if not department:
            raise HTTPException(status_code=400,details=f"Department ID {unit_data.department_id} does not exist.")
        try:
            # Correctly calling .dict() to convert Pydantic model to dictionary
            return super().create(unit_data)
        except SQLAlchemyError as e:
            self.db_session.rollback()  # Ensure transaction is rolled back on error
            print(f"Database error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"Database error during Unit creation: {str(e)}")
      

    def update_unit(self, unit_id: int, unit: UnitUpdate) -> Optional[Unit]:

        db_unit = self.db_session.query(Unit).filter(Unit.is_active==True, Unit.id==unit_id).first()
        if not db_unit:
            return None
        try:
            db_unit.name=unit.name
            self.db_session.commit()
            self.db_session.refresh(db_unit)
            return {"message : The Unit Details updated successfully"}
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"Database error during Unit Fetching: {str(e)}")


    def delete_unit(self, unit_id: int) -> Optional[Unit]:
        try:
            db_unit = self.db_session.query(Unit).filter(Unit.id==unit_id).first()
            if not db_unit:
                logging_helper.log_error(f"Unit with ID {unit_id} not found.")
                raise HTTPException(status_code=404, detail="Department not found")

            if not db_unit.is_active:
                logging_helper.log_info(f"Unit with ID {unit_id} is already deactivated.")
                raise HTTPException(status_code=400, detail="Unit already deactivated")

            db_unit.is_active=False
            self.db_session.commit()
            self.db_session.refresh(db_unit)
            return {"message : The Unit is deleted successfully"}
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"Database error during Unit Delete: {str(e)}")


    def restore_unit(self, unit_id: int) -> Optional[Unit]:
        try:
            db_unit = self.db_session.query(Unit).filter(Unit.id==unit_id).first()
            if not db_unit:
                logging_helper.log_error(f"Unit with ID {unit_id} not found.")
                raise HTTPException(status_code=404, detail="Department not found")

            if db_unit.is_active:
                logging_helper.log_info(f"Unit with ID {unit_id} is already active.")
                raise HTTPException(status_code=400, detail="Unit already active")

            db_unit.is_active=True
            self.db_session.commit()
            self.db_session.refresh(db_unit)
            return {"message : The Unit is Restored successfully"}
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"Database error during Unit Restoration: {str(e)}")
    

    def get_units_by_department_name(self, department_name: str, department_id:Optional[int]=None):
        try:
            # Perform the join and filter operation directly
            units_info = self.db_session.query(
                Unit.id.label('id'), 
                Unit.name.label('name'), 
                Department.id.label('department_id'), 
                Department.name.label('department_name')
            ).join(Department, Unit.department_id == Department.id) \
            .filter(Department.name == department_name)

            if department_id:
                units_info = units_info.filter(Unit.department_id==department_id)

            units_info = units_info.all()

            if not units_info:
                raise HTTPException(status_code=404, detail="No units found for the specified department.")

            # Map the results to a dictionary
            return [
                {
                    "id": unit.id, 
                    "name": unit.name, 
                    "department_id": unit.department_id, 
                    "department_name": unit.department_name
                } for unit in units_info
            ]
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Database error occurred: {e}")
            raise HTTPException(status_code=500, detail="Database error")

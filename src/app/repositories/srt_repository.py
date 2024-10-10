#repositories/srt_repositorya
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from models.all_models import SRT, Employee, Tenancy  
from schemas.srt_schemas import EmployeeInSRTRead, SRTCreate, SRTUpdate,SRTRead  # Adjust import paths as necessary
from repositories.base_repository import BaseRepository


class SRTRepository(BaseRepository[SRT, SRTCreate,SRTUpdate]):
    def __init__(self, db_session: Session):
        super().__init__(SRT, db_session)
    
    def get_srts(self, skip: int = 0, limit: int = 100) -> List[SRT]:
        try:
            return super().get_all(skip=skip, limit=limit)
        except SQLAlchemyError as e:
            # Handle specific database errors or log them
            print(f"Database error occurred: {e}")
            raise

    def get_srt_by_id(self, srt_id: int) -> Optional[SRT]:
        try:
            return super().get_by_id(srt_id)
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise


    def create_srt(self, srt_data: SRTCreate) -> SRT:
        """
        Creates a new SRT record.
        """
        tenancy = self.db_session.query(Tenancy).filter(Tenancy.id == srt_data.tenancy_id).first()
        if not tenancy:
            raise HTTPException(status_code=400, detail=f"Tenancy ID {srt_data.tenancy_id} does not exist.")
    
        try:
            return super().create(srt_data)
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error during SRT creation: {str(e)}")

    def update_srt(self, role_id: int, role: SRTUpdate) -> Optional[SRT]:
        db_role = self.get_srt_by_id(role_id)
        if not db_role:
            return None
        try:
            return super().update(db_role, role)
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise

    def soft_delete_srt(self, role_id: int) -> Optional[SRT]:
        try:
            return super().soft_delete(role_id)
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise
    
    def restore_srt(self, role_id: int) -> Optional[SRT]:
        try:
            return super().restore(role_id)
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise
    
    # def get_employees_in_srt(self, srt_id: int) -> List[Employee]:
    #     """
    #     Retrieves all employees associated with a specific SRT.

    #     :param srt_id: The ID of the SRT for which to find associated employees.
    #     :return: A list of Employee objects associated with the SRT.
    #     """
    #     try:
    #         srt = self.db_session.query(SRT).filter(SRT.id == srt_id).options(joinedload(SRT.employees)).first()
    #         if srt:
    #             return srt.employees
    #         else:
    #             return []
    #     except SQLAlchemyError as e:
    #         print(f"Database error occurred: {e}")
    #         raise

    def get_employees_in_srt(self, srt_id: int) -> List[EmployeeInSRTRead]:
        """
        Retrieves all employees associated with a specific SRT and returns them
        in a format compatible with the EmployeeInSRTRead schema.
        """
        try:
            srt = self.db_session.query(SRT).filter(SRT.id == srt_id).options(joinedload(SRT.employees)).first()
            if not srt:
                return []
            
            # Convert each Employee ORM object into a dictionary matching EmployeeInSRTRead
            employees_data = [
                {
                    "id": employee.id,
                    "first_name": employee.first_name,
                    "last_name": employee.last_name,
                    "phone_number": employee.phone_number,
                    "department_id": employee.department_id,
                    "unit_id": employee.unit_id,
                    # Add any other fields needed by EmployeeInSRTRead
                }
                for employee in srt.employees
            ]

            # Optionally, convert dictionaries to EmployeeInSRTRead objects if needed
            # employees_data = [EmployeeInSRTRead(**data) for data in employees_data]

            return employees_data
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise
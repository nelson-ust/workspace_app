# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from typing import List, Optional
# from models.all_models import Tenancy  # Adjust the import path as necessary
# from schemas.tenancy_schemas import TenancyCreate, TenancyUpdate  # Adjust import paths as necessary
# from repositories.base_repository import BaseRepository
# from fastapi import HTTPException, status

# class TenancyRepository(BaseRepository[Tenancy, TenancyCreate,TenancyUpdate]):
#     def __init__(self, db_session: Session):
#         super().__init__(Tenancy, db_session)


#     def get_tenancies(self, skip: int = 0, limit: int = 100, tenancy_id:Optional[int]=None) -> Optional[List[Tenancy]]:
#         try:
#             tenancies = self.db_session.query(Tenancy).filter(Tenancy.is_active==True)
#             if tenancy_id:
#                 tenancies = tenancies.filter(Tenancy.id == tenancy_id)
#             tenancies = tenancies.offset(offset=skip).limit(limit=limit).all()
#             return tenancies
#         except SQLAlchemyError as e:
#             print(f"Database error occurred: {e}")
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")


#     def get_tenancy_by_id(self, tenancy_id: int, tenanant_id:Optional[int]=None) -> Optional[Tenancy]:
#         try:
#             tenancy = self.db_session.query(Tenancy).filter(Tenancy.is_active==True, Tenancy.id==tenancy_id)
#             if tenanant_id:
#                 tenancy = tenancy.filter(Tenancy.id == tenanant_id)
#             tenancy = tenancy.first()
#             return tenancy
#         except SQLAlchemyError as e:
#             print(f"Database error occurred: {e}")
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")


#     def create_tenancy(self, tenancy: TenancyCreate) -> Tenancy:
#         try:
#             return super().create(tenancy)
#         except SQLAlchemyError as e:
#             print(f"Database error occurred: {e}")
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")
        

#     def update_tenancy(self, tenancy_id: int, tenancy: TenancyUpdate) -> Optional[Tenancy]:
#         db_tenancy = self.get_tenancy_by_id(tenancy_id)
#         if not db_tenancy:
#             return None
#         try:
#             db_tenancy.name=tenancy.name
#             self.db_session.commit()
#             self.db_session.refresh(db_tenancy)
#             return {"message" : "Tanancy name has been updated successfully !"}
#         except SQLAlchemyError as e:
#             print(f"Database error occurred: {e}")
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")
        

#     def soft_delete_tenancy(self, tenancy_id: int) -> Optional[Tenancy]:
#         try:
#             db_tenancy = self.get_tenancy_by_id(tenancy_id)
#             if not db_tenancy:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tenancy not found or already soft deleted")

#             db_tenancy.is_active=False
#             self.db_session.commit()
#             self.db_session.refresh(db_tenancy)
#             return tenancy_id
#         except SQLAlchemyError as e:
#             print(f"Database error occurred: {e}")
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")
        


#     def restore(self, tenancy_id: int) -> Optional[Tenancy]:
#         try:
#             db_tenancy = self.db_session.query(Tenancy).filter(Tenancy.id==tenancy_id).first()
#             if not db_tenancy:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tenancy not found or already  deleted")

#             db_tenancy.is_active=True
#             self.db_session.commit()
#             self.db_session.refresh(db_tenancy)
#             return tenancy_id
#         except SQLAlchemyError as e:
#             print(f"Database error occurred: {e}")
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")
        





from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from models.all_models import Tenancy  # Adjust the import path as necessary
from schemas.tenancy_schemas import TenancyCreate, TenancyUpdate  # Adjust import paths as necessary
from repositories.base_repository import BaseRepository
from fastapi import HTTPException, status

class TenancyRepository(BaseRepository[Tenancy, TenancyCreate,TenancyUpdate]):
    def __init__(self, db_session: Session):
        super().__init__(Tenancy, db_session)


    def get_tenancies(self, skip: int = 0, limit: int = 100, tenancy_id:Optional[int]=None) -> Optional[List[Tenancy]]:
        try:
            tenancies = self.db_session.query(Tenancy).filter(Tenancy.is_active==True)
            if tenancy_id:
                tenancies = tenancies.filter(Tenancy.id == tenancy_id)
            tenancies = tenancies.offset(offset=skip).limit(limit=limit).all()
            return tenancies
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")


    def get_tenancy_by_id(self, tenancy_id: int, tenanant_id:Optional[int]=None) -> Optional[Tenancy]:
        try:
            tenancy = self.db_session.query(Tenancy).filter(Tenancy.is_active==True, Tenancy.id==tenancy_id)
            if tenanant_id:
                tenancy = tenancy.filter(Tenancy.id == tenanant_id)
            tenancy = tenancy.first()
            return tenancy
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")


    def create_tenancy(self, tenancy: TenancyCreate) -> Tenancy:
        try:
            return super().create(tenancy)
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")
        

    def update_tenancy(self, tenancy_id: int, tenancy: TenancyUpdate) -> Optional[Tenancy]:
        db_tenancy = self.get_tenancy_by_id(tenancy_id)
        if not db_tenancy:
            return None
        try:
            db_tenancy.name=tenancy.name
            self.db_session.commit()
            self.db_session.refresh(db_tenancy)
            return {"message" : "Tanancy name has been updated successfully !"}
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")
        

    def soft_delete_tenancy(self, tenancy_id: int) -> Optional[Tenancy]:
        try:
            db_tenancy = self.get_tenancy_by_id(tenancy_id)
            if not db_tenancy:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tenancy not found or already soft deleted")

            db_tenancy.is_active=False
            self.db_session.commit()
            self.db_session.refresh(db_tenancy)
            return tenancy_id
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")
        


    def restore(self, tenancy_id: int) -> Optional[Tenancy]:
        try:
            db_tenancy = self.db_session.query(Tenancy).filter(Tenancy.id==tenancy_id).first()
            if not db_tenancy:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tenancy not found or already  deleted")

            db_tenancy.is_active=True
            self.db_session.commit()
            self.db_session.refresh(db_tenancy)
            return tenancy_id
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{str(e)}")
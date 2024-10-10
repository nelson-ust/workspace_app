# # repositories/location_repository.py

# from fastapi import HTTPException, status
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from typing import List, Optional, Type
# from models.all_models import IssueLogSource
# from schemas.issueLogSource_schemas import IssueLogSourceCreate, IssueLogSourceUpdate
# from repositories.base_repository import BaseRepository
# import logging


# class IssueLogSourceRepository(BaseRepository[IssueLogSource, IssueLogSourceCreate, IssueLogSourceUpdate]):
#     def __init__(self, db_session: Session):
#         super().__init__(IssueLogSource, db_session)

#     def create_issuelogsource(self, issuelogsource_data: IssueLogSourceCreate) -> IssueLogSource:
#         """
#         Creates a new issuelogsource ensuring that the name is unique within the issuelogsource table.
#         """
#         existing_issuelogsource = self.db_session.query(IssueLogSource).filter(IssueLogSource.name==issuelogsource_data.name).first()
#         if existing_issuelogsource:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An issuelogsource with the name {issuelogsource_data.name} already exists")
        
#         try:
#             return self.create(issuelogsource_data)
#         except SQLAlchemyError as err:
#             logging.error(f"Database error during issuelogsource creation: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
    
#     def update_issuelogsource(self, issuelogsource_id: int,  issuelogsource_data: IssueLogSourceUpdate) -> Optional[IssueLogSource]:
#         """
#         Updates an existing issuelogsource_id.
#         """

#         db_issuelogsource = self.get_by_id(issuelogsource_id)
#         if not db_issuelogsource:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"An issuelogsource with the id {issuelogsource_id} does not exist")
        
#         if issuelogsource_data.name and (issuelogsource_data.name == db_issuelogsource.name):
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'issuelogsource with "{issuelogsource_data.name}" already exists')
        
#         try:
#             return self.update(db_issuelogsource, issuelogsource_data)
#         except SQLAlchemyError as err:
#             logging.error(f"Database error during issuelogsource update: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update issuelogsource due to a database error")
            


#     def get_all_issuelogsource(self, skip:int =0, limit:int =100) -> List[IssueLogSource]:
#         """
#         Retrieves all issuelogsource records with optional pagination.
#         """
#         try:
#             return self.get_all(skip=skip, limit=limit)
#         except SQLAlchemyError as err:
#             logging.error(f"Error retrieving issuelogsource: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve issuelogsource")
        

#     def get_issuelogsource_by_id(self, issuelogsource_id: int) -> IssueLogSource:
#         """
#         Retrieves a issuelogsource by its ID.
#         """
#         try:
#             return self.get_by_id(issuelogsource_id)

#         except SQLAlchemyError as err:
#             logging.error(f"Error retrieving issuelogsource: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve issuelogsource")


#     def delete_issuelogsource(self, issuelogsource_id: int, hard_delete: bool = True) ->Optional[IssueLogSource]:
#         """
#         Deletes or soft deletes a issuelogsource by ID based on the hard_delete flag.
#         """

#         try:
#             issuelogsource = self.get_issuelogsource_by_id(issuelogsource_id)
#             if not issuelogsource:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'issuelogsource {issuelogsource_id} not found')
            
#             if hard_delete:
#                 self.delete_hard(issuelogsource_id)
#             else:
#                 return self.soft_delete(issuelogsource_id)
#         except SQLAlchemyError as e:
#             logging.error(f"Error deleting issuelogsource: {e}")
#             raise HTTPException(status_code=500, detail="Failed to delete issuelogsource")


#     def soft_delete_issuelogsource(self, issuelogsource_id):
#         """
#         Soft deletes a issuelogsource by setting its is_active flag to False.
#         """
#         issuelogsource = self.get_issuelogsource_by_id(issuelogsource_id)
#         if not issuelogsource:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'issuelogsource {issuelogsource_id} not found')
        
#         if not issuelogsource.is_active:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"issuelogsource {issuelogsource_id} has already been deactivated")
        
#         try:
#             issuelogsource.is_active = False
#             self.db_session.commit()
#             return issuelogsource
#         except SQLAlchemyError as err:
#             logging.error(f"Error soft deleting issuelogsource: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to soft delete issuelogsource")


#     def restore(self, issuelogsource_id: int) -> Optional[IssueLogSource]:
#         """
#         Restores a soft-deleted issuelogsource by setting its is_active flag to True.
#         """

#         issuelogsource = self.get_all_by_id(issuelogsource_id)
#         if not issuelogsource:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'issuelogsource {issuelogsource_id} not found')
        
#         if issuelogsource.is_active:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"issuelogsource with id {issuelogsource_id.id} is already active")
        
#         try:
#             issuelogsource.is_active = True
#             self.db_session.commit()
#             return issuelogsource
#         except SQLAlchemyError as err:
#             logging.error(f"Error soft deleting issuelogsource: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to restore soft deleted issuelogsource")


# repositories/location_repository.py

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from models.all_models import IssueLogSource
from schemas.issueLogSource_schemas import IssueLogSourceCreate, IssueLogSourceUpdate
from repositories.base_repository import BaseRepository
import logging


class IssueLogSourceRepository(BaseRepository[IssueLogSource, IssueLogSourceCreate, IssueLogSourceUpdate]):
    def __init__(self, db_session: Session):
        super().__init__(IssueLogSource, db_session)

    def create_issuelogsource(self, issuelogsource_data: IssueLogSourceCreate) -> IssueLogSource:
        """
        Creates a new issuelogsource ensuring that the name is unique within the issuelogsource table.
        """
        existing_issuelogsource = self.db_session.query(IssueLogSource).filter(IssueLogSource.name==issuelogsource_data.name).first()
        if existing_issuelogsource:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An issuelogsource with the name {issuelogsource_data.name} already exists")
        
        try:
            return self.create(issuelogsource_data)
        except SQLAlchemyError as err:
            logging.error(f"Database error during issuelogsource creation: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
    
    def update_issuelogsource(self, issuelogsource_id: int,  issuelogsource_data: IssueLogSourceUpdate) -> Optional[IssueLogSource]:
        """
        Updates an existing issuelogsource_id.
        """

        db_issuelogsource = self.get_by_id(issuelogsource_id)
        if not db_issuelogsource:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"An issuelogsource with the id {issuelogsource_id} does not exist")
        
        if issuelogsource_data.name and (issuelogsource_data.name == db_issuelogsource.name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'issuelogsource with "{issuelogsource_data.name}" already exists')
        
        try:
            db_issuelogsource.name = issuelogsource_data.name
            self.db_session.commit()
            self.db_session.refresh(db_issuelogsource)

            return {"message : IssueLogSource Updated Successfully"}
        except SQLAlchemyError as err:
            logging.error(f"Database error during issuelogsource update: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update issuelogsource due to a database error")
            


    def get_all_issuelogsource(self) -> List[IssueLogSource]:
        """
        Retrieves all issuelogsource records with optional pagination.
        """
        try:
            issue_log_sources = self.db_session.query(IssueLogSource).filter(IssueLogSource.is_active==True).all()
            return issue_log_sources
        except SQLAlchemyError as err:
            logging.error(f"Error retrieving issuelogsource: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve issuelogsource")
        

    def get_issuelogsource_by_id(self, issuelogsource_id: int) -> IssueLogSource:
        """
        Retrieves a issuelogsource by its ID.
        """
        try:
            issue_log_source = self.db_session.query(IssueLogSource).filter(IssueLogSource.is_active==True, IssueLogSource.id==issuelogsource_id).first()
            return issue_log_source

        except SQLAlchemyError as err:
            logging.error(f"Error retrieving issuelogsource: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve issuelogsource")


    def delete_issuelogsource(self, issuelogsource_id: int, hard_delete: bool = True) ->Optional[IssueLogSource]:
        """
        Deletes or soft deletes a issuelogsource by ID based on the hard_delete flag.
        """

        try:
            issuelogsource = self.get_issuelogsource_by_id(issuelogsource_id)
            if not issuelogsource:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'issuelogsource {issuelogsource_id} not found')
            
            if hard_delete:
                self.delete_hard(issuelogsource_id)
            else:
                return self.soft_delete(issuelogsource_id)
        except SQLAlchemyError as e:
            logging.error(f"Error deleting issuelogsource: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete issuelogsource")


    def soft_delete_issuelogsource(self, issuelogsource_id):
        """
        Soft deletes a issuelogsource by setting its is_active flag to False.
        """
        issuelogsource = self.db_session.query(IssueLogSource).filter(IssueLogSource.id==issuelogsource_id).first()
        if not issuelogsource:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'issuelogsource {issuelogsource_id} not found')
        
        if not issuelogsource.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"issuelogsource {issuelogsource_id} has already been deactivated")
        
        try:
            issuelogsource.is_active = False
            self.db_session.commit()
            return {"message : IssueLogSource deactivated Successfully"}
        except SQLAlchemyError as err:
            logging.error(f"Error soft deleting issuelogsource: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to soft delete issuelogsource")


    def restore_issue_log_source(self, issuelogsource_id: int) -> Optional[IssueLogSource]:
        """
        Restores a soft-deleted issuelogsource by setting its is_active flag to True.
        """

        issuelogsource = self.db_session.query(IssueLogSource).filter(IssueLogSource.id==issuelogsource_id).first()
        if not issuelogsource:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'issuelogsource {issuelogsource_id} not found')
        
        if issuelogsource.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"issuelogsource with id {issuelogsource_id.id} is already active")
        
        try:
            issuelogsource.is_active = True
            self.db_session.commit()
            return {"message : IssueLogSource activated Successfully"}
        except SQLAlchemyError as err:
            logging.error(f"Error soft deleting issuelogsource: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to restore soft deleted issuelogsource")
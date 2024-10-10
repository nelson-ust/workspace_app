# # repositories/issue_status_repository.py

# from fastapi import HTTPException, status
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from typing import List, Optional
# from models.all_models import IssueStatus
# from schemas.issue_status_schemas import IssueStatusCreate, IssueStatusUpdate
# from repositories.base_repository import BaseRepository
# import logging


# class IssueStatusRepository(BaseRepository[IssueStatus, IssueStatusCreate, IssueStatusUpdate]):
#     def __init__(self, db_session: Session):
#         super().__init__(IssueStatus, db_session)

#     def create_issue_status(self, issue_status_data: IssueStatusCreate) -> IssueStatus:
#         """
#         Creates a new issue_status ensuring that the name is unique within the issue_status table.
#         """
#         existing_issuestatus = self.db_session.query(IssueStatus).filter(IssueStatus.status==issue_status_data.status).first()
#         if existing_issuestatus:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An issue_status with the name {issue_status_data.status} already exists")
        
#         try:
#             return self.create(issue_status_data)
#         except SQLAlchemyError as err:
#             logging.error(f"Database error during issue_status creation: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
    
#     def update_issue_status(self, issue_status_id: int,  issue_status_data: IssueStatusUpdate) -> Optional[IssueStatus]:
#         """
#         Updates an existing issue_status_id.
#         """

#         db_issue_status = self.get_by_id(issue_status_id)
#         if not db_issue_status:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"An issue_status with the id {issue_status_id} does not exist")
        
#         if issue_status_data.status and (issue_status_data.status == db_issue_status.status):
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'issue_status with "{issue_status_data.status}" already exists')
        
#         try:
#             return self.update(db_issue_status, issue_status_data)
#         except SQLAlchemyError as err:
#             logging.error(f"Database error during issuestatus update: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update issuestatus due to a database error")
            


#     def get_all_issue_status(self, skip:int =0, limit:int =100) -> List[IssueStatus]:
#         """
#         Retrieves all issue_status records with optional pagination.
#         """
#         try:
#             return self.get_all(skip=skip, limit=limit, is_active=True)
#         except SQLAlchemyError as err:
#             logging.error(f"Error retrieving issue_status: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve issue_status")
        

#     def get_issue_status_by_id(self, issue_status_id: int) -> IssueStatus:
#         """
#         Retrieves a issue_status by its ID.
#         """
#         try:
#             return self.get_by_id(issue_status_id, is_active=True)

#         except SQLAlchemyError as err:
#             logging.error(f"Error retrieving issue_status: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve issue_status")


#     def delete_issue_status(self, issue_status_id: int, hard_delete: bool = True) ->Optional[IssueStatus]:
#         """
#         Deletes or soft deletes a issue_status by ID based on the hard_delete flag.
#         """

#         try:
#             issue_status = self.get_issue_status_by_id(issue_status_id)
#             if not issue_status:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'issue_status {issue_status_id} not found')
            
#             if hard_delete:
#                 self.delete_hard(issue_status_id)
#             else:
#                 return self.soft_delete(issue_status_id)
#         except SQLAlchemyError as e:
#             logging.error(f"Error deleting issue_status: {e}")
#             raise HTTPException(status_code=500, detail="Failed to delete issue_status")


#     def soft_delete_issue_status(self, issue_status_id):
#         """
#         Soft deletes a issue_status by setting its is_active flag to False.
#         """
#         issue_status = self.get_all_by_id(issue_status_id)
#         if not issue_status:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'issue_status {issue_status_id} not found')
        
#         if not issue_status.is_active:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"issue_status {issue_status_id} has already been deactivated")
        
#         try:
#             issue_status.is_active = False
#             self.db_session.commit()
#             return {f"message: Issue Status with ID {issue_status_id} has been deactivated successfully"}
#         except SQLAlchemyError as err:
#             logging.error(f"Error soft deleting issue_status: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to soft delete issue_status")


#     def restore(self, issue_status_id: int) -> Optional[IssueStatus]:
#         """
#         Restores a soft-deleted issue_status by setting its is_active flag to True.
#         """

#         issue_status = self.get_all_by_id(issue_status_id)
#         if not issue_status:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'issue_status {issue_status_id} not found')
        
#         if issue_status.is_active:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"issue_status with id {issue_status.id} is already active")
        
#         try:
#             issue_status.is_active = True
#             self.db_session.commit()
#             return issue_status
#         except SQLAlchemyError as err:
#             logging.error(f"Error soft deleting issue_status: {err}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to restore soft deleted issue_status")



# repositories/issue_status_repository.py

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from models.all_models import IssueStatus
from schemas.issue_status_schemas import IssueStatusCreate, IssueStatusUpdate
from repositories.base_repository import BaseRepository
import logging


class IssueStatusRepository(BaseRepository[IssueStatus, IssueStatusCreate, IssueStatusUpdate]):
    def __init__(self, db_session: Session):
        super().__init__(IssueStatus, db_session)

    def create_issue_status(self, issue_status_data: IssueStatusCreate) -> IssueStatus:
        """
        Creates a new issue_status ensuring that the name is unique within the issue_status table.
        """
        existing_issuestatus = self.db_session.query(IssueStatus).filter(IssueStatus.status==issue_status_data.status).first()
        if existing_issuestatus:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An issue_status with the name {issue_status_data.status} already exists")
        
        try:
            return self.create(issue_status_data)
        except SQLAlchemyError as err:
            logging.error(f"Database error during issue_status creation: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
    
    def update_issue_status(self, issue_status_id: int,  issue_status_data: IssueStatusUpdate) -> Optional[IssueStatus]:
        """
        Updates an existing issue_status_id.
        """
        db_issue_status = self.db_session.query(IssueStatus).filter(IssueStatus.is_active==True).first()
        if not db_issue_status:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"An issue_status with the id {issue_status_id} does not exist")
        
        if issue_status_data.status and (issue_status_data.status == db_issue_status.status):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'issue_status with "{issue_status_data.status}" already exists')
        
        try:
            db_issue_status.status=issue_status_data.status
            self.db_session.commit()
            self.db_session.refresh(db_issue_status)

            return {"message : Issue Status Updated Successfully"}
        except SQLAlchemyError as err:
            logging.error(f"Database error during issuestatus update: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update issuestatus due to a database error")
            


    def get_all_issue_status(self) -> List[IssueStatus]:
        """
        Retrieves all issue_status records with optional pagination.
        """
        try:
            issue_status = self.db_session.query(IssueStatus).filter(IssueStatus.is_active==True).all()
            return issue_status
        except SQLAlchemyError as err:
            logging.error(f"Error retrieving issue_status: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve issue_status")
        

    def get_issue_status_by_id(self, issue_status_id: int) -> IssueStatus:
        """
        Retrieves a issue_status by its ID.
        """
        try:
            issue_status = self.db_session.query(IssueStatus).filter(IssueStatus.is_active==True, IssueStatus.id==issue_status_id).first()
            return issue_status

        except SQLAlchemyError as err:
            logging.error(f"Error retrieving issue_status: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve issue_status")


    def delete_issue_status(self, issue_status_id: int, hard_delete: bool = True) ->Optional[IssueStatus]:
        """
        Deletes or soft deletes a issue_status by ID based on the hard_delete flag.
        """

        try:
            issue_status = self.db_session.query(IssueStatus).filter(IssueStatus.id==issue_status_id).first()
            if not issue_status:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'issue_status {issue_status_id} not found')
            
            if hard_delete:
                self.delete_hard(issue_status_id)
            else:
                return self.soft_delete(issue_status_id)
        except SQLAlchemyError as e:
            logging.error(f"Error deleting issue_status: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete issue_status")


    def soft_delete_issue_status(self, issue_status_id):
        """
        Soft deletes a issue_status by setting its is_active flag to False.
        """
        issue_status = self.db_session.query(IssueStatus).filter(IssueStatus.id==issue_status_id).first()
        if not issue_status:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'issue_status {issue_status_id} not found')
        
        if not issue_status.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"issue_status {issue_status_id} has already been deactivated")
        
        try:
            issue_status.is_active = False
            self.db_session.commit()
            return {f"message: Issue Status with ID {issue_status_id} has been deactivated successfully"}
        except SQLAlchemyError as err:
            logging.error(f"Error soft deleting issue_status: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to soft delete issue_status")


    def restore(self, issue_status_id: int) -> Optional[IssueStatus]:
        """
        Restores a soft-deleted issue_status by setting its is_active flag to True.
        """

        issue_status = self.db_session.query(IssueStatus).filter(IssueStatus.id==issue_status_id).first()
        if not issue_status:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'issue_status {issue_status_id} not found')
        
        if issue_status.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"issue_status with id {issue_status.id} is already active")
        
        try:
            issue_status.is_active = True
            self.db_session.commit()
            return {f"message: Issue Status with ID {issue_status_id} has been activated successfully"}
        except SQLAlchemyError as err:
            logging.error(f"Error soft deleting issue_status: {err}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to restore soft deleted issue_status")
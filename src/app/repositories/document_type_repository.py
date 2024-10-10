from sqlalchemy.orm import Session
from models.all_models import DocumentType
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

class DocumentTypeRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_document_type_by_id(self, document_type_id: int):
        try:
            document_type = self.db_session.query(DocumentType).filter_by(id=document_type_id, is_active=True).first()
            if not document_type:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document type not found")
            return document_type
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving document type: {str(e)}")

    def get_all_document_types(self):
        try:
            document_types = self.db_session.query(DocumentType).filter_by(is_active=True).all()
            return document_types
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving document types: {str(e)}")

    def create_document_type(self, name: str, description: str = None):
        try:
            new_document_type = DocumentType(name=name, description=description)
            self.db_session.add(new_document_type)
            self.db_session.commit()
            return new_document_type
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating document type: {str(e)}")

    def update_document_type(self, document_type_id: int, name: str = None, description: str = None):
        try:
            document_type = self.get_document_type_by_id(document_type_id)
            if name:
                document_type.name = name
            if description:
                document_type.description = description
            self.db_session.commit()
            return document_type
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error updating document type: {str(e)}")

    def delete_document_type(self, document_type_id: int):
        try:
            document_type = self.get_document_type_by_id(document_type_id)
            document_type.is_active = False
            self.db_session.commit()
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting document type: {str(e)}")

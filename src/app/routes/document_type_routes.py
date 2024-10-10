from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from auth.dependencies import role_checker
from auth.security import get_current_user
from models.all_models import ActionEnum
from schemas.user_schemas import UserRead
from db.database import get_db
from schemas.document_type_schemas import DocumentTypeCreate, DocumentTypeUpdate, DocumentTypeResponse
from repositories.document_type_repository import DocumentTypeRepository
from logging_helpers import logging_helper

# Initialize the router
router = APIRouter()

@router.get("/document_types/", response_model=List[DocumentTypeResponse])
def get_all_document_types(
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    _ = Depends(role_checker(['super_admin']))
):
    """
    Retrieve all document types.

    Roles to Access the endpoint
        super_admin, 
    """
    document_type_repo = DocumentTypeRepository(db)
    return document_type_repo.get_all_document_types()

@router.get("/document_types/{document_type_id}", response_model=DocumentTypeResponse)
def get_document_type_by_id(
    document_type_id: int,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    _ = Depends(role_checker(['super_admin']))
):
    """
    Retrieve a specific document type by its ID.

    Roles to Access the endpoint
        super_admin
    """
    document_type_repo = DocumentTypeRepository(db)
    return document_type_repo.get_document_type_by_id(document_type_id)

@router.post("/document_types/", response_model=DocumentTypeResponse, status_code=status.HTTP_201_CREATED)
def create_document_type(
    document_type: DocumentTypeCreate,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    _ = Depends(role_checker(['super_admin']))
):
    """
    Create a new document type.

    Roles to Access the endpoint
        super_admin
    """
    document_type_repo = DocumentTypeRepository(db)
    new_document_type = document_type_repo.create_document_type(
        name=document_type.name, description=document_type.description
    )
    
    # Log the creation in the audit log
    logging_helper.log_audit(
        db,
        current_user.id,
        ActionEnum.CREATE,
        "DocumentType",
        new_document_type.id,
        {"name": document_type.name, "description": document_type.description}
    )
    
    return new_document_type

@router.put("/document_types/{document_type_id}", response_model=DocumentTypeResponse)
def update_document_type(
    document_type_id: int,
    document_type: DocumentTypeUpdate,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    _ = Depends(role_checker(['super_admin']))
):
    """
    Update an existing document type by its ID.

    Roles to Access the endpoint
        super_admin
    """
    document_type_repo = DocumentTypeRepository(db)
    updated_document_type = document_type_repo.update_document_type(
        document_type_id=document_type_id,
        name=document_type.name,
        description=document_type.description
    )

    # Log the update in the audit log
    changes = {key: value for key, value in document_type.dict(exclude_unset=True).items()}
    logging_helper.log_audit(
        db,
        current_user.id,
        ActionEnum.UPDATE,
        "DocumentType",
        document_type_id,
        changes
    )

    return updated_document_type

@router.delete("/document_types/{document_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_type(
    document_type_id: int,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    _ = Depends(role_checker(['super_admin']))
):
    """
    Soft delete a document type by its ID.

    Roles to Access the endpoint
        super_admin
    """
    document_type_repo = DocumentTypeRepository(db)
    document_type_repo.delete_document_type(document_type_id)

    # Log the deletion in the audit log
    logging_helper.log_audit(
        db,
        current_user.id,
        ActionEnum.SOFT_DELETE,
        "DocumentType",
        document_type_id,
        {"message": f"DocumentType {document_type_id} soft deleted."}
    )

    return {"detail": "Document type deleted successfully"}

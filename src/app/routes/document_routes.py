import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, BackgroundTasks, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from auth.dependencies import role_checker
from auth.security import get_current_user
from models.all_models import ActionEnum
from schemas.user_schemas import UserRead
from db.database import get_db
from repositories.document_repository import DocumentRepository
from schemas.document_schemas import DocumentCreate, DocumentRead, EmployeeWithoutDocumentRead
from logging_helpers import logging_helper

router = APIRouter()

@router.post("/upload", response_model=DocumentRead)
def upload_employee_document(
    employee_id: int,
    document_type_id: int,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['hr', 'tenant_admin', 'super_admin']))
):
    """
    Upload a document for an employee.

    Roles to Access the endpoint
        super_admin, hr
    """
    try:
        document_repo = DocumentRepository(db_session=db)
        document = document_repo.upload_employee_document(employee_id, document_type_id, file)

        # Log audit action
        logging_helper.log_audit(
            db, 
            current_user.id, 
            ActionEnum.CREATE, 
            "Document", 
            document.id, 
            {"employee_id": employee_id, "document_type_id": document_type_id}
        )

        return document
    except HTTPException as e:
        logging_helper.log_error(f"Error uploading document: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/employee/{employee_id}/documents", response_model=List[DocumentRead])
def get_employee_documents(
    employee_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['tenant_admin', 'super_admin', 'hr']))
):
    """
    Retrieve all documents associated with a specific employee.

    Roles to Access the endpoint
        super_admin, hr
    """
    try:
        document_repo = DocumentRepository(db_session=db)
        documents = document_repo.get_documents_by_employee(employee_id)

        return documents
    except HTTPException as e:
        logging_helper.log_error(f"Error retrieving employee documents: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error retrieving employee documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document/{document_id}", response_model=DocumentRead)
def get_document_by_id(
    document_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['tenant_admin', 'super_admin', 'hr']))
):
    """
    Retrieve a specific document by its ID.

    Roles to Access the endpoint
        super_admin, hr
    """
    try:
        document_repo = DocumentRepository(db_session=db)
        document = document_repo.get_document_by_id(document_id)

        return document
    except HTTPException as e:
        logging_helper.log_error(f"Error retrieving document: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error retrieving document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/document/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['tenant_admin', 'super_admin', 'hr']))
):
    """
    Delete a specific document by its ID.

    Roles to Access the endpoint
        super_admin, hr
    """
    try:
        document_repo = DocumentRepository(db_session=db)
        document_repo.delete_document(document_id)

        # Log audit action
        logging_helper.log_audit(
            db, 
            current_user.id, 
            ActionEnum.DELETE, 
            "Document", 
            document_id, 
            {"document_id": document_id}
        )
    except HTTPException as e:
        logging_helper.log_error(f"Error deleting document: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document/{document_id}/download")
def download_document(
    document_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['tenant_admin', 'super_admin']))
):
    """
    Download a specific document by its ID.

    Roles to Access the endpoint
        super_admin, hr
    """
    try:
        document_repo = DocumentRepository(db_session=db)
        file_path = document_repo.download_document(document_id)

        return {"file_path": file_path}
    except HTTPException as e:
        logging_helper.log_error(f"Error downloading document: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error downloading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/employee/{employee_id}/download-all-documents")
def download_all_documents(
    employee_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserRead = Depends(get_current_user),
    _ = Depends(role_checker(['tenant_admin', 'super_admin', 'hr']))
):
    """
    Download all documents associated with a specific employee as a zip file.
    
    Args:
        employee_id (int): The ID of the employee whose documents should be downloaded.

    Returns:
        FileResponse: The zipped file containing all documents of the employee.

    Raises:
        HTTPException: If there is any error during the process.

    Roles to Access the endpoint
        super_admin, hr
    """
    try:
        document_repo = DocumentRepository(db)
        zip_file_path = document_repo.download_all_documents(employee_id)

        if zip_file_path:
            return FileResponse(
                path=zip_file_path, 
                filename=os.path.basename(zip_file_path), 
                media_type='application/zip'
            )
        else:
            raise HTTPException(status_code=404, detail="Documents not found.")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while downloading documents: {str(e)}")


@router.get("/download-all-documents-by-project-or-tenancy")
def download_all_documents_by_project_or_tenancy(
    project_id: Optional[int] = None,
    tenancy_id: Optional[int] = None,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker([ 'hr', 'super_admin', 'tenant_admin']))
):
    """
    Download all employees' documents associated with a selected project or tenancy as a single zip file.

    Roles to Access the endpoint
        super_admin, hr
    """
    try:
        document_repo = DocumentRepository(db)
        file_path = document_repo.download_all_documents_by_project_or_tenancy(project_id=project_id, tenancy_id=tenancy_id)

        # Return the file as a FileResponse to trigger the download
        return FileResponse(file_path, media_type='application/zip', filename=os.path.basename(file_path))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while downloading documents.")


# @router.get("/employees-without-document/{document_type_id}", response_model=List[EmployeeWithoutDocumentRead])
# def get_employees_without_document_type(
#     document_type_id: int,
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db),
#     _ = Depends(role_checker(['tenant_admin', 'super_admin']))
# ):
#     """
#     Retrieve a list of employees who do not have a specific type of document.
#     """
#     try:
#         document_repo = DocumentRepository(db_session=db)
#         employees = document_repo.get_employees_without_document_type(document_type_id)

#         return employees
#     except HTTPException as e:
#         logging_helper.log_error(f"Error retrieving employees without document: {str(e)}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Unexpected error retrieving employees without document: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


@router.get("/employees-without-document/{document_type_id}", response_model=List[EmployeeWithoutDocumentRead])
def get_employees_without_document_type(
    document_type_id: int,
    project_id: Optional[int] = None,
    tenancy_id: Optional[int] = None,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['hr', 'super_admin']))
):
    """
    Retrieve a list of employees who do not have a specific type of document and optionally filter by project or tenancy.

    Roles to Access the endpoint
        super_admin, hr
    """
    try:
        document_repo = DocumentRepository(db_session=db)
        employees = document_repo.get_employees_without_document_type(
            document_type_id=document_type_id,
            project_id=project_id,
            tenancy_id=tenancy_id
        )

        return employees
    except HTTPException as e:
        logging_helper.log_error(f"Error retrieving employees without document: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error retrieving employees without document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
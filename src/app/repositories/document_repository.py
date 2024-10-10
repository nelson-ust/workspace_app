from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.all_models import Document, Employee, Project, Tenancy
from fastapi import HTTPException, UploadFile
from typing import List, Optional
import os
import shutil
import zipfile

class DocumentRepository:
    def __init__(self, db_session: Session):
        """
        Initialize the DocumentRepository with a database session.
        
        Args:
            db_session (Session): SQLAlchemy session object.
        """
        self.db_session = db_session

    def upload_employee_document(self, employee_id: int, document_type_id: int, file: UploadFile) -> Document:
        """
        Upload a document for a specific employee.

        Args:
            employee_id (int): The ID of the employee to whom the document belongs.
            document_type_id (int): The ID of the document type.
            file (UploadFile): The document file to be uploaded.

        Returns:
            Document: The newly created document record.

        Raises:
            HTTPException: If there is any error during the process.
        """
        try:
            # Ensure the Employee_documents directory exists
            upload_dir = "Employee_documents"
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            # Save the file locally or to cloud storage
            file_location = os.path.join(upload_dir, file.filename)
            with open(file_location, "wb+") as file_object:
                shutil.copyfileobj(file.file, file_object)

            # Create a new document record in the database
            new_document = Document(
                name=file.filename,
                document_type_id=document_type_id,
                file_path=file_location,
                employee_id=employee_id,
            )

            self.db_session.add(new_document)
            self.db_session.commit()
            self.db_session.refresh(new_document)

            return new_document
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while uploading the document: {str(e)}")



    def get_documents_by_employee(self, employee_id: int) -> List[Document]:
        """
        Retrieve all documents associated with a specific employee.

        Args:
            employee_id (int): The ID of the employee.

        Returns:
            List[Document]: A list of document records associated with the employee.

        Raises:
            HTTPException: If there is any error during the process.
        """
        try:
            documents = self.db_session.query(Document).filter_by(employee_id=employee_id).all()
            return documents
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """
        Retrieve a specific document by its ID.

        Args:
            document_id (int): The ID of the document to retrieve.

        Returns:
            Optional[Document]: The document record if found, otherwise None.

        Raises:
            HTTPException: If there is any error during the process.
        """
        try:
            document = self.db_session.query(Document).filter_by(id=document_id).first()
            return document
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    def delete_document(self, document_id: int) -> None:
        """
        Delete a specific document by its ID.

        Args:
            document_id (int): The ID of the document to delete.

        Raises:
            HTTPException: If the document is not found or if there is any error during the process.
        """
        try:
            document = self.db_session.query(Document).filter_by(id=document_id).first()
            if not document:
                raise HTTPException(status_code=404, detail="Document not found.")

            # Delete the file from storage
            if os.path.exists(document.file_path):
                os.remove(document.file_path)

            self.db_session.delete(document)
            self.db_session.commit()
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while deleting the document: {str(e)}")


    def download_document(self, document_id: int) -> Optional[str]:
        """
        Get the file path of a specific document for download.

        Args:
            document_id (int): The ID of the document to download.

        Returns:
            Optional[str]: The file path of the document if found, otherwise None.

        Raises:
            HTTPException: If there is any error during the process.
        """
        try:
            document = self.get_document_by_id(document_id)
            if document:
                return document.file_path
            else:
                raise HTTPException(status_code=404, detail="Document not found.")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    def download_all_documents(self, employee_id: int) -> Optional[str]:
        """
        Download all documents associated with a specific employee as a zip file.

        Args:
            employee_id (int): The ID of the employee whose documents should be downloaded.

        Returns:
            Optional[str]: The file path of the generated zip file if successful.

        Raises:
            HTTPException: If there is any error during the process.
        """
        try:
            documents = self.get_documents_by_employee(employee_id)
            if not documents:
                raise HTTPException(status_code=404, detail="No documents found for this employee.")

            # Retrieve employee's full name
            employee = self.db_session.query(Employee).filter_by(id=employee_id).first()
            if not employee:
                raise HTTPException(status_code=404, detail="Employee not found.")

            employee_full_name = f"{employee.first_name}_{employee.last_name}"

            # Set the filename to the employee's full name
            zip_filename = f"{employee_full_name}_HR_Documents.zip"
            zip_filepath = os.path.join("Employee_documents", zip_filename)

            # Create a zip file containing all the documents
            with zipfile.ZipFile(zip_filepath, 'w') as zipf:
                for document in documents:
                    if os.path.exists(document.file_path):
                        zipf.write(document.file_path, arcname=os.path.basename(document.file_path))

            return zip_filepath
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while downloading documents: {str(e)}")



    # def download_all_documents_by_project_or_tenancy(self, project_id: Optional[int] = None, tenancy_id: Optional[int] = None) -> Optional[str]:
    #     """
    #     Download all employees' documents associated with a selected project or tenancy as a single zip file.

    #     Args:
    #         project_id (Optional[int]): The ID of the project to retrieve documents for.
    #         tenancy_id (Optional[int]): The ID of the tenancy to retrieve documents for.

    #     Returns:
    #         Optional[str]: The file path of the generated main zip file if successful.

    #     Raises:
    #         HTTPException: If there is any error during the process.
    #     """
    #     try:
    #         if project_id:
    #             # Query employees associated with the project
    #             employees = self.db_session.query(Employee).join(Employee.projects).filter(Project.id == project_id).all()
    #         elif tenancy_id:
    #             # Query employees associated with the tenancy
    #             employees = self.db_session.query(Employee).filter_by(tenancy_id=tenancy_id).all()
    #         else:
    #             raise HTTPException(status_code=400, detail="Project ID or Tenancy ID must be provided.")

    #         if not employees:
    #             raise HTTPException(status_code=404, detail="No employees found for the selected project or tenancy.")

    #         # Directory to store individual employee zips
    #         project_or_tenancy = f"project_{project_id}" if project_id else f"tenancy_{tenancy_id}"
    #         base_zip_dir = os.path.join("Employee_documents", project_or_tenancy)
    #         if not os.path.exists(base_zip_dir):
    #             os.makedirs(base_zip_dir)

    #         # Create individual zip files for each employee's documents
    #         for employee in employees:
    #             documents = self.get_documents_by_employee(employee.id)
    #             if documents:
    #                 employee_full_name = f"{employee.first_name}_{employee.last_name}"
    #                 zip_filename = f"{employee_full_name}_documents.zip"
    #                 zip_filepath = os.path.join(base_zip_dir, zip_filename)
    #                 with zipfile.ZipFile(zip_filepath, 'w') as zipf:
    #                     for document in documents:
    #                         if os.path.exists(document.file_path):
    #                             zipf.write(document.file_path, arcname=os.path.basename(document.file_path))

    #         # Create main zip file containing all individual employee zip files
    #         main_zip_filename = f"{project_or_tenancy}_all_employees_documents.zip"
    #         main_zip_filepath = os.path.join("Employee_documents", main_zip_filename)
    #         with zipfile.ZipFile(main_zip_filepath, 'w') as main_zipf:
    #             for filename in os.listdir(base_zip_dir):
    #                 file_path = os.path.join(base_zip_dir, filename)
    #                 main_zipf.write(file_path, arcname=filename)

    #         # Clean up the individual employee zips
    #         shutil.rmtree(base_zip_dir)

    #         return main_zip_filepath
    #     except SQLAlchemyError as e:
    #         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=f"An error occurred while downloading documents: {str(e)}")


    def download_all_documents_by_project_or_tenancy(self, project_id: Optional[int] = None, tenancy_id: Optional[int] = None) -> Optional[str]:
        """
        Download all employees' documents associated with a selected project or tenancy as a single zip file.

        Args:
            project_id (Optional[int]): The ID of the project to retrieve documents for.
            tenancy_id (Optional[int]): The ID of the tenancy to retrieve documents for.

        Returns:
            Optional[str]: The file path of the generated main zip file if successful.

        Raises:
            HTTPException: If there is any error during the process.
        """
        try:
            if project_id:
                # Query employees associated with the project
                employees = self.db_session.query(Employee).join(Employee.projects).filter(Project.id == project_id).all()
                project_name = self.db_session.query(Project.name).filter(Project.id == project_id).scalar()
            elif tenancy_id:
                # Query employees associated with the tenancy
                employees = self.db_session.query(Employee).filter_by(tenancy_id=tenancy_id).all()
                tenancy_name = self.db_session.query(Tenancy.name).filter(Tenancy.id == tenancy_id).scalar()
            else:
                raise HTTPException(status_code=400, detail="Project ID or Tenancy ID must be provided.")

            if not employees:
                raise HTTPException(status_code=404, detail="No employees found for the selected project or tenancy.")

            # Directory to store individual employee zips
            project_or_tenancy = f"project_{project_id}" if project_id else f"tenancy_{tenancy_id}"
            base_zip_dir = os.path.join("Employee_documents", project_or_tenancy)
            if not os.path.exists(base_zip_dir):
                os.makedirs(base_zip_dir)

            # Create individual zip files for each employee's documents
            for employee in employees:
                documents = self.get_documents_by_employee(employee.id)
                if documents:
                    employee_full_name = f"{employee.first_name}_{employee.last_name}"
                    zip_filename = f"{employee_full_name}_documents.zip"
                    zip_filepath = os.path.join(base_zip_dir, zip_filename)
                    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
                        for document in documents:
                            if os.path.exists(document.file_path):
                                zipf.write(document.file_path, arcname=os.path.basename(document.file_path))

            # Determine the main zip file name based on project and tenancy names
            main_zip_filename_parts = []
            if project_id and project_name:
                main_zip_filename_parts.append(project_name)
            if tenancy_id and tenancy_name:
                main_zip_filename_parts.append(tenancy_name)
            main_zip_filename = "_".join(main_zip_filename_parts) + "_all_employees_documents.zip"

            # Create main zip file containing all individual employee zip files
            main_zip_filepath = os.path.join("Employee_documents", main_zip_filename)
            with zipfile.ZipFile(main_zip_filepath, 'w') as main_zipf:
                for filename in os.listdir(base_zip_dir):
                    file_path = os.path.join(base_zip_dir, filename)
                    main_zipf.write(file_path, arcname=filename)

            # Clean up the individual employee zips
            shutil.rmtree(base_zip_dir)

            return main_zip_filepath
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while downloading documents: {str(e)}")



    # def get_employees_without_document_type(self, document_type_id: int) -> List[Employee]:
    #     """
    #     Retrieve a list of employees who do not have a specific type of document.

    #     Args:
    #         document_type_id (int): The ID of the document type to check.

    #     Returns:
    #         List[Employee]: A list of employees who do not have the specified document type.

    #     Raises:
    #         HTTPException: If there is any error during the process.
    #     """
    #     try:
    #         # Subquery to get employee IDs that have the specified document type
    #         subquery = (
    #             self.db_session.query(Document.employee_id)
    #             .filter(Document.document_type_id == document_type_id)
    #             .subquery()
    #         )

    #         # Query to get employees that are not in the subquery (i.e., without the specified document type)
    #         employees_without_document = (
    #             self.db_session.query(Employee)
    #             .filter(~Employee.id.in_(subquery))
    #             .all()
    #         )

    #         return employees_without_document
    #     except SQLAlchemyError as e:
    #         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    def get_employees_without_document_type(self, document_type_id: int, project_id: Optional[int] = None, tenancy_id: Optional[int] = None) -> List[Employee]:
        """
        Retrieve a list of employees who do not have a specific type of document and optionally filter by project or tenancy.

        Args:
            document_type_id (int): The ID of the document type to check.
            project_id (Optional[int]): The ID of the project to filter employees (optional).
            tenancy_id (Optional[int]): The ID of the tenancy to filter employees (optional).

        Returns:
            List[Employee]: A list of employees who do not have the specified document type.

        Raises:
            HTTPException: If there is any error during the process.
        """
        try:
            # Subquery to get employee IDs that have the specified document type
            subquery = (
                self.db_session.query(Document.employee_id)
                .filter(Document.document_type_id == document_type_id)
                .subquery()
            )

            # Base query to get employees that are not in the subquery (i.e., without the specified document type)
            query = self.db_session.query(Employee).filter(~Employee.id.in_(subquery))

            # Apply additional filters if project_id or tenancy_id is provided
            if project_id:
                query = query.join(Employee.projects).filter(Project.id == project_id)
            if tenancy_id:
                query = query.filter(Employee.tenancy_id == tenancy_id)

            # Execute the query and return the results
            employees_without_document = query.all()

            return employees_without_document
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

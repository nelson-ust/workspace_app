from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from models.all_models import Module
from schemas.module_schemas import ModuleCreateSchema, ModuleUpdateSchema, ModuleReadSchema
from typing import List

class ModuleRepository:
    def __init__(self, db_session: Session):
        """
        Initializes the ModuleRepository with a database session.

        Args:
            db_session (Session): The SQLAlchemy session for database operations.
        """
        self.db_session = db_session

    def create_module(self, module_data: ModuleCreateSchema) -> ModuleReadSchema:
        """
        Creates a new module in the database using the provided data.

        Args:
            module_data (ModuleCreateSchema): The schema containing all required data for creating a module.

        Returns:
            ModuleReadSchema: The created module data.

        Raises:
            HTTPException: If there is any database error during the operation.
        """
        try:
            new_module = Module(
                name=module_data.name,
                description=module_data.description
            )
            self.db_session.add(new_module)
            self.db_session.commit()
            self.db_session.refresh(new_module)
            # Convert the ORM object to the response schema
            return ModuleReadSchema.from_orm(new_module)
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

    def update_module(self, module_id: int, update_data: ModuleUpdateSchema) -> ModuleReadSchema:
        """
        Updates an existing module based on its ID with the new data provided.

        Args:
            module_id (int): The ID of the module to update.
            update_data (ModuleUpdateSchema): The schema containing all updatable data fields for the module.

        Returns:
            ModuleReadSchema: The updated module data.

        Raises:
            HTTPException: If the module is not found or there is a database error.
        """
        try:
            module = self.db_session.query(Module).filter(Module.id == module_id).first()
            if not module:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Module not found"
                )

            # Update fields if provided in update_data
            if update_data.name is not None:
                module.name = update_data.name
            if update_data.description is not None:
                module.description = update_data.description
            
            self.db_session.commit()
            return ModuleReadSchema.from_orm(module)
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update module: {str(e)}"
            )

    def get_module(self, module_id: int) -> ModuleReadSchema:
        """
        Retrieves a module by its ID.

        Args:
            module_id (int): The ID of the module to retrieve.

        Returns:
            ModuleReadSchema: The module data if found.

        Raises:
            HTTPException: If the module is not found or there is a database error.
        """
        try:
            module = self.db_session.query(Module).filter(Module.id == module_id).first()
            if not module:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Module not found"
                )
            return ModuleReadSchema.from_orm(module)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

    def delete_module(self, module_id: int) -> None:
        """
        Deletes a module by its ID.

        Args:
            module_id (int): The ID of the module to delete.

        Raises:
            HTTPException: If the module is not found or there is a database error during deletion.
        """
        try:
            module = self.db_session.query(Module).filter(Module.id == module_id).first()
            if not module:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Module not found"
                )
            
            self.db_session.delete(module)
            self.db_session.commit()
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete module: {str(e)}"
            )

    def list_modules(self) -> List[ModuleReadSchema]:
        """
        Lists all modules stored in the database.

        Returns:
            List[ModuleReadSchema]: A list of all modules.

        Raises:
            HTTPException: If there is a database error during the retrieval.
        """
        try:
            modules = self.db_session.query(Module).all()
            return [ModuleReadSchema.from_orm(module) for module in modules]
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list modules: {str(e)}"
            )

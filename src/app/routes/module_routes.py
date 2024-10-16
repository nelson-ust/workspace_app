
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from repositories.module_repository import ModuleRepository
from schemas.module_schemas import ModuleCreateSchema, ModuleUpdateSchema, ModuleReadSchema
from auth.dependencies import role_required
from auth.security import get_current_user
from schemas.user_schemas import UserRead
from models.all_models import ActionEnum
from logging_helpers import logging_helper

router = APIRouter()

@router.post("/modules", response_model=ModuleReadSchema, status_code=status.HTTP_201_CREATED)
def create_module(
    module_data: ModuleCreateSchema, 
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    # _ = Depends(role_required(["super_admin", "admin"]))
    _ = Depends(role_required())
):
    """
    Create a new module. Accessible by super_admin and admin roles.

    Args:
        module_data (ModuleCreateSchema): The module data.
    Returns:
        ModuleReadSchema: The created module.
    """
    module_repo = ModuleRepository(db)
    try:
        new_module = module_repo.create_module(module_data)
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.CREATE,
            "Module",
            new_module.id,
            {"data": module_data.dict()}
        )
        return new_module
    except HTTPException as e:
        logging_helper.log_error(f"Error creating module: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error creating module: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the module.")

@router.get("/modules/{module_id}", response_model=ModuleReadSchema)
def get_module(
    module_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    # _ = Depends(role_required(["admin", "manager", "hr"]))
    _ = Depends(role_required())
):
    """
    Retrieve a specific module by ID. Accessible by admin, manager, and hr roles.

    Args:
        module_id (int): The ID of the module to retrieve.
    Returns:
        ModuleReadSchema: The requested module.
    """
    module_repo = ModuleRepository(db)
    try:
        module = module_repo.get_module(module_id)
        return module
    except HTTPException as e:
        logging_helper.log_error(f"Error retrieving module: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error retrieving module: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving the module.")

@router.get("/modules", response_model=List[ModuleReadSchema])
def list_modules(
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    #_ = Depends(role_required(["admin", "manager", "hr"]))
    _ = Depends(role_required()) 
):
    """
    List all modules. Accessible by admin, manager, and hr roles.

    Returns:
        List[ModuleReadSchema]: A list of modules.
    """
    module_repo = ModuleRepository(db)
    try:
        modules = module_repo.list_modules()
        return modules
    except HTTPException as e:
        logging_helper.log_error(f"Error listing modules: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error listing modules: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while listing the modules.")

@router.put("/modules/{module_id}", response_model=ModuleReadSchema)
def update_module(
    module_id: int,
    update_data: ModuleUpdateSchema,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    # _ = Depends(role_required(["super_admin", "admin"]))
    _ = Depends(role_required())
):
    """
    Update an existing module. Accessible by super_admin and admin roles.

    Args:
        module_id (int): The ID of the module to update.
        update_data (ModuleUpdateSchema): The new data for the module.
    Returns:
        ModuleReadSchema: The updated module.
    """
    module_repo = ModuleRepository(db)
    try:
        updated_module = module_repo.update_module(module_id, update_data)
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.UPDATE,
            "Module",
            module_id,
            {"data": update_data.dict()}
        )
        return updated_module
    except HTTPException as e:
        logging_helper.log_error(f"Error updating module: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error updating module: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the module.")

@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_module(
    module_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    # _ = Depends(role_required(["super_admin"]))
    _ = Depends(role_required())
):
    """
    Delete a module. Only accessible by super_admin role.

    Args:
        module_id (int): The ID of the module to delete.
    """
    module_repo = ModuleRepository(db)
    try:
        module_repo.delete_module(module_id)
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.DELETE,
            "Module",
            module_id,
            {}
        )
    except HTTPException as e:
        logging_helper.log_error(f"Error deleting module: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error deleting module: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the module.")

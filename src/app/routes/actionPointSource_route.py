# #routes/actionpoint_route
# import json
# from typing import List
# from fastapi import APIRouter, Depends, HTTPException, status, Request
# from sqlalchemy.orm import Session
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# from db.database import get_db  # Adjust import path as needed
# from schemas.actionPointSource_schemas import ActionPointSourceCreate, ActionPointSourceUpdate, ActionPointSourceRead  # Adjust import paths as necessary
# from repositories.actionPointSource_repository import ActionPointSourceRepository  # Adjust import path as needed
# from logging_helpers import logging_helper
# from auth.security import get_current_user
# from models.all_models import ActionEnum, User
# from auth.dependencies import role_checker

# limiter = Limiter(key_func=get_remote_address)
# router = APIRouter()

# @router.post("/actionpointsource/", response_model=ActionPointSourceRead, status_code=status.HTTP_201_CREATED)
# @limiter.limit("5/minute")
# async def create_actionpointsource(
#     request: Request, 
#     actionpointsource_data: ActionPointSourceCreate, 
#     current_user: User = Depends(get_current_user), 
#     db: Session = Depends(get_db), _=Depends(role_checker(["super_admin"]))):

#     logging_helper.log_info("Accessing - create Actionpoint Source - Endpoint")
#     actionpointsource_repo = ActionPointSourceRepository(db)
#     try:
#         new_actionpointsource = actionpointsource_repo.create_actionpointsource(actionpointsource_data)
#         return new_actionpointsource
#     except Exception as e:
#         logging_helper.log_error(f"{str(e)}")
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error creating ActionPoint Source: Warning Unauthorized: {str(e)}")


# @router.get("/actionpointsource/", response_model=List[ActionPointSourceRead], status_code=status.HTTP_200_OK)
# @limiter.limit("10/minute")
# async def read_all_actionpointsource(
#     request: Request, 
#     current_user: User = Depends(get_current_user), 
#     db: Session = Depends(get_db), _=Depends(role_checker(['unit_member','programs_lead','technical_lead', 'stl', 'hq_backstop', 'tenant_admin','super_admin']))):
#     try:
#         logging_helper.log_info("Accessing - Read all Action Point Source - Endpoint")
#         actionpointsource_repo = ActionPointSourceRepository(db)
#         actionpointsource = actionpointsource_repo.get_all_actionpointsource()
#         logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "ActionPointSource", None)
#         return actionpointsource
#     except Exception as err:
#         logging_helper.log_error(f"{str(err)}")
#         raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


# @router.get("/actionpointsource/{actionpointsource_id}", response_model=ActionPointSourceRead, status_code=status.HTTP_200_OK)
# @limiter.limit("10/minute")
# async def read_actionpointsource(
#     request: Request, 
#     actionpointsource_id: int, 
#     current_user: User = Depends(get_current_user), 
#     db: Session = Depends(get_db), _=Depends(role_checker(['unit_member','programs_lead','technical_lead', 'stl', 'hq_backstop', 'tenant_admin','super_admin']))):
#     try:
#         logging_helper.log_info("Accessing - Read Action Point Source - Endpoint")
#         actionpointsource_repo = ActionPointSourceRepository(db)
#         actionpointsource = actionpointsource_repo.get_actionpointsource_by_id(actionpointsource_id)
#         if actionpointsource is None:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"actionpointsource not found")
#         logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "ActionPointSource", actionpointsource_id, None)
#         return actionpointsource
#     except Exception as err:
#         logging_helper.log_error(f"{str(err)}")
#         raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


# @router.put("/actionpointsource/{actionpointsource_id}")
# @limiter.limit("10/minute")
# async def update_actionpointsource(
#     request: Request, 
#     actionpointsource_id: int, 
#     actionpointsource_data: ActionPointSourceUpdate, 
#     current_user: User = Depends(get_current_user), 
#     db: Session = Depends(get_db), _=Depends(role_checker(["super_admin"]))):

#     try:
#         logging_helper.log_info("Accessing - Update Action Point Source - Endpoint")
#         actionpointsource_repo = ActionPointSourceRepository(db)
#         updated_actionpointsource = actionpointsource_repo.update_actionpointsource(actionpointsource_id, actionpointsource_data)
#         if updated_actionpointsource is None:
#             raise HTTPException(status_code=404, detail="Actionpointsource not found")
#         logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "ActionPointSource", actionpointsource_id, json.dumps(actionpointsource_data.dict()))
#         return updated_actionpointsource
#     except Exception as err:
#         logging_helper.log_error(f"{str(err)}")
#         raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


# @router.post("/actionpointsource/{actionpointsource_id}/soft_delete")
# @limiter.limit("5/minute")
# async def soft_delete_actionpointsource(
#     request: Request, 
#     actionpointsource_id: int, 
#     current_user: User = Depends(get_current_user), 
#     db: Session = Depends(get_db), _=Depends(role_checker(["super_admin"]))):

#     try:
#         logging_helper.log_info("Accessing - Soft Delete Action Point Source - Endpoint")
#         actionpointsource_repo = ActionPointSourceRepository(db)
#         actionpointsource = actionpointsource_repo.soft_delete_actionpointsource(actionpointsource_id)
#         if not actionpointsource:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Actionpointsource not found")
#         return actionpointsource
#     except Exception as err:
#         logging_helper.log_error(f"{str(err)}")
#         raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


# @router.post("/actionpointsource/{actionpointsource_id}/restore")
# @limiter.limit("5/minute")
# async def restore_actionpointsource(
#     request: Request, 
#     actionpointsource_id: int, 
#     current_user: User = Depends(get_current_user), 
#     db: Session = Depends(get_db), _=Depends(role_checker(["super_admin"]))):

#     try:
#         logging_helper.log_info("Accessing - Restore Action Point Source - Endpoint")
#         actionpointsource_repo = ActionPointSourceRepository(db)
#         actionpointsource = actionpointsource_repo.restore(actionpointsource_id)
#         if not actionpointsource:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Actionpointsource not found")
        
#         return actionpointsource
#     except Exception as err:
#         logging_helper.log_error(f"{str(err)}")
#         raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")




# routes/actionpoint_route.py

import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from db.database import get_db
from schemas.actionPointSource_schemas import ActionPointSourceCreate, ActionPointSourceUpdate, ActionPointSourceRead
from repositories.actionPointSource_repository import ActionPointSourceRepository
from logging_helpers import logging_helper
from auth.security import get_current_user
from models.all_models import ActionEnum, User
from auth.dependencies import role_checker

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/actionpointsource/", response_model=ActionPointSourceRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_actionpointsource(
    request: Request, 
    actionpointsource_data: ActionPointSourceCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db), _=Depends(role_checker(["super_admin"]))):
    """
    Create a new ActionPointSource.
    
    Parameters:
        request (Request): The HTTP request object.
        actionpointsource_data (ActionPointSourceCreate): The data required to create a new ActionPointSource.
        current_user (User): The currently authenticated user.
        db (Session): The database session.
        _ (role_checker): Role checker dependency.
    
    Returns:
        ActionPointSourceRead: The newly created ActionPointSource object.
    
    Raises:
        HTTPException: If an error occurs during creation.
    """
    logging_helper.log_info("Accessing - create Actionpoint Source - Endpoint")
    actionpointsource_repo = ActionPointSourceRepository(db)
    try:
        # Create a new ActionPointSource
        new_actionpointsource = actionpointsource_repo.create_actionpointsource(actionpointsource_data)
        return new_actionpointsource
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error creating ActionPoint Source: Warning Unauthorized: {str(e)}")

@router.get("/actionpointsource/", response_model=List[ActionPointSourceRead], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_all_actionpointsource(
    request: Request, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db), _=Depends(role_checker(['unit_member','programs_lead','technical_lead', 'stl', 'hq_backstop', 'tenant_admin','super_admin']))):
    """
    Retrieve all ActionPointSources.
    
    Parameters:
        request (Request): The HTTP request object.
        current_user (User): The currently authenticated user.
        db (Session): The database session.
        _ (role_checker): Role checker dependency.
    
    Returns:
        List[ActionPointSourceRead]: A list of all ActionPointSource objects.
    
    Raises:
        HTTPException: If an error occurs during retrieval.
    """
    logging_helper.log_info("Accessing - Read all Action Point Source - Endpoint")
    actionpointsource_repo = ActionPointSourceRepository(db)
    try:
        # Retrieve all ActionPointSources
        actionpointsource = actionpointsource_repo.get_all_actionpointsource()
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "ActionPointSource", None)
        return actionpointsource
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")

@router.get("/actionpointsource/{actionpointsource_id}", response_model=ActionPointSourceRead, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_actionpointsource(
    request: Request, 
    actionpointsource_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db), _=Depends(role_checker(['unit_member','programs_lead','technical_lead', 'stl', 'hq_backstop', 'tenant_admin','super_admin']))):
    """
    Retrieve an ActionPointSource by its ID.
    
    Parameters:
        request (Request): The HTTP request object.
        actionpointsource_id (int): The ID of the ActionPointSource to retrieve.
        current_user (User): The currently authenticated user.
        db (Session): The database session.
        _ (role_checker): Role checker dependency.
    
    Returns:
        ActionPointSourceRead: The ActionPointSource object if found.
    
    Raises:
        HTTPException: If the ActionPointSource is not found or if an error occurs during retrieval.
    """
    logging_helper.log_info("Accessing - Read Action Point Source - Endpoint")
    actionpointsource_repo = ActionPointSourceRepository(db)
    try:
        # Retrieve the ActionPointSource by ID
        actionpointsource = actionpointsource_repo.get_actionpointsource_by_id(actionpointsource_id)
        if actionpointsource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"actionpointsource not found")
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "ActionPointSource", actionpointsource_id, None)
        return actionpointsource
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")

@router.put("/actionpointsource/{actionpointsource_id}")
@limiter.limit("10/minute")
async def update_actionpointsource(
    request: Request, 
    actionpointsource_id: int, 
    actionpointsource_data: ActionPointSourceUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db), _=Depends(role_checker(["super_admin"]))):
    """
    Update an existing ActionPointSource.
    
    Parameters:
        request (Request): The HTTP request object.
        actionpointsource_id (int): The ID of the ActionPointSource to update.
        actionpointsource_data (ActionPointSourceUpdate): The updated data for the ActionPointSource.
        current_user (User): The currently authenticated user.
        db (Session): The database session.
        _ (role_checker): Role checker dependency.
    
    Returns:
        ActionPointSourceRead: The updated ActionPointSource object if successful.
    
    Raises:
        HTTPException: If the ActionPointSource is not found or if an error occurs during the update.
    """
    logging_helper.log_info("Accessing - Update Action Point Source - Endpoint")
    actionpointsource_repo = ActionPointSourceRepository(db)
    try:
        # Update the ActionPointSource
        updated_actionpointsource = actionpointsource_repo.update_actionpointsource(actionpointsource_id, actionpointsource_data)
        if updated_actionpointsource is None:
            raise HTTPException(status_code=404, detail="Actionpointsource not found")
        logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "ActionPointSource", actionpointsource_id, json.dumps(actionpointsource_data.dict()))
        return updated_actionpointsource
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")

@router.post("/actionpointsource/{actionpointsource_id}/soft_delete")
@limiter.limit("5/minute")
async def soft_delete_actionpointsource(
    request: Request, 
    actionpointsource_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db), _=Depends(role_checker(["super_admin"]))):
    """
    Soft delete an ActionPointSource by setting its is_active flag to False.
    
    Parameters:
        request (Request): The HTTP request object.
        actionpointsource_id (int): The ID of the ActionPointSource to soft delete.
        current_user (User): The currently authenticated user.
        db (Session): The database session.
        _ (role_checker): Role checker dependency.
    
    Returns:
        dict: A message indicating the successful deactivation of the ActionPointSource.
    
    Raises:
        HTTPException: If the ActionPointSource is not found or if an error occurs during the deletion.
    """
    logging_helper.log_info("Accessing - Soft Delete Action Point Source - Endpoint")
    actionpointsource_repo = ActionPointSourceRepository(db)
    try:
        # Soft delete the ActionPointSource
        actionpointsource = actionpointsource_repo.soft_delete_actionpointsource(actionpointsource_id)
        if not actionpointsource:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Actionpointsource not found")
        return actionpointsource
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")

@router.post("/actionpointsource/{actionpointsource_id}/restore")
@limiter.limit("5/minute")
async def restore_actionpointsource(
    request: Request, 
    actionpointsource_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db), _=Depends(role_checker(["super_admin"]))):
    """
    Restore a soft-deleted ActionPointSource by setting its is_active flag to True.
    
    Parameters:
        request (Request): The HTTP request object.
        actionpointsource_id (int): The ID of the ActionPointSource to restore.
        current_user (User): The currently authenticated user.
        db (Session): The database session.
        _ (role_checker): Role checker dependency.
    
    Returns:
        dict: A message indicating the successful restoration of the ActionPointSource.
    
    Raises:
        HTTPException: If the ActionPointSource is not found or if an error occurs during the restoration.
    """
    logging_helper.log_info("Accessing - Restore Action Point Source - Endpoint")
    actionpointsource_repo = ActionPointSourceRepository(db)
    try:
        # Restore the ActionPointSource
        actionpointsource = actionpointsource_repo.restore(actionpointsource_id)
        if not actionpointsource:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Actionpointsource not found")
        return actionpointsource
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")

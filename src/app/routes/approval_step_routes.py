# import os
# from fastapi import APIRouter, Depends, HTTPException, Query, status
# from sqlalchemy.orm import Session
# from typing import List, Optional

# from db.database import get_db
# from repositories.approval_step_repository import ApprovalStepRepository
# from schemas.approval_step_schemas import ApprovalStepCreateSchema, ApprovalStepUpdateSchema, ApprovalStepReadSchema
# from auth.dependencies import role_checker
# from auth.security import get_current_user
# from schemas.user_schemas import UserRead
# from models.all_models import ActionEnum
# from logging_helpers import logging_helper

# router = APIRouter()

# @router.post("/approval-steps", response_model=ApprovalStepReadSchema, status_code=status.HTTP_201_CREATED)
# def create_approval_step(
#     approval_step: ApprovalStepCreateSchema, 
#     db: Session = Depends(get_db), 
#     current_user: UserRead = Depends(get_current_user),
#     _ = Depends(role_checker(['admin', 'hr']))
# ):
#     """
#     Create a new approval step for a module and approval flow. Roles: admin, hr

#     Args:
#         approval_step (ApprovalStepCreateSchema): The approval step data.
#     Returns:
#         ApprovalStepReadSchema: The created approval step.
#     """
#     try:
#         approval_step_repo = ApprovalStepRepository(db_session=db)
#         new_step = approval_step_repo.create_approval_step(approval_step)
#         logging_helper.log_audit(
#             db, 
#             current_user.id, 
#             ActionEnum.CREATE, 
#             "ApprovalStep", 
#             new_step.id, 
#             {
#                 "step_order": approval_step.step_order, 
#                 "module_id": approval_step.module_id,
#                 "flow_id": approval_step.flow_id
#             }
#         )
#         return new_step
#     except HTTPException as e:
#         logging_helper.log_error(f"Error creating approval step: {str(e)}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Unexpected error creating approval step: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/approval-steps/{step_id}", response_model=ApprovalStepReadSchema)
# def get_approval_step(
#     step_id: int, 
#     db: Session = Depends(get_db),
#     current_user: UserRead = Depends(get_current_user),
#     _ = Depends(role_checker(['admin', 'manager', 'hr']))
# ):
#     """
#     Retrieve a specific approval step by ID. Roles: admin, manager, hr

#     Args:
#         step_id (int): The ID of the approval step to retrieve.
#     Returns:
#         ApprovalStepReadSchema: The requested approval step.
#     """
#     try:
#         approval_step_repo = ApprovalStepRepository(db_session=db)
#         step = approval_step_repo.get_approval_step(step_id)
#         if not step:
#             raise HTTPException(status_code=404, detail="Approval step not found")
#         return step
#     except HTTPException as e:
#         logging_helper.log_error(f"Error retrieving approval step: {str(e)}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Unexpected error retrieving approval step: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/approval-steps", response_model=List[ApprovalStepReadSchema])
# def list_approval_steps(
#     module_id: Optional[int] = Query(None, description="Filter approval steps by module ID"),
#     flow_id: Optional[int] = Query(None, description="Filter approval steps by flow ID"),
#     skip: int = Query(0, description="Number of records to skip"),
#     limit: int = Query(10, description="Maximum number of records to retrieve"),
#     db: Session = Depends(get_db),
#     current_user: UserRead = Depends(get_current_user),
#     _ = Depends(role_checker(['admin', 'manager', 'hr']))
# ):
#     """
#     List approval steps with optional filtering by module ID, flow ID, and pagination. Roles: admin, manager, hr

#     Args:
#         module_id (Optional[int]): The ID of the module to filter approval steps by.
#         flow_id (Optional[int]): The ID of the approval flow to filter steps by.
#         skip (int): The number of records to skip.
#         limit (int): The maximum number of records to retrieve.
#     Returns:
#         List[ApprovalStepReadSchema]: A list of approval steps.
#     """
#     try:
#         approval_step_repo = ApprovalStepRepository(db_session=db)
#         steps = approval_step_repo.list_approval_steps(module_id=module_id, flow_id=flow_id, skip=skip, limit=limit)
#         return steps
#     except HTTPException as e:
#         logging_helper.log_error(f"Error listing approval steps: {str(e)}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Unexpected error listing approval steps: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.put("/approval-steps/{step_id}", response_model=ApprovalStepReadSchema)
# def update_approval_step(
#     step_id: int, 
#     step_data: ApprovalStepUpdateSchema, 
#     db: Session = Depends(get_db), 
#     current_user: UserRead = Depends(get_current_user),
#     _ = Depends(role_checker(['super_admin', 'admin']))
# ):
#     """
#     Update an existing approval step. Roles: super_admin, admin

#     Args:
#         step_id (int): The ID of the approval step to update.
#         step_data (ApprovalStepUpdateSchema): The new data for the approval step.
#     Returns:
#         ApprovalStepReadSchema: The updated approval step.
#     """
#     try:
#         approval_step_repo = ApprovalStepRepository(db_session=db)
#         updated_step = approval_step_repo.update_approval_step(step_id, step_data)
#         if not updated_step:
#             raise HTTPException(status_code=404, detail="Approval step not found")
#         logging_helper.log_audit(
#             db, 
#             current_user.id, 
#             ActionEnum.UPDATE, 
#             "ApprovalStep", 
#             updated_step.id, 
#             {
#                 "step_order": updated_step.step_order, 
#                 "module_id": updated_step.module_id,
#                 "flow_id": updated_step.flow_id
#             }
#         )
#         return updated_step
#     except HTTPException as e:
#         logging_helper.log_error(f"Error updating approval step: {str(e)}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Unexpected error updating approval step: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.delete("/approval-steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_approval_step(
#     step_id: int, 
#     db: Session = Depends(get_db), 
#     current_user: UserRead = Depends(get_current_user),
#     _ = Depends(role_checker(['super_admin']))
# ):
#     """
#     Delete an approval step. Roles: super_admin

#     Args:
#         step_id (int): The ID of the approval step to delete.
#     """
#     try:
#         approval_step_repo = ApprovalStepRepository(db_session=db)
#         approval_step_repo.delete_approval_step(step_id)
#         logging_helper.log_audit(
#             db, 
#             current_user.id, 
#             ActionEnum.DELETE, 
#             "ApprovalStep", 
#             step_id
#         )
#     except HTTPException as e:
#         logging_helper.log_error(f"Error deleting approval step: {str(e)}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Unexpected error deleting approval step: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))








import os
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from dotenv import load_dotenv
from db.database import get_db
from auth.dependencies import role_checker
from auth.security import get_current_user
from schemas.user_schemas import UserRead
from schemas.approval_step_schemas import (
    ApprovalStepCreateSchema,
    ApprovalStepUpdateSchema,
    ApprovalStepReadSchema
)
from repositories.approval_step_repository import ApprovalStepRepository
from logging_helpers import logging_helper

# Load environment variables from .env file
load_dotenv()

# Load the base URL for the application from the environment
BASE_URL = os.getenv("BASE_URL", "https://yourapp.com")  # Default to yourapp.com if not found

router = APIRouter()

@router.post("/approval-steps", response_model=ApprovalStepReadSchema, status_code=status.HTTP_201_CREATED)
def create_approval_step(
    step_data: ApprovalStepCreateSchema,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['admin', 'super_admin']))
):
    """
    Create a new approval step.

    Args:
        step_data (ApprovalStepCreateSchema): The data for creating the approval step.
    
    Returns:
        ApprovalStepReadSchema: The newly created approval step.
    """
    try:
        step_repo = ApprovalStepRepository(db, base_url=BASE_URL)
        new_step = step_repo.create_approval_step(step_data)
        
        # Log the creation of the approval step
        logging_helper.log_audit(
            db,
            current_user.id,
            "CREATE",
            "ApprovalStep",
            new_step.id,
            {"data": step_data.dict()}
        )

        return new_step
    except HTTPException as e:
        logging_helper.log_error(f"Error creating approval step: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error creating approval step: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/approval-steps/{step_id}", response_model=ApprovalStepReadSchema)
def get_approval_step(
    step_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['admin', 'super_admin', 'manager']))
):
    """
    Retrieve a specific approval step by ID.

    Args:
        step_id (int): The ID of the approval step to retrieve.
    
    Returns:
        ApprovalStepReadSchema: The requested approval step.
    """
    try:
        step_repo = ApprovalStepRepository(db, base_url=BASE_URL)
        step = step_repo.get_approval_step(step_id)
        if not step:
            raise HTTPException(status_code=404, detail="Approval step not found")
        return step
    except HTTPException as e:
        logging_helper.log_error(f"Error retrieving approval step: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error retrieving approval step: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/approval-steps/{step_id}", response_model=ApprovalStepReadSchema)
def update_approval_step(
    step_id: int,
    update_data: ApprovalStepUpdateSchema,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['admin', 'super_admin']))
):
    """
    Update an existing approval step.

    Args:
        step_id (int): The ID of the approval step to update.
        update_data (ApprovalStepUpdateSchema): The data to update the approval step.
    
    Returns:
        ApprovalStepReadSchema: The updated approval step.
    """
    try:
        step_repo = ApprovalStepRepository(db, base_url=BASE_URL)
        updated_step = step_repo.update_approval_step(step_id, update_data)
        
        # Log the update action
        logging_helper.log_audit(
            db,
            current_user.id,
            "UPDATE",
            "ApprovalStep",
            step_id,
            {"data": update_data.dict()}
        )

        return updated_step
    except HTTPException as e:
        logging_helper.log_error(f"Error updating approval step: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error updating approval step: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/approval-steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_approval_step(
    step_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['super_admin']))
):
    """
    Delete an approval step.

    Args:
        step_id (int): The ID of the approval step to delete.
    """
    try:
        step_repo = ApprovalStepRepository(db, base_url=BASE_URL)
        step_repo.delete_approval_step(step_id)
        
        # Log the deletion
        logging_helper.log_audit(
            db,
            current_user.id,
            "DELETE",
            "ApprovalStep",
            step_id,
            {}
        )

    except HTTPException as e:
        logging_helper.log_error(f"Error deleting approval step: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error deleting approval step: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approval-steps/{step_id}/advance", status_code=status.HTTP_202_ACCEPTED)
def advance_approval_step(
    step_id: int,
    background_tasks: BackgroundTasks,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['admin', 'super_admin', 'manager']))
):
    """
    Advance the approval step to the next in the sequence and notify the next approver.

    Args:
        step_id (int): The ID of the current approval step.
        background_tasks (BackgroundTasks): Background tasks for asynchronous email notifications.

    Returns:
        dict: A message indicating if the approval step was advanced.
    """
    try:
        step_repo = ApprovalStepRepository(db, base_url=BASE_URL)
        advanced = step_repo.advance_approval_step(step_id, background_tasks)
        
        if advanced:
            logging_helper.log_info(f"Approval step {step_id} advanced and next approver notified.")
            return {"message": "Approval step advanced and next approver notified"}
        else:
            logging_helper.log_info(f"Approval flow completed for step {step_id}. No next approver.")
            return {"message": "Approval flow completed. No further steps"}

    except HTTPException as e:
        logging_helper.log_error(f"Error advancing approval step: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error advancing approval step: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/approval-steps", response_model=List[ApprovalStepReadSchema])
def list_approval_steps(
    module_id: Optional[int] = None,
    flow_id: Optional[int] = None,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['super_admin', 'manager']))
):
    """
    List all approval steps, optionally filtered by module ID or flow ID.

    Args:
        module_id (Optional[int]): Filter steps by module ID.
        flow_id (Optional[int]): Filter steps by flow ID.
    
    Returns:
        List[ApprovalStepReadSchema]: A list of approval steps.
    """
    try:
        step_repo = ApprovalStepRepository(db, base_url=BASE_URL)
        steps = step_repo.list_approval_steps(module_id=module_id, flow_id=flow_id)
        return steps
    except HTTPException as e:
        logging_helper.log_error(f"Error listing approval steps: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error listing approval steps: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




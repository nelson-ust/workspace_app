

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from auth.dependencies import role_required
from auth.security import get_current_user
from schemas.user_schemas import UserRead
from db.database import get_db
from repositories.approval_flow_repository import ApprovalFlowRepository
from schemas.approval_flow_schemas import ApprovalFlowCreateSchema, ApprovalFlowUpdateSchema, ApprovalFlowDisplaySchema
from logging_helpers import logging_helper

router = APIRouter()

@router.post(
    "/approval-flows",
    response_model=ApprovalFlowDisplaySchema,
    status_code=status.HTTP_201_CREATED,
)
def create_approval_flow(
    approval_flow_data: ApprovalFlowCreateSchema, 
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_required())  # Define a default role requirement here
):
    """
    Create a new approval flow and associate it with a module.
    Accessible by super_admin role.
    """
    try:
        approval_flow_repo = ApprovalFlowRepository(db)
        approval_flow = approval_flow_repo.create_approval_flow(approval_flow_data)

        logging_helper.log_audit(
            db,
            current_user.id,
            "CREATE",
            "ApprovalFlow",
            approval_flow.id,
            {
                "data": approval_flow_data.dict(),
                "module_id": approval_flow_data.module_id
            }
        )

        return approval_flow
    except HTTPException as e:
        logging_helper.log_error(f"Error creating approval flow: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error creating approval flow: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the approval flow.")

@router.get(
    "/approval-flows/{flow_id}",
    response_model=ApprovalFlowDisplaySchema,
)
def get_approval_flow(
    flow_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_required())  # Allow dynamic role check based on database route
):
    """
    Retrieve a specific approval flow by ID.
    Accessible by dynamically defined roles.
    """
    try:
        approval_flow_repo = ApprovalFlowRepository(db)
        approval_flow = approval_flow_repo.get_approval_flow_by_id(flow_id)
        if not approval_flow:
            raise HTTPException(status_code=404, detail="Approval flow not found")

        return approval_flow
    except HTTPException as e:
        logging_helper.log_error(f"Error retrieving approval flow: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error retrieving approval flow: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving the approval flow.")

@router.get(
    "/approval-flows",
    response_model=List[ApprovalFlowDisplaySchema],
)
def list_approval_flows(
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_required())  # Allow dynamic role check based on database route
):
    """
    List all approval flows.
    Accessible by dynamically defined roles.
    """
    try:
        approval_flow_repo = ApprovalFlowRepository(db)
        approval_flows = approval_flow_repo.list_approval_flows()

        return approval_flows
    except HTTPException as e:
        logging_helper.log_error(f"Error listing approval flows: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error listing approval flows: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while listing the approval flows.")

@router.put(
    "/approval-flows/{flow_id}",
    response_model=ApprovalFlowDisplaySchema,
)
def update_approval_flow(
    flow_id: int, 
    approval_flow_data: ApprovalFlowUpdateSchema, 
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_required(["super_admin", "unit_member"]))  # Define role requirement as needed
):
    """
    Update an existing approval flow. Optionally update its associated module.
    Accessible by super_admin and unit_member roles.
    """
    try:
        approval_flow_repo = ApprovalFlowRepository(db)
        approval_flow = approval_flow_repo.update_approval_flow(flow_id, approval_flow_data)
        if not approval_flow:
            raise HTTPException(status_code=404, detail="Approval flow not found")

        logging_helper.log_audit(
            db,
            current_user.id,
            "UPDATE",
            "ApprovalFlow",
            flow_id,
            {
                "data": approval_flow_data.dict(),
                "module_id": approval_flow_data.module_id
            }
        )

        return approval_flow
    except HTTPException as e:
        logging_helper.log_error(f"Error updating approval flow: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error updating approval flow: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the approval flow.")

@router.delete(
    "/approval-flows/{flow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_approval_flow(
    flow_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_required(["super_admin"]))  # Define a specific role for delete
):
    """
    Delete an approval flow.
    Accessible by super_admin role.
    """
    try:
        approval_flow_repo = ApprovalFlowRepository(db)
        approval_flow_repo.delete_approval_flow(flow_id)

        logging_helper.log_audit(
            db, 
            current_user.id, 
            "DELETE",
            "ApprovalFlow",
            flow_id,
            {}
        )
    except HTTPException as e:
        logging_helper.log_error(f"Error deleting approval flow: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error deleting approval flow: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the approval flow.")

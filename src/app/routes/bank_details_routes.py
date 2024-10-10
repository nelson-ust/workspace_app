from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from schemas.bank_detail_schemas import BankDetail, BankDetailCreate, BankDetailUpdate, BankDetailsFilter
from repositories.bank_details_repository import BankDetailsRepository
from auth.dependencies import role_checker
from auth.security import get_current_user
from db.database import get_db
from logging_helpers import logging_helper
from schemas.user_schemas import UserRead

router = APIRouter()

# Create Bank Detail
@router.post("/bank-details/", response_model=BankDetail)
def create_bank_detail(
    bank_detail: BankDetailCreate,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['tenant_admin', 'super_admin']))
):
    """
    Create a new bank detail record for an employee.

    Roles to Access the endpoint
        super_admin, tenant_admin
    """
    try:
        bank_details_repo = BankDetailsRepository(db_session=db)
        created_detail = bank_details_repo.create_bank_detail(
            employee_id=bank_detail.employee_id,
            bank_name=bank_detail.bank_name,
            account_number=bank_detail.account_number,
            ifsc_code=bank_detail.ifsc_code,
        )
        logging_helper.log_audit(
            user_id=current_user.id,
            action="CREATE",
            model="BankDetail",
            model_id=created_detail.id,
            changes=f"Created bank detail for employee ID {bank_detail.employee_id}",
            db_session=db
        )
        return created_detail
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update Bank Detail
@router.put("/bank-details/{bank_detail_id}", response_model=BankDetail)
def update_bank_detail(
    bank_detail_id: int,
    bank_detail_update: BankDetailUpdate,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['tenant_admin', 'super_admin']))
):
    """
    Update an existing bank detail record.

    Roles to Access the endpoint
        super_admin, tenant_admin
    """
    try:
        bank_details_repo = BankDetailsRepository(db_session=db)
        updated_detail = bank_details_repo.update_bank_detail(
            bank_detail_id=bank_detail_id,
            bank_name=bank_detail_update.bank_name,
            account_number=bank_detail_update.account_number,
            ifsc_code=bank_detail_update.ifsc_code,
        )
        logging_helper.log_audit(
            user_id=current_user.id,
            action="UPDATE",
            model="BankDetail",
            model_id=bank_detail_id,
            changes=f"Updated bank detail with ID {bank_detail_id}",
            db_session=db
        )
        return updated_detail
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete Bank Detail by ID
@router.delete("/bank-details/{bank_detail_id}")
def delete_bank_detail(
    bank_detail_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['tenant_admin', 'super_admin']))
):
    """
    Delete a specific bank detail record by its ID.

    Roles to Access the endpoint
        super_admin, tenant_admin
    """
    try:
        bank_details_repo = BankDetailsRepository(db_session=db)
        bank_details_repo.delete_bank_detail(bank_detail_id=bank_detail_id)
        logging_helper.log_audit(
            user_id=current_user.id,
            action="DELETE",
            model="BankDetail",
            model_id=bank_detail_id,
            changes=f"Deleted bank detail with ID {bank_detail_id}",
            db_session=db
        )
        return {"message": "Bank detail deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get All Bank Details
@router.get("/bank-details/", response_model=List[BankDetail])
def get_all_bank_details(
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['tenant_admin', 'super_admin']))
):
    """
    Retrieve a list of all bank details.

    Roles to Access the endpoint
        super_admin, tenant_admin
    """
    try:
        bank_details_repo = BankDetailsRepository(db_session=db)
        return bank_details_repo.get_all_bank_details()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get Bank Detail by ID
@router.get("/bank-details/{bank_detail_id}", response_model=BankDetail)
def get_bank_detail_by_id(
    bank_detail_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['tenant_admin', 'super_admin']))
):
    """
    Retrieve a specific bank detail by its ID.

    Roles to Access the endpoint
        super_admin, tenant_admin
    """
    try:
        bank_details_repo = BankDetailsRepository(db_session=db)
        return bank_details_repo.get_bank_detail_by_id(bank_detail_id=bank_detail_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# # Get Bank Details by Project ID or Tenancy ID
# @router.get("/bank-details/filter/", response_model=List[BankDetail])
# def get_bank_details_by_project_or_tenancy(
#     project_id: Optional[int] = None,
#     tenancy_id: Optional[int] = None,
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db),
#     _ = Depends(role_checker(['tenant_admin', 'super_admin']))
# ):
#     """
#     Retrieve bank details of all employees with an optional filter by project_id or tenancy_id.
#     """
#     try:
#         bank_details_repo = BankDetailsRepository(db_session=db)
#         return bank_details_repo.get_bank_details_by_project_or_tenancy(
#             project_id=project_id, tenancy_id=tenancy_id
#         )
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.post("/bank-details/filter/", response_model=List[BankDetail])
def get_bank_details_by_project_or_tenancy(
    filter_data: BankDetailsFilter,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['tenant_admin', 'super_admin']))
):
    """
    Retrieve bank details of all employees filtered by project_ids or tenancy_ids.

    Roles to Access the endpoint
        super_admin, tenant_admin
    """
    try:
        bank_details_repo = BankDetailsRepository(db_session=db)
        return bank_details_repo.get_bank_details_by_project_or_tenancy(
            project_ids=filter_data.project_ids, 
            tenancy_ids=filter_data.tenancy_ids
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

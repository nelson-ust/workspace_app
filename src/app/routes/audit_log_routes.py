# #routes/audit_log_routes.py
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import Any, List, Dict
# from db.database import get_db
# from repositories.audit_log_repository import AuditLogRepository
# from logging_helpers import logging_helper
# from auth.security import get_current_user
# from models.all_models import User
# from datetime import datetime

# router = APIRouter()

# @router.get("/audit-logs/", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
# async def read_audit_logs(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info("Accessing - Read all Audit Logs - Endpoint")
#     audit_log_repo = AuditLogRepository(db)
#     try:
#         audit_logs = audit_log_repo.get_audit_logs(skip=skip, limit=limit, user_id=current_user.id)
#         return audit_logs
#     except Exception as e:
#         logging_helper.log_error(f"Failed to fetch audit logs: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch audit logs")
    

# @router.get("/audit-logs/date-range/", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
# async def read_audit_logs_by_date_range(start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info("Accessing - Read Audit Logs by Date Range - Endpoint")
#     audit_log_repo = AuditLogRepository(db)
#     try:
#         audit_logs = audit_log_repo.get_audit_logs_by_date_range(start_date=start_date, end_date=end_date, skip=skip, limit=limit, user_id=current_user.id)
#         return audit_logs
#     except Exception as e:
#         logging_helper.log_error(f"Failed to fetch audit logs by date range: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch audit logs by date range")


#routes/audit_log_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List, Dict
from db.database import get_db
from repositories.audit_log_repository import AuditLogRepository
from logging_helpers import logging_helper
from auth.security import get_current_user
from models.all_models import User
from datetime import datetime

# Initialize the APIRouter instance for defining routes
router = APIRouter()

@router.get("/audit-logs/", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def read_audit_logs(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Endpoint to fetch all audit logs with optional pagination.
    
    Args:
        skip (int): The number of records to skip for pagination.
        limit (int): The maximum number of records to return for pagination.
        current_user (User, optional): The currently authenticated user.
        db (Session, optional): The database session dependency.

    Returns:
        List[Dict[str, Any]]: A list of audit logs with user details.

    Roles to Access the endpoint
        super_admin, tenant_admin
    """
    logging_helper.log_info("Accessing - Read all Audit Logs - Endpoint")
    audit_log_repo = AuditLogRepository(db)
    try:
        # Fetch audit logs using the repository method
        audit_logs = audit_log_repo.get_audit_logs(skip=skip, limit=limit, user_id=current_user.id)
        return audit_logs
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch audit logs: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch audit logs")
    

@router.get("/audit-logs/date-range/", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def read_audit_logs_by_date_range(start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Endpoint to fetch audit logs by date range with optional pagination.
    
    Args:
        start_date (datetime): The start date for filtering audit logs.
        end_date (datetime): The end date for filtering audit logs.
        skip (int): The number of records to skip for pagination.
        limit (int): The maximum number of records to return for pagination.
        current_user (User, optional): The currently authenticated user.
        db (Session, optional): The database session dependency.

    Returns:
        List[Dict[str, Any]]: A list of audit logs within the specified date range with user details.
    
    Roles to Access the endpoint
        super_admin, tenant_admin
    """
    logging_helper.log_info("Accessing - Read Audit Logs by Date Range - Endpoint")
    audit_log_repo = AuditLogRepository(db)
    try:
        # Fetch audit logs by date range using the repository method
        audit_logs = audit_log_repo.get_audit_logs_by_date_range(start_date=start_date, end_date=end_date, skip=skip, limit=limit, user_id=current_user.id)
        return audit_logs
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch audit logs by date range: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch audit logs by date range")

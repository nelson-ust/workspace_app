from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter #_rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from auth.dependencies import role_checker
from db.database import get_db  
from schemas.department_schemas import DepartmentCreate, DepartmentUpdate, DepartmentRead 
from repositories.department_repository import DepartmentRepository  
from logging_helpers import logging_helper
from schemas.user_schemas import UserRead
from auth.security import get_current_user


limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

# # Add rate limit exceeded handler
# router.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/departments/", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")

async def create_department(request: Request,department: DepartmentCreate, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):

    """
    Roles to Access the endpoint
            super_admin
    """
    try:
        logging_helper.log_info("Accessing - Crete Department - Endpoint")
        department_repo = DepartmentRepository(db)
        return department_repo.create_department(department)
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/departments/", response_model=List[DepartmentRead])
@limiter.limit("20/minute")
async def read_departments(request: Request,skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user:UserRead=Depends(get_current_user), _=Depends(role_checker(['hq_backstop','unit_member','unit_lead','programs-lead', 'tech-lead', 'stl', 'tenant_admin', 'super_admin']))):
    """
    Roles to Access the endpoint
        unit_member  
    """
    
    try:
        logging_helper.log_info("Accessing - Read Departments - Endpoint")
        department_repo = DepartmentRepository(db)
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                departments = department_repo.get_departments(skip=skip, limit=limit)
            else:
                departments = department_repo.get_departments(skip=skip, limit=limit, department_id=current_user.department_id)
            return departments
    except Exception as e:
        logging_helper.log_error(f"Encountered and Error Fetching departments: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/departments/{department_id}", response_model=DepartmentRead)
@limiter.limit("20/minute")
async def read_department(request: Request,department_id: int, db: Session = Depends(get_db), current_user:UserRead=Depends(get_current_user), _=Depends(role_checker(['hq_backstop','unit_member','unit_lead','programs-lead', 'tech-lead', 'stl', 'tenant_admin', 'super_admin']))):

    """
    Roles to Access the endpoint
        unit_member
    """
    try:
        logging_helper.log_info("Accessing - Read Department - Endpoint")
        department_repo = DepartmentRepository(db)
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                department = department_repo.get_department_by_id(department_id)
                if department is None:
                    raise HTTPException(status_code=404, detail="Department not found")
            else:
                department = department_repo.get_department_by_id(department_id, dept_id=current_user.department_id)
                if department is None:
                    raise HTTPException(status_code=404, detail="Department not found")
            return department
    except Exception as e:
        logging_helper.log_error(f"Encountered and Error Fetching departments: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/departments/{department_id}")
@limiter.limit("5/minute")
async def update_department(request: Request,department_id: int, department: DepartmentUpdate, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):

    """
    Roles to Access the endpoint
        super_admin
    """
    try:
        logging_helper.log_info("Accessing - Update Department - Endpoint")
        department_repo = DepartmentRepository(db)
        updated_department = department_repo.update_department(department_id, department)
        if updated_department is None:
            raise HTTPException(status_code=404, detail="Department not found")
        return updated_department
    except Exception as e:
        logging_helper.log_error(f"Encountered and Error Fetching departments: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/departments/{department_id}")
@limiter.limit("5/minute")
async def soft_delete_department(request: Request,department_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):

    """
    Roles to Access the endpoint
        super_admin
    """
    try:
        logging_helper.log_info("Accessing - Soft Delete Department - Endpoint")
        department_repo = DepartmentRepository(db)
        deleted_department = department_repo.soft_delete_department(department_id)
        if deleted_department is None:
            raise HTTPException(status_code=404, detail="Department not found")
        return deleted_department
    except Exception as e:
        logging_helper.log_error(f"Encountered and Error Fetching departments: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/departments/{department_id}/restore")
@limiter.limit("5/minute")
async def restore_department(request: Request,department_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):

    """
    Roles to Access the endpoint
        super_admin
    """
    try:
        logging_helper.log_info("Accessing - Restore Department - Endpoint")
        department_repo = DepartmentRepository(db)
        restored_department = department_repo.restore_department(department_id)
        if restored_department is None:
            raise HTTPException(status_code=404, detail="Department not found or not deleted")
        return restored_department
    except Exception as e:
        logging_helper.log_error(f"Encountered and Error Fetching departments: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

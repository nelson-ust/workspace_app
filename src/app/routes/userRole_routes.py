from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from typing import List
from sqlalchemy.orm import Session
from auth.dependencies import role_checker
from schemas.userRole_schemas import UserRoleCreate, UserRole, UserRoleUpdate  # Adjust import paths
from repositories.userRole_repository import UserRoleRepository  # Adjust import paths
from db.database import get_db  # Adjust import paths
from slowapi import Limiter
from slowapi.util import get_remote_address
from logging_helpers import logging_helper

# Initialize the limiter
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

# Rate limit exceeded handler
#router.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/user-roles/", response_model=UserRole, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_user_role(request:Request,user_role: UserRoleCreate, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    try:
        logging_helper.log_info("Accessing - Create User Role - Endpoint")
        user_role_repo = UserRoleRepository(db)
    
        return user_role_repo.create_role(user_role)
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user-roles/{role_id}", response_model=UserRole, responses={404: {"description": "Role not found"}})
@limiter.limit("10/minute")
async def read_user_role(request:Request,role_id: int, db: Session = Depends(get_db)): #,_=Depends(role_checker(['super_admin']))):
    try:
        logging_helper.log_info("Accessing - Read User Role - Endpoint")
        user_role_repo = UserRoleRepository(db)
        role = user_role_repo.get_role_by_id(role_id)
        if role is None:
            raise HTTPException(status_code=404, detail="UserRole not found")
        return role
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Add more routes as needed for update, delete, etc.
@router.get("/user-roles/", response_model=List[UserRole], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_user_roles(request:Request, skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)): #,_=Depends(role_checker(['super_admin']))):
    try:
        logging_helper.log_info("accessing - Read User Roles - Endpoint")
        user_role_repo = UserRoleRepository(db)
        roles = user_role_repo.get_roles(skip=skip, limit=limit)
        return roles
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/user-roles/{role_id}", responses={404: {"description": "Role not found"}})
@limiter.limit("5/minute")
async def update_user_role(request:Request,role_id: int, role_update: UserRoleUpdate, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    try:
        logging_helper.log_info("Accessing - Update Usser Role - Endpoint")
        user_role_repo = UserRoleRepository(db)
        updated_role = user_role_repo.update_role(role_id, role_update)
        if updated_role is None:
            raise HTTPException(status_code=404, detail="UserRole not found")
        return updated_role
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/user-roles/{role_id}")
@limiter.limit("5/minute")
async def soft_delete_user_role(request:Request,role_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    try:
        logging_helper.log_info("Accessing - Soft delete User Role - Endpoint")
        user_role_repo = UserRoleRepository(db)
        if not user_role_repo.soft_delete_role(role_id):
            raise HTTPException(status_code=404, detail="UserRole not found")
        return {"message": "UserRole soft-deleted successfully"}
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/user-roles/{role_id}/restore", responses={404: {"description": "Role not found or not deleted"}})
@limiter.limit("5/minute")
async def restore_user_role(request:Request,role_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['super_admin']))):
    try:
        logging_helper.log_info("Accessing - Restore User Role - Endpoint")
        user_role_repo = UserRoleRepository(db)
        restored_role = user_role_repo.restore_role(role_id)
        if restored_role is None:
            raise HTTPException(status_code=404, detail="UserRole not found or not deleted")
        return {"message": "UserRole restored successfully"}
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

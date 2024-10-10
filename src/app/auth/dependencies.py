# auth/dependencies.py
from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.user_schemas import UserRead
from db.database import get_db
from models.all_models import User, UserRole
from auth.security import get_current_user as security_get_current_user

def get_current_user(db: Session = Depends(get_db), token: str = Depends(security_get_current_user)):
    """
    Dependency to get the current user from the token. Uses the get_current_user
    function defined in security.py and extends it with database access.
    """
    user = db.query(User).filter(User.id == token.id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Dependency to check if the current user is active.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_user_with_roles(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Dependency to get the current user along with their roles. This can be useful for role-based access control.
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def has_role(db: Session = Depends(get_db), role: str = "", current_user: User = Depends(get_current_user_with_roles)):
    """
    Dependency to check if the current user has a specific role.
    """
    roles = [user_role.name for user_role in current_user.roles]
    if role not in roles:
        raise HTTPException(status_code=403, detail="Operation not permitted")

# Dependency for role check
def role_checker(allowed_roles: List[str]):
    async def _role_check(current_user=Depends(get_current_user_with_roles)):
        user_roles = [role.name for role in current_user.roles]
        if not set(allowed_roles) & set(user_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have the required permissions")
        return True
    return _role_check

#Depency for tenancy check
def tenancy_checker(alloowed_tenant: List[str]):
    pass

# def require_roles(required_roles: List[str]):
#     def _role_checker(current_user=Depends(get_current_user)):  
#         user_roles = [role.name for role in current_user.roles]  
#         if not any(role in user_roles for role in required_roles):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="The user doesn't have the required permissions",
#             )
#         return True
#     return _role_checker
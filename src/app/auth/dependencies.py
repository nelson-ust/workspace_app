# # auth/dependencies.py
# from typing import List
# from fastapi import Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from schemas.user_schemas import UserRead
# from db.database import get_db
# from models.all_models import User, UserRole
# from auth.security import get_current_user as security_get_current_user

# def get_current_user(db: Session = Depends(get_db), token: str = Depends(security_get_current_user)):
#     """
#     Dependency to get the current user from the token. Uses the get_current_user
#     function defined in security.py and extends it with database access.
#     """
#     user = db.query(User).filter(User.id == token.id).first()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user


# def get_current_active_user(current_user: User = Depends(get_current_user)):
#     """
#     Dependency to check if the current user is active.
#     """
#     if not current_user.is_active:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user

# def get_current_user_with_roles(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
#     """
#     Dependency to get the current user along with their roles. This can be useful for role-based access control.
#     """
#     user = db.query(User).filter(User.id == current_user.id).first()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user


# def has_role(db: Session = Depends(get_db), role: str = "", current_user: User = Depends(get_current_user_with_roles)):
#     """
#     Dependency to check if the current user has a specific role.
#     """
#     roles = [user_role.name for user_role in current_user.roles]
#     if role not in roles:
#         raise HTTPException(status_code=403, detail="Operation not permitted")

# # Dependency for role check
# def role_checker(allowed_roles: List[str]):
#     async def _role_check(current_user=Depends(get_current_user_with_roles)):
#         user_roles = [role.name for role in current_user.roles]
#         if not set(allowed_roles) & set(user_roles):
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have the required permissions")
#         return True
#     return _role_check

# #Depency for tenancy check
# def tenancy_checker(alloowed_tenant: List[str]):
#     pass


# auth/dependencies.py

from typing import List, Callable, Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.database import get_db
from models.all_models import User, Route, RouteRole
from auth.security import get_current_user as security_get_current_user
from schemas.user_schemas import UserRead
import logging


def get_current_user(db: Session = Depends(get_db), token: str = Depends(security_get_current_user)) -> User:
    try:
        user = db.query(User).filter(User.id == token.id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while retrieving the user."
        ) from e


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_user_with_roles(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
) -> User:
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while retrieving user roles."
        ) from e


# def role_required(allowed_roles: Optional[List[str]] = None) -> Callable:
#     """
#     Hybrid role-based access control.

#     Args:
#         allowed_roles (Optional[List[str]]): List of roles permitted to access the endpoint. 
#                                              If None, retrieves roles from the database.

#     Returns:
#         Callable: Dependency function for role verification.
#     """
#     async def _role_check(
#         request: Request, 
#         current_user: User = Depends(get_current_user_with_roles), 
#         db: Session = Depends(get_db)
#     ) -> bool:
#         # Get the requested path and method
#         request_path = request.scope["path"]
#         request_method = request.method

#         try:
#             # If roles are injected directly, use them
#             if allowed_roles:
#                 required_roles = set(allowed_roles)
#             else:
#                 # Otherwise, retrieve roles dynamically from the database
#                 route = db.query(Route).filter(
#                     Route.path == request_path,
#                     Route.method == request_method
#                 ).first()

#                 if route is None:
#                     raise HTTPException(
#                         status_code=status.HTTP_404_NOT_FOUND,
#                         detail="Route not found or not configured for access control."
#                     )

#                 required_roles = {route_role.role.name for route_role in route.route_roles}

#             # Check if the user has any of the required roles
#             user_roles = {role.name for role in current_user.roles}
#             if not user_roles.intersection(required_roles):
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="The user doesn't have the required permissions for this route."
#                 )
            
#             return True

#         except SQLAlchemyError as e:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Database error occurred while checking route permissions."
#             ) from e


#     return _role_check


# Modified role_required function
def role_required(allowed_roles: Optional[List[str]] = None) -> Callable:
    async def _role_check(
        request: Request, 
        current_user: User = Depends(get_current_user_with_roles), 
        db: Session = Depends(get_db)
    ) -> bool:
        # Get the requested path and method
        request_path = request.scope["path"]
        request_method = request.method

        # Log request path and method
        logging.info(f"Checking access for path: {request_path} and method: {request_method}")

        try:
            if allowed_roles:
                required_roles = set(allowed_roles)
            else:
                # Retrieve roles dynamically from the database
                route = db.query(Route).filter(
                    Route.path == request_path,
                    Route.method == request_method
                ).first()

                # Log route retrieval status
                if route:
                    logging.info(f"Route found in DB: {route.path} with method: {route.method}")
                else:
                    logging.warning(f"No matching route found in DB for path: {request_path} and method: {request_method}")
                
                if not route:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Route not found or not configured for access control."
                    )

                required_roles = {route_role.role.name for route_role in route.route_roles}
                if not required_roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="No roles configured for this route in the database."
                    )

            # Check if the user has any of the required roles
            user_roles = {role.name for role in current_user.roles}
            if not user_roles.intersection(required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="The user doesn't have the required permissions for this route."
                )
            
            return True

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while checking route permissions."
            ) from e

    return _role_check


def tenancy_required(allowed_tenants: List[str]) -> Callable:
    async def _tenant_check(current_user: User = Depends(get_current_user_with_roles)) -> bool:
        user_tenants = {tenant.name for tenant in current_user.tenancy}
        if not user_tenants.intersection(allowed_tenants):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have the required permissions for this tenant."
            )
        return True

    return _tenant_check

# Dependency for role check
def role_checker(allowed_roles: List[str]):
    async def _role_check(current_user=Depends(get_current_user_with_roles)):
        user_roles = [role.name for role in current_user.roles]
        if not set(allowed_roles) & set(user_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have the required permissions")
        return True
    return _role_check








# # auth/dependencies.py
# from typing import List
# from fastapi import Depends, HTTPException, status, Request
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from db.database import get_db
# from models.all_models import User, UserRole, Route, RouteRole
# from auth.security import get_current_user as security_get_current_user
# from logging_helpers import logging_helper  # Assuming you have a logging helper for consistent logging

# def get_current_user(db: Session = Depends(get_db), token: str = Depends(security_get_current_user)):
#     """
#     Retrieve the current user from the token and database session.

#     Args:
#         db (Session, optional): The database session.
#         token (str): The token containing user ID for authentication.

#     Returns:
#         User: The authenticated user instance.

#     Raises:
#         HTTPException: If the user is not found or a database error occurs.
#     """
#     try:
#         user = db.query(User).filter(User.id == token.id).first()
#         if user is None:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#         return user
#     except SQLAlchemyError as e:
#         logging_helper.log_error(f"Database error during get_current_user: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error") from e

# def get_current_active_user(current_user: User = Depends(get_current_user)):
#     """
#     Ensure the current user is active.

#     Args:
#         current_user (User, optional): The current authenticated user.

#     Returns:
#         User: The active user instance.

#     Raises:
#         HTTPException: If the user is inactive.
#     """
#     if not current_user.is_active:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
#     return current_user

# def get_current_user_with_roles(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
#     """
#     Retrieve the current active user along with their roles.

#     Args:
#         db (Session, optional): The database session.
#         current_user (User, optional): The current active user.

#     Returns:
#         User: The user instance with associated roles.

#     Raises:
#         HTTPException: If the user is not found or a database error occurs.
#     """
#     try:
#         user = db.query(User).filter(User.id == current_user.id).first()
#         if user is None:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#         return user
#     except SQLAlchemyError as e:
#         logging_helper.log_error(f"Database error during get_current_user_with_roles: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error") from e

# def get_allowed_roles_for_route(db: Session, path: str, method: str) -> List[str]:
#     """
#     Retrieve allowed roles for a specific route path and method.

#     Args:
#         db (Session): The database session.
#         path (str): The path of the route.
#         method (str): The HTTP method (GET, POST, etc.) of the route.

#     Returns:
#         List[str]: List of role names permitted for this route.

#     Raises:
#         HTTPException: If the route is not found or a database error occurs.
#     """
#     try:
#         route = db.query(Route).filter(Route.path == path, Route.method == method).first()
#         if route:
#             return [role_role.role.name for role_role in route.route_roles]
#         else:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Route not found or not configured with roles"
#             )
#     except SQLAlchemyError as e:
#         logging_helper.log_error(f"Database error during get_allowed_roles_for_route: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error") from e

# def route_role_checker(db: Session = Depends(get_db)):
#     """
#     Verifies if the current user has permission for the specific route.

#     Args:
#         db (Session, optional): The database session.

#     Returns:
#         Function: A dependency function for dynamic role-based permission checking.

#     Raises:
#         HTTPException: If the user lacks permissions for the route.
#     """
#     async def _role_check(request: Request, current_user: User = Depends(get_current_user_with_roles)):
#         try:
#             allowed_roles = get_allowed_roles_for_route(db, request.url.path, request.method)
#             user_roles = {role.name for role in current_user.roles}
#             if not user_roles.intersection(allowed_roles):
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="The user doesn't have the required permissions for this route"
#                 )
#             return True
#         except HTTPException as e:
#             raise e
#         except Exception as e:
#             logging_helper.log_error(f"Unexpected error in route_role_checker: {str(e)}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e
#     return _role_check

# def tenancy_checker(allowed_tenants: List[str]):
#     """
#     Tenant-based access control.

#     Args:
#         allowed_tenants (List[str]): List of tenants permitted to access the endpoint.

#     Returns:
#         Callable: Dependency function for tenant verification.

#     Raises:
#         HTTPException: If the user does not belong to the allowed tenants.
#     """
#     async def _tenant_check(current_user: User = Depends(get_current_user_with_roles)):
#         try:
#             user_tenants = {tenant.name for tenant in current_user.tenancy}
#             if not user_tenants.intersection(allowed_tenants):
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="The user doesn't have the required permissions for this tenant"
#                 )
#             return True
#         except Exception as e:
#             logging_helper.log_error(f"Unexpected error in tenancy_checker: {str(e)}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e
#     return _tenant_check


# # Dependency for role check
# def role_checker(allowed_roles: List[str]):
#     async def _role_check(current_user=Depends(get_current_user_with_roles)):
#         user_roles = [role.name for role in current_user.roles]
#         if not set(allowed_roles) & set(user_roles):
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have the required permissions")
#         return True
#     return _role_check
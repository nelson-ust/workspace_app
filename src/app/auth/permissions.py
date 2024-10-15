# auth/permission.py
from fastapi import HTTPException, status, Request, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from models.all_models import UserRole, RouteRole, Route
from auth.dependencies import get_current_user_with_roles


class RoleChecker:
    def __init__(self, db: Session):
        self.db = db

    def check_route_access(self, allowed_roles: list, path: str, method: str) -> bool:
        """
        Checks if any of the allowed roles has access to the specified route and method.
        """
        # Query for the route based on the path and method
        route = self.db.query(Route).filter_by(path=path, method=method).first()
        
        if not route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requested route not found."
            )
        
        # Get all roles that have access to this route
        route_roles = (
            self.db.query(RouteRole)
            .filter(RouteRole.route_id == route.id)
            .join(UserRole)
            .filter(UserRole.name.in_(allowed_roles))
            .all()
        )
        
        return bool(route_roles)  # Returns True if any allowed role matches


async def role_checker(allowed_roles: list, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user_with_roles)):
    """
    Dependency function that checks if the current user has access to the route based on allowed roles.
    """
    role_checker = RoleChecker(db)
    
    # Retrieve user roles
    user_roles = [role.name for role in current_user.roles]
    
    # Check if the user has any of the allowed roles for this path and method
    if not role_checker.check_route_access(user_roles, request.url.path, request.method):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the required permissions for this operation."
        )
    
    return True  # Access granted

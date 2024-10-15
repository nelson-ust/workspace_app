# #routes/route_management_routes.py
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from db.database import get_db
# from auth.dependencies import role_required
# from repositories.route_repository import RouteRepository
# from schemas.route_schemas import RouteCreateSchema, RouteUpdateSchema
# from logging_helpers import logging_helper
# from auth.security import get_current_user
# from models.all_models import ActionEnum, Route
# from typing import List

# router = APIRouter()

# # Define the role required to access these endpoints (super_admin)
# super_admin_role = ["super_admin"]

# @router.post("/routes", response_model=dict, status_code=status.HTTP_201_CREATED)
# async def create_route(
#     route_data: RouteCreateSchema,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
#     _ = Depends(role_required(super_admin_role))
# ):
#     """
#     Creates a new route with associated permitted roles.

#     Args:
#         route_data (RouteCreateSchema): The data for creating a new route.
#         db (Session, optional): The database session.

#     Returns:
#         dict: Confirmation message and the created route ID.

#     Raises:
#         HTTPException: If there is a database error or any role is not found.
#     """
#     try:
#         route_repo = RouteRepository(db)
#         route = route_repo.create_route(route_data)
        
#         # Log audit action
#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.CREATE,
#             "Route",
#             route.id,
#             {"data": route_data.dict()}
#         )
        
#         return {"message": "Route created successfully", "route_id": route.id}
#     except HTTPException as e:
#         raise e
#     except SQLAlchemyError as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Error creating route."
#         ) from e


# @router.put("/routes/{route_id}", response_model=dict)
# async def update_route(
#     route_id: int,
#     update_data: RouteUpdateSchema,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
#     _ = Depends(role_required(super_admin_role))
# ):
#     """
#     Updates an existing route and its permitted roles.

#     Args:
#         route_id (int): The ID of the route to update.
#         update_data (RouteUpdateSchema): The updated route data.
#         db (Session, optional): The database session.

#     Returns:
#         dict: Confirmation message of successful update.

#     Raises:
#         HTTPException: If the route or any specified role is not found, or if a database error occurs.
#     """
#     try:
#         route_repo = RouteRepository(db)
#         route_repo.update_route(route_id, update_data)
        
#         # Log audit action
#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.UPDATE,
#             "Route",
#             route_id,
#             {"data": update_data.dict()}
#         )
        
#         return {"message": "Route updated successfully"}
#     except HTTPException as e:
#         raise e
#     except SQLAlchemyError as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Error updating route."
#         ) from e


# @router.delete("/routes/{route_id}", response_model=dict)
# async def delete_route(
#     route_id: int,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
#     _ = Depends(role_required(super_admin_role))
# ):
#     """
#     Deletes an existing route and its associated role links.

#     Args:
#         route_id (int): The ID of the route to delete.
#         db (Session, optional): The database session.

#     Returns:
#         dict: Confirmation message of successful deletion.

#     Raises:
#         HTTPException: If the route is not found or if a database error occurs.
#     """
#     try:
#         route_repo = RouteRepository(db)
#         route_repo.delete_route(route_id)
        
#         # Log audit action
#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.DELETE,
#             "Route",
#             route_id,
#             {}
#         )
        
#         return {"message": "Route deleted successfully"}
#     except HTTPException as e:
#         raise e
#     except SQLAlchemyError as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Error deleting route."
#         ) from e


# @router.get("/routes", response_model=list)
# async def list_routes(
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
#     _ = Depends(role_required(super_admin_role))
# ):
#     """
#     Retrieves a list of all available routes.

#     Args:
#         db (Session, optional): The database session.

#     Returns:
#         list: A list of all route instances.

#     Raises:
#         HTTPException: If a database error occurs.
#     """
#     try:
#         route_repo = RouteRepository(db)
#         routes = route_repo.get_routes()
        
#         # Log audit action
#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.VIEW,
#             "Route",
#             None,
#             {}
#         )
        
#         return routes
#     except SQLAlchemyError as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Error retrieving routes."
#         ) from e


# @router.get("/routes/{route_id}", response_model=dict)
# async def get_route(
#     route_id: int,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
#     _ = Depends(role_required(super_admin_role))
# ):
#     """
#     Retrieves details of a specific route by its ID.

#     Args:
#         route_id (int): The ID of the route to retrieve.
#         db (Session, optional): The database session.

#     Returns:
#         dict: The route instance details.

#     Raises:
#         HTTPException: If the route is not found or if a database error occurs.
#     """
#     try:
#         route_repo = RouteRepository(db)
#         route = route_repo.get_route(route_id)
        
#         # Log audit action
#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.VIEW,
#             "Route",
#             route_id,
#             {}
#         )
        
#         return route
#     except HTTPException as e:
#         raise e
#     except SQLAlchemyError as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Error retrieving route."
#         ) from e


# @router.post("/routes/bulk", response_model=List[dict], status_code=status.HTTP_201_CREATED)
# async def bulk_create_routes(
#     routes_data: List[RouteCreateSchema],
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
#     _ = Depends(role_required(super_admin_role))
# ):
#     """
#     Bulk creates multiple routes with associated permitted roles.
#     """
#     try:
#         route_repo = RouteRepository(db)
#         created_routes = route_repo.bulk_create_routes(routes_data)
        
#         # Perform audit logging for successfully created Route objects
#         response = []
#         for route in created_routes:
#             if isinstance(route, Route):
#                 logging_helper.log_audit(
#                     db,
#                     current_user.id,
#                     ActionEnum.CREATE,
#                     "Route",
#                     route.id,
#                     {"data": {"path": route.path, "method": route.method, "description": route.description}}
#                 )
#                 response.append({
#                     "message": "Route created successfully",
#                     "route_id": route.id
#                 })
#             else:
#                 # Add any messages or error details for routes that failed
#                 response.append(route)
        
#         return response
    
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTP Error: {e.detail}")
#         raise e
#     except SQLAlchemyError as e:
#         logging_helper.log_error(f"Database Error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Error creating routes in bulk."
#         ) from e
#     except Exception as e:
#         logging_helper.log_error(f"Unexpected Error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="An unexpected error occurred while creating routes in bulk."
#         ) from e
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.database import get_db
from auth.dependencies import role_required
from repositories.route_repository import RouteRepository
from schemas.route_schemas import RouteCreateSchema, RouteUpdateSchema, RouteDisplaySchema
from logging_helpers import logging_helper
from auth.security import get_current_user
from models.all_models import ActionEnum, Route
from typing import List

router = APIRouter()

# Define the role required to access these endpoints (super_admin)
super_admin_role = ["super_admin"]

@router.post("/routes", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_route(
    route_data: RouteCreateSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    _ = Depends(role_required(super_admin_role))
):
    """
    Creates a new route with associated permitted roles and module.

    Args:
        route_data (RouteCreateSchema): The data for creating a new route.
        db (Session, optional): The database session.

    Returns:
        dict: Confirmation message and the created route ID.

    Raises:
        HTTPException: If there is a database error or any role is not found.
    """
    try:
        route_repo = RouteRepository(db)
        route = route_repo.create_route(route_data)
        
        # Log audit action
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.CREATE,
            "Route",
            route.id,
            {"data": route_data.dict()}
        )
        
        return {"message": "Route created successfully", "route_id": route.id}
    except HTTPException as e:
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating route."
        ) from e


@router.put("/routes/{route_id}", response_model=dict)
async def update_route(
    route_id: int,
    update_data: RouteUpdateSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    _ = Depends(role_required(super_admin_role))
):
    """
    Updates an existing route and its permitted roles and module.

    Args:
        route_id (int): The ID of the route to update.
        update_data (RouteUpdateSchema): The updated route data.
        db (Session, optional): The database session.

    Returns:
        dict: Confirmation message of successful update.

    Raises:
        HTTPException: If the route or any specified role is not found, or if a database error occurs.
    """
    try:
        route_repo = RouteRepository(db)
        route_repo.update_route(route_id, update_data)
        
        # Log audit action
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.UPDATE,
            "Route",
            route_id,
            {"data": update_data.dict()}
        )
        
        return {"message": "Route updated successfully"}
    except HTTPException as e:
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating route."
        ) from e


@router.delete("/routes/{route_id}", response_model=dict)
async def delete_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    _ = Depends(role_required(super_admin_role))
):
    """
    Deletes an existing route and its associated role links.

    Args:
        route_id (int): The ID of the route to delete.
        db (Session, optional): The database session.

    Returns:
        dict: Confirmation message of successful deletion.

    Raises:
        HTTPException: If the route is not found or if a database error occurs.
    """
    try:
        route_repo = RouteRepository(db)
        route_repo.delete_route(route_id)
        
        # Log audit action
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.DELETE,
            "Route",
            route_id,
            {}
        )
        
        return {"message": "Route deleted successfully"}
    except HTTPException as e:
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting route."
        ) from e


# @router.get("/routes", response_model=List[RouteDisplaySchema])
# async def list_routes(
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
#     _ = Depends(role_required(super_admin_role))
# ):
#     """
#     Retrieves a list of all available routes along with their associated modules.

#     Args:
#         db (Session, optional): The database session.

#     Returns:
#         List[RouteDisplaySchema]: A list of all route instances with module details.

#     Raises:
#         HTTPException: If a database error occurs.
#     """
#     try:
#         route_repo = RouteRepository(db)
#         routes = route_repo.get_routes()
        
#         # Log audit action
#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.VIEW,
#             "Route",
#             None,
#             {}
#         )
        
#         return routes
#     except SQLAlchemyError as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Error retrieving routes."
#         ) from e

@router.get("/routes", response_model=List[RouteDisplaySchema])
async def list_routes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    _ = Depends(role_required(super_admin_role))
):
    """
    Retrieves a list of all available routes with associated modules.

    Args:
        db (Session, optional): The database session.

    Returns:
        List[RouteDisplaySchema]: A list of all route instances with module details.

    Raises:
        HTTPException: If a database error occurs.
    """
    try:
        route_repo = RouteRepository(db)
        routes = route_repo.get_routes()
        
        # Log audit action
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.VIEW,
            "Route",
            None,
            {}
        )
        
        return routes
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving routes."
        ) from e


@router.get("/routes/{route_id}", response_model=RouteDisplaySchema)
async def get_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    _ = Depends(role_required(super_admin_role))
):
    """
    Retrieves details of a specific route by its ID, including associated module details.

    Args:
        route_id (int): The ID of the route to retrieve.
        db (Session, optional): The database session.

    Returns:
        RouteDisplaySchema: The route instance details with associated module and roles.

    Raises:
        HTTPException: If the route is not found or if a database error occurs.
    """
    try:
        route_repo = RouteRepository(db)
        route = route_repo.get_route(route_id)
        
        # Log audit action
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.VIEW,
            "Route",
            route_id,
            {}
        )
        
        return route
    except HTTPException as e:
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving route."
        ) from e


# @router.post("/routes/bulk", response_model=List[dict], status_code=status.HTTP_201_CREATED)
# async def bulk_create_routes(
#     routes_data: List[RouteCreateSchema],
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
#     _ = Depends(role_required(super_admin_role))
# ):
#     """
#     Bulk creates multiple routes with associated permitted roles and modules.

#     Args:
#         routes_data (List[RouteCreateSchema]): The list of routes to create.
#         db (Session, optional): The database session.

#     Returns:
#         List[dict]: A list of dictionaries containing success messages and route IDs for created routes.

#     Raises:
#         HTTPException: If there is a database error.
#     """
#     try:
#         route_repo = RouteRepository(db)
#         created_routes = route_repo.bulk_create_routes(routes_data)
        
#         # Perform audit logging for successfully created Route objects
#         response = []
#         for route in created_routes:
#             if isinstance(route, Route):
#                 logging_helper.log_audit(
#                     db,
#                     current_user.id,
#                     ActionEnum.CREATE,
#                     "Route",
#                     route.id,
#                     {"data": {"path": route.path, "method": route.method, "description": route.description}}
#                 )
#                 response.append({
#                     "message": "Route created successfully",
#                     "route_id": route.id
#                 })
#             else:
#                 # Add any messages or error details for routes that failed
#                 response.append(route)
        
#         return response
    
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTP Error: {e.detail}")
#         raise e
#     except SQLAlchemyError as e:
#         logging_helper.log_error(f"Database Error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Error creating routes in bulk."
#         ) from e
#     except Exception as e:
#         logging_helper.log_error(f"Unexpected Error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="An unexpected error occurred while creating routes in bulk."
#         ) from e
@router.post("/routes/bulk", response_model=List[dict], status_code=status.HTTP_201_CREATED)
async def bulk_create_routes(
    routes_data: List[RouteCreateSchema],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    _ = Depends(role_required(super_admin_role))
):
    """
    Bulk creates multiple routes with associated permitted roles and modules.

    Args:
        routes_data (List[RouteCreateSchema]): The list of routes to create.
        db (Session, optional): The database session.

    Returns:
        List[dict]: A list of dictionaries containing success messages and route IDs for created routes.

    Raises:
        HTTPException: If there is a database error.
    """
    try:
        route_repo = RouteRepository(db)
        created_routes = route_repo.bulk_create_routes(routes_data)
        
        # Perform audit logging for successfully created Route objects
        response = []
        for route in created_routes:
            if isinstance(route, Route):
                logging_helper.log_audit(
                    db,
                    current_user.id,
                    ActionEnum.CREATE,
                    "Route",
                    route.id,
                    {
                        "data": {
                            "path": route.path,
                            "method": route.method,
                            "description": route.description,
                            "module_id": route.module_id  # Include the module_id in the audit log
                        }
                    }
                )
                response.append({
                    "message": "Route created successfully",
                    "route_id": route.id
                })
            else:
                # Add any messages or error details for routes that failed
                response.append(route)
        
        return response
    
    except HTTPException as e:
        logging_helper.log_error(f"HTTP Error: {e.detail}")
        raise e
    except SQLAlchemyError as e:
        logging_helper.log_error(f"Database Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating routes in bulk."
        ) from e
    except Exception as e:
        logging_helper.log_error(f"Unexpected Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating routes in bulk."
        ) from e

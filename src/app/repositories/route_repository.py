# repositories/route_repository.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from schemas.module_schemas import ModuleSchema
from models.all_models import Route, UserRole, RouteRole, Module
from schemas.route_schemas import RouteCreateSchema, RouteDisplaySchema, RouteUpdateSchema
from fastapi import HTTPException, status
from typing import List
from logging_helpers import logging_helper

class RouteRepository:
    """
    Repository class for handling CRUD operations on Route entities.

    Attributes:
        db_session (Session): The database session used for database operations.
    """

    def __init__(self, db_session: Session):
        """
        Initializes the RouteRepository with a database session.
        
        Args:
            db_session (Session): The database session.
        """
        self.db_session = db_session

    def create_route(self, route_data: RouteCreateSchema) -> Route:
        """
        Creates a new route and associates it with the specified roles and module.

        Args:
            route_data (RouteCreateSchema): The schema containing route details, permitted roles, and associated module ID.
        
        Returns:
            Route: The newly created route instance.

        Raises:
            HTTPException: If a route with the same path and method already exists, or if a database error occurs.
        """
        try:
            # Check for duplicate route
            existing_route = self.db_session.query(Route).filter(
                Route.path == route_data.path,
                Route.method == route_data.method
            ).first()

            if existing_route:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Route with path '{route_data.path}' and method '{route_data.method}' already exists."
                )

            # Fetch the module if specified
            module = self.db_session.query(Module).filter(Module.id == route_data.module_id).first()
            if not module:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Module with ID '{route_data.module_id}' not found."
                )

            # Create and add the route
            route = Route(
                path=route_data.path,
                method=route_data.method,
                description=route_data.description,
                module_id=route_data.module_id
            )
            self.db_session.add(route)
            self.db_session.flush()  # To get the route ID before committing

            # Associate the roles with the route
            for role_name in route_data.permitted_roles:
                role = self.db_session.query(UserRole).filter(UserRole.name == role_name).first()
                if not role:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Role '{role_name}' not found"
                    )

                route_role = RouteRole(route_id=route.id, role_id=role.id)
                self.db_session.add(route_role)

            self.db_session.commit()
            return route

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating route"
            ) from e

    def update_route(self, route_id: int, update_data: RouteUpdateSchema) -> Route:
        """
        Updates an existing route and its associated roles.

        Args:
            route_id (int): The ID of the route to update.
            update_data (RouteUpdateSchema): The schema containing updated route details and roles.

        Returns:
            Route: The updated route instance.

        Raises:
            HTTPException: If the route or any specified role is not found.
            HTTPException: If a database error occurs during route update.
        """
        try:
            # Fetch the route
            route = self.db_session.query(Route).filter(Route.id == route_id).first()
            if not route:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

            # Update description if provided
            if update_data.description:
                route.description = update_data.description

            # Update roles if specified
            if update_data.permitted_roles is not None:
                # Delete existing role associations
                self.db_session.query(RouteRole).filter(RouteRole.route_id == route_id).delete()

                # Associate new roles
                for role_name in update_data.permitted_roles:
                    role = self.db_session.query(UserRole).filter(UserRole.name == role_name).first()
                    if not role:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role '{role_name}' not found")

                    route_role = RouteRole(route_id=route.id, role_id=role.id)
                    self.db_session.add(route_role)

            self.db_session.commit()
            return route

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating route") from e



    def get_routes(self) -> List[RouteDisplaySchema]:
        """
        Retrieves all routes with associated module data.
        
        Returns:
            List[RouteDisplaySchema]: A list of all routes as Pydantic models.
        
        Raises:
            HTTPException: If a database error occurs during retrieval.
        """
        try:
            routes = self.db_session.query(Route).options(joinedload(Route.module)).all()
            return [RouteDisplaySchema.from_orm(route) for route in routes]
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving routes"
            ) from e
        

    def get_route(self, route_id: int) -> RouteDisplaySchema:
        """
        Retrieves a specific route by its ID, with its associated module.
        
        Args:
            route_id (int): The ID of the route to retrieve.
        
        Returns:
            RouteDisplaySchema: The retrieved route with module details.
        
        Raises:
            HTTPException: If the route is not found or a database error occurs.
        """
        try:
            route = (
                self.db_session.query(Route)
                .options(joinedload(Route.module))
                .filter(Route.id == route_id)
                .first()
            )
            if not route:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
            
            # Convert module to ModuleSchema
            module_data = ModuleSchema.from_orm(route.module) if route.module else None
            
            # Return RouteDisplaySchema with module
            return RouteDisplaySchema(
                id=route.id,
                path=route.path,
                method=route.method,
                description=route.description,
                module=module_data
            )
            
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving route: {str(e)}"
            ) from e

    def bulk_create_routes(self, routes_data: List[RouteCreateSchema]) -> List[dict]:
        """
            Bulk creates multiple routes and associates them with the specified roles.

            Args:
                routes_data (List[RouteCreateSchema]): A list of route schemas containing route details and permitted roles.
            
            Returns:
                List[Route]: A list of newly created route instances.

            Raises:
                HTTPException: If any of the specified roles are not found.
                HTTPException: If a database error occurs during route creation.
        """

        created_routes = []
        
        try:
            for route_data in routes_data:
                existing_route = self.db_session.query(Route).filter(
                    Route.path == route_data.path,
                    Route.method == route_data.method
                ).first()

                if existing_route:
                    created_routes.append({
                        "message": f"Route with path '{route_data.path}' and method '{route_data.method}' already exists.",
                        "route_id": existing_route.id
                    })
                    continue

                # Create and add the route with the module_id
                route = Route(
                    path=route_data.path,
                    method=route_data.method,
                    description=route_data.description,
                    module_id=route_data.module_id  # Include the module_id here
                )
                self.db_session.add(route)
                self.db_session.flush()  # To get route.id before committing

                # Associate roles with the route
                all_roles_exist = True
                for role_name in route_data.permitted_roles:
                    role = self.db_session.query(UserRole).filter(UserRole.name == role_name).first()
                    if not role:
                        all_roles_exist = False
                        created_routes.append({
                            "message": f"Role '{role_name}' not found for route '{route_data.path}'",
                            "route_id": None
                        })
                        break

                    route_role = RouteRole(route_id=route.id, role_id=role.id)
                    self.db_session.add(route_role)

                if all_roles_exist:
                    self.db_session.commit()
                    created_routes.append({
                        "message": "Route created successfully",
                        "route_id": route.id
                    })
                else:
                    self.db_session.rollback()

            return created_routes  # Return the route creation results

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating routes: {str(e)}"
            ) from e
        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred while creating routes in bulk: {str(e)}"
            ) from e


    def delete_route(self, route_id: int) -> None:
        """
        Deletes an existing route and its associated roles.

        Args:
            route_id (int): The ID of the route to delete.

        Raises:
            HTTPException: If the route is not found.
            HTTPException: If a database error occurs during route deletion.
        """
        try:
            # Fetch the route
            route = self.db_session.query(Route).filter(Route.id == route_id).first()
            if not route:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

            # Delete associated roles and the route itself
            self.db_session.query(RouteRole).filter(RouteRole.route_id == route_id).delete()
            self.db_session.delete(route)
            self.db_session.commit()

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting route") from e

    def get_routes(self) -> List[Route]:
        """
        Retrieves all routes.

        Returns:
            List[Route]: A list of all routes.
        
        Raises:
            HTTPException: If a database error occurs during retrieval.
        """
        try:
            return self.db_session.query(Route).all()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving routes") from e

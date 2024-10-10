# from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
# from sqlalchemy.orm import Session
# from typing import Dict, List
# from db.database import get_db
# from repositories.assignment_repository import AssignmentRepository
# from logging_helpers import logging_helper
# from auth.security import get_current_user
# from schemas.assignment_schemas import (
#     AssignmentCreate,
#     AssignmentUpdate,
#     AssignmentResponse,
#     AssignmentWithEmployees,
#     EmployeeInfo,
# )
# from models.all_models import User, ActionEnum, Assignment as AssignmentModel
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# import json
# from datetime import date, datetime

# limiter = Limiter(key_func=get_remote_address)

# router = APIRouter()


# def model_to_dict(instance):
#     data = {c.name: getattr(instance, c.name) for c in instance.__table__.columns}
#     # Convert date fields to strings
#     for key, value in data.items():
#         if isinstance(value, (date, datetime)):
#             data[key] = value.isoformat()
#     return data


# @router.post(
#     "/assignments/",
#     response_model=AssignmentResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# @limiter.limit("5/minute")
# async def create_assignment(
#     request: Request,
#     assignment: AssignmentCreate,
#     background_tasks: BackgroundTasks,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     logging_helper.log_info("Accessing - Create Assignment - Endpoint")
#     assignment_repo = AssignmentRepository(db)
#     try:
#         new_assignment = assignment_repo.create_assignment(
#             assignment, user_id=current_user.id, background_tasks=background_tasks
#         )
#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.CREATE,
#             "Assignment",
#             new_assignment.id,
#             json.dumps(model_to_dict(new_assignment)),
#         )
#         return AssignmentResponse.from_orm(new_assignment)
#     except Exception as e:
#         logging_helper.log_error(f"Failed to create assignment: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to create assignment",
#         )



# @router.put(
#     "/assignments/{assignment_id}",
#     response_model=AssignmentResponse,
#     status_code=status.HTTP_200_OK,
# )
# @limiter.limit("5/minute")
# async def update_assignment(
#     request: Request,
#     assignment_id: int,
#     assignment: AssignmentUpdate,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     logging_helper.log_info("Accessing - Update Assignment - Endpoint")
#     assignment_repo = AssignmentRepository(db)
#     try:
#         updated_assignment = assignment_repo.update_assignment(
#             assignment_id, assignment, user_id=current_user.id
#         )
#         if updated_assignment is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found"
#             )
#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.UPDATE,
#             "Assignment",
#             updated_assignment.id,
#             json.dumps(model_to_dict(updated_assignment)),
#         )
#         return AssignmentResponse.from_orm(updated_assignment)
#     except Exception as e:
#         logging_helper.log_error(f"Failed to update assignment: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to update assignment",
#         )


# @router.delete(
#     "/assignments/{assignment_id}",
#     response_model=Dict[str, str],
#     status_code=status.HTTP_200_OK,
# )
# @limiter.limit("5/minute")
# async def delete_assignment(
#     request: Request,
#     assignment_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     logging_helper.log_info("Accessing - Delete Assignment - Endpoint")
#     assignment_repo = AssignmentRepository(db)
#     try:
#         deleted_assignment = assignment_repo.delete_assignment(
#             assignment_id, user_id=current_user.id
#         )
#         if deleted_assignment is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found"
#             )
#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.DELETE,
#             "Assignment",
#             assignment_id,
#             json.dumps(model_to_dict(deleted_assignment)),
#         )
#         return {
#             "message": f"The Assignment with ID: {assignment_id} deleted successfully!"
#         }
#     except Exception as e:
#         logging_helper.log_error(f"Failed to delete assignment: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to delete assignment",
#         )

# @router.put(
#     "/assignments/{assignment_id}/extend_due_date", response_model=AssignmentResponse
# )
# async def extend_assignment_due_date(
#     assignment_id: int,
#     new_end_date: date,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     Extend the due date of an assignment.
#     """
#     logging_helper.log_info(f"Accessing - Extend Due Date for Assignment - Endpoint")
#     assignment_repo = AssignmentRepository(db)
#     try:
#         updated_assignment = assignment_repo.extend_assignment_due_date(
#             assignment_id=assignment_id,
#             new_end_date=new_end_date,
#             user_id=current_user.id,
#         )

#         # Log audit information
#         changes = {
#             "old_end_date": updated_assignment.old_end_date,
#             "new_end_date": updated_assignment.end_date,
#         }
#         logging_helper.log_audit(
#             db, current_user.id, ActionEnum.UPDATE, "Assignment", assignment_id, changes
#         )

#         return updated_assignment
#     except Exception as e:
#         logging_helper.log_error(
#             f"Failed to extend due date for assignment with ID {assignment_id}: {str(e)}"
#         )
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# @router.put(
#     "/assignments/{assignment_id}/substitute_employee",
#     response_model=AssignmentResponse,
#     status_code=status.HTTP_200_OK,
# )
# @limiter.limit("5/minute")
# async def substitute_employee(
#     request: Request,
#     assignment_id: int,
#     old_employee_id: int,
#     new_employee_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     logging_helper.log_info("Accessing - Substitute Employee in Assignment - Endpoint")
#     assignment_repo = AssignmentRepository(db)
#     try:
#         substituted_assignment = assignment_repo.substitute_employee(
#             assignment_id, old_employee_id, new_employee_id, user_id=current_user.id
#         )
#         if substituted_assignment is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Assignment or Employee not found",
#             )
#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.UPDATE,
#             "Assignment",
#             substituted_assignment.id,
#             json.dumps(model_to_dict(substituted_assignment)),
#         )
#         return AssignmentResponse.from_orm(substituted_assignment)
#     except Exception as e:
#         logging_helper.log_error(
#             f"Failed to substitute employee in assignment: {str(e)}"
#         )
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to substitute employee in assignment",
#         )


# @router.get(
#     "/assignments/",
#     response_model=List[AssignmentResponse],
#     status_code=status.HTTP_200_OK,
# )
# @limiter.limit("10/minute")
# async def read_assignments(
#     request: Request,
#     skip: int = 0,
#     limit: int = 10,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     logging_helper.log_info("Accessing - Read All Assignments - Endpoint")
#     assignment_repo = AssignmentRepository(db)
#     try:
#         assignments = assignment_repo.get_assignments(skip=skip, limit=limit)
#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.READ,
#             "Assignment",
#             None,
#             f"skip={skip}, limit={limit}",
#         )
#         return assignments
#     except Exception as e:
#         logging_helper.log_error(f"Failed to fetch assignments: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch assignments: {str(e)}",
#         )


# @router.get(
#     "/assignments/{assignment_id}",
#     response_model=AssignmentResponse,
#     status_code=status.HTTP_200_OK,
# )
# @limiter.limit("10/minute")
# async def read_assignment(
#     request: Request,
#     assignment_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     logging_helper.log_info("Accessing - Read Assignment - Endpoint")
#     assignment_repo = AssignmentRepository(db)
#     try:
#         assignment = assignment_repo.get_assignment(assignment_id)
#         if assignment is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found"
#             )
#         logging_helper.log_audit(
#             db, current_user.id, ActionEnum.READ, "Assignment", assignment_id, None
#         )
#         return assignment
#     except Exception as e:
#         logging_helper.log_error(f"Failed to fetch assignment: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch assignment: {str(e)}",
#         )


# @router.get(
#     "/assignments/{assignment_id}/employees",
#     response_model=AssignmentWithEmployees,
#     status_code=status.HTTP_200_OK,
# )
# @limiter.limit("10/minute")
# async def get_employees_assigned_to_assignment(
#     request: Request,
#     assignment_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     logging_helper.log_info(
#         "Accessing - Get Employees Assigned to Assignment - Endpoint"
#     )
#     assignment_repo = AssignmentRepository(db)
#     try:
#         assignment_with_employees = (
#             assignment_repo.get_employees_assigned_to_assignment(assignment_id)
#         )
#         if not assignment_with_employees["assignment"]:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found"
#             )
#         if not assignment_with_employees["employees"]:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="No employees found for this assignment",
#             )
#         return AssignmentWithEmployees(
#             assignment=AssignmentResponse(**assignment_with_employees["assignment"]),
#             employees=[
#                 EmployeeInfo(**emp) for emp in assignment_with_employees["employees"]
#             ],
#         )
#     except Exception as e:
#         logging_helper.log_error(
#             f"Failed to fetch employees for assignment ID {assignment_id}: {str(e)}"
#         )
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch employees for assignment ID {assignment_id}: {str(e)}",
#         )


# @router.put("/assignments/{assignment_id}/complete", status_code=status.HTTP_200_OK)
# @limiter.limit("20/minute")
# async def complete_assignment(
#     request: Request,
#     assignment_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     logging_helper.log_info(
#         f"Accessing - Complete Assignment - Endpoint for assignment ID {assignment_id}"
#     )
#     assignment_repo = AssignmentRepository(db)
#     try:
#         completed_assignment = assignment_repo.complete_assignment(
#             assignment_id, user_id=current_user.id
#         )
#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.UPDATE,
#             "Assignment",
#             assignment_id,
#             f"Assignment completed: {completed_assignment}",
#         )
#         return {"message": completed_assignment}
#     except Exception as e:
#         logging_helper.log_error(
#             f"Failed to complete assignment with ID {assignment_id}: {str(e)}"
#         )
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to complete assignment: {str(e)}",
#         )


# @router.get("/assignments/{assignment_id}/for_assignment", response_model=Dict)
# @limiter.limit("5/minute")
# async def get_employees_for_assignment(
#     assignment_id: int, 
#     request: Request, 
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     assignment_repo = AssignmentRepository(db)
#     try:
#         result = assignment_repo.get_employees_for_assignment(assignment_id)
#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.READ,
#             "Assignment",
#             assignment_id,
#             json.dumps(result),
#         )
#         return result
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTP exception occurred: {e.detail}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Unhandled exception occurred: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="An unexpected error occurred",
#         )


# @router.post("/assignments/{assignment_id}/add_employee/{employee_id}", response_model=dict)
# @limiter.limit("5/minute")
# async def add_employee_to_assignment(
#     request: Request,
#     assignment_id: int,
#     employee_id: int,  
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     assignment_repo = AssignmentRepository(db)
#     try:
#         result = assignment_repo.add_employee_to_assignment(assignment_id, employee_id, current_user.id)
#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.UPDATE,
#             "Assignment",
#             assignment_id,
#             {"added_employee_id": employee_id}
#         )
#         return result
#     except HTTPException as e:
#         logging_helper.log_error(f"HTTP exception occurred: {e.detail}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Unhandled exception occurred: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An unexpected error occurred: {str(e)}",
#         )




from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Dict, List
from db.database import get_db
from repositories.assignment_repository import AssignmentRepository
from logging_helpers import logging_helper
from auth.security import get_current_user
from schemas.assignment_schemas import (
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentResponse,
    AssignmentWithEmployees,
    EmployeeInfo,
)
from models.all_models import User, ActionEnum, Assignment as AssignmentModel
from slowapi import Limiter
from slowapi.util import get_remote_address
import json
from datetime import date, datetime

# Initialize the Limiter for rate limiting
limiter = Limiter(key_func=get_remote_address)

# Create the API router
router = APIRouter()

def model_to_dict(instance):
    """
    Convert a SQLAlchemy model instance to a dictionary, converting date fields to strings.
    """
    data = {c.name: getattr(instance, c.name) for c in instance.__table__.columns}
    for key, value in data.items():
        if isinstance(value, (date, datetime)):
            data[key] = value.isoformat()
    return data

@router.post(
    "/assignments/",
    response_model=AssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
async def create_assignment(
    request: Request,
    assignment: AssignmentCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new assignment.
    
    Args:
        request (Request): The HTTP request object.
        assignment (AssignmentCreate): The assignment data to create.
        background_tasks (BackgroundTasks): Background tasks to be executed.
        current_user (User): The current authenticated user.
        db (Session): The database session.

    Returns:
        AssignmentResponse: The created assignment details.
        
    Roles to Access the endpoint
        super_admin, hq_backstop, tenant_admin, stl, technical_lead, Program_lead, unit_lead, department_lead   
    """
    logging_helper.log_info("Accessing - Create Assignment - Endpoint")
    assignment_repo = AssignmentRepository(db)
    try:
        # Create a new assignment
        new_assignment = assignment_repo.create_assignment(
            assignment, user_id=current_user.id, background_tasks=background_tasks
        )
        # Log the creation action
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.CREATE,
            "Assignment",
            new_assignment.id,
            json.dumps(model_to_dict(new_assignment)),
        )
        return AssignmentResponse.from_orm(new_assignment)
    except Exception as e:
        logging_helper.log_error(f"Failed to create assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create assignment",
        )

@router.put(
    "/assignments/{assignment_id}",
    response_model=AssignmentResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("5/minute")
async def update_assignment(
    request: Request,
    assignment_id: int,
    assignment: AssignmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing assignment.
    
    Args:
        request (Request): The HTTP request object.
        assignment_id (int): The ID of the assignment to update.
        assignment (AssignmentUpdate): The updated assignment data.
        current_user (User): The current authenticated user.
        db (Session): The database session.

    Returns:
        AssignmentResponse: The updated assignment details.

    Roles to Access the endpoint:
        super_admin, hq_backstop, tenant_admin, stl, technical_lead, Program_lead, unit_lead, department_lead   
    """
    logging_helper.log_info("Accessing - Update Assignment - Endpoint")
    assignment_repo = AssignmentRepository(db)
    try:
        # Update the assignment
        updated_assignment = assignment_repo.update_assignment(
            assignment_id, assignment, user_id=current_user.id
        )
        if updated_assignment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found"
            )
        # Log the update action
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.UPDATE,
            "Assignment",
            updated_assignment.id,
            json.dumps(model_to_dict(updated_assignment)),
        )
        return AssignmentResponse.from_orm(updated_assignment)
    except Exception as e:
        logging_helper.log_error(f"Failed to update assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update assignment",
        )

@router.delete(
    "/assignments/{assignment_id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
)
@limiter.limit("5/minute")
async def delete_assignment(
    request: Request,
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete an assignment.
    
    Args:
        request (Request): The HTTP request object.
        assignment_id (int): The ID of the assignment to delete.
        current_user (User): The current authenticated user.
        db (Session): The database session.

    Returns:
        Dict[str, str]: A message indicating the successful deletion.
        Roles to Access the endpoint
        super_admin, hq_backstop, tenant_admin, stl, technical_lead, Program_lead, unit_lead, department_lead   
    """
    logging_helper.log_info("Accessing - Delete Assignment - Endpoint")
    assignment_repo = AssignmentRepository(db)
    try:
        # Delete the assignment
        deleted_assignment = assignment_repo.delete_assignment(
            assignment_id, user_id=current_user.id
        )
        if deleted_assignment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found"
            )
        # Log the deletion action
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.DELETE,
            "Assignment",
            assignment_id,
            json.dumps(model_to_dict(deleted_assignment)),
        )
        return {
            "message": f"The Assignment with ID: {assignment_id} deleted successfully!"
        }
    except Exception as e:
        logging_helper.log_error(f"Failed to delete assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete assignment",
        )

@router.put(
    "/assignments/{assignment_id}/extend_due_date", response_model=AssignmentResponse
)
async def extend_assignment_due_date(
    assignment_id: int,
    new_end_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Extend the due date of an assignment.
    
    Args:
        assignment_id (int): The ID of the assignment to update.
        new_end_date (date): The new end date for the assignment.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        AssignmentResponse: The updated assignment details.
    
    Roles to Access the endpoint
        super_admin, hq_backstop, tenant_admin, stl, technical_lead, Program_lead, unit_lead, department_lead   
    """
    logging_helper.log_info(f"Accessing - Extend Due Date for Assignment - Endpoint")
    assignment_repo = AssignmentRepository(db)
    try:
        # Extend the assignment due date
        updated_assignment = assignment_repo.extend_assignment_due_date(
            assignment_id=assignment_id,
            new_end_date=new_end_date,
            user_id=current_user.id,
        )
        # Log the extension action
        changes = {
            "old_end_date": updated_assignment.old_end_date,
            "new_end_date": updated_assignment.end_date,
        }
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.UPDATE, "Assignment", assignment_id, changes
        )
        return updated_assignment
    except Exception as e:
        logging_helper.log_error(
            f"Failed to extend due date for assignment with ID {assignment_id}: {str(e)}"
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put(
    "/assignments/{assignment_id}/substitute_employee",
    response_model=AssignmentResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("5/minute")
async def substitute_employee(
    request: Request,
    assignment_id: int,
    old_employee_id: int,
    new_employee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Substitute an employee in an assignment.
    
    Args:
        request (Request): The HTTP request object.
        assignment_id (int): The ID of the assignment.
        old_employee_id (int): The ID of the old employee.
        new_employee_id (int): The ID of the new employee.
        current_user (User): The current authenticated user.
        db (Session): The database session.

    Returns:
        AssignmentResponse: The updated assignment details.

    Roles to Access the endpoint
        super_admin, hq_backstop, tenant_admin, stl, technical_lead, Program_lead, unit_lead, department_lead   
    """
    logging_helper.log_info("Accessing - Substitute Employee in Assignment - Endpoint")
    assignment_repo = AssignmentRepository(db)
    try:
        # Substitute the employee
        substituted_assignment = assignment_repo.substitute_employee(
            assignment_id, old_employee_id, new_employee_id, user_id=current_user.id
        )
        if substituted_assignment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment or Employee not found",
            )
        # Log the substitution action
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.UPDATE,
            "Assignment",
            substituted_assignment.id,
            json.dumps(model_to_dict(substituted_assignment)),
        )
        return AssignmentResponse.from_orm(substituted_assignment)
    except Exception as e:
        logging_helper.log_error(
            f"Failed to substitute employee in assignment: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to substitute employee in assignment",
        )

@router.get(
    "/assignments/",
    response_model=List[AssignmentResponse],
    status_code=status.HTTP_200_OK,
)
@limiter.limit("10/minute")
async def read_assignments(
    request: Request,
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a list of assignments with pagination.
    
    Args:
        request (Request): The HTTP request object.
        skip (int): The number of records to skip.
        limit (int): The maximum number of records to return.
        current_user (User): The current authenticated user.
        db (Session): The database session.

    Returns:
        List[AssignmentResponse]: A list of assignments.

    Roles to Access the endpoint
        unit_member   
    """
    logging_helper.log_info("Accessing - Read All Assignments - Endpoint")
    assignment_repo = AssignmentRepository(db)
    try:
        # Fetch the assignments
        assignments = assignment_repo.get_assignments(skip=skip, limit=limit)
        # Log the read action
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.READ,
            "Assignment",
            None,
            f"skip={skip}, limit={limit}",
        )
        return assignments
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch assignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch assignments: {str(e)}",
        )

@router.get(
    "/assignments/{assignment_id}",
    response_model=AssignmentResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("10/minute")
async def read_assignment(
    request: Request,
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get details of a specific assignment by its ID.
    
    Args:
        request (Request): The HTTP request object.
        assignment_id (int): The ID of the assignment.
        current_user (User): The current authenticated user.
        db (Session): The database session.

    Returns:
        AssignmentResponse: The assignment details.

    Roles to Access the endpoint
        super_admin, hq_backstop, tenant_admin, stl, technical_lead, Program_lead, unit_lead, department_lead               
    """
    logging_helper.log_info("Accessing - Read Assignment - Endpoint")
    assignment_repo = AssignmentRepository(db)
    try:
        # Fetch the assignment by ID
        assignment = assignment_repo.get_assignment(assignment_id)
        if assignment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found"
            )
        # Log the read action
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.READ, "Assignment", assignment_id, None
        )
        return assignment
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch assignment: {str(e)}",
        )

@router.get(
    "/assignments/{assignment_id}/employees",
    response_model=AssignmentWithEmployees,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("10/minute")
async def get_employees_assigned_to_assignment(
    request: Request,
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get employees assigned to a specific assignment.
    
    Args:
        request (Request): The HTTP request object.
        assignment_id (int): The ID of the assignment.
        current_user (User): The current authenticated user.
        db (Session): The database session.

    Returns:
        AssignmentWithEmployees: The assignment details along with the assigned employees.
    Roles to Access the endpoint
        unit_member       
    """
    logging_helper.log_info(
        "Accessing - Get Employees Assigned to Assignment - Endpoint"
    )
    assignment_repo = AssignmentRepository(db)
    try:
        # Fetch employees assigned to the assignment
        assignment_with_employees = (
            assignment_repo.get_employees_assigned_to_assignment(assignment_id)
        )
        if not assignment_with_employees["assignment"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found"
            )
        if not assignment_with_employees["employees"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No employees found for this assignment",
            )
        return AssignmentWithEmployees(
            assignment=AssignmentResponse(**assignment_with_employees["assignment"]),
            employees=[
                EmployeeInfo(**emp) for emp in assignment_with_employees["employees"]
            ],
        )
    except Exception as e:
        logging_helper.log_error(
            f"Failed to fetch employees for assignment ID {assignment_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch employees for assignment ID {assignment_id}: {str(e)}",
        )

@router.put("/assignments/{assignment_id}/complete", status_code=status.HTTP_200_OK)
@limiter.limit("20/minute")
async def complete_assignment(
    request: Request,
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark an assignment as completed.
    
    Args:
        request (Request): The HTTP request object.
        assignment_id (int): The ID of the assignment to complete.
        current_user (User): The current authenticated user.
        db (Session): The database session.

    Returns:
        Dict[str, str]: A message indicating the successful completion of the assignment.
    
    Roles to Access the endpoint
        unit_memeber
    """
    logging_helper.log_info(
        f"Accessing - Complete Assignment - Endpoint for assignment ID {assignment_id}"
    )
    assignment_repo = AssignmentRepository(db)
    try:
        # Mark the assignment as completed
        completed_assignment = assignment_repo.complete_assignment(
            assignment_id, user_id=current_user.id
        )
        # Log the completion action
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.UPDATE,
            "Assignment",
            assignment_id,
            f"Assignment completed: {completed_assignment}",
        )
        return {"message": completed_assignment}
    except Exception as e:
        logging_helper.log_error(
            f"Failed to complete assignment with ID {assignment_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete assignment: {str(e)}",
        )

@router.get("/assignments/{assignment_id}/for_assignment", response_model=Dict)
@limiter.limit("5/minute")
async def get_employees_for_assignment(
    assignment_id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get assignment details and its responsible employees.
    
    Args:
        assignment_id (int): The ID of the assignment.
        request (Request): The HTTP request object.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        Dict: The assignment details and responsible employees.

    Roles to Access the endpoint
        super_admin, hq_backstop, tenant_admin, stl, technical_lead, Program_lead, unit_lead, department_lead
    """
    assignment_repo = AssignmentRepository(db)
    try:
        # Fetch assignment details and employees
        result = assignment_repo.get_employees_for_assignment(assignment_id)
        # Log the read action
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.READ,
            "Assignment",
            assignment_id,
            json.dumps(result),
        )
        return result
    except HTTPException as e:
        logging_helper.log_error(f"HTTP exception occurred: {e.detail}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unhandled exception occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

@router.post("/assignments/{assignment_id}/add_employee/{employee_id}", response_model=dict)
@limiter.limit("5/minute")
async def add_employee_to_assignment(
    request: Request,
    assignment_id: int,
    employee_id: int,  
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add an employee to an assignment.
    
    Args:
        request (Request): The HTTP request object.
        assignment_id (int): The ID of the assignment.
        employee_id (int): The ID of the employee to add.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        Dict[str, str]: A message indicating the successful addition of the employee to the assignment.

    Roles to Access the endpoint
        super_admin, hq_backstop, tenant_admin, stl, technical_lead, Program_lead, unit_lead, department_lead
    """
    assignment_repo = AssignmentRepository(db)
    try:
        # Add employee to the assignment
        result = assignment_repo.add_employee_to_assignment(assignment_id, employee_id, current_user.id)
        # Log the addition action
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.UPDATE,
            "Assignment",
            assignment_id,
            {"added_employee_id": employee_id}
        )
        return result
    except HTTPException as e:
        logging_helper.log_error(f"HTTP exception occurred: {e.detail}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unhandled exception occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )

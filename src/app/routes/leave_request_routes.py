
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List, Optional

# from db.database import get_db
# from schemas.leave_request_schemas import LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestResponse
# from repositories.leave_request_repository import LeaveRequestRepository

# router = APIRouter()

# @router.post("/leave-requests/", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
# def create_leave_request_route(leave_request: LeaveRequestCreate, db: Session = Depends(get_db)):
#     """
#     Create a new leave request.
    
#     Args:
#         leave_request (LeaveRequestCreate): Data for creating the leave request.
#         db (Session): SQLAlchemy session object.
        
#     Returns:
#         LeaveRequest: The created leave request object.
#     """
#     try:
#         leave_request_repo = LeaveRequestRepository(db)
#         new_leave_request = leave_request_repo.create_leave_request(leave_request.employee_id, leave_request.dict())
#         return new_leave_request
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# @router.get("/leave-requests/{employee_id}", response_model=List[LeaveRequestResponse])
# def get_leave_requests_by_employee_route(employee_id: int, db: Session = Depends(get_db)):
#     """
#     Retrieve all leave requests made by a specific employee.
    
#     Args:
#         employee_id (int): ID of the employee whose leave requests to retrieve.
#         db (Session): SQLAlchemy session object.
        
#     Returns:
#         list[LeaveRequest]: List of leave requests for the specified employee.
#     """
#     try:
#         leave_request_repo = LeaveRequestRepository(db)
#         leave_requests = leave_request_repo.get_leave_requests_by_employee(employee_id)
#         if not leave_requests:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No leave requests found for this employee.")
#         return leave_requests
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# @router.patch("/leave-requests/{leave_request_id}/status", response_model=LeaveRequestResponse)
# def update_leave_request_status_route(
#     leave_request_id: int,
#     status: str,
#     approver_id: int,
#     db: Session = Depends(get_db)
# ):
#     """
#     Update the status of a leave request.
    
#     Args:
#         leave_request_id (int): ID of the leave request to update.
#         status (str): The new status of the leave request.
#         approver_id (int): ID of the approver updating the status.
#         db (Session): SQLAlchemy session object.
        
#     Returns:
#         LeaveRequest: The updated leave request object.
#     """
#     try:
#         leave_request_repo = LeaveRequestRepository(db)
#         updated_leave_request = leave_request_repo.update_leave_request_status(leave_request_id, status, approver_id)
#         return updated_leave_request
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# @router.delete("/leave-requests/{leave_request_id}", response_model=dict)
# def delete_leave_request_route(leave_request_id: int, db: Session = Depends(get_db)):
#     """
#     Delete a leave request.
    
#     Args:
#         leave_request_id (int): ID of the leave request to delete.
#         db (Session): SQLAlchemy session object.
        
#     Returns:
#         dict: Confirmation of successful deletion.
#     """
#     try:
#         leave_request_repo = LeaveRequestRepository(db)
#         result = leave_request_repo.delete_leave_request(leave_request_id)
#         if result:
#             return {"detail": "Leave request deleted successfully."}
#         else:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found.")
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# @router.get("/staff/", response_model=List[dict])
# def get_hr_or_finance_staff_route(
#     staff_type: str,
#     db: Session = Depends(get_db)
# ):
#     """
#     Retrieve the list of HR or Finance staff.
    
#     Args:
#         staff_type (str): The type of staff to retrieve (HR or Finance).
#         db (Session): SQLAlchemy session object.
        
#     Returns:
#         list[dict]: List of HR or Finance staff.
#     """
#     try:
#         leave_request_repo = LeaveRequestRepository(db)
#         staff_list = leave_request_repo.get_hr_or_finance_staff(staff_type)
#         return staff_list
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# @router.post("/assign-responsibility/", response_model=dict)
# def assign_employee_to_special_responsibility_route(
#     employee_id: int,
#     responsibility: str,
#     project_id: Optional[int] = None,
#     db: Session = Depends(get_db)
# ):
#     """
#     Assign an employee to a specific responsibility (HR, Finance, Budget Holder, etc.).
    
#     Args:
#         employee_id (int): ID of the employee to assign a responsibility to.
#         responsibility (str): The responsibility to assign.
#         project_id (Optional[int]): The ID of the project (required for assigning Budget Holder).
#         db (Session): SQLAlchemy session object.
        
#     Returns:
#         dict: Confirmation of successful assignment.
#     """
#     try:
#         leave_request_repo = LeaveRequestRepository(db)
#         leave_request_repo.assign_employee_to_special_responsibility(employee_id, responsibility, project_id)
#         return {"detail": f"Employee {employee_id} assigned to {responsibility} responsibility successfully."}
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))




from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from db.database import get_db
from schemas.leave_request_schemas import LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestResponse
from repositories.leave_request_repository import LeaveRequestRepository

router = APIRouter()

# @router.post("/leave-requests/", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
# def create_leave_request_route(leave_request: LeaveRequestCreate, db: Session = Depends(get_db)):
#     """
#     Create a new leave request.

#     Args:
#         leave_request (LeaveRequestCreate): Data for creating the leave request.
#         db (Session): SQLAlchemy session object.

#     Returns:
#         LeaveRequest: The created leave request object.
#     """
#     try:
#         leave_request_repo = LeaveRequestRepository(db)
#         new_leave_request = leave_request_repo.create_leave_request(leave_request.employee_id, leave_request.dict())
#         return new_leave_request
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/leave-requests/", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
def create_leave_request_route(leave_request: LeaveRequestCreate, db: Session = Depends(get_db)):
    """
    Create a new leave request.

    Args:
        leave_request (LeaveRequestCreate): Data for creating the leave request.
        db (Session): SQLAlchemy session object.

    Returns:
        LeaveRequest: The created leave request object.
    """
    try:
        leave_request_repo = LeaveRequestRepository(db)
        new_leave_request = leave_request_repo.create_leave_request(leave_request.employee_id, leave_request.dict())
        return new_leave_request
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/leave-requests/{employee_id}", response_model=List[LeaveRequestResponse])
def get_leave_requests_by_employee_route(employee_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all leave requests made by a specific employee.

    Args:
        employee_id (int): ID of the employee whose leave requests to retrieve.
        db (Session): SQLAlchemy session object.

    Returns:
        list[LeaveRequest]: List of leave requests for the specified employee.
    """
    try:
        leave_request_repo = LeaveRequestRepository(db)
        leave_requests = leave_request_repo.get_leave_requests_by_employee(employee_id)
        if not leave_requests:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No leave requests found for this employee.")
        return leave_requests
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/leave-requests/{leave_request_id}/status", response_model=LeaveRequestResponse)
def update_leave_request_status_route(
    leave_request_id: int,
    status: str,
    approver_id: int,
    db: Session = Depends(get_db)
):
    """
    Update the status of a leave request.

    Args:
        leave_request_id (int): ID of the leave request to update.
        status (str): The new status of the leave request.
        approver_id (int): ID of the approver updating the status.
        db (Session): SQLAlchemy session object.

    Returns:
        LeaveRequest: The updated leave request object.
    """
    try:
        leave_request_repo = LeaveRequestRepository(db)
        updated_leave_request = leave_request_repo.update_leave_request_status(leave_request_id, status, approver_id)
        return updated_leave_request
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/leave-requests/{leave_request_id}", response_model=dict)
def delete_leave_request_route(leave_request_id: int, db: Session = Depends(get_db)):
    """
    Delete a leave request.

    Args:
        leave_request_id (int): ID of the leave request to delete.
        db (Session): SQLAlchemy session object.

    Returns:
        dict: Confirmation of successful deletion.
    """
    try:
        leave_request_repo = LeaveRequestRepository(db)
        result = leave_request_repo.delete_leave_request(leave_request_id)
        if result:
            return {"detail": "Leave request deleted successfully."}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found.")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/staff/", response_model=List[dict])
def get_hr_or_finance_staff_route(
    staff_type: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve the list of HR or Finance staff.

    Args:
        staff_type (str): The type of staff to retrieve (HR or Finance).
        db (Session): SQLAlchemy session object.

    Returns:
        list[dict]: List of HR or Finance staff.
    """
    try:
        leave_request_repo = LeaveRequestRepository(db)
        staff_list = leave_request_repo.get_hr_or_finance_staff(staff_type)
        return staff_list
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/assign-responsibility/", response_model=dict)
def assign_employee_to_special_responsibility_route(
    employee_id: int,
    responsibility: str,
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Assign an employee to a specific responsibility (HR, Finance, Budget Holder, etc.).

    Args:
        employee_id (int): ID of the employee to assign a responsibility to.
        responsibility (str): The responsibility to assign.
        project_id (Optional[int]): The ID of the project (required for assigning Budget Holder).
        db (Session): SQLAlchemy session object.

    Returns:
        dict: Confirmation of successful assignment.
    """
    try:
        leave_request_repo = LeaveRequestRepository(db)
        leave_request_repo.assign_employee_to_special_responsibility(employee_id, responsibility, project_id)
        return {"detail": f"Employee {employee_id} assigned to {responsibility} responsibility successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

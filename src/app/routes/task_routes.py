from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from db.database import get_db
from repositories.task_repository import TaskRepository
from logging_helpers import logging_helper
from auth.security import get_current_user
from schemas.task_schemas import ReopenTaskRequest, TaskCreate, TaskUpdate
from models.all_models import User, ActionEnum
from slowapi import Limiter
from slowapi.util import get_remote_address
import json
from datetime import date, datetime

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


def model_to_dict(instance):
    data = {c.name: getattr(instance, c.name) for c in instance.__table__.columns}
    for key, value in data.items():
        if isinstance(value, (date, datetime)):
            data[key] = value.isoformat()
    return data


def convert_datetime_to_str(data):
    """ Recursively convert datetime objects to strings """
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (datetime, date)):
                data[key] = value.isoformat()
            elif isinstance(value, dict):
                convert_datetime_to_str(value)
            elif isinstance(value, list):
                for item in value:
                    convert_datetime_to_str(item)
    elif isinstance(data, list):
        for item in data:
            convert_datetime_to_str(item)
    return data


@router.post("/tasks/", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_task(request: Request, task: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Create Task - Endpoint")
    task_repo = TaskRepository(db)
    try:
        task_data = task.dict()  # Convert TaskCreate object to a dictionary
        new_task = task_repo.create_task(task_data)
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.CREATE, "Task", new_task["id"], json.dumps(new_task, default=str)
        )
        return new_task
    except Exception as e:
        logging_helper.log_error(f"Failed to create task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create task")


@router.get("/tasks/{task_id}", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_task(request: Request, task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Read Task - Endpoint")
    task_repo = TaskRepository(db)
    try:
        task_data = task_repo.get_task(task_id)
        if not task_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Task", task_id, None)
        return task_data
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch task")


@router.get("/tasks/", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def read_tasks(request: Request, skip: int = 0, limit: int = 10, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Read All Tasks - Endpoint")
    task_repo = TaskRepository(db)
    try:
        tasks_data = task_repo.get_tasks(skip=skip, limit=limit)
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Task", None, f"skip={skip}, limit={limit}")
        return tasks_data
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch tasks: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch tasks")


@router.put("/tasks/{task_id}", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def update_task(request: Request, task_id: int, task: TaskUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Update Task - Endpoint")
    task_repo = TaskRepository(db)
    try:
        updated_task = task_repo.update_task(task_id, task)
        if not updated_task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.UPDATE, "Task", updated_task.id, json.dumps(model_to_dict(updated_task))
        )
        return {"id": updated_task.id, **model_to_dict(updated_task)}
    except Exception as e:
        logging_helper.log_error(f"Failed to update task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update task")


@router.delete("/tasks/{task_id}", response_model=Dict[str, str], status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def delete_task(request: Request, task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Delete Task - Endpoint")
    task_repo = TaskRepository(db)
    try:
        deleted_task = task_repo.delete_task(task_id)
        if not deleted_task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.DELETE, "Task", task_id, json.dumps(model_to_dict(deleted_task))
        )
        return {"message": f"The Task with ID: {task_id} deleted successfully!"}
    except Exception as e:
        logging_helper.log_error(f"Failed to delete task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete task")


@router.put("/tasks/{task_id}/substitute_employees", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def substitute_task_employees(request: Request, task_id: int, employee_ids: List[int], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Substitute Task Employees - Endpoint")
    task_repo = TaskRepository(db)
    try:
        substituted_task = task_repo.substitute_task_employees(task_id, employee_ids)
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.UPDATE, "Task", task_id, json.dumps(substituted_task, default=str)
        )
        return substituted_task
    except Exception as e:
        logging_helper.log_error(f"Failed to substitute employees for task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to substitute employees for task")


@router.get("/assignments/hierarchy/")
def get_assignments_hierarchy(start_date: date, end_date: date, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Get Assignments Hierarchy - Endpoint")
    
    task_repo = TaskRepository(db)
    try:
        return task_repo.get_assignments_hierarchy(start_date, end_date)
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch assignments hierarchy: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch assignments hierarchy")
    

@router.get("/assignments/{assignment_id}/tasks")
def get_tasks_by_assignment(assignment_id: int, db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Get Task by Assignmnet_id - Endpoint")
    
    task_repo = TaskRepository(db)
    return task_repo.get_tasks_by_assignment(assignment_id)

@router.get("/milestones/{milestone_id}/tasks")
def get_tasks_by_milestone(milestone_id: int, db: Session = Depends(get_db)):
    task_repo = TaskRepository(db)
    return task_repo.get_tasks_by_milestone(milestone_id)

@router.get("/users/{user_id}/assignments-hierarchy")
def get_user_assignments_hierarchy(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task_repo = TaskRepository(db)
    try:
        return task_repo.get_user_assignments_hierarchy(current_user.employee_id)
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch assignments associted with the user with Employee_id: {current_user.employee_id} and user_id: {current_user.id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch assignments hierarchy")


@router.put("/tasks/{task_id}/complete", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def complete_task(request: Request, task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info(f"Accessing - Complete Task - Endpoint for task ID: {task_id}")
    task_repo = TaskRepository(db)
    try:
        completed_task_info = task_repo.complete_task(task_id)
        if "message" in completed_task_info and completed_task_info["message"] == "Task is already completed.":
            logging_helper.log_info(f"Task with ID: {task_id} is already completed.")
            return {"message": "Task is already completed."}
        
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.COMPLETED, "Task", task_id, completed_task_info
        )
        
        return completed_task_info
    except HTTPException as e:
        logging_helper.log_error(f"Failed to complete task: {str(e.detail)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Failed to complete task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to complete task")


@router.put("/tasks/{task_id}/reopen", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def reopen_task(request: Request, task_id: int, comment: str = Query(..., description="Comment is required to reopen the task"), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info(f"Accessing - Reopen Task - Endpoint for task ID: {task_id}")
    task_repo = TaskRepository(db)
    try:
        logging_helper.log_info(f"Received comment: {comment}")

        if not comment:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment is required to reopen the task")

        # Retrieve the previous state of the task
        previous_state = task_repo.get_task_state(task_id)

        # Reopen the task
        reopened_task_info = task_repo.reopen_task(task_id, comment)
        
        # Retrieve the new state of the task
        new_state = task_repo.get_task_state(task_id)

        # Log the changes in the audit log
        changes = {
            "task_action": "Task Reopened",
            "task_id": task_id,
            "previous_state": previous_state,
            "new_state": new_state,
        }
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.RE_OPENED, "Task", task_id, json.dumps(changes, default=str)
        )
        return {"message": f"The task with ID: {task_id} reopened successfully"}
    except HTTPException as e:
        logging_helper.log_error(f"Failed to reopen task: {str(e.detail)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Failed to reopen task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reopen task")


# @router.delete("/tasks/{task_id}/employees/{employee_id}", response_model=dict)
# async def remove_employee_from_task(
#     task_id: int,
#     employee_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Remove an employee from a task.
#     """
#     task_repo = TaskRepository(db)
#     try:
#         result = task_repo.remove_employee_from_task(task_id, employee_id)
#         changes = {
#             "task_id": task_id,
#             "employee_id_removed": employee_id
#         }
#         logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "Task", task_id, json.dumps(changes))
#         return result
#     except HTTPException as e:
#         logging_helper.log_error(f"Failed to remove employee from task: {e.detail}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Failed to remove employee from task: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/tasks/{task_id}/employees/{employee_id}", response_model=dict)
async def remove_employee_from_task(
    task_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove an employee from a task.
    """
    task_repo = TaskRepository(db)
    try:
        result = task_repo.remove_employee_from_task(task_id, employee_id)
        changes = {
            "task_id": task_id,
            "employee_id_removed": employee_id
        }
        logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "Task", task_id, json.dumps(changes))
        return result
    except HTTPException as e:
        logging_helper.log_error(f"Failed to remove employee from task: {e.detail}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Failed to remove employee from task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# @router.delete("/assignments/{assignment_id}/employees/{employee_id}", response_model=dict)
# @limiter.limit("5/minute")
# async def remove_employee_from_assignment(
#     request: Request,
#     assignment_id: int,
#     employee_id: int,
#     new_responsible_employee_id: int = None,  # Optional parameter for the new responsible employee
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Remove an employee from an assignment.
#     """
#     task_repo = TaskRepository(db)
#     try:
#         result = task_repo.remove_employee_from_assignment(assignment_id, employee_id, new_responsible_employee_id)
#         changes = {
#             "assignment_id": assignment_id,
#             "employee_id_removed": employee_id,
#             "new_responsible_employee_id": new_responsible_employee_id
#         }
#         logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "Assignment", assignment_id, json.dumps(changes))
#         return result
#     except HTTPException as e:
#         logging_helper.log_error(f"Failed to remove employee from assignment: {e.detail}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Failed to remove employee from assignment: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/assignments/{assignment_id}/employees/{employee_id}", response_model=dict)
@limiter.limit("5/minute")
async def remove_employee_from_assignment(
    request: Request,
    assignment_id: int,
    employee_id: int,
    new_responsible_employee_id: Optional[int] = None,  # Optional parameter for the new responsible employee
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove an employee from an assignment.
    """
    task_repo = TaskRepository(db)
    try:
        result = task_repo.remove_employee_from_assignment(assignment_id, employee_id, new_responsible_employee_id)
        changes = {
            "assignment_id": assignment_id,
            "employee_id_removed": employee_id,
            "new_responsible_employee_id": new_responsible_employee_id
        }
        logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "Assignment", assignment_id, json.dumps(changes))
        return result
    except HTTPException as e:
        logging_helper.log_error(f"Failed to remove employee from assignment: {e.detail}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Failed to remove employee from assignment: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
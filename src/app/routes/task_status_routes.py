from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.task_status_schemas import TaskStatusCreate, TaskStatusInDBBase, TaskStatusUpdate, TaskStatusResponse
from repositories.task_status_repository import TaskStatusRepository
from models.all_models import ActionEnum, User
from auth.dependencies import role_checker
from auth.security import get_current_user
from logging_helpers import logging_helper

router = APIRouter()

@router.get("/task-statuses", response_model=List[TaskStatusInDBBase])
def list_task_statuses(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(role_checker(['unit_member', 'tenant_admin', 'super_admin', 'hq_backstop']))
):
    """
    Retrieve a list of task statuses with optional pagination.
    """
    try:
        task_status_repo = TaskStatusRepository(db)
        task_statuses = task_status_repo.list_task_statuses(skip=skip, limit=limit, user_id=current_user.id)
        return task_statuses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task-statuses/{task_status_id}", response_model=TaskStatusResponse)
def get_task_status(task_status_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve a task status by its ID.
    """
    try:
        task_status_repo = TaskStatusRepository(db)
        task_status = task_status_repo.get_task_status_by_id(task_status_id, user_id=current_user.id)
        return task_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/task-statuses", response_model=TaskStatusResponse)
def create_task_status(
    task_status_in: TaskStatusCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task status.
    """
    try:
        task_status_repo = TaskStatusRepository(db)
        new_task_status = task_status_repo.create_task_status(task_status_in, user_id=current_user.id)

        background_tasks.add_task(
            logging_helper.log_audit, 
            db, 
            user_id=current_user.id, 
            action=ActionEnum.CREATE, 
            model="TaskStatus", 
            model_id=new_task_status.id, 
            changes=task_status_in.dict()
        )

        return new_task_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/task-statuses/{task_status_id}", response_model=TaskStatusResponse)
def update_task_status(
    task_status_id: int, 
    task_status_in: TaskStatusUpdate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing task status.
    """
    try:
        task_status_repo = TaskStatusRepository(db)
        updated_task_status = task_status_repo.update_task_status(task_status_id, task_status_in, user_id=current_user.id)

        background_tasks.add_task(
            logging_helper.log_audit, 
            db, 
            user_id=current_user.id, 
            action=ActionEnum.UPDATE, 
            model="TaskStatus", 
            model_id=task_status_id, 
            changes=task_status_in.dict()
        )

        return updated_task_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/task-statuses/{task_status_id}")
def delete_task_status(
    task_status_id: int, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Delete a task status by its ID.
    """
    try:
        task_status_repo = TaskStatusRepository(db)
        task_status_repo.delete_task_status(task_status_id, user_id=current_user.id)

        background_tasks.add_task(
            logging_helper.log_audit, 
            db, 
            user_id=current_user.id, 
            action=ActionEnum.DELETE, 
            model="TaskStatus", 
            model_id=task_status_id
        )

        return {"detail": "Task status deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

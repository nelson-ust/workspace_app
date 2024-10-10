from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.all_models import TaskStatus, ActionEnum
from schemas.task_status_schemas import TaskStatusCreate, TaskStatusUpdate
from logging_helpers import logging_helper

class TaskStatusRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_task_status_by_id(self, task_status_id: int, user_id: Optional[int] = None) -> TaskStatus:
        try:
            task_status = self.db_session.query(TaskStatus).filter(TaskStatus.id == task_status_id, TaskStatus.is_active == True).first()
            if not task_status:
                logging_helper.log_error(f"Task status with ID {task_status_id} not found")
                raise HTTPException(status_code=404, detail="Task status not found")
            
            logging_helper.log_info(f"Task status with ID {task_status_id} retrieved successfully")
            #logging_helper.log_audit(self.db_session, user_id, ActionEnum.READ, "TaskStatus", task_status_id)
            return task_status
        except SQLAlchemyError as err:
            logging_helper.log_error(f"Error retrieving task status by ID: {err}")
            raise Exception(f"Failed to retrieve task status: {str(err)}")

    def get_task_status_by_name(self, name: str, user_id: Optional[int] = None) -> TaskStatus:
        try:
            task_status = self.db_session.query(TaskStatus).filter(TaskStatus.name == name, TaskStatus.is_active == True).first()
            if not task_status:
                logging_helper.log_error(f"Task status with name {name} not found")
                raise HTTPException(status_code=404, detail="Task status not found")
            
            logging_helper.log_info(f"Task status with name {name} retrieved successfully")
            #logging_helper.log_audit(self.db_session, user_id, ActionEnum.READ, "TaskStatus", task_status.id)
            return task_status
        except SQLAlchemyError as err:
            logging_helper.log_error(f"Error retrieving task status by name: {err}")
            raise Exception(f"Failed to retrieve task status: {str(err)}")

    def list_task_statuses(self, skip: int = 0, limit: int = 10, user_id: Optional[int] = None) -> List[TaskStatus]:
        try:
            task_statuses = self.db_session.query(TaskStatus).filter(TaskStatus.is_active == True).offset(skip).limit(limit).all()
            logging_helper.log_info("Task statuses listed successfully")
            #logging_helper.log_audit(self.db_session, user_id, ActionEnum.READ, "TaskStatus", None, "list_task_statuses")
            return task_statuses
        except SQLAlchemyError as err:
            logging_helper.log_error(f"Error retrieving task statuses: {err}")
            raise Exception(f"Failed to retrieve task statuses: {str(err)}")

    def create_task_status(self, task_status_in: TaskStatusCreate, user_id: Optional[int] = None) -> TaskStatus:
        task_status = TaskStatus(name=task_status_in.name)
        self.db_session.add(task_status)
        try:
            self.db_session.commit()
            logging_helper.log_info(f"Task status {task_status.name} created successfully")
            #logging_helper.log_audit(self.db_session, user_id, ActionEnum.CREATE, "TaskStatus", task_status.id, task_status_in.dict())
            return task_status
        except SQLAlchemyError as err:
            self.db_session.rollback()
            logging_helper.log_error(f"Error creating task status: {err}")
            raise HTTPException(status_code=500, detail=f"Error creating task status: {err}")

    def update_task_status(self, task_status_id: int, task_status_in: TaskStatusUpdate, user_id: Optional[int] = None) -> TaskStatus:
        task_status = self.get_task_status_by_id(task_status_id, user_id)
        if task_status_in.name:
            task_status.name = task_status_in.name
        try:
            self.db_session.commit()
            logging_helper.log_info(f"Task status {task_status.id} updated successfully")
            #logging_helper.log_audit(self.db_session, user_id, ActionEnum.UPDATE, "TaskStatus", task_status_id, task_status_in.dict())
            return task_status
        except SQLAlchemyError as err:
            self.db_session.rollback()
            logging_helper.log_error(f"Error updating task status: {err}")
            raise HTTPException(status_code=500, detail=f"Error updating task status: {err}")

    def delete_task_status(self, task_status_id: int, user_id: Optional[int] = None):
        task_status = self.get_task_status_by_id(task_status_id, user_id)
        task_status.is_active = False
        try:
            self.db_session.commit()
            logging_helper.log_info(f"Task status {task_status.id} deleted successfully")
            #logging_helper.log_audit(self.db_session, user_id, ActionEnum.DELETE, "TaskStatus", task_status_id)
        except SQLAlchemyError as err:
            self.db_session.rollback()
            logging_helper.log_error(f"Error deleting task status: {err}")
            raise HTTPException(status_code=500, detail=f"Error deleting task status: {err}")

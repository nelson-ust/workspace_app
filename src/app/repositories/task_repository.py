import json
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.all_models import Task, Assignment, Milestone, Employee, TaskStatus, task_employee_association, assignment_employee_association, AuditLog, ActionEnum
from schemas.task_schemas import TaskCreate, TaskUpdate
from logging_helpers import logging_helper
from datetime import date, datetime

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db


    def get_task_state(self, task_id: int):
        db_task = self.get_task(task_id)["task"]
        task_state = {
            "is_completed": db_task.get("is_completed"),
            "date_completed": db_task.get("date_completed"),
            "status_id": db_task.get("status_id"),
            "comment": db_task.get("comment")
        }
        return task_state

    def create_task(self, task_data: dict):
        logging_helper.log_info("Creating a new task")
        try:
            milestone_id = task_data.get("milestone_id")
            employee_ids = task_data.get("employee_ids", [])
            due_date = task_data.get("due_date")
            status_id = task_data.get("status_id")
            comment = task_data.get("comment")
            assignment_id = task_data.get("assignment_id")

            milestone = self.db.query(Milestone).filter(Milestone.id == milestone_id).first()
            if not milestone:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

            assignment = self.db.query(Assignment).filter(Assignment.id == milestone.assignment_id).first()
            if not assignment:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

            if due_date and due_date > milestone.due_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Task due date cannot be greater than the milestone's due date"
                )

            assignment_employee_ids = {emp.id for emp in assignment.responsible_employees}
            if not set(employee_ids).issubset(assignment_employee_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="All employees involved in the task must be part of the responsible employees for the associated assignment"
                )

            db_task = Task(
                description=task_data.get("description"),
                due_date=due_date,
                status_id=status_id,
                comment=comment,
                assignment_id=milestone.assignment_id,
                milestone_id=milestone_id
            )
            self.db.add(db_task)
            self.db.commit()
            self.db.refresh(db_task)

            # Add employees to the task
            for employee_id in employee_ids:
                self.db.execute(
                    task_employee_association.insert().values(task_id=db_task.id, employee_id=employee_id)
                )
            self.db.commit()

            logging_helper.log_info(f"Task created successfully with ID: {db_task.id}")

            response_task = {
                "id": db_task.id,
                "description": db_task.description,
                "due_date": db_task.due_date,
                "status_id": db_task.status_id,
                "comment": db_task.comment,
                "assignment_id": db_task.assignment_id,
                "milestone_id": db_task.milestone_id,
                "employee_ids": employee_ids,
                "date_created": db_task.date_created,
                "date_updated": db_task.date_updated
            }

            return response_task
        except Exception as e:
            logging_helper.log_error(f"Failed to create task: {str(e)}")
            self.db.rollback()
            raise

    def update_task(self, task_id: int, task: TaskUpdate):
        logging_helper.log_info(f"Updating task with ID: {task_id}")
        try:
            db_task = self.db.query(Task).filter(Task.id == task_id).first()
            if not db_task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

            milestone = self.db.query(Milestone).filter(Milestone.id == db_task.milestone_id).first()
            if not milestone:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

            assignment = self.db.query(Assignment).filter(Assignment.id == milestone.assignment_id).first()
            if not assignment:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

            if task.due_date and task.due_date > milestone.due_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Task due date cannot be greater than the milestone's due date"
                )

            if task.employee_ids:
                assignment_employee_ids = {emp.id for emp in assignment.responsible_employees}
                if not set(task.employee_ids).issubset(assignment_employee_ids):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="All employees involved in the task must be part of the responsible employees for the associated assignment"
                    )

                # Update task employees
                self.db.execute(
                    task_employee_association.delete().where(task_employee_association.c.task_id == db_task.id)
                )
                for employee_id in task.employee_ids:
                    self.db.execute(
                        task_employee_association.insert().values(task_id=db_task.id, employee_id=employee_id)
                    )

            for key, value in task.dict(exclude_unset=True).items():
                setattr(db_task, key, value)

            self.db.commit()
            self.db.refresh(db_task)

            task_employee_ids = [emp.id for emp in self.db.query(Employee).join(task_employee_association).filter(task_employee_association.c.task_id == db_task.id).all()]

            response_task = {
                "id": db_task.id,
                "description": db_task.description,
                "due_date": db_task.due_date,
                "status_id": db_task.status_id,
                "comment": db_task.comment,
                "assignment_id": db_task.assignment_id,
                "milestone_id": db_task.milestone_id,
                "employee_ids": task_employee_ids,
                "date_created": db_task.date_created,
                "date_updated": db_task.date_updated
            }

            logging_helper.log_info(f"Task updated successfully with ID: {db_task.id}")
            return response_task
        except Exception as e:
            logging_helper.log_error(f"Failed to update task: {str(e)}")
            self.db.rollback()
            raise

    def get_task(self, task_id: int):
        logging_helper.log_info(f"Fetching task with ID: {task_id}")
        try:
            db_task = self.db.query(Task).filter(Task.id == task_id).first()
            if not db_task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

            milestone = db_task.milestone
            assignment = milestone.assignment

            task_employees = (
                self.db.query(Employee.id, Employee.first_name, Employee.last_name)
                .join(task_employee_association)
                .filter(task_employee_association.c.task_id == db_task.id)
                .all()
            )

            assignment_employees = (
                self.db.query(Employee.id, Employee.first_name, Employee.last_name)
                .join(assignment_employee_association)
                .filter(assignment_employee_association.c.assignment_id == assignment.id)
                .all()
            )

            response_task = {
                "id": db_task.id,
                "description": db_task.description,
                "due_date": db_task.due_date,
                "status_id": db_task.status_id,
                "comment": db_task.comment,
                "assignment_id": db_task.assignment_id,
                "milestone_id": db_task.milestone_id,
                "employee_ids": [emp.id for emp in task_employees],
                "date_created": db_task.date_created,
                "date_updated": db_task.date_updated
            }

            return {
                "task": response_task,
                "milestone": {
                    "id": milestone.id,
                    "name": milestone.name,
                    "description": milestone.description,
                    "due_date": milestone.due_date,
                    "completion_date": milestone.completion_date,
                    "status": milestone.status,
                    "comment": milestone.comment
                },
                "assignment": {
                    "id": assignment.id,
                    "name": assignment.name,
                    "description": assignment.description,
                    "start_date": assignment.start_date,
                    "end_date": assignment.end_date,
                    "status": assignment.status,
                    "comment": assignment.comment
                },
                "task_employees": [{"id": emp.id, "full_name": f"{emp.first_name} {emp.last_name}"} for emp in task_employees],
                "assignment_employees": [{"id": emp.id, "full_name": f"{emp.first_name} {emp.last_name}"} for emp in assignment_employees],
            }
        except Exception as e:
            logging_helper.log_error(f"Failed to fetch task: {str(e)}")
            raise

    def get_tasks(self, skip: int = 0, limit: int = 10):
        logging_helper.log_info(f"Fetching tasks with skip: {skip}, limit: {limit}")
        try:
            tasks = self.db.query(Task).offset(skip).limit(limit).all()

            result = []
            for task in tasks:
                milestone = task.milestone
                assignment = milestone.assignment

                task_employees = (
                    self.db.query(Employee.id, Employee.first_name, Employee.last_name)
                    .join(task_employee_association)
                    .filter(task_employee_association.c.task_id == task.id)
                    .all()
                )

                assignment_employees = (
                    self.db.query(Employee.id, Employee.first_name, Employee.last_name)
                    .join(assignment_employee_association)
                    .filter(assignment_employee_association.c.assignment_id == assignment.id)
                    .all()
                )

                response_task = {
                    "id": task.id,
                    "description": task.description,
                    "due_date": task.due_date,
                    "status_id": task.status_id,
                    "comment": task.comment,
                    "assignment_id": task.assignment_id,
                    "milestone_id": task.milestone_id,
                    "employee_ids": [emp.id for emp in task_employees],
                    "date_created": task.date_created,
                    "date_updated": task.date_updated
                }

                result.append({
                    "task": response_task,
                    "milestone": {
                        "id": milestone.id,
                        "name": milestone.name,
                        "description": milestone.description,
                        "due_date": milestone.due_date,
                        "completion_date": milestone.completion_date,
                        "status": milestone.status,
                        "comment": milestone.comment
                    },
                    "assignment": {
                        "id": assignment.id,
                        "name": assignment.name,
                        "description": assignment.description,
                        "start_date": assignment.start_date,
                        "end_date": assignment.end_date,
                        "status": assignment.status,
                        "comment": assignment.comment
                    },
                    "task_employees": [{"id": emp.id, "full_name": f"{emp.first_name} {emp.last_name}"} for emp in task_employees],
                    "assignment_employees": [{"id": emp.id, "full_name": f"{emp.first_name} {emp.last_name}"} for emp in assignment_employees],
                })

            return result
        except Exception as e:
            logging_helper.log_error(f"Failed to fetch tasks: {str(e)}")
            raise

    def delete_task(self, task_id: int):
        logging_helper.log_info(f"Deleting task with ID: {task_id}")
        try:
            db_task = self.db.query(Task).filter(Task.id == task_id).first()
            if not db_task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

            self.db.delete(db_task)
            self.db.commit()
            logging_helper.log_info(f"Task deleted successfully with ID: {task_id}")

            response_task = {
                "id": db_task.id,
                "description": db_task.description,
                "due_date": db_task.due_date,
                "status_id": db_task.status_id,
                "comment": db_task.comment,
                "assignment_id": db_task.assignment_id,
                "milestone_id": db_task.milestone_id,
                "employee_ids": [emp.id for emp in self.db.query(Employee).join(task_employee_association).filter(task_employee_association.c.task_id == db_task.id).all()],
                "date_created": db_task.date_created,
                "date_updated": db_task.date_updated
            }

            return response_task
        except Exception as e:
            logging_helper.log_error(f"Failed to delete task: {str(e)}")
            self.db.rollback()
            raise

    def substitute_task_employees(self, task_id: int, employee_ids: List[int]):
        logging_helper.log_info(f"Substituting employees for task with ID: {task_id}")
        try:
            db_task = self.db.query(Task).filter(Task.id == task_id).first()
            if not db_task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

            assignment = self.db.query(Assignment).join(Milestone).filter(Milestone.id == db_task.milestone_id).first()
            if not assignment:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

            assignment_employee_ids = {emp.id for emp in assignment.responsible_employees}
            if not set(employee_ids).issubset(assignment_employee_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="All employees involved in the task must be part of the responsible employees for the associated assignment"
                )

            # Update task employees
            self.db.execute(
                task_employee_association.delete().where(task_employee_association.c.task_id == db_task.id)
            )
            for employee_id in employee_ids:
                self.db.execute(
                    task_employee_association.insert().values(task_id=db_task.id, employee_id=employee_id)
                )

            self.db.commit()
            self.db.refresh(db_task)
            logging_helper.log_info(f"Substituted employees for task with ID: {db_task.id}")

            task_employees = (
                self.db.query(Employee.id, Employee.first_name, Employee.last_name)
                .join(task_employee_association)
                .filter(task_employee_association.c.task_id == db_task.id)
                .all()
            )

            response_task = {
                "id": db_task.id,
                "description": db_task.description,
                "assignment_id": db_task.assignment_id,
                "due_date": db_task.due_date,
                "status_id": db_task.status_id,
                "milestone_id": db_task.milestone_id,
                "comment": db_task.comment,
                "date_created": db_task.date_created,
                "date_updated": db_task.date_updated,
                "employee_ids": [emp.id for emp in task_employees]
            }

            return response_task

        except Exception as e:
            logging_helper.log_error(f"Failed to substitute employees for task: {str(e)}")
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to substitute employees for task")



    def get_assignments_hierarchy(self, start_date: date, end_date: date):
        logging_helper.log_info("Fetching assignments hierarchy")
        try:
            assignments = self.db.query(Assignment).filter(
                Assignment.start_date >= start_date,
                Assignment.end_date <= end_date
            ).all()
            result = []
            for assignment in assignments:
                assignment_data = {
                    "id": int(assignment.id),
                    "name": assignment.name,
                    "description": assignment.description,
                    "start_date": assignment.start_date.isoformat(),
                    "end_date": assignment.end_date.isoformat() if assignment.end_date else None,
                    "status": assignment.status,
                    "comment": assignment.comment,
                    "employees": [
                        {
                            "employee_id": emp.id,
                            "full_name": f"{emp.first_name} {emp.last_name}"
                        } for emp in assignment.responsible_employees
                    ],
                    "milestones": [
                        {
                            "id": milestone.id,
                            "assignment_id":assignment.id,
                            "name": milestone.name,
                            "description": milestone.description,
                            "due_date": milestone.due_date.isoformat(),
                            "completion_date": milestone.completion_date.isoformat() if milestone.completion_date else None,
                            "status": milestone.status,
                            "comment": milestone.comment,
                            "responsible_employee": {
                                "id": milestone.responsible_employee.id,
                                "full_name": f"{milestone.responsible_employee.first_name} {milestone.responsible_employee.last_name}"
                            },
                            "tasks": [
                                {
                                    "id": task.id,
                                    "assignment_id":assignment.id,
                                    "milestone_id":milestone.id,
                                    "description": task.description,
                                    "due_date": task.due_date.isoformat() if task.due_date else None,
                                    "status_id": task.status_id,
                                    "status_name": self.db.query(TaskStatus.name).filter(TaskStatus.id == task.status_id).scalar(),
                                    "comment": task.comment,
                                    "employees": [
                                        {
                                            "employee_id": emp.id,
                                            "full_name": f"{emp.first_name} {emp.last_name}"
                                        } for emp in task.employees
                                    ]
                                } for task in milestone.tasks
                            ]
                        } for milestone in assignment.milestones
                    ]
                }
                result.append(assignment_data)

                # # Log audit information
                # audit_log = AuditLog(
                #     user_id=assignment.initiating_user_id,
                #     action=ActionEnum.READ,
                #     model="Assignment",
                #     model_id=assignment.id,
                #     changes=None
                # )
                # self.db.add(audit_log)
                self.db.commit()

            return result
        except Exception as e:
            logging_helper.log_error(f"Failed to fetch assignments hierarchy: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch assignments hierarchy")


    def get_tasks_by_assignment(self, assignment_id: int):
        logging_helper.log_info(f"Fetching tasks for assignment with ID: {assignment_id}")
        try:
            tasks = self.db.query(Task).filter(Task.assignment_id == assignment_id).all()
            result = []
            for task in tasks:
                milestone = task.milestone

                task_employees = (
                    self.db.query(Employee.id, Employee.first_name, Employee.last_name)
                    .join(task_employee_association)
                    .filter(task_employee_association.c.task_id == task.id)
                    .all()
                )

                response_task = {
                    "id": task.id,
                    "description": task.description,
                    "due_date": task.due_date,
                    "status_id": task.status_id,
                    "comment": task.comment,
                    "assignment_id": task.assignment_id,
                    "milestone_id": task.milestone_id,
                    "employee_ids": [emp.id for emp in task_employees],
                    "date_created": task.date_created,
                    "date_updated": task.date_updated
                }

                result.append(response_task)

            return result
        except Exception as e:
            logging_helper.log_error(f"Failed to fetch tasks for assignment: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch tasks for assignment")

    def get_tasks_by_milestone(self, milestone_id: int):
        logging_helper.log_info(f"Fetching tasks for milestone with ID: {milestone_id}")
        try:
            tasks = self.db.query(Task).filter(Task.milestone_id == milestone_id).all()
            result = []
            for task in tasks:

                task_employees = (
                    self.db.query(Employee.id, Employee.first_name, Employee.last_name)
                    .join(task_employee_association)
                    .filter(task_employee_association.c.task_id == task.id)
                    .all()
                )

                response_task = {
                    "id": task.id,
                    "description": task.description,
                    "due_date": task.due_date,
                    "status_id": task.status_id,
                    "comment": task.comment,
                    "assignment_id": task.assignment_id,
                    "milestone_id": task.milestone_id,
                    "employee_ids": [emp.id for emp in task_employees],
                    "date_created": task.date_created,
                    "date_updated": task.date_updated
                }

                result.append(response_task)

            return result
        except Exception as e:
            logging_helper.log_error(f"Failed to fetch tasks for milestone: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch tasks for milestone")

    def update_task_status(self, task_id: int, status_id: int):
        logging_helper.log_info(f"Updating status of task with ID: {task_id} to status ID: {status_id}")
        try:
            db_task = self.db.query(Task).filter(Task.id == task_id).first()
            if not db_task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

            db_task.status_id = status_id

            self.db.commit()
            self.db.refresh(db_task)

            response_task = {
                "id": db_task.id,
                "description": db_task.description,
                "due_date": db_task.due_date,
                "status_id": db_task.status_id,
                "comment": db_task.comment,
                "assignment_id": db_task.assignment_id,
                "milestone_id": db_task.milestone_id,
                "date_created": db_task.date_created,
                "date_updated": db_task.date_updated
            }

            logging_helper.log_info(f"Task status updated successfully with ID: {db_task.id}")
            return response_task
        except Exception as e:
            logging_helper.log_error(f"Failed to update task status: {str(e)}")
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update task status")


    def get_user_assignments_hierarchy(self, user_id: int):
        logging_helper.log_info(f"Fetching assignments hierarchy for user with ID: {user_id}")
        try:
            user = self.db.query(Employee).filter(Employee.id == user_id).first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            assignments = self.db.query(Assignment).join(assignment_employee_association).filter(
                assignment_employee_association.c.employee_id == user_id).all()

            result = []
            for assignment in assignments:
                assignment_data = {
                    "id": assignment.id,
                    "name": assignment.name,
                    "description": assignment.description,
                    "start_date": assignment.start_date.isoformat(),
                    "end_date": assignment.end_date.isoformat() if assignment.end_date else None,
                    "status": assignment.status,
                    "comment": assignment.comment,
                    "employees": [
                        {
                            "employee_id": emp.id,
                            "full_name": f"{emp.first_name} {emp.last_name}"
                        } for emp in assignment.responsible_employees
                    ],
                    "milestones": []
                }

                for milestone in assignment.milestones:
                    milestone_data = {
                        "id": milestone.id,
                        "assignment_id":assignment.id,
                        "name": milestone.name,
                        "description": milestone.description,
                        "due_date": milestone.due_date.isoformat(),
                        "completion_date": milestone.completion_date.isoformat() if milestone.completion_date else None,
                        "status": milestone.status,
                        "comment": milestone.comment,
                        "responsible_employee": {
                            "employee_id": milestone.responsible_employee.id,
                            "full_name": f"{milestone.responsible_employee.first_name} {milestone.responsible_employee.last_name}"
                        },
                        "tasks": []
                    }

                    for task in milestone.tasks:
                        task_data = {
                            "id": task.id,
                            "assignment_id":assignment.id,
                            "milestone_id":milestone.id,
                            "description": task.description,
                            "due_date": task.due_date.isoformat() if task.due_date else None,
                            "status_id": task.status_id,
                            "comment": task.comment,
                            "employees": [
                                {
                                    "employee_id": emp.id,
                                    "full_name": f"{emp.first_name} {emp.last_name}"
                                } for emp in task.employees
                            ]
                        }
                        milestone_data["tasks"].append(task_data)

                    assignment_data["milestones"].append(milestone_data)

                result.append(assignment_data)

            return result
        except Exception as e:
            logging_helper.log_error(f"Failed to fetch assignments hierarchy for user: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch assignments hierarchy for user")


    def complete_task(self, task_id: int):
        logging_helper.log_info(f"Completing task with ID: {task_id}")
        try:
            db_task = self.db.query(Task).filter(Task.id == task_id).first()
            if not db_task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

            if db_task.is_completed:
                logging_helper.log_info(f"Task with ID: {task_id} is already completed.")
                return {"message": "Task is already completed."}

            db_task.is_completed = True
            db_task.date_completed = datetime.utcnow()
            db_task.comment = "Task Completed"
            db_task.status_id = 3  # Set the status_id to 3

            self.db.commit()
            self.db.refresh(db_task)

            # Check if all tasks in the milestone are completed
            milestone = db_task.milestone
            if milestone:
                all_tasks_completed = all(
                    task.is_completed for task in self.db.query(Task).filter(Task.milestone_id == milestone.id).all()
                )
                if all_tasks_completed:
                    milestone.is_completed = True
                    milestone.date_completed = datetime.utcnow()
                    self.db.commit()
                    self.db.refresh(milestone)

                assignment = milestone.assignment
                if assignment:
                    all_milestones_completed = all(
                        milestone.is_completed for milestone in self.db.query(Milestone).filter(Milestone.assignment_id == assignment.id).all()
                    )
                    if all_milestones_completed:
                        assignment.is_completed = True
                        assignment.date_completed = datetime.utcnow()
                        self.db.commit()
                        self.db.refresh(assignment)

            logging_helper.log_info(f"Task completed successfully with ID: {db_task.id}")
            changes = {
                "task_id": db_task.id,
                "status_id": db_task.status_id,
                "is_completed": db_task.is_completed,
                "date_completed": db_task.date_completed,
                "milestone_id": milestone.id if milestone else None,
                "assignment_id": assignment.id if assignment else None
            }
            logging_helper.log_audit(self.db, db_task.assignment.initiating_user.id, ActionEnum.COMPLETE, "Task", task_id, changes)
            return {
                "task": {
                    "id": db_task.id,
                    "status_id": db_task.status_id,
                    "is_completed": db_task.is_completed,
                    "date_completed": db_task.date_completed,
                    "comment": db_task.comment
                },
                "milestone": {
                    "id": milestone.id if milestone else None,
                    "is_completed": milestone.is_completed if milestone else None,
                    "date_completed": milestone.date_completed if milestone else None
                },
                "assignment": {
                    "id": assignment.id if assignment else None,
                    "is_completed": assignment.is_completed if assignment else None,
                    "date_completed": assignment.date_completed if assignment else None
                },
                "message": "Task completed successfully"
            }
        except Exception as e:
            logging_helper.log_error(f"Failed to complete task: {str(e)}")
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to complete task")


    def reopen_task(self, task_id: int, comment: str):
        logging_helper.log_info(f"Reopening task with ID: {task_id}")
        try:
            db_task = self.db.query(Task).filter(Task.id == task_id).first()
            if not db_task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

            logging_helper.log_info(f"Current task state before reopening: {db_task.__dict__}")

            db_task.is_completed = False
            db_task.date_completed = None
            db_task.comment = comment
            db_task.status_id = 2  # Set the status_id to 2

            self.db.commit()
            self.db.refresh(db_task)

            logging_helper.log_info(f"Task state after reopening: {db_task.__dict__}")

            # Reopen associated milestone and assignment
            milestone = db_task.milestone
            assignment = milestone.assignment if milestone else None

            if milestone and milestone.is_completed:
                milestone.is_completed = False
                milestone.date_completed = None
                self.db.commit()
                self.db.refresh(milestone)
                logging_helper.log_info(f"Milestone state after reopening: {milestone.__dict__}")

            if assignment and assignment.is_completed:
                assignment.is_completed = False
                assignment.date_completed = None
                self.db.commit()
                self.db.refresh(assignment)
                logging_helper.log_info(f"Assignment state after reopening: {assignment.__dict__}")

            logging_helper.log_info(f"Task reopened successfully with ID: {db_task.id}")
            return {
                "task_id": db_task.id,
                "is_completed": db_task.is_completed,
                "date_completed": db_task.date_completed,
                "status_id": db_task.status_id,
                "comment": db_task.comment,
                "milestone_id": milestone.id if milestone else None,
                "assignment_id": assignment.id if assignment else None
            }
        except Exception as e:
            logging_helper.log_error(f"Failed to reopen task: {str(e)}")
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reopen task")


    def remove_employee_from_task(self, task_id: int, employee_id: int):
        logging_helper.log_info(f"Removing employee with ID: {employee_id} from task with ID: {task_id}")
        try:
            db_task = self.db.query(Task).filter(Task.id == task_id).first()
            if not db_task:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

            if db_task.is_completed:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove employee from a completed task")

            db_employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
            if not db_employee:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

            if db_employee not in db_task.employees:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee not associated with the task")

            # Remove employee from task
            self.db.execute(
                task_employee_association.delete().where(
                    (task_employee_association.c.task_id == task_id) & 
                    (task_employee_association.c.employee_id == employee_id)
                )
            )
            self.db.commit()
            self.db.refresh(db_task)

            logging_helper.log_info(f"Employee with ID: {employee_id} removed from task with ID: {task_id}")
            changes = {
                "task_id": db_task.id,
                "employee_id_removed": employee_id
            }
            logging_helper.log_audit(self.db, db_task.assignment.initiating_user.id, ActionEnum.UPDATE, "Task", task_id, json.dumps(changes))
            return {"message": "Employee removed from task successfully"}
        except HTTPException as e:
            logging_helper.log_error(f"Failed to remove employee from task: {e.detail}")
            raise e
        except Exception as e:
            logging_helper.log_error(f"Failed to remove employee from task: {str(e)}")
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove employee from task")


    def remove_employee_from_assignment(self, assignment_id: int, employee_id: int, new_responsible_employee_id: Optional[int] = None):
        logging_helper.log_info(f"Removing employee with ID: {employee_id} from assignment with ID: {assignment_id}")
        try:
            db_assignment = self.db.query(Assignment).filter(Assignment.id == assignment_id).first()
            if not db_assignment:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

            db_employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
            if not db_employee:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

            if db_employee not in db_assignment.responsible_employees:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee not associated with the assignment")

            # Check if the employee has any completed tasks in the assignment
            completed_tasks = self.db.query(Task).filter(
                Task.assignment_id == assignment_id,
                Task.employees.any(id=employee_id),
                Task.is_completed == True
            ).all()

            if completed_tasks:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove employee with completed tasks in the assignment."
                )

            # Check if the employee is responsible for any completed milestones in the assignment
            completed_milestones = self.db.query(Milestone).filter(
                Milestone.assignment_id == assignment_id,
                Milestone.responsible_employee_id == employee_id,
                Milestone.is_completed == True
            ).all()

            if completed_milestones:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove employee responsible for completed milestones in the assignment."
                )

            # Remove employee from assignment
            self.db.execute(
                assignment_employee_association.delete().where(
                    (assignment_employee_association.c.assignment_id == assignment_id) & 
                    (assignment_employee_association.c.employee_id == employee_id)
                )
            )

            # Remove employee from all tasks associated with the assignment
            tasks = self.db.query(Task).filter(Task.assignment_id == assignment_id).all()
            for task in tasks:
                if db_employee in task.employees:
                    self.db.execute(
                        task_employee_association.delete().where(
                            (task_employee_association.c.task_id == task.id) &
                            (task_employee_association.c.employee_id == employee_id)
                        )
                    )

            # Remove employee as responsible employee for any milestones in the assignment
            milestones = self.db.query(Milestone).filter(Milestone.assignment_id == assignment_id).all()
            for milestone in milestones:
                if milestone.responsible_employee_id == employee_id:
                    if new_responsible_employee_id:
                        new_responsible_employee = self.db.query(Employee).filter(Employee.id == new_responsible_employee_id).first()
                        if not new_responsible_employee:
                            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New responsible employee not found")
                        milestone.responsible_employee_id = new_responsible_employee_id
                    else:
                        milestone.responsible_employee_id = None
                    self.db.commit()
                    self.db.refresh(milestone)

            self.db.commit()
            self.db.refresh(db_assignment)

            logging_helper.log_info(f"Employee with ID: {employee_id} removed from assignment with ID: {assignment_id}")
            changes = {
                "assignment_id": db_assignment.id,
                "employee_id_removed": employee_id,
                "new_responsible_employee_id": new_responsible_employee_id
            }
            logging_helper.log_audit(self.db, db_assignment.initiating_user.id, ActionEnum.UPDATE, "Assignment", assignment_id, json.dumps(changes))
            return {"message": "Employee removed from assignment successfully"}
        except HTTPException as e:
            logging_helper.log_error(f"Failed to remove employee from assignment: {e.detail}")
            raise e
        except Exception as e:
            logging_helper.log_error(f"Failed to remove employee from assignment: {str(e)}")
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove employee from assignment")

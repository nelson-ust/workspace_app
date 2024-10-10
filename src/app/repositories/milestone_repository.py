
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.all_models import Milestone, Assignment, Employee
from schemas.milestone_schemas import MilestoneCreate, MilestoneUpdate
from logging_helpers import logging_helper
from datetime import date, datetime
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError


class MilestoneRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_milestone(self, milestone: MilestoneCreate):
        logging_helper.log_info("Creating a new milestone")
        try:
            assignment = self.db.query(Assignment).filter(Assignment.id == milestone.assignment_id).first()
            if not assignment:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

            # Check for duplicate milestone name within the same assignment
            existing_milestone = (
                self.db.query(Milestone)
                .filter(Milestone.assignment_id == milestone.assignment_id, Milestone.name == milestone.name)
                .first()
            )
            if existing_milestone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Milestone name already exists for this assignment"
                )
            
            # Check the due date constraint
            if milestone.due_date > assignment.end_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Milestone due date cannot be greater than the assignment's end date"
                )

            # Check if the responsible employee is part of the assignment's responsible employees
            assignment_employees = (
                self.db.query(Employee.id)
                .join(Assignment.responsible_employees)
                .filter(Assignment.id == milestone.assignment_id)
                .all()
            )
            assignment_employee_ids = {emp.id for emp in assignment_employees}
            if milestone.responsible_employee_id not in assignment_employee_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Responsible employee must be part of the employees responsible for the associated assignment"
                )

            db_milestone = Milestone(**milestone.dict())
            self.db.add(db_milestone)
            self.db.commit()
            self.db.refresh(db_milestone)
            logging_helper.log_info(f"Milestone created successfully with ID: {db_milestone.id}")
            return db_milestone
        except Exception as e:
            logging_helper.log_error(f"Failed to create milestone: {str(e)}")
            self.db.rollback()
            raise

    def update_milestone(self, milestone_id: int, milestone: MilestoneUpdate):
        logging_helper.log_info(f"Updating milestone with ID: {milestone_id}")
        try:
            db_milestone = self.db.query(Milestone).filter(Milestone.id == milestone_id).first()
            if not db_milestone:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

            assignment = self.db.query(Assignment).filter(Assignment.id == db_milestone.assignment_id).first()
            if not assignment:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

            # Check for duplicate milestone name within the same assignment
            if milestone.name and milestone.name != db_milestone.name:
                existing_milestone = (
                    self.db.query(Milestone)
                    .filter(Milestone.assignment_id == db_milestone.assignment_id, Milestone.name == milestone.name)
                    .first()
                )
                if existing_milestone:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=F"Milestone name {milestone.name} already exists for this assignment with ID: {milestone.assignment_id}"
                    )

            # Check the due date constraint
            if milestone.due_date and milestone.due_date > assignment.end_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Milestone due date cannot be greater than the assignment's end date"
                )

            # Check if the responsible employee is part of the assignment's responsible employees
            if milestone.responsible_employee_id:
                assignment_employees = (
                    self.db.query(Employee.id)
                    .join(Assignment.responsible_employees)
                    .filter(Assignment.id == db_milestone.assignment_id)
                    .all()
                )
                assignment_employee_ids = {emp.id for emp in assignment_employees}
                if milestone.responsible_employee_id not in assignment_employee_ids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Responsible employee must be part of the employees responsible for the associated assignment"
                    )

            for key, value in milestone.dict(exclude_unset=True).items():
                setattr(db_milestone, key, value)

            self.db.commit()
            self.db.refresh(db_milestone)
            logging_helper.log_info(f"Milestone updated successfully with ID: {db_milestone.id}")
            return db_milestone
        except Exception as e:
            logging_helper.log_error(f"Failed to update milestone: {str(e)}")
            self.db.rollback()
            raise


    def get_milestone(self, milestone_id: int):
        logging_helper.log_info(f"Fetching milestone with ID: {milestone_id}")
        try:
            db_milestone = self.db.query(Milestone).filter(Milestone.id == milestone_id).first()
            if not db_milestone:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

            assignment = db_milestone.assignment
            responsible_employee = db_milestone.responsible_employee

            employees = (
                self.db.query(Employee.id, Employee.first_name, Employee.last_name)
                .join(Assignment.responsible_employees)
                .filter(Assignment.id == assignment.id)
                .all()
            )

            return {
                "milestone": db_milestone,
                "assignment_employees": [{"id": emp.id, "full_name": f"{emp.first_name} {emp.last_name}"} for emp in employees],
                "responsible_employee": {"id": responsible_employee.id, "full_name": f"{responsible_employee.first_name} {responsible_employee.last_name}"}
            }
        except Exception as e:
            logging_helper.log_error(f"Failed to fetch milestone: {str(e)}")
            raise

    def get_milestones(self, skip: int = 0, limit: int = 10):
        logging_helper.log_info(f"Fetching milestones with skip: {skip}, limit: {limit}")
        try:
            milestones = self.db.query(Milestone).offset(skip).limit(limit).all()

            result = []
            for milestone in milestones:
                assignment = milestone.assignment
                responsible_employee = milestone.responsible_employee

                employees = (
                    self.db.query(Employee.id, Employee.first_name, Employee.last_name)
                    .join(Assignment.responsible_employees)
                    .filter(Assignment.id == assignment.id)
                    .all()
                )

                result.append({
                    "milestone": milestone,
                    "assignment_employees": [{"id": emp.id, "full_name": f"{emp.first_name} {emp.last_name}"} for emp in employees],
                    "responsible_employee": {"id": responsible_employee.id, "full_name": f"{responsible_employee.first_name} {responsible_employee.last_name}"}
                })

            return result
        except Exception as e:
            logging_helper.log_error(f"Failed to fetch milestones: {str(e)}")
            raise

    def delete_milestone(self, milestone_id: int):
        logging_helper.log_info(f"Deleting milestone with ID: {milestone_id}")
        try:
            db_milestone = self.db.query(Milestone).filter(Milestone.id == milestone_id).first()
            if not db_milestone:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

            self.db.delete(db_milestone)
            self.db.commit()
            logging_helper.log_info(f"Milestone deleted successfully with ID: {milestone_id}")
            return db_milestone
        except Exception as e:
            logging_helper.log_error(f"Failed to delete milestone: {str(e)}")
            self.db.rollback()
            raise


    def complete_milestone(self, milestone_id: int, user_id: Optional[int] = None):
        logging_helper.log_info(f"Completing milestone with ID: {milestone_id}")
        try:
            db_milestone = self.db.query(Milestone).filter(Milestone.id == milestone_id).first()
            if not db_milestone:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

            # Check if the assignment has been completed already
            assignment = db_milestone.assignment
            if assignment.is_completed:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignment has already been completed")

            # Check if all tasks associated with the milestone are completed
            tasks = db_milestone.tasks
            if not all(task.is_completed for task in tasks):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot complete milestone as not all tasks are completed")

            db_milestone.is_completed = True
            db_milestone.date_completed = datetime.utcnow()

            self.db.commit()
            logging_helper.log_info(f"Milestone with ID {milestone_id} marked as completed")
            return {"message": f"Milestone with ID {milestone_id} has been completed successfully"}
        except Exception as e:
            logging_helper.log_error(f"Failed to complete milestone with ID {milestone_id}: {str(e)}")
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to complete milestone: {str(e)}")


    def substitute_responsible_person_for_milestone(
        self, milestone_id: int, new_employee_id: int, user_id: Optional[int] = None
    ) -> Optional[Milestone]:
        try:
            # Fetch the milestone
            db_milestone = self.db_session.query(Milestone).filter(Milestone.id == milestone_id).first()
            if not db_milestone:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

            # Check if the milestone is completed
            if db_milestone.is_completed:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot substitute responsible person for a completed milestone")

            # Fetch the assignment associated with the milestone
            db_assignment = self.db_session.query(Assignment).filter(Assignment.id == db_milestone.assignment_id).first()
            if not db_assignment:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment associated with the milestone does not exist")

            # Check if the new employee is associated with the assignment
            new_employee = self.db_session.query(Employee).get(new_employee_id)
            if not new_employee or new_employee not in db_assignment.responsible_employees:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Employee is not associated with the assignment"
                )

            # Substitute the responsible person for the milestone
            old_responsible_employee_id = db_milestone.responsible_employee_id
            db_milestone.responsible_employee_id = new_employee_id
            self.db_session.commit()
            self.db_session.refresh(db_milestone)

            # Log the substitution
            changes = {
                "old_responsible_employee_id": old_responsible_employee_id,
                "new_responsible_employee_id": new_employee_id,
            }
            # logging_helper.log_audit(
            #     self.db_session,
            #     user_id,
            #     ActionEnum.UPDATE,
            #     "Milestone",
            #     milestone_id,
            #     changes,
            # )
            logging_helper.log_info(f"Responsible person for milestone ID {milestone_id} substituted successfully")
            return db_milestone
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error substituting responsible person for milestone with ID {milestone_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to substitute responsible person: {str(e)}")
        except Exception as e:
            logging_helper.log_error(f"Unhandled exception: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to substitute responsible person: {str(e)}")

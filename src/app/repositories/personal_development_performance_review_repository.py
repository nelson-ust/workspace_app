from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, BackgroundTasks
from models.all_models import (
    PersonalDevelopmentReview,
    ApprovalFlow,
    BroadBasedObjective,
    ResultBasedObjective,
)
from schemas.personal_development_performance_review_schemas import (
    PersonalDevelopmentPerformanceReviewCreateSchema,
    PersonalDevelopmentPerformanceReviewUpdateSchema,
)
from repositories.approval_step_repository import ApprovalStepRepository
from auth.email import (
    notify_next_approval_step,
    notify_request_initiator_of_rejection,
    notify_request_initiator_of_approval,
)
from logging_helpers import logging_helper
from typing import List, Optional

class PersonalDevelopmentPerformanceReviewRepository:
    def __init__(self, db_session: Session, base_url: str):
        """
        Initializes the PersonalDevelopmentPerformanceReviewRepository with a database session.

        Args:
            db_session (Session): SQLAlchemy session object.
            base_url (str): Base URL for email links to approval requests.
        """
        self.db_session = db_session
        self.base_url = base_url

    def create_performance_review(
        self,
        review_data: PersonalDevelopmentPerformanceReviewCreateSchema,
        background_tasks: BackgroundTasks
    ) -> PersonalDevelopmentReview:
        """
        Creates a new personal development performance review and initiates the approval flow.

        Args:
            review_data (PersonalDevelopmentPerformanceReviewCreateSchema): Data to create the performance review.
            background_tasks (BackgroundTasks): Background tasks for asynchronous operations.

        Returns:
            PersonalDevelopmentReview: The newly created performance review.

        Raises:
            HTTPException: If there is an issue creating the performance review or initiating the approval flow.
        """
        try:
            approval_flow = self._get_approval_flow(review_data.approval_flow_id)
            new_review = self._create_new_review(review_data)
            self._start_approval_flow(new_review, approval_flow, background_tasks)
            return new_review
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Database error during performance review creation: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error: Could not create performance review")
        except Exception as e:
            logging_helper.log_error(f"Unexpected error during performance review creation: {str(e)}")
            raise HTTPException(status_code=500, detail="Unexpected error: Could not create performance review")

    def _get_approval_flow(self, approval_flow_id: int) -> ApprovalFlow:
        """
        Retrieves an approval flow by ID or raises a 404 error if not found.

        Args:
            approval_flow_id (int): ID of the approval flow to retrieve.

        Returns:
            ApprovalFlow: The retrieved approval flow.
        
        Raises:
            HTTPException: If the approval flow is not found.
        """
        approval_flow = self.db_session.query(ApprovalFlow).filter(ApprovalFlow.id == approval_flow_id).first()
        if not approval_flow:
            raise HTTPException(status_code=404, detail="Approval flow not found")
        return approval_flow

    def _create_new_review(
        self,
        review_data: PersonalDevelopmentPerformanceReviewCreateSchema
    ) -> PersonalDevelopmentReview:
        """
        Creates and commits a new PersonalDevelopmentReview object with its objectives.

        Args:
            review_data (PersonalDevelopmentPerformanceReviewCreateSchema): Data for the new performance review.

        Returns:
            PersonalDevelopmentReview: The newly created performance review.
        """
        new_review = PersonalDevelopmentReview(
            employee_id=review_data.employee_id,
            review_period_start=review_data.review_period_start,
            review_period_end=review_data.review_period_end,
            strengths=review_data.strengths,
            areas_for_improvement=review_data.areas_for_improvement,
            next_steps=review_data.next_steps,
            approval_flow_id=review_data.approval_flow_id,
            created_at=datetime.now()
        )
        self.db_session.add(new_review)
        self.db_session.flush()  # Flush to get new_review.id before committing

        # Add Broad-Based Objectives and their nested Result-Based Objectives
        self._add_objectives(new_review.id, review_data.broad_based_objectives)
        
        self.db_session.commit()
        self.db_session.refresh(new_review)
        return new_review

    def _add_objectives(self, review_id: int, objectives: List[BroadBasedObjective]):
        """
        Adds Broad-Based Objectives and their Result-Based Objectives to the review.

        Args:
            review_id (int): ID of the personal development review.
            objectives (List[BroadBasedObjectiveSchema]): List of broad-based objectives to add.
        """
        for broad_based_data in objectives:
            broad_based_objective = BroadBasedObjective(
                review_id=review_id,
                objective_name=broad_based_data.objective_name,
                description=broad_based_data.description
            )
            self.db_session.add(broad_based_objective)
            self.db_session.flush()

            for result_based_data in broad_based_data.result_based_objectives:
                result_based_objective = ResultBasedObjective(
                    broad_objective_id=broad_based_objective.id,
                    objective_name=result_based_data.objective_name,
                    description=result_based_data.description,
                    result=result_based_data.result
                )
                self.db_session.add(result_based_objective)

    def _start_approval_flow(
        self,
        review: PersonalDevelopmentReview,
        approval_flow: ApprovalFlow,
        background_tasks: BackgroundTasks
    ):
        """
        Starts the approval process for a newly created performance review.

        Args:
            review (PersonalDevelopmentReview): The performance review for which to initiate the approval flow.
            approval_flow (ApprovalFlow): The approval flow object.
            background_tasks (BackgroundTasks): Background tasks for asynchronous operations.
        """
        approval_step_repo = ApprovalStepRepository(self.db_session, self.base_url)
        first_step = approval_step_repo.get_next_step(review.approval_flow_id)
        
        if first_step:
            next_approver = approval_step_repo.get_user_for_role(first_step.role_id)
            if next_approver:
                request_link = f"{self.base_url}/approval-requests/{review.id}"
                background_tasks.add_task(
                    notify_next_approval_step,
                    email_to=next_approver.email,
                    employee_name=next_approver.name,
                    flow_name=approval_flow.name,
                    request_link=request_link
                )
                logging_helper.log_info(f"Approval process initiated for review {review.id}. Notification sent to {next_approver.email}")

    def get_performance_review_by_id(self, review_id: int) -> Optional[PersonalDevelopmentReview]:
        """
        Retrieves a personal development performance review by ID.

        Args:
            review_id (int): The ID of the performance review.

        Returns:
            Optional[PersonalDevelopmentReview]: The performance review if found.

        Raises:
            HTTPException: If the review is not found.
        """
        try:
            review = self.db_session.query(PersonalDevelopmentReview).filter(PersonalDevelopmentReview.id == review_id).first()
            if not review:
                raise HTTPException(status_code=404, detail="Performance review not found")
            return review
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Database error during retrieval of review {review_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error: Could not retrieve performance review")

    def update_performance_review(
        self,
        review_id: int,
        update_data: PersonalDevelopmentPerformanceReviewUpdateSchema
    ) -> Optional[PersonalDevelopmentReview]:
        """
        Updates an existing personal development performance review by ID.

        Args:
            review_id (int): The ID of the performance review to update.
            update_data (PersonalDevelopmentPerformanceReviewUpdateSchema): Data to update the performance review.

        Returns:
            Optional[PersonalDevelopmentPerformanceReview]: The updated performance review if successful.
        """
        try:
            review = self.get_performance_review_by_id(review_id)
            if not review:
                raise HTTPException(status_code=404, detail="Performance review not found")
            
            # Update fields only if provided
            self._apply_updates_to_review(review, update_data)
            
            review.updated_at = datetime.now()
            self.db_session.commit()
            logging_helper.log_info(f"Performance review {review_id} updated successfully")
            return review
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Database error during update of review {review_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error: Could not update performance review")

    def _apply_updates_to_review(
        self,
        review: PersonalDevelopmentReview,
        update_data: PersonalDevelopmentPerformanceReviewUpdateSchema
    ):
        """
        Applies updates to a review only if update fields are provided.

        Args:
            review (PersonalDevelopmentReview): The review object to update.
            update_data (PersonalDevelopmentPerformanceReviewUpdateSchema): Data with updates to apply.
        """
        if update_data.review_period_start:
            review.review_period_start = update_data.review_period_start
        if update_data.review_period_end:
            review.review_period_end = update_data.review_period_end
        if update_data.strengths:
            review.strengths = update_data.strengths
        if update_data.areas_for_improvement:
            review.areas_for_improvement = update_data.areas_for_improvement
        if update_data.next_steps:
            review.next_steps = update_data.next_steps
        if update_data.approval_flow_id:
            approval_flow = self._get_approval_flow(update_data.approval_flow_id)
            review.approval_flow_id = approval_flow.id
        # Clear existing objectives and add updated ones
        if update_data.broad_based_objectives:
            self._clear_existing_objectives(review.id)
            self._add_objectives(review.id, update_data.broad_based_objectives)

    def _clear_existing_objectives(self, review_id: int):
        """
        Clears all Broad-Based and Result-Based Objectives associated with a review.

        Args:
            review_id (int): ID of the review to clear objectives from.
        """
        objectives = self.db_session.query(BroadBasedObjective).filter_by(review_id=review_id).all()
        for obj in objectives:
            self.db_session.query(ResultBasedObjective).filter_by(broad_objective_id=obj.id).delete()
        self.db_session.query(BroadBasedObjective).filter_by(review_id=review_id).delete()

    def delete_performance_review(self, review_id: int) -> None:
        """
        Deletes a personal development performance review by ID.

        Args:
            review_id (int): The ID of the performance review to delete.

        Raises:
            HTTPException: If the review is not found or there is a database error.
        """
        try:
            review = self.get_performance_review_by_id(review_id)
            if not review:
                raise HTTPException(status_code=404, detail="Performance review not found")
            
            self._clear_existing_objectives(review_id)
            self.db_session.delete(review)
            self.db_session.commit()
            logging_helper.log_info(f"Performance review {review_id} deleted successfully")
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Database error during deletion of review {review_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error: Could not delete performance review")

    def list_performance_reviews(self, employee_id: Optional[int] = None) -> List[PersonalDevelopmentReview]:
        """
        Lists all personal development performance reviews, optionally filtered by employee ID.

        Args:
            employee_id (Optional[int]): The ID of the employee to filter reviews by.

        Returns:
            List[PersonalDevelopmentReview]: A list of performance reviews.
        
        Raises:
            HTTPException: If there is a database error while retrieving the list.
        """
        try:
            query = self.db_session.query(PersonalDevelopmentReview)
            if employee_id:
                query = query.filter(PersonalDevelopmentReview.employee_id == employee_id)
            return query.all()
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Database error while listing performance reviews: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error: Could not list performance reviews")

    def advance_performance_review_approval(
        self,
        performance_review_id: int,
        background_tasks: BackgroundTasks
    ) -> bool:
        """
        Advances the approval flow for the specified performance review.

        Args:
            performance_review_id (int): The ID of the performance review.
            background_tasks (BackgroundTasks): Background tasks for asynchronous operations.

        Returns:
            bool: True if there is a next step and notifications were sent; False if this is the last step.

        Raises:
            HTTPException: If there is an error advancing the approval process.
        """
        try:
            performance_review = self.get_performance_review_by_id(performance_review_id)
            if not performance_review:
                raise HTTPException(status_code=404, detail="Performance review not found")

            approval_step_repo = ApprovalStepRepository(self.db_session, self.base_url)
            advanced = approval_step_repo.advance_approval_step(
                current_step_id=performance_review.approval_flow_id,
                initiator_email=performance_review.employee.email,
                initiator_name=performance_review.employee.name,
                background_tasks=background_tasks
            )

            if advanced:
                logging_helper.log_info(f"Approval step advanced for review {performance_review_id}. Notification sent to next approver.")
            else:
                logging_helper.log_info(f"Approval process completed for review {performance_review_id}.")
            return advanced
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Database error during approval advancement for review {performance_review_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error: Could not advance approval process")

    def reject_performance_review(self, review_id: int, rejection_comment: str, background_tasks: BackgroundTasks, current_user: str) -> None:
        """
        Rejects a performance review and notifies the initiator.

        Args:
            review_id (int): The ID of the performance review to reject.
            rejection_comment (str): The comment explaining the reason for rejection.
            background_tasks (BackgroundTasks): Background tasks for asynchronous operations.
            current_user (str): The name of the current user (approver) who rejected the review.

        Raises:
            HTTPException: If the review or approval step is not found, or a database error occurs.
        """
        try:
            review = self.db_session.query(PersonalDevelopmentReview).filter(PersonalDevelopmentReview.id == review_id).first()
            if not review:
                raise HTTPException(status_code=404, detail="Performance review not found")

            review.status = "Rejected"
            review.supervisor_comments = rejection_comment
            review.updated_at = datetime.now()
            self.db_session.commit()

            request_link = f"{self.base_url}/performance-reviews/{review_id}"
            background_tasks.add_task(
                notify_request_initiator_of_rejection,
                email_to=review.employee.email,
                employee_name=review.employee.name,
                approver_name=current_user,
                rejection_comment=rejection_comment,
                request_link=request_link
            )
            logging_helper.log_info(f"Performance review {review_id} rejected by {current_user}. Notification sent to {review.employee.email}.")
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail="Database error: Could not reject performance review")


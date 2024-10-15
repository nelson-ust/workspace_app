
# # #repositories/approval_steps_repository.py

# from typing import Optional
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from fastapi import HTTPException
# from models.all_models import ApprovalStep
# from schemas.approval_step_schemas import ApprovalStepCreateSchema, ApprovalStepUpdateSchema, ApprovalStepReadSchema

# class ApprovalStepRepository:
#     def __init__(self, db_session: Session):
#         """
#         Initializes the ApprovalStepRepository with a database session.

#         Args:
#             db_session (Session): The SQLAlchemy session for database operations.
#         """
#         self.db_session = db_session

#     def create_approval_step(self, approval_step_data: ApprovalStepCreateSchema) -> ApprovalStepReadSchema:
#         """
#         Creates a new approval step in the database using the provided data.
#         Ensures that there are no duplicate step orders for the same module.

#         Args:
#             approval_step_data (ApprovalStepCreateSchema): The schema containing all required data for creating an approval step.

#         Returns:
#             ApprovalStepReadSchema: The created approval step data.

#         Raises:
#             HTTPException: If there is any database error during the operation or a duplicate step order for the module.
#         """
#         # Check for duplicate step order within the same module
#         existing_step = self.db_session.query(ApprovalStep).filter(
#             ApprovalStep.step_order == approval_step_data.step_order,
#             ApprovalStep.module_id == approval_step_data.module_id
#         ).first()
        
#         if existing_step:
#             raise HTTPException(
#                 status_code=400, 
#                 detail=f"Step order {approval_step_data.step_order} already exists for module {approval_step_data.module_id}."
#             )
        
#         try:
#             new_step = ApprovalStep(
#                 step_order=approval_step_data.step_order,
#                 role_id=approval_step_data.role_id,
#                 module_id=approval_step_data.module_id,
#                 description=approval_step_data.description
#             )
#             self.db_session.add(new_step)
#             self.db_session.commit()
#             self.db_session.refresh(new_step)
#             return ApprovalStepReadSchema.from_orm(new_step)
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

#     def update_approval_step(self, step_id: int, update_data: ApprovalStepUpdateSchema) -> ApprovalStepReadSchema:
#         """
#         Updates an existing approval step based on its ID with the new data provided.
#         Ensures that there are no duplicate step orders for the same module.

#         Args:
#             step_id (int): The ID of the approval step to update.
#             update_data (ApprovalStepUpdateSchema): The schema containing all updatable data fields for the approval step.

#         Returns:
#             ApprovalStepReadSchema: The updated approval step data.

#         Raises:
#             HTTPException: If the approval step is not found, if there is a duplicate step order for the module, or if there is a database error.
#         """
#         try:
#             step = self.db_session.query(ApprovalStep).filter(ApprovalStep.id == step_id).first()
#             if not step:
#                 raise HTTPException(status_code=404, detail="Approval step not found")

#             # If step_order or module_id are being updated, ensure no duplicates
#             new_step_order = update_data.step_order if update_data.step_order is not None else step.step_order
#             new_module_id = update_data.module_id if update_data.module_id is not None else step.module_id
            
#             if self.db_session.query(ApprovalStep).filter(
#                 ApprovalStep.step_order == new_step_order,
#                 ApprovalStep.module_id == new_module_id,
#                 ApprovalStep.id != step_id
#             ).first():
#                 raise HTTPException(
#                     status_code=400, 
#                     detail=f"Step order {new_step_order} already exists for module {new_module_id}."
#                 )

#             # Update fields only if they are provided in update_data
#             step.step_order = new_step_order
#             step.role_id = update_data.role_id if update_data.role_id is not None else step.role_id
#             step.module_id = new_module_id
#             step.description = update_data.description if update_data.description is not None else step.description

#             self.db_session.commit()
#             return ApprovalStepReadSchema.from_orm(step)
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Failed to update approval step: {str(e)}")

#     def get_approval_step(self, step_id: int) -> ApprovalStepReadSchema:
#         """
#         Retrieves an approval step by its ID.

#         Args:
#             step_id (int): The ID of the approval step to retrieve.

#         Returns:
#             ApprovalStepReadSchema: The approval step data if found.

#         Raises:
#             HTTPException: If the approval step is not found or there is a database error.
#         """
#         try:
#             step = self.db_session.query(ApprovalStep).filter(ApprovalStep.id == step_id).first()
#             if not step:
#                 raise HTTPException(status_code=404, detail="Approval step not found")
#             return ApprovalStepReadSchema.from_orm(step)
#         except SQLAlchemyError as e:
#             raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

#     def delete_approval_step(self, step_id: int) -> None:
#         """
#         Deletes an approval step by its ID.

#         Args:
#             step_id (int): The ID of the approval step to delete.

#         Raises:
#             HTTPException: If the approval step is not found or there is a database error during deletion.
#         """
#         try:
#             step = self.db_session.query(ApprovalStep).filter(ApprovalStep.id == step_id).first()
#             if not step:
#                 raise HTTPException(status_code=404, detail="Approval step not found")

#             self.db_session.delete(step)
#             self.db_session.commit()
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Failed to delete approval step: {str(e)}")

#     def list_approval_steps(self, module_id: Optional[int] = None) -> list[ApprovalStepReadSchema]:
#         """
#         Lists all approval steps stored in the database, optionally filtered by module ID.

#         Args:
#             module_id (Optional[int]): The ID of the module to filter approval steps by.

#         Returns:
#             list[ApprovalStepReadSchema]: A list of all approval steps.

#         Raises:
#             HTTPException: If there is a database error during the retrieval.
#         """
#         try:
#             query = self.db_session.query(ApprovalStep)
#             if module_id is not None:
#                 query = query.filter(ApprovalStep.module_id == module_id)
#             steps = query.all()
#             return [ApprovalStepReadSchema.from_orm(step) for step in steps]
#         except SQLAlchemyError as e:
#             raise HTTPException(status_code=500, detail=f"Failed to list approval steps: {str(e)}")

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, BackgroundTasks
from typing import List, Optional
from models.all_models import ApprovalStep, ApprovalFlow, User
from schemas.approval_step_schemas import ApprovalStepCreateSchema, ApprovalStepUpdateSchema
# from auth.email import notify_next_approval_step

#from auth.email import notify_next_approval_step, notify_request_initiator_of_approval, notify_request_initiator_of_rejection
from auth.email import notify_next_approval_step, notify_request_initiator_of_approval, notify_request_initiator_of_rejection


from logging_helpers import logging_helper

class ApprovalStepRepository:
    def __init__(self, db_session: Session, base_url: str):
        """
        Initialize the ApprovalStepRepository with a database session.

        Args:
            db_session (Session): SQLAlchemy session object.
            base_url (str): Base URL for building links to approval requests.
        """
        self.db_session = db_session
        self.base_url = base_url

    def create_approval_step(self, step_data: ApprovalStepCreateSchema) -> ApprovalStep:
        """
        Create a new approval step.

        Args:
            step_data (ApprovalStepCreateSchema): The data for creating the approval step.

        Returns:
            ApprovalStep: The newly created approval step.
        """
        try:
            new_step = ApprovalStep(
                step_order=step_data.step_order,
                role_id=step_data.role_id,
                action=step_data.action,
                description=step_data.description,
                module_id=step_data.module_id,
                flow_id=step_data.flow_id,
            )
            self.db_session.add(new_step)
            self.db_session.commit()
            self.db_session.refresh(new_step)
            return new_step
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Database error while creating approval step: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error: Could not create approval step")

    def update_approval_step(self, step_id: int, update_data: ApprovalStepUpdateSchema) -> Optional[ApprovalStep]:
        """
        Update an existing approval step.

        Args:
            step_id (int): The ID of the approval step to update.
            update_data (ApprovalStepUpdateSchema): The data to update the approval step.

        Returns:
            Optional[ApprovalStep]: The updated approval step if successful.
        """
        try:
            step = self.db_session.query(ApprovalStep).filter(ApprovalStep.id == step_id).first()
            if not step:
                raise HTTPException(status_code=404, detail="Approval step not found")

            # Update fields if they are provided
            step.step_order = update_data.step_order or step.step_order
            step.role_id = update_data.role_id or step.role_id
            step.action = update_data.action or step.action
            step.description = update_data.description or step.description
            step.module_id = update_data.module_id or step.module_id
            step.flow_id = update_data.flow_id or step.flow_id

            self.db_session.commit()
            return step
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Database error while updating approval step: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error: Could not update approval step")

    def delete_approval_step(self, step_id: int) -> None:
        """
        Delete an approval step.

        Args:
            step_id (int): The ID of the approval step to delete.
        """
        try:
            step = self.db_session.query(ApprovalStep).filter(ApprovalStep.id == step_id).first()
            if not step:
                raise HTTPException(status_code=404, detail="Approval step not found")

            self.db_session.delete(step)
            self.db_session.commit()
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Database error while deleting approval step: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error: Could not delete approval step")

    def get_approval_step(self, step_id: int) -> Optional[ApprovalStep]:
        """
        Retrieve a specific approval step by its ID.

        Args:
            step_id (int): The ID of the approval step to retrieve.

        Returns:
            Optional[ApprovalStep]: The requested approval step.
        """
        try:
            return self.db_session.query(ApprovalStep).filter(ApprovalStep.id == step_id).first()
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Database error while retrieving approval step: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error: Could not retrieve approval step")

    def list_approval_steps(self, module_id: Optional[int] = None, flow_id: Optional[int] = None) -> List[ApprovalStep]:
        """
        List all approval steps, optionally filtered by module ID or flow ID.

        Args:
            module_id (Optional[int]): Filter by module ID.
            flow_id (Optional[int]): Filter by flow ID.

        Returns:
            List[ApprovalStep]: A list of approval steps.
        """
        try:
            query = self.db_session.query(ApprovalStep)
            if module_id:
                query = query.filter(ApprovalStep.module_id == module_id)
            if flow_id:
                query = query.filter(ApprovalStep.flow_id == flow_id)
            return query.all()
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Database error while listing approval steps: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error: Could not list approval steps")

    # 

    def advance_approval_step(self, current_step_id: int, initiator_email: str, initiator_name: str, background_tasks: BackgroundTasks) -> bool:
        """
        Advance the approval flow to the next step and notify both the next approver and the request initiator.

        Args:
            current_step_id (int): The ID of the current approval step.
            initiator_email (str): The email of the request initiator.
            initiator_name (str): The name of the request initiator.
            background_tasks (BackgroundTasks): Background tasks for asynchronous operations.

        Returns:
            bool: True if there is a next step and notifications were sent; False if this is the last step.
        """
        current_step = self.get_approval_step(current_step_id)
        if not current_step:
            raise HTTPException(status_code=404, detail="Current approval step not found")

        next_step = self.get_next_step(current_step_id)
        if next_step:
            # Notify the next approver
            next_approver = self.get_user_for_role(next_step.role_id)
            if next_approver:
                request_link = f"{self.base_url}/approval-requests/{current_step.id}"  # Adjust the URL as necessary
                background_tasks.add_task(
                    notify_next_approval_step,
                    email_to=next_approver.email,
                    employee_name=next_approver.name,
                    flow_name=current_step.flow.name,
                    request_link=request_link
                )

            # Notify the request initiator
            request_link_initiator = f"{self.base_url}/approval-requests/{current_step.id}"
            background_tasks.add_task(
                notify_request_initiator_of_approval,
                email_to=initiator_email,
                initiator_name=initiator_name,
                flow_name=current_step.flow.name,
                step_description=next_step.description,
                request_link=request_link_initiator
            )

            logging_helper.log_info(f"Approval step advanced. Notification sent to next approver: {next_approver.email} and initiator: {initiator_email}")
            return True
        
        logging_helper.log_info("No next step available; approval process completed")
        return False    


    def get_next_step(self, current_step_id: int) -> Optional[ApprovalStep]:
        """
        Get the next step in the approval flow.

        Args:
            current_step_id (int): The ID of the current approval step.

        Returns:
            Optional[ApprovalStep]: The next approval step, or None if this is the last step.
        """
        current_step = self.get_approval_step(current_step_id)
        if not current_step:
            raise HTTPException(status_code=404, detail="Current approval step not found")

        return self.db_session.query(ApprovalStep).filter(
            ApprovalStep.flow_id == current_step.flow_id,
            ApprovalStep.step_order > current_step.step_order
        ).order_by(ApprovalStep.step_order.asc()).first()

    def get_user_for_role(self, role_id: int) -> Optional[User]:
        """
        Retrieve the user associated with a specific role.

        Args:
            role_id (int): The role ID to find a user for.

        Returns:
            Optional[User]: The user object with the given role ID.
        """
        try:
            return self.db_session.query(User).filter(User.role_id == role_id).first()
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Database error while retrieving user for role {role_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error: Could not retrieve user for role")

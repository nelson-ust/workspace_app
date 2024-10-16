# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from fastapi import HTTPException
# from models.all_models import ApprovalFlow, ApprovalStep
# from schemas.approval_flow_schemas import ApprovalFlowCreateSchema, ApprovalFlowUpdateSchema
# from typing import List, Optional

# class ApprovalFlowRepository:
#     def __init__(self, db_session: Session):
#         """
#         Initialize the ApprovalFlowRepository with a database session.

#         Args:
#             db_session (Session): SQLAlchemy session object.
#         """
#         self.db_session = db_session

#     def create_approval_flow(self, approval_flow_data: ApprovalFlowCreateSchema) -> ApprovalFlow:
#         """
#         Create a new approval flow.

#         Args:
#             approval_flow_data (ApprovalFlowCreateSchema): The approval flow data to create.

#         Returns:
#             ApprovalFlow: The newly created approval flow record.

#         Raises:
#             HTTPException: If there is any error during the process.
#         """
#         try:
#             new_flow = ApprovalFlow(
#                 name=approval_flow_data.name,
#                 description=approval_flow_data.description,
#                 steps=[
#                     ApprovalStep(
#                         step_order=step.step_order,
#                         role_id=step.role_id,
#                         description=step.description
#                     ) for step in approval_flow_data.steps
#                 ]
#             )
#             self.db_session.add(new_flow)
#             self.db_session.commit()
#             self.db_session.refresh(new_flow)
#             return new_flow
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

#     def get_approval_flow_by_id(self, flow_id: int) -> Optional[ApprovalFlow]:
#         """
#         Retrieve a specific approval flow by its ID.

#         Args:
#             flow_id (int): The ID of the approval flow to retrieve.

#         Returns:
#             Optional[ApprovalFlow]: The approval flow record if found, otherwise None.

#         Raises:
#             HTTPException: If there is any error during the process.
#         """
#         try:
#             return self.db_session.query(ApprovalFlow).filter(ApprovalFlow.id == flow_id).first()
#         except SQLAlchemyError as e:
#             raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

#     def update_approval_flow(self, flow_id: int, update_data: ApprovalFlowUpdateSchema) -> ApprovalFlow:
#         """
#         Update an existing approval flow.

#         Args:
#             flow_id (int): The ID of the approval flow to update.
#             update_data (ApprovalFlowUpdateSchema): The updated data for the approval flow.

#         Returns:
#             ApprovalFlow: The updated approval flow record.

#         Raises:
#             HTTPException: If there is any error during the process or if the flow is not found.
#         """
#         try:
#             flow = self.db_session.query(ApprovalFlow).filter(ApprovalFlow.id == flow_id).first()
#             if not flow:
#                 raise HTTPException(status_code=404, detail="Approval flow not found")

#             flow.name = update_data.name if update_data.name else flow.name
#             flow.description = update_data.description if update_data.description else flow.description

#             # Update steps
#             for step_data in update_data.steps:
#                 step = next((s for s in flow.steps if s.step_order == step_data.step_order), None)
#                 if step:
#                     step.role_id = step_data.role_id
#                     step.description = step_data.description
#                 else:
#                     new_step = ApprovalStep(
#                         step_order=step_data.step_order,
#                         role_id=step_data.role_id,
#                         description=step_data.description
#                     )
#                     flow.steps.append(new_step)
#             self.db_session.commit()
#             return flow
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

#     def delete_approval_flow(self, flow_id: int) -> None:
#         """
#         Delete a specific approval flow by its ID.

#         Args:
#             flow_id (int): The ID of the approval flow to delete.

#         Raises:
#             HTTPException: If the flow is not found or if there is any error during the process.
#         """
#         try:
#             flow = self.db_session.query(ApprovalFlow).filter(ApprovalFlow.id == flow_id).first()
#             if not flow:
#                 raise HTTPException(status_code=404, detail="Approval flow not found")

#             self.db_session.delete(flow)
#             self.db_session.commit()
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

#     def list_approval_flows(self) -> List[ApprovalFlow]:
#         """
#         List all approval flows in the database.

#         Returns:
#             List[ApprovalFlow]: A list of all approval flows.

#         Raises:
#             HTTPException: If there is any error during the process.
#         """
#         try:
#             return self.db_session.query(ApprovalFlow).all()
#         except SQLAlchemyError as e:
#             raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException
from models.all_models import ApprovalFlow, ApprovalStep, Module, UserRole
from schemas.approval_flow_schemas import ApprovalFlowCreateSchema, ApprovalFlowUpdateSchema
from typing import List, Optional
from logging_helpers import logging_helper

class ApprovalFlowRepository:
    def __init__(self, db_session: Session ):
        """
        Initialize the ApprovalFlowRepository with a database session.

        Args:
            db_session (Session): SQLAlchemy session object.
        """
        self.db_session = db_session

    # def create_approval_flow(self, approval_flow_data: ApprovalFlowCreateSchema) -> ApprovalFlow:
    #     """
    #     Create a new approval flow.

    #     Args:
    #         approval_flow_data (ApprovalFlowCreateSchema): The approval flow data to create.

    #     Returns:
    #         ApprovalFlow: The newly created approval flow record.

    #     Raises:
    #         HTTPException: If there is any error during the process.
    #     """        
    #     try:
    #         # Verify if the module exists
    #         module = self.db_session.query(Module).filter(Module.id == approval_flow_data.module_id).first()
    #         if not module:
    #             raise HTTPException(status_code=404, detail="Module not found")

    #         # Create the approval flow and ensure that module_id is assigned to each step
    #         new_flow = ApprovalFlow(
    #             name=approval_flow_data.name,
    #             description=approval_flow_data.description,
    #             module_id=approval_flow_data.module_id,
    #             steps=[
    #                 ApprovalStep(
    #                     step_order=step.step_order,
    #                     role_id=step.role_id,
    #                     action="REVIEW",  # Assuming action is static for now; modify as needed
    #                     description=step.description,
    #                     module_id=approval_flow_data.module_id  # Ensure module_id is set here
    #                 ) for step in approval_flow_data.steps
    #             ]
    #         )
    #         self.db_session.add(new_flow)
    #         self.db_session.commit()
    #         self.db_session.refresh(new_flow)
    #         return new_flow
    #     except SQLAlchemyError as e:
    #         self.db_session.rollback()
    #         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")






    def create_approval_flow(self, approval_flow_data: ApprovalFlowCreateSchema) -> ApprovalFlow:
        try:
            # Verify if the module exists
            module = self.db_session.query(Module).filter(Module.id == approval_flow_data.module_id).first()
            if not module:
                raise HTTPException(status_code=404, detail="Module not found")

            # Create the approval flow with its steps, explicitly setting module_id for each step
            new_flow = ApprovalFlow(
                name=approval_flow_data.name,
                description=approval_flow_data.description,
                module_id=approval_flow_data.module_id,
                steps=[
                    ApprovalStep(
                        step_order=step.step_order,
                        role_id=step.role_id,
                        description=step.description,
                        module_id=approval_flow_data.module_id  # Set module_id for each step
                    ) for step in approval_flow_data.steps
                ]
            )
            self.db_session.add(new_flow)
            self.db_session.commit()
            self.db_session.refresh(new_flow)
            return new_flow
        except IntegrityError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Integrity error: {str(e)}")
            raise HTTPException(status_code=400, detail="Database integrity error occurred.")
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="A database error occurred.")
        except Exception as e:
            logging_helper.log_error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the approval flow.")



    # def create_approval_flow(self, approval_flow_data: ApprovalFlowCreateSchema) -> ApprovalFlow:
    #     try:
    #         # Verify if the module exists
    #         module = self.db_session.query(Module).filter(Module.id == approval_flow_data.module_id).first()
    #         if not module:
    #             raise HTTPException(status_code=404, detail="Module not found")

    #         # Prepare the steps with role lookup
    #         steps = []
    #         for step_data in approval_flow_data.steps:
    #             # Look up the role ID based on the role name provided
    #             role = self.db_session.query(UserRole).filter(UserRole.name == step_data.approval_role).first()
    #             if not role:
    #                 raise HTTPException(status_code=404, detail=f"Role '{step_data.approval_role}' not found")
                
    #             steps.append(ApprovalStep(
    #                 step_order=step_data.order,  # Map 'order' to 'step_order'
    #                 role_id=role.id,  # Use the role ID from the lookup
    #                 action="REVIEW",  # Example static action, modify if needed
    #                 description=step_data.name,  # Assuming 'name' is the description of the step
    #                 module_id=approval_flow_data.module_id  # Set the module ID for the step
    #             ))

    #         # Create the approval flow
    #         new_flow = ApprovalFlow(
    #             name=approval_flow_data.name,
    #             description=approval_flow_data.description,
    #             module_id=approval_flow_data.module_id,
    #             steps=steps
    #         )
    #         self.db_session.add(new_flow)
    #         self.db_session.commit()
    #         self.db_session.refresh(new_flow)
    #         return new_flow

    #     # except SQLAlchemyError as e:
    #     #     self.db_session.rollback()
    #     #     raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
    #     except SQLAlchemyError as e:
    #         self.db_session.rollback()
    #         logging_helper.log_error(f"Database error: {str(e)}")  # Log the specific error message
    #         raise HTTPException(status_code=500, detail="A database error occurred while creating the approval flow.")



    def get_approval_flow_by_id(self, flow_id: int) -> Optional[ApprovalFlow]:
        """
        Retrieve a specific approval flow by its ID.

        Args:
            flow_id (int): The ID of the approval flow to retrieve.

        Returns:
            Optional[ApprovalFlow]: The approval flow record if found, otherwise None.

        Raises:
            HTTPException: If there is any error during the process.
        """
        try:
            return self.db_session.query(ApprovalFlow).filter(ApprovalFlow.id == flow_id).first()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def update_approval_flow(self, flow_id: int, update_data: ApprovalFlowUpdateSchema) -> ApprovalFlow:
        """
        Update an existing approval flow.

        Args:
            flow_id (int): The ID of the approval flow to update.
            update_data (ApprovalFlowUpdateSchema): The updated data for the approval flow.

        Returns:
            ApprovalFlow: The updated approval flow record.

        Raises:
            HTTPException: If there is any error during the process or if the flow is not found.
        """
        try:
            flow = self.db_session.query(ApprovalFlow).filter(ApprovalFlow.id == flow_id).first()
            if not flow:
                raise HTTPException(status_code=404, detail="Approval flow not found")

            # Update flow attributes
            flow.name = update_data.name if update_data.name else flow.name
            flow.description = update_data.description if update_data.description else flow.description
            
            # Update module_id if provided and check if the module exists
            if update_data.module_id:
                module = self.db_session.query(Module).filter(Module.id == update_data.module_id).first()
                if not module:
                    raise HTTPException(status_code=404, detail="Module not found")
                flow.module_id = update_data.module_id

            # Update steps
            for step_data in update_data.steps:
                step = next((s for s in flow.steps if s.step_order == step_data.step_order), None)
                if step:
                    step.role_id = step_data.role_id
                    step.description = step_data.description
                else:
                    new_step = ApprovalStep(
                        step_order=step_data.step_order,
                        role_id=step_data.role_id,
                        description=step_data.description
                    )
                    flow.steps.append(new_step)
            self.db_session.commit()
            return flow
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def delete_approval_flow(self, flow_id: int) -> None:
        """
        Delete a specific approval flow by its ID.

        Args:
            flow_id (int): The ID of the approval flow to delete.

        Raises:
            HTTPException: If the flow is not found or if there is any error during the process.
        """
        try:
            flow = self.db_session.query(ApprovalFlow).filter(ApprovalFlow.id == flow_id).first()
            if not flow:
                raise HTTPException(status_code=404, detail="Approval flow not found")

            self.db_session.delete(flow)
            self.db_session.commit()
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def list_approval_flows(self) -> List[ApprovalFlow]:
        """
        List all approval flows in the database.

        Returns:
            List[ApprovalFlow]: A list of all approval flows.

        Raises:
            HTTPException: If there is any error during the process.
        """
        try:
            return self.db_session.query(ApprovalFlow).all()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

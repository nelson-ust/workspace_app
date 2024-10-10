
# #routes/workplan_routes.py
# # import datetime
# from datetime import date
# import logging
# # from pathlib import Path
# from typing import List, Optional
# from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Query, status, Path
# from sqlalchemy.orm import Session
# from auth.dependencies import role_checker
# from auth.security import get_current_user
# from schemas.user_schemas import UserRead
# from db.database import get_db  # Adjust according to your project structure
# #from repositories.workplan_repository import WorkPlanRepository
# # from repositories.work_plan_repo import WorkPlanRepository
# from repositories.workplan_repository import WorkPlanRepository
# from schemas.workplan_schemas import EmployeeModel, EmployeeWithoutWorkPlan, MonthlyWorkPlanSummary, WorkPlanCreate, WorkPlanRead, WorkPlanReadByDateRange, WorkPlanUpdate as WorkPlanUpdateSchema, WorkPlanReschedule as WorkPlanRescheduleSchema
# from logging_helpers import logging_helper
# from models.all_models import ActionEnum

# router = APIRouter()

# ## Tenancy ID added to restrict users to create workplan for only their state with expeption of the Super Admin
# @router.post("/create", response_model=WorkPlanRead, status_code=status.HTTP_201_CREATED)
# async def create_work_plan(
#     background_tasks: BackgroundTasks,
#     work_plan_data: WorkPlanCreate,
#     current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db),_=Depends(role_checker(['unit_member','technical_lead','programs_lead','stl','hq_staff','tenant_admin', 'super_admin']))):
#     """
#     Create a new work plan with specified details from the WorkPlanCreate schema. This function
#     also sends asynchronous notifications to relevant stakeholders about the creation of the work plan.
#     """
#     logging_helper.log_info("Accessing Create Workplan Endpoint...")
#     repo = WorkPlanRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin" or current_user.tenancy_id == work_plan_data.tenancy_id:
#                 new_work_plan = repo.create_work_plan(background_tasks, work_plan_data)
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "WorkPlan", new_work_plan.id, new_work_plan.activity_title)
#                 break
#             else:
#                 raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{current_user.first_name} {current_user.last_name}, your authorized to create workplan only in your state")
#         return new_work_plan
#     except HTTPException as e:
        
#         raise e
#     except Exception as e:
#         logging.error(f"Creating work plan failed due to: {e}")
#         raise HTTPException(status_code=500, detail="An error occurred while creating the work plan.")

# ## Tenancy ID added to restrict users to update workplan for only their state with expeption of the Super Admin
# @router.put("/workplans/{work_plan_id}", response_model=WorkPlanRead)
# async def update_work_plan(work_plan_id: int, work_plan_update: WorkPlanUpdateSchema, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db),_=Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))):
#     """
#     Updates an existing work plan with provided data. Only the fields that are provided in the request body will be updated.
#     """
#     logging_helper.log_info("Accessing Update Workplan Endpoint ...")
#     try:
#         work_plan_repo = WorkPlanRepository(db)

#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 updated_work_plan = work_plan_repo.update_work_plan(work_plan_id=work_plan_id, update_data=work_plan_update)
#                 if updated_work_plan is None:
#                     raise HTTPException(status_code=404, detail="Work plan not found")
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "WorkPlan", work_plan_id, work_plan_update.json())
#                 return updated_work_plan
#             else:
#                 updated_work_plan = work_plan_repo.update_work_plan(work_plan_id=work_plan_id, update_data=work_plan_update, tenancy_id=current_user.tenancy_id)
#                 if updated_work_plan is None:
#                     raise HTTPException(status_code=404, detail="Work plan not found")
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "WorkPlan", work_plan_id, work_plan_update.json())
#                 return updated_work_plan
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/workplans/for-approval")
# def get_work_plans_for_approval(current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db),_=Depends(role_checker(['unit_member','programs_lead', 'tenant_admin', 'super_admin']))):
#     logging_helper.log_info("Accessing Workplan for Approval Endpoints ...")
#     plan_repo = WorkPlanRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 work_plans = plan_repo.fetch_pending_work_plans_for_week()
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch pending work plans for approval")
#                 return work_plans
#             elif role_dict.name in ['programs_lead', 'technical_lead', 'stl', 'tenant_admin']:
#                 work_plans = plan_repo.fetch_pending_work_plans_for_week(tenancy_id=current_user.tenancy_id)
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch pending work plans for approval")
#                 return work_plans
#             else:
#                 work_plans = plan_repo.fetch_pending_work_plans_for_week(tenancy_id=current_user.tenancy_id, employee_id=current_user.employee_id)
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch pending work plans for approval")
#                 return work_plans
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# # @router.get("/current-week-work-plans", response_model=list)  # Adjust the response model according to your data structure
# # def get_current_week_work_plans(current_user:UserRead=Depends(get_current_user), 
# #                          db: Session = Depends(get_db),_=Depends(role_checker(['unit_member','programs_lead', 'tenant_admin', 'super_admin']))):
# #     plan_repo = WorkPlanRepository(db)
# #     try:
# #         for role_dict in current_user.roles:
# #             if role_dict.name == "super_admin":
# #                 work_plans = plan_repo.fetch_current_week_work_plans_with_status()
# #                 return work_plans
# #             elif role_dict.name in ['programs_lead', 'technical_lead', 'stl', 'tenant_admin']:
# #                 work_plans = plan_repo.fetch_current_week_work_plans_with_status(tenancy_id=current_user.tenancy_id)
# #                 return work_plans
# #             else:
# #                 work_plans = plan_repo.fetch_current_week_work_plans_with_status(tenancy_id=current_user.tenancy_id, employee_id=current_user.employee_id)
# #                 return work_plans
# #     except Exception as e:
# #         raise HTTPException(status_code=400, detail=str(e))


# @router.get("/current-week-work-plans/{start_of_week}/{end_of_week}", response_model=list)  # Adjust the response model according to your data structure
# def get_current_week_work_plans(start_of_week: date = Path(..., description="Start of the week (Monday)"),
#                                 end_of_week: date = Path(..., description="End of the week (Sunday)"),
#                                 vehicle_assigned: Optional[bool] = Query(None, description="Check if the vehicle is already assigned"),
#                                 current_user: UserRead = Depends(get_current_user), 
#                                 db: Session = Depends(get_db), 
#                                 _=Depends(role_checker(['unit_member','stl','technical_lead', 'programs_lead', 'tenant_admin', 'super_admin']))):
    
#     logging_helper.log_info("Accessing get current week workplan Endpoint ...")
#     plan_repo = WorkPlanRepository(db)
#     try:
#         if 'super_admin' in [role.name for role in current_user.roles]:
#             work_plans = plan_repo.fetch_current_week_work_plans_with_status(start_of_week=start_of_week, end_of_week=end_of_week,vehicle_assigned=vehicle_assigned)
#             logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch current week work plans")
#         elif any(role.name in ['programs_lead', 'technical_lead', 'stl', 'tenant_admin'] for role in current_user.roles):
#             work_plans = plan_repo.fetch_current_week_work_plans_with_status(start_of_week=start_of_week, end_of_week=end_of_week,vehicle_assigned=vehicle_assigned,tenancy_id=current_user.tenancy_id )
#             logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch current week work plans")
#         else:
#             work_plans = plan_repo.fetch_current_week_work_plans_with_status(start_of_week=start_of_week, end_of_week=end_of_week,vehicle_assigned=vehicle_assigned,tenancy_id=current_user.tenancy_id, employee_id=current_user.employee_id, )
#             logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch current week work plans")
#         return work_plans
#     except Exception as e:  
#         raise HTTPException(status_code=400, detail=str(e))


# @router.get("/workplans/active", response_model=List[WorkPlanRead])
# def read_active_work_plans(current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db),_=Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))):
#     logging_helper.log_info("Accessing Get Active Workplans Endpoint")
#     repo = WorkPlanRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 work_plans = repo.get_active_work_plans()
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch active work plans")
#                 return work_plans
#             else:
#                 work_plans = repo.get_active_work_plans(tenancy_id=current_user.tenancy_id)
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch active work plans")
#                 return work_plans
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.patch("/review/{work_plan_id}", response_model=WorkPlanRead)
# def review_work_plan(
#     work_plan_id: int, review_data: WorkPlanCreate, db: Session = Depends(get_db)
# ):
#     if not review_data.date_reviewed or not review_data.reviewed_by:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Review date and reviewer must be provided",
#         )
#     logging_helper.log_info("Accessing the -Review Workplan- Endpoint")
#     try:
#         repo = WorkPlanRepository(db)
#         updated_work_plan = repo.review_work_plan(
#             work_plan_id, review_data.reviewed_by, review_data.date_reviewed
#         )
#         logging_helper.log_audit(db, review_data.reviewed_by, ActionEnum.REVIEW, "WorkPlan", work_plan_id, f"Reviewed on {review_data.date_reviewed}")
#         return updated_work_plan
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logging.error(f"Reviewing work plan failed due to: {e}")
#         raise HTTPException(status_code=500, detail="An error occurred while reviewing the work plan.")
    

# @router.put("/workplans/{work_plan_id}/approve", status_code=status.HTTP_200_OK)
# def approve_work_plan(background_tasks: BackgroundTasks, work_plan_id: int, approver_id: int, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db),_=Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))):
#     """
#     Approve a work plan with the specified Work Plan ID by a given approver.
#     This endpoint schedules background tasks for sending notifications post-approval.
#     """
#     logging_helper.log_info("Accessing -Approve Workplan- Endpoint")
#     repo = WorkPlanRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 approved_work_plan = repo.approve_work_plan(background_tasks, work_plan_id, approver_id)
#                 logging_helper.log_audit(db, approver_id, ActionEnum.APPROVE, "WorkPlan", work_plan_id, "Approved")
#                 return approved_work_plan
#             else:
#                 approved_work_plan = repo.approve_work_plan(background_tasks, work_plan_id, approver_id, tenancy_id=current_user.tenancy_id)
#                 logging_helper.log_audit(db, approver_id, ActionEnum.APPROVE, "WorkPlan", work_plan_id, "Approved")
#                 return approved_work_plan

#     except HTTPException as http_exc:
#         raise http_exc
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Approving work plan failed: {e}")    


# @router.patch("/workplans/{work_plan_id}/deny", status_code=200)
# def deny_work_plan(
#     background_tasks: BackgroundTasks,
#     work_plan_id: int = Path(..., description="The ID of the work plan to deny"),
#     reason: str = Body(..., embed=True),
#     current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db),_=Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))):
#     """
#     Deny a work plan, setting its is_denied status to True and recording the reason.
#     If the work plan was previously approved, it will reverse the approval.
#     """
#     logging_helper.log_info("Accessing - Deny Work Plan - Endpoint")
#     repo = WorkPlanRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 denied_work_plan = repo.deny_work_plan(background_tasks, work_plan_id, reason)
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.DENY, "WorkPlan", work_plan_id, f"Denied: {reason}")
#                 return denied_work_plan
#             else:
#                 denied_work_plan = repo.deny_work_plan(background_tasks, work_plan_id, reason, tenancy_id = current_user.tenancy_id)
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.DENY, "WorkPlan", work_plan_id, f"Denied: {reason}")
#                 return denied_work_plan
#     except HTTPException as http_exc:
#         raise http_exc
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post("/workplans/{work_plan_id}/reschedule",status_code=200) # response_model=WorkPlanRescheduleSchema, status_code=200)
# def reschedule_work_plan_endpoint(
#     background_tasks: BackgroundTasks,
#     work_plan_id: int = Path(..., description="The ID of the work plan to reschedule"),
#     reschedule_data: WorkPlanRescheduleSchema = Body(...),
#     current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db),_=Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))):
    
#     """Reschedule a work plan based on its ID."""
#     logging_helper.log_info("Accessing - Recheduleled Workplan - Endpoint")
#     work_plan_repository = WorkPlanRepository(db_session=db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 rescheduled_work_plan = work_plan_repository.reschedule_work_plan(background_tasks, work_plan_id, reschedule_data.reason, reschedule_data.new_date)
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.RESCHEDULE, "WorkPlan", work_plan_id, f"Rescheduled: {reschedule_data.reason} to {reschedule_data.new_date}")
#                 return rescheduled_work_plan
#             else:
#                 rescheduled_work_plan = work_plan_repository.reschedule_work_plan(background_tasks, work_plan_id, reschedule_data.reason, reschedule_data.new_date, tenancy_id = current_user.tenancy_id)
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.RESCHEDULE, "WorkPlan", work_plan_id, f"Rescheduled: {reschedule_data.reason} to {reschedule_data.new_date}")
#                 return rescheduled_work_plan
#     except HTTPException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.detail)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/employees/without-workplan", response_model=List[EmployeeWithoutWorkPlan], status_code=status.HTTP_200_OK)
# def get_employees_without_work_plan(
#     activity_date: date = Query(..., description="The activity date to check for employee availability"),
#     current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db),_=Depends(role_checker(['programs_lead','unit_member','stl','technical_lead', 'tenant_admin', 'super_admin']))):
#     """
#     Retrieve all employees who are not assigned to any work plan on a given date.
#     Handles exceptions such as database errors and unexpected issues.
#     """
#     logging_helper.log_info("Accessing the - Get Employees Without Workplan - Endpoint")
#     repo = WorkPlanRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 employees = repo.list_employees_without_work_plan_on_date(activity_date)
#                 #logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Employee", None, f"Employees without work plan on {activity_date}")
#                 return employees
#             else:
#                 employees = repo.list_employees_without_work_plan_on_date(activity_date, tenancy_id = current_user.tenancy_id)
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Employee", None, f"Employees without work plan on {activity_date}")
#                 return employees
            
#         if not employees:
#             return []
    
#     except HTTPException as http_exc:  # Handles HTTP errors thrown manually in the repository
#         raise http_exc
#     except Exception as e:  # Generic exception for any other errors
#         logging.error(f"Unexpected error occurred: {e}")  # Ensure you have logging configured
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request.")


# @router.put("/update-workplan/{work_plan_id}", response_model=WorkPlanUpdateSchema)
# def update_work_plan_if_pending(work_plan_id: int, updates: WorkPlanUpdateSchema, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db),_=Depends(role_checker(["unit_member", 'programs_lead', 'tenant_admin', 'super_admin']))):
#     """
#     Update a work plan only if its status is 'Pending'.
#     :param work_plan_id: ID of the work plan to update.
#     :param updates: Data to update the work plan with.
#     :param db: Database session dependency.
#     :return: Updated work plan data.
#     """
#     logging_helper.log_info("Accessing - Update Wrkplan if Pending - Endpoint")
#     work_plan_repo = WorkPlanRepository(db_session=db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 updated_work_plan = work_plan_repo.update_work_plan_if_pending(work_plan_id=work_plan_id, updates=updates.dict(exclude_unset=True))
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "WorkPlan", work_plan_id, f"Update if pending: {updates.json()}")
#                 return updated_work_plan
#             elif role_dict.name in ["programs_lead", "tenant_admin"]:
#                 updated_work_plan = work_plan_repo.update_work_plan_if_pending(work_plan_id=work_plan_id, updates=updates.dict(exclude_unset=True), tenancy_id = current_user.tenancy_id)
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "WorkPlan", work_plan_id, f"Update if pending: {updates.json()}")
#                 return updated_work_plan
#             else:
#                 updated_work_plan = work_plan_repo.update_work_plan_if_pending(work_plan_id=work_plan_id, updates=updates.dict(exclude_unset=True), tenancy_id = current_user.tenancy_id, user_id=current_user.id)
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "WorkPlan", work_plan_id, f"Update if pending: {updates.json()}")
#                 return updated_work_plan
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/workplans/employees", response_model=List[EmployeeModel])
# def fetch_employees_associated_with_work_plan(
#     workplan_code: Optional[str] = None,
#     initiator_name: Optional[str] = None,
#     activity_date: Optional[date] = None,
#     current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db),_=Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))):
#     logging_helper.log_info("Accessing - Fetch Employee Associated with Workplan - Endpoint")
#     repository = WorkPlanRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 employees = repository.fetch_employees_by_work_plan(workplan_code, initiator_name, activity_date)
#                 #logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Employee", None, "Fetch employees associated with work plan")
#                 return employees
#             else:
#                 employees = repository.fetch_employees_by_work_plan(workplan_code, initiator_name, activity_date, tenancy_id = current_user.tenancy_id)
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Employee", None, "Fetch employees associated with work plan")
#                 return employees
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
   
# @router.get("/workplans/approved-weekly/")# , response_model=List[ApprovedWorkPlan])
# def get_approved_weekly_workplans(current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db),_=Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))):
#     logging_helper.log_info("Accessing - Get Approved Weekly Workplan - Endpoint")
#     workplan_repo = WorkPlanRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin":
#                 approved_workplans = workplan_repo.fetch_approved_weekly_work_plans()
#                 #logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch approved weekly work plans")
#                 return approved_workplans
#             else:
#                 approved_workplans = workplan_repo.fetch_approved_weekly_work_plans(tenancy_id=current_user.tenancy_id)
#                 #logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch approved weekly work plans")
#                 return approved_workplans
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    

# @router.get("/workplans/approved/", response_model=WorkPlanRead)
# def fetch_approved_work_plan(identifier: str, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db),_=Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))):
#     """
#     Fetch an approved work plan by its ID or work plan code.
#     """
#     logging_helper.log_info("Accessing - Fetch Approved Workplan - Endpoint")
#     work_plan_repo = WorkPlanRepository(db)
#     try:
#         for role_dict in current_user.roles:
#                 if role_dict.name == "super_admin":
#                     work_plan = work_plan_repo.fetch_approved_work_plan_by_code_or_id(identifier)
#                     if work_plan == None:
#                         raise HTTPException(status_code=404, detail="Approved work plan not found")
#                     #logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", identifier, "Fetch approved work plan by ID or code")
#                     return work_plan
#                 else:
#                     work_plan = work_plan_repo.fetch_approved_work_plan_by_code_or_id(identifier, tenancy_id=current_user.tenancy_id)
#                     if work_plan == None:
#                         raise HTTPException(status_code=404, detail="Approved work plan not found")
#                     #logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", identifier, "Fetch approved work plan by ID or code")
#                     return work_plan
#     except Exception as e:
#         raise HTTPException(status_code=404, detail="Approved work plan not found")


# @router.get("/work-plans/approved/by-entity/{entity_type}") #, responses={404: {"model": HTTPException}})
# def fetch_approved_work_plan_by_entity(
#     entity_type: str = Path(..., description="The type of entity (unit, srt, department, thematicarea)"),
#     entity_name: str = Query(..., description="The name of the entity (SRT A, SRT B, SI, Admin, HI)"),
#     current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db),_=Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))):
#     """
#     Fetches an approved work plan based on the provided entity type and name.
#     """
#     logging_helper.log_info("Accessing - Fetch Approved Workplan by Entity - Endpoint")
#     work_plan_repo = WorkPlanRepository(db)
#     try:
#         for role_dict in current_user.roles:
#                 if role_dict.name == "super_admin":
#                     result = work_plan_repo.fetch_approved_work_plan_by_entity(entity_type, entity_name)
#                     if result == None:
#                         raise HTTPException(status_code=404, detail="Approved work plan not found")
#                     #logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, f"Fetch approved work plan by entity: {entity_type} - {entity_name}")
#                     return result
#                 else:
#                     result = work_plan_repo.fetch_approved_work_plan_by_entity(entity_type, entity_name, tenancy_id=current_user.tenancy_id)
#                     if result == None:
#                         raise HTTPException(status_code=404, detail="Approved work plan not found")
#                     #logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, f"Fetch approved work plan by entity: {entity_type} - {entity_name}")
#                     return result
#     except Exception as e:
#         raise HTTPException(status_code=404, detail="No approved work plan found for the specified entity")


# @router.get("/workplans/monthly-summary/{year}/{month}", response_model=MonthlyWorkPlanSummary)
# def get_monthly_work_plan_summary(year: int, month: int, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db),_=Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))):
#     logging_helper.log_info("Accessing - Get Monthly Workplan Summary - Endpoint")
#     repo = WorkPlanRepository(db)
#     try:
#         for role_dict in current_user.roles:
#                 if role_dict.name == "super_admin":
#                     summary = repo.fetch_monthly_work_plan_summary(year, month)
#                     #logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, f"Fetch monthly work plan summary for {month}/{year}")
#                 else:
#                     summary = repo.fetch_monthly_work_plan_summary(year, month, tenancy_id=current_user.tenancy_id)
#                     #logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, f"Fetch monthly work plan summary for {month}/{year}")
#                 return summary
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.get("/workplans/by-date-range/", response_model=List[WorkPlanReadByDateRange])
# def get_workplans_by_date_range(
#     start_date: date,
#     end_date: date,
#     status: Optional[str] = Query(None, description="Filter by status (e.g., 'Approved', 'Pending')"),
#     current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db),_=Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))):

#     """
#     Endpoint to fetch work plans between two dates, including details about associated employees and optionally filtering by status.
#     """
#     logging_helper.log_info("Accessing - Get Workplan by Date Range - Endpoint")
#     try:
#         work_plan_repo = WorkPlanRepository(db)
#         for role_dict in current_user.roles:
#                 if role_dict.name == "super_admin":
#                     work_plans = work_plan_repo.fetch_workplans_by_date_range(start_date, end_date, status)
#                     #logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, f"Fetch work plans by date range: {start_date} to {end_date}")
#                 else:
#                     work_plans = work_plan_repo.fetch_workplans_by_date_range(start_date, end_date, status, tenancy_id=current_user.tenancy_id)
#                     #logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, f"Fetch work plans by date range: {start_date} to {end_date}")
#                 return work_plans
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error retrieving work plans: {str(e)}")


# @router.get("/workplans/by-logistics/{logistics_requirement}") #, response_model=List[WorkPlanDetails])
# def get_work_plans_by_logistics(logistics_requirement: str, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db),_=Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))):
#     """
#     Retrieves work plans based on logistics requirements, including associated sources, employees,
#     locations, and sites. This endpoint will filter work plans by the specified logistics requirement.
    
#     - **logistics_requirement**: string name of the logistics requirement to filter work plans by
#     """
#     logging_helper.log_info("Accessing - Get Workplans by Logistics - Endpoint")
#     try:
#         repo = WorkPlanRepository(db)
#         work_plans = repo.get_work_plans_by_logistics(logistics_requirement, tenancy_id=current_user.tenancy_id)
#         if not work_plans:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="No work plan found with the specified logistics requirement")
#         #logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, f"Fetch work plans by logistics requirement: {logistics_requirement}")
#         return work_plans
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# @router.post("/assign-trip/{work_plan_id}")
# def assign_trip(
#     work_plan_id: int,
#     vehicle_ids: List[int],
#     driver_ids: List[int],
#     background_tasks: BackgroundTasks,
#     current_user:UserRead=Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Assign vehicles and drivers to a trip for a specific work plan.
#     Requires lists of vehicle IDs and driver IDs to select from.

#     - **work_plan_id**: The ID of the work plan to create trips for.
#     - **vehicle_ids**: List of vehicle IDs available for the trip.
#     - **driver_ids**: List of driver IDs available for the trip.
#     """
#     logging_helper.log_info("Accessing - Assign Trip - Endpoint")
#     try:
#         repo=WorkPlanRepository(db)
#         result =repo. create_and_assign_trip_with_location_matching(
#             background_tasks=background_tasks,
#             work_plan_id=work_plan_id,
#             selected_vehicles=vehicle_ids,
#             selected_drivers=driver_ids,
#             db_session=db
#         )
#         #logging_helper.log_audit(db, current_user.id, ActionEnum.SCHEDULE, "Trip", work_plan_id, f"Assign trip with vehicles: {vehicle_ids} and drivers: {driver_ids}")
#         return {"message": result}
#     except HTTPException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.detail)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



from datetime import date
import logging
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Query, status, Path
from sqlalchemy.orm import Session
from auth.dependencies import role_checker
from auth.security import get_current_user
from schemas.user_schemas import UserRead
from db.database import get_db
from repositories.workplan_repository import WorkPlanRepository
from schemas.workplan_schemas import EmployeeModel, EmployeeWithoutWorkPlan, MonthlyWorkPlanSummary, WorkPlanCreate, WorkPlanRead, WorkPlanReadByDateRange, WorkPlanUpdate as WorkPlanUpdateSchema, WorkPlanReschedule as WorkPlanRescheduleSchema
from logging_helpers import logging_helper
from models.all_models import ActionEnum

router = APIRouter()

@router.post("/create", response_model=WorkPlanRead, status_code=status.HTTP_201_CREATED)
async def create_work_plan(
    background_tasks: BackgroundTasks,
    work_plan_data: WorkPlanCreate,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['unit_member', 'technical_lead', 'programs_lead', 'stl', 'hq_staff', 'tenant_admin', 'super_admin']))
):
    """
    Create a new work plan with specified details from the WorkPlanCreate schema.
    Sends asynchronous notifications to relevant stakeholders about the creation of the work plan.
    """
    logging_helper.log_info("Accessing Create Workplan Endpoint...")
    repo = WorkPlanRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin" or current_user.tenancy_id == work_plan_data.tenancy_id:
                new_work_plan = repo.create_work_plan(background_tasks, work_plan_data)
                logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "WorkPlan", new_work_plan.id, new_work_plan.activity_title)
                break
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{current_user.first_name} {current_user.last_name}, you are authorized to create workplan only in your state")
        return new_work_plan
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Creating work plan failed due to: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while creating the work plan.")



# @router.post("/create", response_model=WorkPlanRead, status_code=status.HTTP_201_CREATED)
# async def create_work_plan(
#     background_tasks: BackgroundTasks,
#     work_plan_data: WorkPlanCreate,
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db),
#     _ = Depends(role_checker(['unit_member', 'technical_lead', 'programs_lead', 'stl', 'hq_staff', 'tenant_admin', 'super_admin']))
# ):
#     """
#     Create a new work plan with specified details from the WorkPlanCreate schema.
#     Sends asynchronous notifications to relevant stakeholders about the creation of the work plan.
#     """
#     logging_helper.log_info("Accessing Create Workplan Endpoint...")
#     repo = WorkPlanRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin" or current_user.tenancy_id == work_plan_data.tenancy_id:
#                 new_work_plan = repo.create_work_plan(background_tasks, work_plan_data)
#                 logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "WorkPlan", new_work_plan.id, new_work_plan.activity_title)
#                 break
#             else:
#                 raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{current_user.first_name} {current_user.last_name}, you are authorized to create workplan only in your state")
#         return new_work_plan
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logging.error(f"Creating work plan failed due to: {e}")
#         raise HTTPException(status_code=500, detail="An error occurred while creating the work plan.")

@router.put("/workplans/{work_plan_id}", response_model=WorkPlanRead)
async def update_work_plan(
    work_plan_id: int,
    work_plan_update: WorkPlanUpdateSchema,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))
):
    """
    Updates an existing work plan with provided data. Only the fields that are provided in the request body will be updated.
    """
    logging_helper.log_info("Accessing Update Workplan Endpoint ...")
    try:
        work_plan_repo = WorkPlanRepository(db)

        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                updated_work_plan = work_plan_repo.update_work_plan(work_plan_id=work_plan_id, update_data=work_plan_update)
                if updated_work_plan is None:
                    raise HTTPException(status_code=404, detail="Work plan not found")
                logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "WorkPlan", work_plan_id, work_plan_update.json())
                return updated_work_plan
            else:
                updated_work_plan = work_plan_repo.update_work_plan(work_plan_id=work_plan_id, update_data=work_plan_update, tenancy_id=current_user.tenancy_id)
                if updated_work_plan is None:
                    raise HTTPException(status_code=404, detail="Work plan not found")
                logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "WorkPlan", work_plan_id, work_plan_update.json())
                return updated_work_plan
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workplans/for-approval")
def get_work_plans_for_approval(
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['unit_member', 'programs_lead', 'tenant_admin', 'super_admin']))
):
    """
    Get work plans pending approval for the current week.
    """
    logging_helper.log_info("Accessing Workplan for Approval Endpoints ...")
    plan_repo = WorkPlanRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                work_plans = plan_repo.fetch_pending_work_plans_for_week()
                logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch pending work plans for approval")
                return work_plans
            elif role_dict.name in ['programs_lead', 'technical_lead', 'stl', 'tenant_admin']:
                work_plans = plan_repo.fetch_pending_work_plans_for_week(tenancy_id=current_user.tenancy_id)
                logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch pending work plans for approval")
                return work_plans
            else:
                work_plans = plan_repo.fetch_pending_work_plans_for_week(tenancy_id=current_user.tenancy_id, employee_id=current_user.employee_id)
                logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch pending work plans for approval")
                return work_plans
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/current-week-work-plans/{start_of_week}/{end_of_week}", response_model=list)  # Adjust the response model according to your data structure
def get_current_week_work_plans(
    start_of_week: date = Path(..., description="Start of the week (Monday)"),
    end_of_week: date = Path(..., description="End of the week (Sunday)"),
    vehicle_assigned: Optional[bool] = Query(None, description="Check if the vehicle is already assigned"),
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['unit_member', 'stl', 'technical_lead', 'programs_lead', 'tenant_admin', 'super_admin']))
):
    """
    Get work plans for the current week within a specified date range.
    """
    logging_helper.log_info("Accessing get current week workplan Endpoint ...")
    plan_repo = WorkPlanRepository(db)
    try:
        if 'super_admin' in [role.name for role in current_user.roles]:
            work_plans = plan_repo.fetch_current_week_work_plans_with_status(start_of_week=start_of_week, end_of_week=end_of_week, vehicle_assigned=vehicle_assigned)
            logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch current week work plans")
        elif any(role.name in ['programs_lead', 'technical_lead', 'stl', 'tenant_admin'] for role in current_user.roles):
            work_plans = plan_repo.fetch_current_week_work_plans_with_status(start_of_week=start_of_week, end_of_week=end_of_week, vehicle_assigned=vehicle_assigned, tenancy_id=current_user.tenancy_id)
            logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch current week work plans")
        else:
            work_plans = plan_repo.fetch_current_week_work_plans_with_status(start_of_week=start_of_week, end_of_week=end_of_week, vehicle_assigned=vehicle_assigned, tenancy_id=current_user.tenancy_id, employee_id=current_user.employee_id)
            logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch current week work plans")
        return work_plans
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/workplans/active", response_model=List[WorkPlanRead])
def read_active_work_plans(
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))
):
    """
    Retrieve all active work plans.
    """
    logging_helper.log_info("Accessing Get Active Workplans Endpoint")
    repo = WorkPlanRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                work_plans = repo.get_active_work_plans()
                logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch active work plans")
                return work_plans
            else:
                work_plans = repo.get_active_work_plans(tenancy_id=current_user.tenancy_id)
                logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch active work plans")
                return work_plans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/review/{work_plan_id}", response_model=WorkPlanRead)
def review_work_plan(
    work_plan_id: int,
    review_data: WorkPlanCreate,
    db: Session = Depends(get_db)
):
    """
    Review a work plan by providing a review date and reviewer.
    """
    if not review_data.date_reviewed or not review_data.reviewed_by:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review date and reviewer must be provided",
        )
    logging_helper.log_info("Accessing the -Review Workplan- Endpoint")
    try:
        repo = WorkPlanRepository(db)
        updated_work_plan = repo.review_work_plan(work_plan_id, review_data.reviewed_by, review_data.date_reviewed)
        logging_helper.log_audit(db, review_data.reviewed_by, ActionEnum.REVIEW, "WorkPlan", work_plan_id, f"Reviewed on {review_data.date_reviewed}")
        return updated_work_plan
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Reviewing work plan failed due to: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while reviewing the work plan.")

@router.put("/workplans/{work_plan_id}/approve", status_code=status.HTTP_200_OK)
def approve_work_plan(
    background_tasks: BackgroundTasks,
    work_plan_id: int,
    approver_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))
):
    """
    Approve a work plan with the specified Work Plan ID by a given approver.
    This endpoint schedules background tasks for sending notifications post-approval.
    """
    logging_helper.log_info("Accessing -Approve Workplan- Endpoint")
    repo = WorkPlanRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                approved_work_plan = repo.approve_work_plan(background_tasks, work_plan_id, approver_id)
                logging_helper.log_audit(db, approver_id, ActionEnum.APPROVE, "WorkPlan", work_plan_id, "Approved")
                return approved_work_plan
            else:
                approved_work_plan = repo.approve_work_plan(background_tasks, work_plan_id, approver_id, tenancy_id=current_user.tenancy_id)
                logging_helper.log_audit(db, approver_id, ActionEnum.APPROVE, "WorkPlan", work_plan_id, "Approved")
                return approved_work_plan

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approving work plan failed: {e}")

@router.patch("/workplans/{work_plan_id}/deny", status_code=200)
def deny_work_plan(
    background_tasks: BackgroundTasks,
    work_plan_id: int = Path(..., description="The ID of the work plan to deny"),
    reason: str = Body(..., embed=True),
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))
):
    """
    Deny a work plan, setting its is_denied status to True and recording the reason.
    If the work plan was previously approved, it will reverse the approval.
    """
    logging_helper.log_info("Accessing - Deny Work Plan - Endpoint")
    repo = WorkPlanRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                denied_work_plan = repo.deny_work_plan(background_tasks, work_plan_id, reason)
                logging_helper.log_audit(db, current_user.id, ActionEnum.DENY, "WorkPlan", work_plan_id, f"Denied: {reason}")
                return denied_work_plan
            else:
                denied_work_plan = repo.deny_work_plan(background_tasks, work_plan_id, reason, tenancy_id=current_user.tenancy_id)
                logging_helper.log_audit(db, current_user.id, ActionEnum.DENY, "WorkPlan", work_plan_id, f"Denied: {reason}")
                return denied_work_plan
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workplans/{work_plan_id}/reschedule", status_code=200)
def reschedule_work_plan_endpoint(
    background_tasks: BackgroundTasks,
    work_plan_id: int = Path(..., description="The ID of the work plan to reschedule"),
    reschedule_data: WorkPlanRescheduleSchema = Body(...),
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))
):
    """
    Reschedule a work plan based on its ID.
    """
    logging_helper.log_info("Accessing - Reschedule Workplan - Endpoint")
    work_plan_repository = WorkPlanRepository(db_session=db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                rescheduled_work_plan = work_plan_repository.reschedule_work_plan(background_tasks, work_plan_id, reschedule_data.reason, reschedule_data.new_date)
                logging_helper.log_audit(db, current_user.id, ActionEnum.RESCHEDULE, "WorkPlan", work_plan_id, f"Rescheduled: {reschedule_data.reason} to {reschedule_data.new_date}")
                return rescheduled_work_plan
            else:
                rescheduled_work_plan = work_plan_repository.reschedule_work_plan(background_tasks, work_plan_id, reschedule_data.reason, reschedule_data.new_date, tenancy_id=current_user.tenancy_id)
                logging_helper.log_audit(db, current_user.id, ActionEnum.RESCHEDULE, "WorkPlan", work_plan_id, f"Rescheduled: {reschedule_data.reason} to {reschedule_data.new_date}")
                return rescheduled_work_plan
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/employees/without-workplan", response_model=List[EmployeeWithoutWorkPlan], status_code=status.HTTP_200_OK)
def get_employees_without_work_plan(
    activity_date: date = Query(..., description="The activity date to check for employee availability"),
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['programs_lead', 'unit_member', 'stl', 'technical_lead', 'tenant_admin', 'super_admin']))
):
    """
    Retrieve all employees who are not assigned to any work plan on a given date.
    Handles exceptions such as database errors and unexpected issues.
    """
    logging_helper.log_info("Accessing the - Get Employees Without Workplan - Endpoint")
    repo = WorkPlanRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                employees = repo.list_employees_without_work_plan_on_date(activity_date)
                # logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Employee", None, f"Employees without work plan on {activity_date}")
                return employees
            else:
                employees = repo.list_employees_without_work_plan_on_date(activity_date, tenancy_id=current_user.tenancy_id)
                logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Employee", None, f"Employees without work plan on {activity_date}")
                return employees

        if not employees:
            return []
    except HTTPException as http_exc:  # Handles HTTP errors thrown manually in the repository
        raise http_exc
    except Exception as e:  # Generic exception for any other errors
        logging.error(f"Unexpected error occurred: {e}")  # Ensure you have logging configured
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request.")

@router.put("/update-workplan/{work_plan_id}", response_model=WorkPlanUpdateSchema)
def update_work_plan_if_pending(
    work_plan_id: int,
    updates: WorkPlanUpdateSchema,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(["unit_member", 'programs_lead', 'tenant_admin', 'super_admin']))
):
    """
    Update a work plan only if its status is 'Pending'.
    :param work_plan_id: ID of the work plan to update.
    :param updates: Data to update the work plan with.
    :param db: Database session dependency.
    :return: Updated work plan data.
    """
    logging_helper.log_info("Accessing - Update Workplan if Pending - Endpoint")
    work_plan_repo = WorkPlanRepository(db_session=db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                updated_work_plan = work_plan_repo.update_work_plan_if_pending(work_plan_id=work_plan_id, updates=updates.dict(exclude_unset=True))
                logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "WorkPlan", work_plan_id, f"Update if pending: {updates.json()}")
                return updated_work_plan
            elif role_dict.name in ["programs_lead", "tenant_admin"]:
                updated_work_plan = work_plan_repo.update_work_plan_if_pending(work_plan_id=work_plan_id, updates=updates.dict(exclude_unset=True), tenancy_id=current_user.tenancy_id)
                logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "WorkPlan", work_plan_id, f"Update if pending: {updates.json()}")
                return updated_work_plan
            else:
                updated_work_plan = work_plan_repo.update_work_plan_if_pending(work_plan_id=work_plan_id, updates=updates.dict(exclude_unset=True), tenancy_id=current_user.tenancy_id, user_id=current_user.id)
                logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "WorkPlan", work_plan_id, f"Update if pending: {updates.json()}")
                return updated_work_plan
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workplans/employees", response_model=List[EmployeeModel])
def fetch_employees_associated_with_work_plan(
    workplan_code: Optional[str] = None,
    initiator_name: Optional[str] = None,
    activity_date: Optional[date] = None,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))
):
    """
    Fetch employees associated with a specific work plan by code, initiator name, or activity date.
    """
    logging_helper.log_info("Accessing - Fetch Employee Associated with Workplan - Endpoint")
    repository = WorkPlanRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                employees = repository.fetch_employees_by_work_plan(workplan_code, initiator_name, activity_date)
                # logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Employee", None, "Fetch employees associated with work plan")
                return employees
            else:
                employees = repository.fetch_employees_by_work_plan(workplan_code, initiator_name, activity_date, tenancy_id=current_user.tenancy_id)
                logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Employee", None, "Fetch employees associated with work plan")
                return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workplans/approved-weekly/")
def get_approved_weekly_workplans(
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))
):
    """
    Retrieve approved work plans for the current week.
    """
    logging_helper.log_info("Accessing - Get Approved Weekly Workplan - Endpoint")
    workplan_repo = WorkPlanRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                approved_workplans = workplan_repo.fetch_approved_weekly_work_plans()
                # logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch approved weekly work plans")
                return approved_workplans
            else:
                approved_workplans = workplan_repo.fetch_approved_weekly_work_plans(tenancy_id=current_user.tenancy_id)
                # logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, "Fetch approved weekly work plans")
                return approved_workplans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workplans/approved/", response_model=WorkPlanRead)
def fetch_approved_work_plan(
    identifier: str,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))
):
    """
    Fetch an approved work plan by its ID or work plan code.
    """
    logging_helper.log_info("Accessing - Fetch Approved Workplan - Endpoint")
    work_plan_repo = WorkPlanRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                work_plan = work_plan_repo.fetch_approved_work_plan_by_code_or_id(identifier)
                if work_plan is None:
                    raise HTTPException(status_code=404, detail="Approved work plan not found")
                # logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", identifier, "Fetch approved work plan by ID or code")
                return work_plan
            else:
                work_plan = work_plan_repo.fetch_approved_work_plan_by_code_or_id(identifier, tenancy_id=current_user.tenancy_id)
                if work_plan is None:
                    raise HTTPException(status_code=404, detail="Approved work plan not found")
                # logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", identifier, "Fetch approved work plan by ID or code")
                return work_plan
    except Exception as e:
        raise HTTPException(status_code=404, detail="Approved work plan not found")

@router.get("/work-plans/approved/by-entity/{entity_type}")
def fetch_approved_work_plan_by_entity(
    entity_type: str = Path(..., description="The type of entity (unit, srt, department, thematicarea)"),
    entity_name: str = Query(..., description="The name of the entity (SRT A, SRT B, SI, Admin, HI)"),
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))
):
    """
    Fetches an approved work plan based on the provided entity type and name.
    """
    logging_helper.log_info("Accessing - Fetch Approved Workplan by Entity - Endpoint")
    work_plan_repo = WorkPlanRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                result = work_plan_repo.fetch_approved_work_plan_by_entity(entity_type, entity_name)
                if result is None:
                    raise HTTPException(status_code=404, detail="Approved work plan not found")
                # logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, f"Fetch approved work plan by entity: {entity_type} - {entity_name}")
                return result
            else:
                result = work_plan_repo.fetch_approved_work_plan_by_entity(entity_type, entity_name, tenancy_id=current_user.tenancy_id)
                if result is None:
                    raise HTTPException(status_code=404, detail="Approved work plan not found")
                # logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, f"Fetch approved work plan by entity: {entity_type} - {entity_name}")
                return result
    except Exception as e:
        raise HTTPException(status_code=404, detail="No approved work plan found for the specified entity")

@router.get("/workplans/monthly-summary/{year}/{month}", response_model=MonthlyWorkPlanSummary)
def get_monthly_work_plan_summary(
    year: int,
    month: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))
):
    """
    Retrieve a summary of work plans for a given month and year.
    """
    logging_helper.log_info("Accessing - Get Monthly Workplan Summary - Endpoint")
    repo = WorkPlanRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                summary = repo.fetch_monthly_work_plan_summary(year, month)
                # logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, f"Fetch monthly work plan summary for {month}/{year}")
            else:
                summary = repo.fetch_monthly_work_plan_summary(year, month, tenancy_id=current_user.tenancy_id)
                # logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, f"Fetch monthly work plan summary for {month}/{year}")
            return summary
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/workplans/by-date-range/", response_model=List[WorkPlanReadByDateRange])
def get_workplans_by_date_range(
    start_date: date,
    end_date: date,
    status: Optional[str] = Query(None, description="Filter by status (e.g., 'Approved', 'Pending')"),
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))
):
    """
    Endpoint to fetch work plans between two dates, including details about associated employees and optionally filtering by status.
    """
    logging_helper.log_info("Accessing - Get Workplan by Date Range - Endpoint")
    try:
        work_plan_repo = WorkPlanRepository(db)
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                work_plans = work_plan_repo.fetch_workplans_by_date_range(start_date, end_date, status)
                # logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, f"Fetch work plans by date range: {start_date} to {end_date}")
            else:
                work_plans = work_plan_repo.fetch_workplans_by_date_range(start_date, end_date, status, tenancy_id=current_user.tenancy_id)
                # logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, f"Fetch work plans by date range: {start_date} to {end_date}")
            return work_plans
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving work plans: {str(e)}")

@router.get("/workplans/by-logistics/{logistics_requirement}")
def get_work_plans_by_logistics(
    logistics_requirement: str,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _ = Depends(role_checker(['programs_lead', 'tenant_admin', 'super_admin']))
):
    """
    Retrieves work plans based on logistics requirements, including associated sources, employees,
    locations, and sites. This endpoint will filter work plans by the specified logistics requirement.
    
    - **logistics_requirement**: string name of the logistics requirement to filter work plans by
    """
    logging_helper.log_info("Accessing - Get Workplans by Logistics - Endpoint")
    try:
        repo = WorkPlanRepository(db)
        work_plans = repo.get_work_plans_by_logistics(logistics_requirement, tenancy_id=current_user.tenancy_id)
        if not work_plans:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No work plan found with the specified logistics requirement")
        # logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "WorkPlan", None, f"Fetch work plans by logistics requirement: {logistics_requirement}")
        return work_plans
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/assign-trip/{work_plan_id}")
def assign_trip(
    work_plan_id: int,
    vehicle_ids: List[int],
    driver_ids: List[int],
    background_tasks: BackgroundTasks,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Assign vehicles and drivers to a trip for a specific work plan.
    Requires lists of vehicle IDs and driver IDs to select from.

    - **work_plan_id**: The ID of the work plan to create trips for.
    - **vehicle_ids**: List of vehicle IDs available for the trip.
    - **driver_ids**: List of driver IDs available for the trip.
    """
    logging_helper.log_info("Accessing - Assign Trip - Endpoint")
    try:
        repo = WorkPlanRepository(db)
        result = repo.create_and_assign_trip_with_location_matching(
            background_tasks=background_tasks,
            work_plan_id=work_plan_id,
            selected_vehicles=vehicle_ids,
            selected_drivers=driver_ids,
            db_session=db
        )
        # logging_helper.log_audit(db, current_user.id, ActionEnum.SCHEDULE, "Trip", work_plan_id, f"Assign trip with vehicles: {vehicle_ids} and drivers: {driver_ids}")
        return {"message": result}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

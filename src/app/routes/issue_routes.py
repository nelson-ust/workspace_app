
# from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
# from sqlalchemy.orm import Session
# from auth.dependencies import role_checker
# from auth.security import get_current_user
# from schemas.user_schemas import UserRead
# from schemas.issue_schemas import IssueCreate, IssueUpdate, IssueLogClosure
# from db.database import get_db
# from repositories.issue_log_repository import IssueRepository
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# from datetime import datetime, date
# from logging_helpers import logging_helper


# limiter = Limiter(key_func=get_remote_address)
# router = APIRouter()

# @router.post("/issue_log") #
# @limiter.limit("5/minute")
# async def create_issue_log(request:Request, background_tasks:BackgroundTasks, issue_data:IssueCreate, db: Session = Depends(get_db),
#     _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
#     current_user: UserRead = Depends(get_current_user)
# ):
#     "The is the main Issue Log Module"
#     try:
#         repo = IssueRepository(db_session=db)
#         logging_helper.log_info("Accessing - create IssueLog - Endpoint")
#          #super_admin check
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin" or current_user.tenancy_id == issue_data.tenancy_id:
#                 # Check Date Reported
#                 if issue_data.date_reported != datetime.now().date():
#                     raise  HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Date Reported must be today's date")
#                 new_issue = repo.create_issue_log(background_tasks=background_tasks, issue_create_data=issue_data)
#                 break
#             else:
#                 raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{current_user.first_name} {current_user.last_name}, your authorized to create issue for only your state")
#         return new_issue
        
#     except HTTPException as err:
#         logging_helper.log_error(f"{str(err)}")
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Error creating issue due {str(err)} ")
    

# @router.put("/issue_log/{issue_log_id}") #
# @limiter.limit("5/minute")
# async def update_issue_log(request:Request, background_tasks:BackgroundTasks, issue_log_id:int, issue_update_data:IssueUpdate, db: Session = Depends(get_db),
#     _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
#     current_user: UserRead = Depends(get_current_user)
# ):
#     try:
#         repo = IssueRepository(db_session=db)
#         logging_helper.log_info("Accessing - Update IssueLog - Endpoint")
#         #super_admin check
#         for role_dict in current_user.roles:
#             if role_dict.name in ["super_admin"]:
#                 issue_log = repo.update_pending_issue_log(background_tasks=background_tasks, issue_log_id=issue_log_id, issue_update_data=issue_update_data)
#             else:
#                 issue_log = repo.update_pending_issue_log(background_tasks=background_tasks, issue_log_id=issue_log_id, issue_update_data=issue_update_data,
#                                                   tenancy_id=current_user.tenancy_id, reported_by_id=current_user.employee_id)
#             return issue_log
        
#     except HTTPException as err:
#         logging_helper.log_error(f"{str(err)}")
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Error updating issue due {str(err)} ")
    

# @router.get("/issue_log/{issue_log_id}") #
# @limiter.limit("5/minute")
# async def get_all_status_issue_log_by_id(request:Request, issue_log_id:int, db: Session = Depends(get_db),
#     _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
#     current_user: UserRead = Depends(get_current_user)
# ):
#     try:
#         issue_repo = IssueRepository(db_session=db)
#         logging_helper.log_info("Accessing - Get All Status IssueLog By ID - Endpoint")
#         for role_dict in current_user.roles:
#             if role_dict.name in ["super_admin"]:
#                 issue_log = issue_repo.get_all_status_issue_log_by_id(issue_log_id=issue_log_id)
#             elif role_dict.name in ["program_lead", "tenancy_admin"]:
#                 issue_log = issue_repo.get_all_status_issue_log_by_id(issue_log_id=issue_log_id, tenancy_id=current_user.tenancy_id)
#             else:
#                 issue_log = issue_repo.get_all_status_issue_log_by_id(issue_log_id=issue_log_id, tenancy_id=current_user.tenancy_id, reported_by_id=current_user.employee_id)
#             return issue_log
#     except HTTPException as err:
#         logging_helper.log_error(f"{str(err)}")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")
    

# @router.get("/issue_log/")#
# @limiter.limit("5/minute")
# async def get_all_status_all_issue_log(request:Request, skip:int=0, limit:int=100, db: Session = Depends(get_db),
#     _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
#     current_user: UserRead = Depends(get_current_user)
# ):
#     try:
#         issue_repo = IssueRepository(db_session=db)
#         logging_helper.log_info("Accessing - Get All Status All IssueLog - Endpoint")
#         for role_dict in current_user.roles:
#             if role_dict.name in ["super_admin"]:
#                 issue_log = issue_repo.get_all_status_all_issue_log(skip=skip, limit=limit)
#             elif role_dict.name in ["program_lead", "tenancy_admin"]:
#                 issue_log = issue_repo.get_all_status_all_issue_log(skip=skip, limit=limit, tenancy_id=current_user.tenancy_id)
#             else:
#                 issue_log = issue_repo.get_all_status_all_issue_log(skip=skip, limit=limit, tenancy_id=current_user.tenancy_id, reported_by_id=current_user.employee_id)
#             return issue_log
#     except HTTPException as err:
#         logging_helper.log_error(f"{str(err)}")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


# @router.get("/issue_log/{issue_log_id}/pending") #
# @limiter.limit("5/minute")
# async def get_pending_issue_log_by_id(request:Request, issue_log_id:int, db: Session = Depends(get_db),
#     _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
#     current_user: UserRead = Depends(get_current_user)
# ):
#     try:
#         issue_repo = IssueRepository(db_session=db)
#         logging_helper.log_info("Accessing - Get Pending IssueLog By ID - Endpoint")
#         for role_dict in current_user.roles:
#             if role_dict.name in ["super_admin"]:
#                 issue_log = issue_repo.get_pending_issue_log_by_id(issue_log_id=issue_log_id)
#             elif role_dict.name in ["program_lead", "tenancy_admin"]:
#                 issue_log = issue_repo.get_pending_issue_log_by_id(issue_log_id=issue_log_id, tenancy_id=current_user.tenancy_id)
#             else:
#                 issue_log = issue_repo.get_pending_issue_log_by_id(issue_log_id=issue_log_id, tenancy_id=current_user.tenancy_id, reported_by_id=current_user.employee_id)
#             return issue_log
#     except HTTPException as err:
#         logging_helper.log_error(f"{str(err)}")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")
    

# @router.get("/issue_log/pending/all")#
# @limiter.limit("5/minute")
# async def get_pending_issue_log_all(request:Request, skip:int=0, limit:int=100, db: Session = Depends(get_db),
#     _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
#     current_user: UserRead = Depends(get_current_user)
# ):
#     try:
#         issue_repo = IssueRepository(db_session=db)
#         logging_helper.log_info("Accessing - Get All Pending IssueLog - Endpoint")
#         for role_dict in current_user.roles:
#             if role_dict.name in ["super_admin"]:
#                 issue_log = issue_repo.get_pending_issue_log_all(skip=skip, limit=limit)
#             elif role_dict.name in ["program_lead", "tenancy_admin"]:
#                 issue_log = issue_repo.get_pending_issue_log_all(skip=skip, limit=limit, tenancy_id=current_user.tenancy_id)
#             else:
#                 issue_log = issue_repo.get_pending_issue_log_all(skip=skip, limit=limit, tenancy_id=current_user.tenancy_id, reported_by_id=current_user.employee_id)
#             return issue_log
#     except HTTPException as err:
#         logging_helper.log_error(f"{str(err)}")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")
    

# @router.delete("/issue_log/{issue_log_id}/hard_delete") #
# @limiter.limit("5/minute")
# async def delete_issue_by_id(request:Request, issue_log_id:int, db: Session = Depends(get_db),
#     _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
#     current_user: UserRead = Depends(get_current_user)
# ):
#     try:
#         issue_repo = IssueRepository(db_session=db)
#         logging_helper.log_info("Accessing - Hard Delete IssueLog - Endpoint")
#         for role_dict in current_user.roles:
#             if role_dict.name in ["super_admin"]:
#                 issue_log = issue_repo.delete_issue_by_id(issue_log_id=issue_log_id)
#                 break
#             else:
#                 issue_log = issue_repo.delete_issue_by_id(issue_log_id=issue_log_id, tenancy_id=current_user.tenancy_id)
#                 break
#         return issue_log
#     except HTTPException as err:
#         logging_helper.log_error(f"{str(err)}")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")
    

# @router.post("/issue_log/{issue_log_id}/soft_delete") #
# @limiter.limit("5/minute")
# async def soft_delete_issue_by_id(request:Request, issue_log_id:int, db: Session = Depends(get_db),
#     _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
#     current_user: UserRead = Depends(get_current_user)
# ):
#     try:
#         issue_repo = IssueRepository(db_session=db)
#         logging_helper.log_info("Accessing - Soft Delete IssueLog - Endpoint")
#         for role_dict in current_user.roles:
#             if role_dict.name in ["super_admin"]:
#                 issue_log = issue_repo.soft_delete_issue_by_id(issue_log_id=issue_log_id)
#                 break
#             else:
#                 issue_log = issue_repo.soft_delete_issue_by_id(issue_log_id=issue_log_id, tenancy_id=current_user.tenancy_id)
#                 break
#         return issue_log
#     except HTTPException as err:
#         logging_helper.log_error(f"{str(err)}")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")
    

# @router.post("/issue_log/{issue_log_id}/restore") #
# @limiter.limit("5/minute")
# async def restore_issue_by_id(request:Request, issue_log_id:int, db: Session = Depends(get_db),
#     _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
#     current_user: UserRead = Depends(get_current_user)
# ):
#     try:
#         issue_repo = IssueRepository(db_session=db)
#         logging_helper.log_info("Accessing - Restore IssueLog - Endpoint")
#         for role_dict in current_user.roles:
#             if role_dict.name in ["super_admin"]:
#                 issue_log = issue_repo.restore_issue_by_id(issue_log_id=issue_log_id)
#                 break
#             else:
#                 issue_log = issue_repo.restore_issue_by_id(issue_log_id=issue_log_id, tenancy_id=current_user.tenancy_id)
#                 break
#         return issue_log
#     except HTTPException as err:
#         logging_helper.log_error(f"{str(err)}")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")
    

# @router.post("/issue_log/{issue_log_id}/closure") #
# @limiter.limit("5/minute")
# async def close_completed_issue_log(request:Request, background_tasks:BackgroundTasks, issue_log_id:int, issue_close_data:IssueLogClosure, db: Session = Depends(get_db),
#     _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
#     current_user: UserRead = Depends(get_current_user)
# ):
#     try:
#         issue_repo = IssueRepository(db_session=db)
#         logging_helper.log_info("Accessing - Closure IssueLog - Endpoint")
#         for role_dict in current_user.roles:
#             if role_dict.name in ["super_admin"]:

#                 # Check Closure Date
#                 if issue_close_data.close_date != datetime.now().date():
#                     raise  HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Close Date must be today's date")
                
#                 issue_log = issue_repo.close_completed_issue_log(background_tasks=background_tasks, issue_log_id=issue_log_id,
#                                                                  issue_close_data=issue_close_data)
#                 break
#             else:
#                 # Check Closure Date
#                 if issue_close_data.close_date != datetime.now().date():
#                     raise  HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Close Date must be today's date")
                
#                 issue_log = issue_repo.close_completed_issue_log(background_tasks=background_tasks, issue_log_id=issue_log_id,
#                                                                  issue_close_data=issue_close_data, tenancy_id=current_user.tenancy_id)
#                 break
#         return issue_log

#     except HTTPException as err:
#         logging_helper.log_error(f"{str(err)}")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")
    



from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from sqlalchemy.orm import Session
from auth.dependencies import role_checker
from auth.security import get_current_user
from schemas.user_schemas import UserRead
from schemas.issue_schemas import IssueCreate, IssueUpdate, IssueLogClosure
from db.database import get_db
from repositories.issue_log_repository import IssueRepository
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime, date
from logging_helpers import logging_helper


limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/issue_log") #
@limiter.limit("5/minute")
async def create_issue_log(request:Request, background_tasks:BackgroundTasks, issue_data:IssueCreate, db: Session = Depends(get_db),
    _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
    current_user: UserRead = Depends(get_current_user)
):
    "The is the main Issue Log Module"
    try:
        repo = IssueRepository(db_session=db)
        logging_helper.log_info("Accessing - create IssueLog - Endpoint")
        
         #super_admin check
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin" or current_user.tenancy_id == issue_data.tenancy_id:
                new_issue = repo.create_issue_log(background_tasks=background_tasks, issue_create_data=issue_data)
                break
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{current_user.first_name} {current_user.last_name}, your authorized to create issue for only your state")
        return new_issue
        
    except HTTPException as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Error creating issue due {str(err)} ")
    

@router.put("/issue_log/{issue_log_id}") #
@limiter.limit("5/minute")
async def update_issue_log(request:Request, background_tasks:BackgroundTasks, issue_log_id:int, issue_update_data:IssueUpdate, db: Session = Depends(get_db),
    _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
    current_user: UserRead = Depends(get_current_user)
):
    try:
        repo = IssueRepository(db_session=db)
        logging_helper.log_info("Accessing - Update IssueLog - Endpoint")
        #super_admin check
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                issue_log = repo.update_pending_issue_log(background_tasks=background_tasks, issue_log_id=issue_log_id, issue_update_data=issue_update_data)
            else:
                issue_log = repo.update_pending_issue_log(background_tasks=background_tasks, issue_log_id=issue_log_id, issue_update_data=issue_update_data,
                                                  tenancy_id=current_user.tenancy_id, reported_by_id=current_user.employee_id)
            return issue_log
        
    except HTTPException as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Error updating issue due {str(err)} ")
    

@router.get("/issue_log/{issue_log_id}") #
@limiter.limit("5/minute")
async def get_all_status_issue_log_by_id(request:Request, issue_log_id:int, db: Session = Depends(get_db),
    _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
    current_user: UserRead = Depends(get_current_user)
):
    try:
        issue_repo = IssueRepository(db_session=db)
        logging_helper.log_info("Accessing - Get All Status IssueLog By ID - Endpoint")
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                issue_log = issue_repo.get_all_status_issue_log_by_id(issue_log_id=issue_log_id)
            elif role_dict.name in ["program_lead", "tenancy_admin"]:
                issue_log = issue_repo.get_all_status_issue_log_by_id(issue_log_id=issue_log_id, tenancy_id=current_user.tenancy_id)
            else:
                issue_log = issue_repo.get_all_status_issue_log_by_id(issue_log_id=issue_log_id, tenancy_id=current_user.tenancy_id, reported_by_id=current_user.employee_id)
            return issue_log
    except HTTPException as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")
    

@router.get("/issue_log/")#
@limiter.limit("5/minute")
async def get_all_status_all_issue_log(request:Request, skip:int=0, limit:int=100, db: Session = Depends(get_db),
    _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
    current_user: UserRead = Depends(get_current_user)
):
    try:
        issue_repo = IssueRepository(db_session=db)
        logging_helper.log_info("Accessing - Get All Status All IssueLog - Endpoint")
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                issue_log = issue_repo.get_all_status_all_issue_log(skip=skip, limit=limit)
            elif role_dict.name in ["program_lead", "tenancy_admin"]:
                issue_log = issue_repo.get_all_status_all_issue_log(skip=skip, limit=limit, tenancy_id=current_user.tenancy_id)
            else:
                issue_log = issue_repo.get_all_status_all_issue_log(skip=skip, limit=limit, tenancy_id=current_user.tenancy_id, reported_by_id=current_user.employee_id)
            return issue_log
    except HTTPException as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")


@router.get("/issue_log/{issue_log_id}/pending") #
@limiter.limit("5/minute")
async def get_pending_issue_log_by_id(request:Request, issue_log_id:int, db: Session = Depends(get_db),
    _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
    current_user: UserRead = Depends(get_current_user)
):
    try:
        issue_repo = IssueRepository(db_session=db)
        logging_helper.log_info("Accessing - Get Pending IssueLog By ID - Endpoint")
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                issue_log = issue_repo.get_pending_issue_log_by_id(issue_log_id=issue_log_id)
            elif role_dict.name in ["program_lead", "tenancy_admin"]:
                issue_log = issue_repo.get_pending_issue_log_by_id(issue_log_id=issue_log_id, tenancy_id=current_user.tenancy_id)
            else:
                issue_log = issue_repo.get_pending_issue_log_by_id(issue_log_id=issue_log_id, tenancy_id=current_user.tenancy_id, reported_by_id=current_user.employee_id)
            return issue_log
    except HTTPException as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")
    

@router.get("/issue_log/pending/all")#
@limiter.limit("5/minute")
async def get_pending_issue_log_all(request:Request, skip:int=0, limit:int=100, db: Session = Depends(get_db),
    _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
    current_user: UserRead = Depends(get_current_user)
):
    try:
        issue_repo = IssueRepository(db_session=db)
        logging_helper.log_info("Accessing - Get All Pending IssueLog - Endpoint")
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                issue_log = issue_repo.get_pending_issue_log_all(skip=skip, limit=limit)
            elif role_dict.name in ["program_lead", "tenancy_admin"]:
                issue_log = issue_repo.get_pending_issue_log_all(skip=skip, limit=limit, tenancy_id=current_user.tenancy_id)
            else:
                issue_log = issue_repo.get_pending_issue_log_all(skip=skip, limit=limit, tenancy_id=current_user.tenancy_id, reported_by_id=current_user.employee_id)
            return issue_log
    except HTTPException as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")
    

@router.delete("/issue_log/{issue_log_id}/hard_delete") #
@limiter.limit("5/minute")
async def delete_issue_by_id(request:Request, issue_log_id:int, db: Session = Depends(get_db),
    _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
    current_user: UserRead = Depends(get_current_user)
):
    try:
        issue_repo = IssueRepository(db_session=db)
        logging_helper.log_info("Accessing - Hard Delete IssueLog - Endpoint")
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                issue_log = issue_repo.delete_issue_by_id(issue_log_id=issue_log_id)
                break
            else:
                issue_log = issue_repo.delete_issue_by_id(issue_log_id=issue_log_id, tenancy_id=current_user.tenancy_id)
                break
        return issue_log
    except HTTPException as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")
    

@router.post("/issue_log/{issue_log_id}/soft_delete") #
@limiter.limit("5/minute")
async def soft_delete_issue_by_id(request:Request, issue_log_id:int, db: Session = Depends(get_db),
    _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
    current_user: UserRead = Depends(get_current_user)
):
    try:
        issue_repo = IssueRepository(db_session=db)
        logging_helper.log_info("Accessing - Soft Delete IssueLog - Endpoint")
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                issue_log = issue_repo.soft_delete_issue_by_id(issue_log_id=issue_log_id)
                break
            else:
                issue_log = issue_repo.soft_delete_issue_by_id(issue_log_id=issue_log_id, tenancy_id=current_user.tenancy_id)
                break
        return issue_log
    except HTTPException as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")
    

@router.post("/issue_log/{issue_log_id}/restore") #
@limiter.limit("5/minute")
async def restore_issue_by_id(request:Request, issue_log_id:int, db: Session = Depends(get_db),
    _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
    current_user: UserRead = Depends(get_current_user)
):
    try:
        issue_repo = IssueRepository(db_session=db)
        logging_helper.log_info("Accessing - Restore IssueLog - Endpoint")
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                issue_log = issue_repo.restore_issue_by_id(issue_log_id=issue_log_id)
                break
            else:
                issue_log = issue_repo.restore_issue_by_id(issue_log_id=issue_log_id, tenancy_id=current_user.tenancy_id)
                break
        return issue_log
    except HTTPException as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")
    

@router.post("/issue_log/{issue_log_id}/closure") #
@limiter.limit("5/minute")
async def close_completed_issue_log(request:Request, background_tasks:BackgroundTasks, issue_log_id:int, issue_close_data:IssueLogClosure, db: Session = Depends(get_db),
    _=Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])),
    current_user: UserRead = Depends(get_current_user)
):
    try:
        issue_repo = IssueRepository(db_session=db)
        logging_helper.log_info("Accessing - Closure IssueLog - Endpoint")
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                issue_log = issue_repo.close_completed_issue_log(background_tasks=background_tasks, issue_log_id=issue_log_id,
                                                                 issue_close_data=issue_close_data)
                break
            else:
                # Check Closure Date
                if issue_close_data.close_date != datetime.now().date():
                    raise  HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Close Date must be today's date")
                
                issue_log = issue_repo.close_completed_issue_log(background_tasks=background_tasks, issue_log_id=issue_log_id,
                                                                 issue_close_data=issue_close_data, tenancy_id=current_user.tenancy_id)
                break
        return issue_log

    except HTTPException as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured {err.detail}")
    

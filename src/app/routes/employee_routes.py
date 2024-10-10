
# #routes/employee_routes.py
# import json
# from fastapi import APIRouter, Depends, HTTPException, Query, status
# from typing import Any, Dict, List, Optional
# from sqlalchemy.orm import Session

# from db.database import get_db
# from models.all_models import ActionEnum, AuditLog
# from schemas.employee_schemas import EmployeeReadWithUserID, SRTAssignment, EmployeeCreate, EmployeeRead, EmployeeUpdate,Department_and_Unit_Update
# from auth.dependencies import role_checker
# from repositories.employee_repository import EmployeeRepository
# from schemas.user_schemas import UserRead
# from auth.security import get_current_user
# from logging_helpers import logging_helper

# router = APIRouter()

# @router.post("/employees/", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
# async def create_employee(employee_data: EmployeeCreate, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Create Employee - Endpoint")
#     employee_repo = EmployeeRepository(db)
#     try:
#         # Attempt to create a new employee record
#         #super_admin and tenancy check
#         for role_dict in current_user.roles:
#             if role_dict.name == "super_admin" or current_user.tenancy_id == employee_data.tenancy_id:
#                 new_employee = employee_repo.create_employee(employee_data)
#                 break
#             else:
#                 raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{current_user.first_name} {current_user.last_name}, your authorized to create employee for only your state !!!")
#     except HTTPException as e:
#         # If an HTTPException is raised within the repository, re-raise it to be handled by FastAPI
#         raise e
#     except Exception as e:
#         # Catch any other exceptions and return a generic HTTP 500 error
#         raise HTTPException(status_code=500, detail=f"An error occurred while creating the employee: {str(e)}")

#     return new_employee


# @router.put("/employees/{employee_id}/", response_model=EmployeeRead)
# async def update_employee(employee_id: int, employee_update: EmployeeUpdate, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Update Employee - Endpoint")
#     employee_repo = EmployeeRepository(db)
#     try:
#         for role_dict in current_user.roles:
#                 if role_dict.name == "super_admin":
#                     employee = employee_repo.update_employee(employee_id=employee_id, employee_data=employee_update)
#                     if not employee:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} is not found")
#                     return employee
#                 else:
#                     employee = employee_repo.update_employee(employee_id=employee_id, employee_data=employee_update, tenancy_id=current_user.tenancy_id)
#                     if not employee:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} is not found")
#                     return employee
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"{str(e)}")


# @router.get("/employees/", response_model=List[EmployeeReadWithUserID])
# async def list_employees(
#     limit: int = Query(100, description="Maximum number of results to return"),
#     cursor: Optional[int] = Query(None, description="ID of the last item from the previous result set"),
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db),
#     _=Depends(role_checker(['hq_staff','unit_member','tenant_admin','super_admin']))
# ):
#     logging_helper.log_info("Accessing - List Employee - Endpoint")
#     employee_repo = EmployeeRepository(db)
#     try:
#         for role_dict in current_user.roles:
#             if role_dict.name in ["super_admin", "hq_backstop"]:
#                 employees = employee_repo.get_all_employees(limit=limit, cursor=cursor)
#                 return employees
#             else:
#                 employees = employee_repo.get_all_employees(limit=limit, cursor=cursor, tenancy_id=current_user.tenancy_id)
#                 return employees
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"{str(e)}")

# @router.get("/employees/{employee_id}/", response_model=EmployeeRead)
# async def get_employee(employee_id: int, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['unit_member','hq_backstop','tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Get Employee - Endpoint")
#     employee_repo = EmployeeRepository(db)
#     try:
#         for role_dict in current_user.roles:
#                 if role_dict.name in ["super_admin", "hq_staff"]:
#                     employee = employee_repo.get_employee_by_id(employee_id=employee_id)
#                     if not employee:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist")
#                     return employee
#                 else:
#                     employee = employee_repo.get_employee_by_id(employee_id=employee_id, tenancy_id=current_user.tenancy_id)
#                     if not employee:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or does not belong to your state")
#                     return employee
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"{str(e)}")


# @router.delete("/employees/{employee_id}/")
# async def delete_employee(employee_id: int, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Delete Employee - Endpoint")
#     employee_repo = EmployeeRepository(db)
#     try:
#         for role_dict in current_user.roles:
#                 if role_dict.name == "super_admin":
#                     employee = employee_repo.delete_employee(employee_id=employee_id)
#                     if not employee:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist")
#                     return f'"detail": "Employee with id {employee_id} has been deleted successfully"'
#                 else:
#                     employee = employee_repo.delete_employee(employee_id=employee_id, tenancy_id=current_user.tenancy_id)
#                     if not employee:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or does not belong to your state")
#                     return f'"detail": "Employee with id {employee_id} has been deleted successfully"'
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"{str(e)}")


# @router.get("/employees/by-department/{department_name}/", response_model=List[EmployeeRead])
# async def get_employees_by_department(department_name: str, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['unit_member','hq_backstop','tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Get Employees by Department - Endpoint")
#     employee_repo = EmployeeRepository(db)
#     try:
#         for role_dict in current_user.roles:
#                 if role_dict.name in ["super_admin", "hq_staff"]:
#                     employee = employee_repo.get_employees_by_department_name(department_name=department_name.upper())
#                     if len(employee) ==0:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Please check the department name supplied")
#                     return employee
#                 else:
#                     employee = employee_repo.get_employees_by_department_name(department_name=department_name.upper(), tenancy_id=current_user.tenancy_id)
#                     if len(employee) ==0:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Please check the department name supplied")
#                     return employee
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"{str(e)}")


# @router.get("/employees/by-srt/{srt_name}/",response_model=List[EmployeeRead])
# async def get_employee_by_srt(srt_name:str, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['unit_member','tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Get Employee by SRT - Endpoint")
#     employee_repo=EmployeeRepository(db)
#     try:
#         for role_dict in current_user.roles:
#                 if role_dict.name in ["super_admin", "hq_backstop"]:
#                     employee = employee_repo.find_employees_by_srt_name(srt_name=srt_name.upper())
#                     if not employee:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Please check the SRT name supplied")
#                     return employee
#                 else:
#                     employee = employee_repo.find_employees_by_srt_name(srt_name=srt_name.upper(), tenancy_id=current_user.tenancy_id)
#                     if not employee:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Please check the SRT name supplied")
#                     return employee
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"{str(e)}")
    
# #get_employees_by_unit_name

# @router.get("/employees/by-unit/{unit_name}/", response_model=List[EmployeeRead])
# async def get_employee_by_unit(unit_name:str, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['unit_member','tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Get Employee by Unit - Endpoint")
#     employee_repo=EmployeeRepository(db)
#     try:
#         for role_dict in current_user.roles:
#                 if role_dict.name in ["super_admin", "hq_backstop"]:
#                     employee = employee_repo.get_employees_by_unit_name(unit_name=unit_name.upper())
#                     if not employee:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Please check the Unit name supplied")
#                     return employee
#                 else:
#                     employee = employee_repo.get_employees_by_unit_name(unit_name=unit_name.upper(), tenancy_id=current_user.tenancy_id)
#                     if not employee:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Please check the Unit name supplied")
#                     return employee
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"{str(e)}")


# @router.post("/employees/{employee_id}/assign-srts", status_code=status.HTTP_200_OK)
# async def assign_employee_to_srts(
#     employee_id: int, 
#     srt_assignment: SRTAssignment, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Assign Employee to SRT - Endpoint")
#     employee_repo = EmployeeRepository(db)
#     try:
#         for role_dict in current_user.roles:
#                 if role_dict.name == "super_admin":
#                     result = employee_repo.assign_employee_to_srt(employee_id, srt_assignment.srt_ids)
#                     if not result:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist")
#                 else:
#                     result = employee_repo.assign_employee_to_srt(employee_id, srt_assignment.srt_ids, tenancy_id=current_user.tenancy_id)
#                     if not result:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or does not belong to your state")
#         return {"message": "Feedback", "data": result}
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    

# @router.get("/employees/no-department", response_model=List[EmployeeRead])
# async def find_employees_without_department(current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['unit_member','tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Find Employees without Department - Endpoint")
#     employee_repo = EmployeeRepository(db)
#     try:
#         for role_dict in current_user.roles:
#                 if role_dict.name in ["super_admin", "hq_backstop"]:
#                     employees = employee_repo.find_employees_without_department()
#                     return employees
#                 else:
#                     employees = employee_repo.find_employees_without_department(tenancy_id=current_user.tenancy_id)
#                     return employees
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"{str(e)}")


# @router.patch("/employees/{employee_id}/department", response_model=EmployeeRead)
# async def change_employee_department_and_unit(employee_id: int, department_unit_update: Department_and_Unit_Update, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin','super_admin']))):
    
    
#     logging_helper.log_info("Accessing - Change Employee Department and Unit - Endpoint")
#     employee_repo = EmployeeRepository(db)
#     try:
#         for role_dict in current_user.roles:
#                 if role_dict.name == "super_admin":
#                     updated_employee = employee_repo.change_employee_department_and_unit(employee_id, department_unit_update)
#                     if not updated_employee:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist!")
#                     return updated_employee
#                 else:
#                     updated_employee = employee_repo.change_employee_department_and_unit(employee_id, department_unit_update, tenancy_id=current_user.tenancy_id)
#                     if not updated_employee:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or does not belong to your state")
#                     return updated_employee
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/employees/by-name/{name}", response_model=List[EmployeeRead])
# async def find_employees_by_name(name: str, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['unit_member','hq_staff','tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Find Employees by Name - Endpoint")
#     employee_repo = EmployeeRepository(db)
#     try:
#         for role_dict in current_user.roles:
#                 if role_dict.name in ["super_admin", "hq_backstop"]:
#                     employee = employee_repo.find_employees_by_name(name=name)
#                     return employee
#                 else:
#                     employee = employee_repo.find_employees_by_name(name=name, tenancy_id=current_user.tenancy_id)
#                     return employee
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"{str(e)}")


# @router.delete("/employees/{employee_id}/srt/{srt_id}")
# async def remove_employee_from_srt(employee_id: int, srt_id: int, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Remove employees from SRT - Endpoint")
#     employee_repo = EmployeeRepository(db)
#     try:
#         for role_dict in current_user.roles:
#                 if role_dict.name == "super_admin":
#                     updated_employee = employee_repo.remove_employee_from_srt(employee_id=employee_id, srt_id=srt_id)
#                     if not updated_employee:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist!")
#                     return {"detail": "Employee removed from SRT successfully"}
#                 else:
#                     updated_employee = employee_repo.remove_employee_from_srt(employee_id=employee_id, srt_id=srt_id, tenancy_id=current_user.tenancy_id)
#                     if not updated_employee:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or does not belong to your state")
#                     return {"detail": "Employee removed from SRT successfully"}
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



# @router.get("/employees/no-srt", response_model=List[EmployeeRead])
# async def get_employees_with_no_srt(current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['stl','technical_lead','tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Get Employee with no SRT - Endpoint")
#     employee_repo = EmployeeRepository(db)
#     try:
#         for role_dict in current_user.roles:
#                 if role_dict.name in ["super_admin", "hq_backstop"]:
#                     employees = employee_repo.get_employees_with_no_srt()
#                     return employees
#                 else:
#                     employees = employee_repo.get_employees_with_no_srt(tenancy_id=current_user.tenancy_id)
#                     return employees
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"{str(e)}")


# @router.post("/employees/{employee_id}/assign-department-unit")
# async def assign_employee_to_department_and_unit(employee_id: int, department_id: int, unit_id: Optional[int] = None, current_user:UserRead=Depends(get_current_user), 
#                          db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Assign Employee to Department and Unit - Endpoint")
#     employee_repo = EmployeeRepository(db)
#     try:
#         for role_dict in current_user.roles:
#                 if role_dict.name == "super_admin":
#                     updated_employee = employee_repo.assign_employee_to_department_and_unit(employee_id=employee_id, department_id=department_id, unit_id=unit_id)
#                     if not updated_employee:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist!")
#                     return {"detail": "Employee assigned to department and unit successfully"}
#                 else:
#                     updated_employee = employee_repo.assign_employee_to_department_and_unit(employee_id=employee_id, department_id=department_id, unit_id=unit_id, tenancy_id=current_user.tenancy_id)
#                     if not updated_employee:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or does not belong to your state")
#                     return {"detail": "Employee assigned to department and unit successfully"}
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/birthdays", response_model=List[Dict[str, Any]])
# def get_employees_with_birthdays_in_current_month(
#     db: Session = Depends(get_db),
#     current_user: UserRead = Depends(get_current_user),
#     _=Depends(role_checker(['unit_member', 'tenant_admin', 'super_admin', 'hq_backstop']))
# ):
#     logging_helper.log_info("Accessing - Get Employees with Birthdays in Current month - Endpoint")
#     repository = EmployeeRepository(db)
#     try:
#         if any(role.name in ['super_admin', 'hq_backstop'] for role in current_user.roles):
#             employees = repository.get_employees_with_birthdays_in_current_month()
#         else:
#             employees = repository.get_employees_with_birthdays_in_current_month(tenancy_id=current_user.tenancy_id)
#         return employees
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/employee_with_birthday", response_model=List[Dict[str, Any]])
# def get_employees_with_birthday(
#     tenancy: int = None,
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db),
#     _=Depends(role_checker(['unit_member', 'tenant_admin', 'super_admin', 'hq_backstop']))
# ):
#     logging_helper.log_info("Accessing - Get Employees with Birthday - Endpoint")
#     repository = EmployeeRepository(db)
#     try:
#         if any(role.name in ['super_admin', 'hq_backstop'] for role in current_user.roles):
#             employees_with_dob = repository.get_all_employees_with_birth_date()
#         else:
#             employees_with_dob = repository.get_all_employees_with_birth_date(current_user.tenancy_id)
#         return employees_with_dob
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/employees/birthdays/today", response_model=List[Dict[str, Any]])
# def get_employees_with_birthday_today(
#     tenancy_id: int = None,
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db),
#     _=Depends(role_checker(['unit_member', 'tenant_admin', 'super_admin', 'hq_backstop']))
# ):
#     logging_helper.log_info("Accessing - Get Employees with Birthday Today - Endpoint")
#     try:
#         repository = EmployeeRepository(db)
#         if any(role.name in ['super_admin', 'hq_backstop'] for role in current_user.roles):
#             employees_with_dob_today = repository.get_employees_with_today_birthday()
#         else:
#             employees_with_dob_today = repository.get_employees_with_today_birthday(current_user.tenancy_id)
#         return employees_with_dob_today
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post("/employees/{employee_id}/assign-to-project/{project_id}")
# async def assign_employee_to_project(
#     employee_id: int, 
#     project_id: int, 
#     current_user: UserRead = Depends(get_current_user), 
#     db: Session = Depends(get_db), 
#     _ = Depends(role_checker(['tenant_admin', 'super_admin']))
# ):
#     employee_repo = EmployeeRepository(db)
#     logging_helper.log_info(f"User {current_user.username} is assigning employee {employee_id} to project {project_id}")
#     try:
#         employee_repo.add_employee_to_project(employee_id, project_id)

#         # Log the action
#         changes = {
#             "action": "ADD_EMPLOYEE_TO_PROJECT",
#             "employee_id": employee_id,
#             "project_id": project_id
#         }
#         logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, 'Employee', employee_id, changes)

#         logging_helper.log_info(f"Employee {employee_id} assigned to project {project_id} successfully")
#         return {"detail": "Employee added to project successfully"}
#     except ValueError as e:
#         logging_helper.log_error(f"Error assigning employee {employee_id} to project {project_id}: {str(e)}")
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         logging_helper.log_error(f"An error occurred while assigning employee {employee_id} to project {project_id}: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# @router.post("/employees/assign-to-project/{project_id}")
# async def assign_group_of_employees_to_project(
#     employee_ids: List[int], 
#     project_id: int, 
#     current_user: UserRead = Depends(get_current_user), 
#     db: Session = Depends(get_db), 
#     _ = Depends(role_checker(['tenant_admin', 'super_admin']))
# ):
#     employee_repo = EmployeeRepository(db)
#     logging_helper.log_info(f"User {current_user.username} is assigning employees {employee_ids} to project {project_id}")
#     try:
#         employee_repo.add_group_of_employees_to_project(employee_ids, project_id)

#         # Log the action
#         changes = {
#             "action": "ADD_GROUP_OF_EMPLOYEES_TO_PROJECT",
#             "employee_ids": employee_ids,
#             "project_id": project_id
#         }
#         logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, 'Project', project_id, changes)

#         logging_helper.log_info(f"Group of employees {employee_ids} assigned to project {project_id} successfully")
#         return {"detail": "Group of employees added to project successfully"}
#     except ValueError as e:
#         logging_helper.log_error(f"Error assigning group of employees {employee_ids} to project {project_id}: {str(e)}")
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         logging_helper.log_error(f"An error occurred while assigning group of employees {employee_ids} to project {project_id}: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")





#routes/employee_routes.py
import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from db.database import get_db
from models.all_models import ActionEnum, AuditLog
from schemas.employee_schemas import EmployeeReadWithUserID, SRTAssignment, EmployeeCreate, EmployeeRead, EmployeeUpdate,Department_and_Unit_Update
from auth.dependencies import role_checker
from repositories.employee_repository import EmployeeRepository
from schemas.user_schemas import UserRead
from auth.security import get_current_user
from logging_helpers import logging_helper

router = APIRouter()

@router.post("/employees/", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
async def create_employee(employee_data: EmployeeCreate, current_user: UserRead = Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin', 'super_admin']))):
    """
    Create a new employee.
    - **employee_data**: EmployeeCreate - Data required to create an employee.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Create Employee - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        # Check if the user has the right role to create an employee
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin" or current_user.tenancy_id == employee_data.tenancy_id:
                new_employee = employee_repo.create_employee(employee_data)
                break
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{current_user.first_name} {current_user.last_name}, you are authorized to create employees only for your state!")
    except HTTPException as e:
        # Re-raise HTTP exceptions to be handled by FastAPI
        raise e
    except Exception as e:
        # Catch other exceptions and raise a generic HTTP 500 error
        raise HTTPException(status_code=500, detail=f"An error occurred while creating the employee: {str(e)}")

    return new_employee

@router.put("/employees/{employee_id}/", response_model=EmployeeRead)
async def update_employee(employee_id: int, employee_update: EmployeeUpdate, current_user: UserRead = Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin', 'super_admin']))):
    """
    Update an existing employee's information.
    - **employee_id**: int - ID of the employee to update.
    - **employee_update**: EmployeeUpdate - Updated employee data.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Update Employee - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        # Check if the user has the right role to update an employee
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                employee = employee_repo.update_employee(employee_id=employee_id, employee_data=employee_update)
                if not employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} is not found")
                return employee
            else:
                employee = employee_repo.update_employee(employee_id=employee_id, employee_data=employee_update, tenancy_id=current_user.tenancy_id)
                if not employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} is not found")
                return employee
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")

@router.get("/employees/", response_model=List[EmployeeReadWithUserID])
async def list_employees(
    limit: int = Query(100, description="Maximum number of results to return"),
    cursor: Optional[int] = Query(None, description="ID of the last item from the previous result set"),
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _=Depends(role_checker(['hq_staff', 'unit_member', 'tenant_admin', 'super_admin']))
):
    """
    List all employees with optional pagination.
    - **limit**: int - Maximum number of results to return.
    - **cursor**: Optional[int] - ID of the last item from the previous result set.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - List Employee - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        # Check if the user has the right role to list employees
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_backstop"]:
                employees = employee_repo.get_all_employees(limit=limit, cursor=cursor)
                return employees
            else:
                employees = employee_repo.get_all_employees(limit=limit, cursor=cursor, tenancy_id=current_user.tenancy_id)
                return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")


@router.get("/employees/{employee_id}/", response_model=EmployeeRead)
async def get_employee(employee_id: int, current_user: UserRead = Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['unit_member', 'hq_backstop', 'tenant_admin', 'super_admin']))):
    """
    Get an employee by ID.
    - **employee_id**: int - ID of the employee to retrieve.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Get Employee - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        # Check if the user has the right role to get an employee
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_staff"]:
                employee = employee_repo.get_employee_by_id(employee_id=employee_id)
                if not employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist")
                return employee
            else:
                employee = employee_repo.get_employee_by_id(employee_id=employee_id, tenancy_id=current_user.tenancy_id)
                if not employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or does not belong to your state")
                return employee
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")

@router.delete("/employees/{employee_id}/")
async def delete_employee(employee_id: int, current_user: UserRead = Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin', 'super_admin']))):
    """
    Soft delete an employee by ID.
    - **employee_id**: int - ID of the employee to delete.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Delete Employee - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        # Check if the user has the right role to delete an employee
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                employee = employee_repo.delete_employee(employee_id=employee_id)
                if not employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist")
                return f'"detail": "Employee with id {employee_id} has been deleted successfully"'
            else:
                employee = employee_repo.delete_employee(employee_id=employee_id, tenancy_id=current_user.tenancy_id)
                if not employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or does not belong to your state")
                return f'"detail": "Employee with id {employee_id} has been deleted successfully"'
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")

@router.get("/employees/by-department/{department_name}/", response_model=List[EmployeeRead])
async def get_employees_by_department(department_name: str, current_user: UserRead = Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['unit_member', 'hq_backstop', 'tenant_admin', 'super_admin']))):
    """
    Get employees by department name.
    - **department_name**: str - Name of the department.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Get Employees by Department - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        # Check if the user has the right role to get employees by department
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_staff"]:
                employee = employee_repo.get_employees_by_department_name(department_name=department_name.upper())
                if len(employee) == 0:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Please check the department name supplied")
                return employee
            else:
                employee = employee_repo.get_employees_by_department_name(department_name=department_name.upper(), tenancy_id=current_user.tenancy_id)
                if len(employee) == 0:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Please check the department name supplied")
                return employee
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")

@router.get("/employees/by-srt/{srt_name}/", response_model=List[EmployeeRead])
async def get_employee_by_srt(srt_name: str, current_user: UserRead = Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['unit_member', 'tenant_admin', 'super_admin']))):
    """
    Get employees by SRT name.
    - **srt_name**: str - Name of the SRT.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Get Employee by SRT - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        # Check if the user has the right role to get employees by SRT
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_backstop"]:
                employee = employee_repo.find_employees_by_srt_name(srt_name=srt_name.upper())
                if not employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Please check the SRT name supplied")
                return employee
            else:
                employee = employee_repo.find_employees_by_srt_name(srt_name=srt_name.upper(), tenancy_id=current_user.tenancy_id)
                if not employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Please check the SRT name supplied")
                return employee
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")

@router.get("/employees/by-unit/{unit_name}/", response_model=List[EmployeeRead])
async def get_employee_by_unit(unit_name: str, current_user: UserRead = Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['unit_member', 'tenant_admin', 'super_admin']))):
    """
    Get employees by unit name.
    - **unit_name**: str - Name of the unit.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Get Employee by Unit - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        # Check if the user has the right role to get employees by unit
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_backstop"]:
                employee = employee_repo.get_employees_by_unit_name(unit_name=unit_name.upper())
                if not employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Please check the Unit name supplied")
                return employee
            else:
                employee = employee_repo.get_employees_by_unit_name(unit_name=unit_name.upper(), tenancy_id=current_user.tenancy_id)
                if not employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Please check the Unit name supplied")
                return employee
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")

@router.post("/employees/{employee_id}/assign-srts", status_code=status.HTTP_200_OK)
async def assign_employee_to_srts(
    employee_id: int, 
    srt_assignment: SRTAssignment, current_user: UserRead = Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin', 'super_admin']))):
    """
    Assign an employee to multiple SRTs.
    - **employee_id**: int - ID of the employee.
    - **srt_assignment**: SRTAssignment - List of SRT IDs to assign.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Assign Employee to SRT - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        # Check if the user has the right role to assign SRTs
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                result = employee_repo.assign_employee_to_srt(employee_id, srt_assignment.srt_ids)
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist")
            else:
                result = employee_repo.assign_employee_to_srt(employee_id, srt_assignment.srt_ids, tenancy_id=current_user.tenancy_id)
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or does not belong to your state")
        return {"message": "Feedback", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/employees/no-department", response_model=List[EmployeeRead])
async def find_employees_without_department(current_user: UserRead = Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['unit_member', 'tenant_admin', 'super_admin']))):
    """
    Find employees who are not assigned to any department.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Find Employees without Department - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        # Check if the user has the right role to find employees without a department
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_backstop"]:
                employees = employee_repo.find_employees_without_department()
                return employees
            else:
                employees = employee_repo.find_employees_without_department(tenancy_id=current_user.tenancy_id)
                return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")

@router.patch("/employees/{employee_id}/department", response_model=EmployeeRead)
async def change_employee_department_and_unit(employee_id: int, department_unit_update: Department_and_Unit_Update, current_user: UserRead = Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin', 'super_admin']))):
    """
    Change the department and unit of an employee.
    - **employee_id**: int - ID of the employee.
    - **department_unit_update**: Department_and_Unit_Update - Updated department and unit data.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Change Employee Department and Unit - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        # Check if the user has the right role to change the department and unit
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                updated_employee = employee_repo.change_employee_department_and_unit(employee_id, department_unit_update)
                if not updated_employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist!")
                return updated_employee
            else:
                updated_employee = employee_repo.change_employee_department_and_unit(employee_id, department_unit_update, tenancy_id=current_user.tenancy_id)
                if not updated_employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or does not belong to your state")
                return updated_employee
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/employees/by-name/{name}", response_model=List[EmployeeRead])
async def find_employees_by_name(name: str, current_user: UserRead = Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['unit_member', 'hq_staff', 'tenant_admin', 'super_admin']))):
    """
    Find employees by name.
    - **name**: str - Name of the employee to search for.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Find Employees by Name - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        # Check if the user has the right role to find employees by name
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_backstop"]:
                employee = employee_repo.find_employees_by_name(name=name)
                return employee
            else:
                employee = employee_repo.find_employees_by_name(name=name, tenancy_id=current_user.tenancy_id)
                return employee
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")

@router.delete("/employees/{employee_id}/srt/{srt_id}")
async def remove_employee_from_srt(employee_id: int, srt_id: int, current_user: UserRead = Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin', 'super_admin']))):
    """
    Remove an employee from a specific SRT.
    - **employee_id**: int - ID of the employee.
    - **srt_id**: int - ID of the SRT.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Remove employees from SRT - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        # Check if the user has the right role to remove an employee from an SRT
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                updated_employee = employee_repo.remove_employee_from_srt(employee_id=employee_id, srt_id=srt_id)
                if not updated_employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist!")
                return {"detail": "Employee removed from SRT successfully"}
            else:
                updated_employee = employee_repo.remove_employee_from_srt(employee_id=employee_id, srt_id=srt_id, tenancy_id=current_user.tenancy_id)
                if not updated_employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or does not belong to your state")
                return {"detail": "Employee removed from SRT successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/employees/no-srt", response_model=List[EmployeeRead])
async def get_employees_with_no_srt(current_user: UserRead = Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['stl', 'technical_lead', 'tenant_admin', 'super_admin']))):
    """
    Get employees who are not assigned to any SRT.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Get Employee with no SRT - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        # Check if the user has the right role to get employees with no SRT
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_backstop"]:
                employees = employee_repo.get_employees_with_no_srt()
                return employees
            else:
                employees = employee_repo.get_employees_with_no_srt(tenancy_id=current_user.tenancy_id)
                return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")

@router.post("/employees/{employee_id}/assign-department-unit")
async def assign_employee_to_department_and_unit(employee_id: int, department_id: int, unit_id: Optional[int] = None, current_user: UserRead = Depends(get_current_user), 
                         db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin', 'super_admin']))):
    """
    Assign an employee to a department and optionally a unit.
    - **employee_id**: int - ID of the employee.
    - **department_id**: int - ID of the department.
    - **unit_id**: Optional[int] - ID of the unit (optional).
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Assign Employee to Department and Unit - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        # Check if the user has the right role to assign an employee to a department and unit
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin":
                updated_employee = employee_repo.assign_employee_to_department_and_unit(employee_id=employee_id, department_id=department_id, unit_id=unit_id)
                if not updated_employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist!")
                return {"detail": "Employee assigned to department and unit successfully"}
            else:
                updated_employee = employee_repo.assign_employee_to_department_and_unit(employee_id=employee_id, department_id=department_id, unit_id=unit_id, tenancy_id=current_user.tenancy_id)
                if not updated_employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or does not belong to your state")
                return {"detail": "Employee assigned to department and unit successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/birthdays", response_model=List[Dict[str, Any]])
def get_employees_with_birthdays_in_current_month(
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    _=Depends(role_checker(['unit_member', 'tenant_admin', 'super_admin', 'hq_backstop']))
):
    """
    Get employees with birthdays in the current month.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Get Employees with Birthdays in Current month - Endpoint")
    repository = EmployeeRepository(db)
    try:
        # Check if the user has the right role to get employees with birthdays in the current month
        if any(role.name in ['super_admin', 'hq_backstop'] for role in current_user.roles):
            employees = repository.get_employees_with_birthdays_in_current_month()
        else:
            employees = repository.get_employees_with_birthdays_in_current_month(tenancy_id=current_user.tenancy_id)
        return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/employee_with_birthday", response_model=List[Dict[str, Any]])
def get_employees_with_birthday(
    tenancy: int = None,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _=Depends(role_checker(['unit_member', 'tenant_admin', 'super_admin', 'hq_backstop']))
):
    """
    Get employees with birthdays.
    - **tenancy**: int - Tenancy ID (optional).
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Get Employees with Birthday - Endpoint")
    repository = EmployeeRepository(db)
    try:
        # Check if the user has the right role to get employees with birthdays
        if any(role.name in ['super_admin', 'hq_backstop'] for role in current_user.roles):
            employees_with_dob = repository.get_all_employees_with_birth_date()
        else:
            employees_with_dob = repository.get_all_employees_with_birth_date(current_user.tenancy_id)
        return employees_with_dob
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/employees/birthdays/today", response_model=List[Dict[str, Any]])
def get_employees_with_birthday_today(
    tenancy_id: int = None,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _=Depends(role_checker(['unit_member', 'tenant_admin', 'super_admin', 'hq_backstop']))
):
    """
    Get employees with birthdays today.
    - **tenancy_id**: int - Tenancy ID (optional).
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Get Employees with Birthday Today - Endpoint")
    try:
        repository = EmployeeRepository(db)
        # Check if the user has the right role to get employees with birthdays today
        if any(role.name in ['super_admin', 'hq_backstop'] for role in current_user.roles):
            employees_with_dob_today = repository.get_employees_with_today_birthday()
        else:
            employees_with_dob_today = repository.get_employees_with_today_birthday(current_user.tenancy_id)
        return employees_with_dob_today
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/employees/{employee_id}/assign-to-project/{project_id}")
async def assign_employee_to_project(
    employee_id: int, 
    project_id: int, 
    current_user: UserRead = Depends(get_current_user), 
    db: Session = Depends(get_db), 
    _ = Depends(role_checker(['tenant_admin', 'super_admin']))
):
    """
    Assign an employee to a project.
    - **employee_id**: int - ID of the employee.
    - **project_id**: int - ID of the project.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    employee_repo = EmployeeRepository(db)
    logging_helper.log_info(f"User {current_user.username} is assigning employee {employee_id} to project {project_id}")
    try:
        employee_repo.add_employee_to_project(employee_id, project_id)

        # Log the action
        changes = {
            "action": "ADD_EMPLOYEE_TO_PROJECT",
            "employee_id": employee_id,
            "project_id": project_id
        }
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, 'Employee', employee_id, changes)

        logging_helper.log_info(f"Employee {employee_id} assigned to project {project_id} successfully")
        return {"detail": "Employee added to project successfully"}
    except ValueError as e:
        logging_helper.log_error(f"Error assigning employee {employee_id} to project {project_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging_helper.log_error(f"An error occurred while assigning employee {employee_id} to project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/employees/assign-to-project/{project_id}")
async def assign_group_of_employees_to_project(
    employee_ids: List[int], 
    project_id: int, 
    current_user: UserRead = Depends(get_current_user), 
    db: Session = Depends(get_db), 
    _ = Depends(role_checker(['tenant_admin', 'super_admin']))
):
    """
    Assign a group of employees to a project.
    - **employee_ids**: List[int] - List of employee IDs.
    - **project_id**: int - ID of the project.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    employee_repo = EmployeeRepository(db)
    logging_helper.log_info(f"User {current_user.username} is assigning employees {employee_ids} to project {project_id}")
    try:
        employee_repo.add_group_of_employees_to_project(employee_ids, project_id)

        # Log the action
        changes = {
            "action": "ADD_GROUP_OF_EMPLOYEES_TO_PROJECT",
            "employee_ids": employee_ids,
            "project_id": project_id
        }
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, 'Project', project_id, changes)

        logging_helper.log_info(f"Group of employees {employee_ids} assigned to project {project_id} successfully")
        return {"detail": "Group of employees added to project successfully"}
    except ValueError as e:
        logging_helper.log_error(f"Error assigning group of employees {employee_ids} to project {project_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging_helper.log_error(f"An error occurred while assigning group of employees {employee_ids} to project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    

@router.post("/employees/{employee_id}/set-supervisor", response_model=EmployeeRead)
async def set_employee_supervisor(
    employee_id: int, 
    supervisor_id: Optional[int], 
    tenancy_id: Optional[int] = None, 
    current_user: UserRead = Depends(get_current_user), 
    db: Session = Depends(get_db), 
    _ = Depends(role_checker(['tenant_admin', 'super_admin']))
):
    """
    Set or update the supervisor for an employee.
    - **employee_id**: int - ID of the employee to update.
    - **supervisor_id**: Optional[int] - ID of the new supervisor.
    - **tenancy_id**: Optional[int] - Tenancy ID for filtering.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    employee_repo = EmployeeRepository(db)
    logging_helper.log_info(f"User {current_user.username} is setting supervisor for employee {employee_id} to {supervisor_id}")
    try:
        updated_employee = employee_repo.set_supervisor(employee_id, supervisor_id, tenancy_id)
        if not updated_employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or is not in your state")
        
        logging_helper.log_info(f"Supervisor for employee {employee_id} set to {supervisor_id} successfully")
        return updated_employee
    except HTTPException as e:
        logging_helper.log_error(f"Error setting supervisor for employee {employee_id} to {supervisor_id}: {str(e)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"An error occurred while setting supervisor for employee {employee_id} to {supervisor_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/employees/supervised-by/{supervisor_id}/", response_model=List[EmployeeRead])
async def get_supervised_employees(
    supervisor_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _=Depends(role_checker(['unit_member', 'tenant_admin', 'super_admin']))
):
    """
    Get all employees supervised by a specific supervisor.
    - **supervisor_id**: int - ID of the supervisor.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Get Employees Supervised by - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        # Check if the user has the right role to get supervised employees
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_backstop"]:
                employees = employee_repo.get_supervised_employees(supervisor_id=supervisor_id)
                return employees
            else:
                employees = employee_repo.get_supervised_employees(supervisor_id=supervisor_id, tenancy_id=current_user.tenancy_id)
                return employees
    except HTTPException as e:
        raise e
    except Exception as e:
        logging_helper.log_error(f"An error occurred while retrieving supervised employees for supervisor {supervisor_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/employees/hierarchy/{employee_id}/", response_model=Dict[str, Any])
async def get_employee_hierarchy(
    employee_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _=Depends(role_checker(['unit_member', 'tenant_admin', 'super_admin']))
):
    """
    Get the employee hierarchy starting from a specific employee.
    - **employee_id**: int - ID of the employee to start the hierarchy.
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Get Employee Hierarchy - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        # Check if the user has the right role to get the employee hierarchy
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_backstop"]:
                hierarchy = employee_repo.get_employee_hierarchy(employee_id=employee_id)
                return hierarchy
            else:
                hierarchy = employee_repo.get_employee_hierarchy(employee_id=employee_id, tenancy_id=current_user.tenancy_id)
                return hierarchy
    except HTTPException as e:
        raise e
    except Exception as e:
        logging_helper.log_error(f"An error occurred while retrieving the hierarchy for employee {employee_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/employees/hierarchy", response_model=List[Dict[str, Any]])
async def get_full_employee_hierarchy(
    tenancy_id: Optional[int] = Query(None, description="Tenancy ID for filtering (optional)"),
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db),
    _=Depends(role_checker(['tenant_admin', 'super_admin']))
):
    """
    Get the full employee hierarchy for organizational chart.
    - **tenancy_id**: Optional[int] - Tenancy ID for filtering (optional).
    - **current_user**: UserRead - Current authenticated user.
    - **db**: Session - Database session.
    """
    logging_helper.log_info("Accessing - Get Full Employee Hierarchy for Organizational Chart - Endpoint")
    employee_repo = EmployeeRepository(db)
    try:
        hierarchy = employee_repo.get_full_hierarchy(tenancy_id=tenancy_id)
        return hierarchy
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")

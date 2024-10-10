from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from models.all_models import ActionEnum
from repositories.project_repository import ProjectRepository
from schemas.project_schemas import EmployeeProjectDetail, ProjectCreate, ProjectUpdate, ProjectOut, FunderOut, ProjectComponentOut, EmployeeOut  # Assuming you have these Pydantic schemas
from auth.dependencies import role_checker
from auth.security import get_current_user
from schemas.user_schemas import UserRead
from logging_helpers import logging_helper

router = APIRouter()

@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user), _=Depends(role_checker(['super_admin', 'tenant_admin']))):
    logging_helper.log_info(f"User {current_user.username} is fetching project with ID {project_id}")
    repo = ProjectRepository(db)
    try:
        project = repo.get_project(project_id)
        if not project:
            logging_helper.log_warning(f"Project with ID {project_id} not found")
            raise HTTPException(status_code=404, detail="Project not found")
        logging_helper.log_info(f"Project with ID {project_id} fetched successfully")
        return project
    except Exception as e:
        logging_helper.log_error(f"An error occurred while fetching project with ID {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/projects", response_model=List[ProjectOut])
def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user), _=Depends(role_checker(['super_admin', 'tenant_admin']))):
    logging_helper.log_info(f"User {current_user.username} is fetching projects with skip={skip} and limit={limit}")
    repo = ProjectRepository(db)
    try:
        projects = repo.get_projects(skip=skip, limit=limit)
        logging_helper.log_info(f"Fetched {len(projects)} projects successfully")
        return projects
    except Exception as e:
        logging_helper.log_error(f"An error occurred while fetching projects: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user), _=Depends(role_checker(['super_admin', 'tenant_admin']))):
    logging_helper.log_info(f"User {current_user.username} is creating a new project")
    repo = ProjectRepository(db)
    try:
        new_project = repo.create_project(project)
        changes = {"action": "CREATE_PROJECT", "project_name": new_project.name, "project_id": new_project.id}
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, 'Project', new_project.id, changes)
        logging_helper.log_info(f"Project {new_project.name} created successfully with ID {new_project.id}")
        return new_project
    except Exception as e:
        logging_helper.log_error(f"An error occurred while creating a new project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.put("/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user), _=Depends(role_checker(['super_admin', 'tenant_admin']))):
    logging_helper.log_info(f"User {current_user.username} is updating project with ID {project_id}")
    repo = ProjectRepository(db)
    try:
        updated_project = repo.update_project(project_id, project)
        if not updated_project:
            logging_helper.log_warning(f"Project with ID {project_id} not found")
            raise HTTPException(status_code=404, detail="Project not found")
        changes = {"action": "UPDATE_PROJECT", "project_id": project_id}
        logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, 'Project', project_id, changes)
        logging_helper.log_info(f"Project with ID {project_id} updated successfully")
        return updated_project
    except Exception as e:
        logging_helper.log_error(f"An error occurred while updating project with ID {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.delete("/projects/{project_id}", response_model=ProjectOut)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user), _=Depends(role_checker(['super_admin', 'tenant_admin']))):
    logging_helper.log_info(f"User {current_user.username} is deleting project with ID {project_id}")
    repo = ProjectRepository(db)
    try:
        deleted_project = repo.delete_project(project_id)
        if not deleted_project:
            logging_helper.log_warning(f"Project with ID {project_id} not found")
            raise HTTPException(status_code=404, detail="Project not found")
        changes = {"action": "DELETE_PROJECT", "project_id": project_id}
        logging_helper.log_audit(db, current_user.id, ActionEnum.DELETE, 'Project', project_id, changes)
        logging_helper.log_info(f"Project with ID {project_id} deleted successfully")
        return deleted_project
    except Exception as e:
        logging_helper.log_error(f"An error occurred while deleting project with ID {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/projects/{project_id}/funders", response_model=List[FunderOut])
def get_project_funders(project_id: int, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user), _=Depends(role_checker(['super_admin', 'tenant_admin']))):
    logging_helper.log_info(f"User {current_user.username} is fetching funders for project ID {project_id}")
    repo = ProjectRepository(db)
    try:
        funders = repo.get_project_funders(project_id)
        logging_helper.log_info(f"Fetched {len(funders)} funders for project ID {project_id}")
        return funders
    except Exception as e:
        logging_helper.log_error(f"An error occurred while fetching funders for project ID {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/projects/{project_id}/components", response_model=List[ProjectComponentOut])
def get_project_components(project_id: int, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user), _=Depends(role_checker(['super_admin', 'tenant_admin']))):
    logging_helper.log_info(f"User {current_user.username} is fetching components for project ID {project_id}")
    repo = ProjectRepository(db)
    try:
        components = repo.get_project_components(project_id)
        logging_helper.log_info(f"Fetched {len(components)} components for project ID {project_id}")
        return components
    except Exception as e:
        logging_helper.log_error(f"An error occurred while fetching components for project ID {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



# @router.get("/projects/{project_id}/employees", response_model=List[EmployeeOut])
# def get_project_employees(project_id: int, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user), _=Depends(role_checker(['super_admin', 'tenant_admin']))):
#     logging_helper.log_info(f"User {current_user.username} is fetching employees for project ID {project_id}")
#     repo = ProjectRepository(db)
#     try:
#         employees = repo.get_project_employees(project_id)
#         logging_helper.log_info(f"Fetched {len(employees)} employees for project ID {project_id}")
#         return employees
#     except Exception as e:
#         logging_helper.log_error(f"An error occurred while fetching employees for project ID {project_id}: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# @router.get("/projects/{project_id}/employees", response_model=EmployeeProjectDetail)
# def get_project_employees(project_id: int, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user), _=Depends(role_checker(['super_admin', 'tenant_admin']))):
#     logging_helper.log_info(f"User {current_user.username} is fetching employees for project ID {project_id}")
#     repo = ProjectRepository(db)
#     try:
#         project_with_employees = repo.get_project_employees(project_id)
#         if not project_with_employees:
#             logging_helper.log_warning(f"No employees found for project ID {project_id}")
#             raise HTTPException(status_code=404, detail="Project or employees not found")
#         logging_helper.log_info(f"Fetched employees for project ID {project_id} successfully")
#         return project_with_employees
#     except Exception as e:
#         logging_helper.log_error(f"An error occurred while fetching employees for project ID {project_id}: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/projects/{project_id}/employees", response_model=EmployeeProjectDetail)
def get_project_employees(project_id: int, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user), _=Depends(role_checker(['super_admin', 'tenant_admin']))):
    logging_helper.log_info(f"User {current_user.username} is fetching employees for project ID {project_id}")
    repo = ProjectRepository(db)
    try:
        project_with_employees = repo.get_project_employees(project_id)
        if not project_with_employees:
            logging_helper.log_warning(f"No employees found for project ID {project_id}")
            raise HTTPException(status_code=404, detail="Project or employees not found")
        logging_helper.log_info(f"Fetched employees for project ID {project_id}")
        return project_with_employees
    except Exception as e:
        logging_helper.log_error(f"An error occurred while fetching employees for project ID {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/projects/{project_id}/tenants", response_model=ProjectOut)
def add_tenants_to_project(project_id: int, tenant_ids: List[int], db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user), _=Depends(role_checker(['super_admin', 'tenant_admin']))):
    logging_helper.log_info(f"User {current_user.username} is adding tenants to project ID {project_id}")
    repo = ProjectRepository(db)
    try:
        project = repo.add_tenants_to_project(project_id, tenant_ids)
        if not project:
            logging_helper.log_warning(f"Project with ID {project_id} not found")
            raise HTTPException(status_code=404, detail="Project not found")
        changes = {"action": "ADD_TENANTS_TO_PROJECT", "project_id": project_id, "tenant_ids": tenant_ids}
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, 'Project', project_id, changes)
        logging_helper.log_info(f"Tenants added to project ID {project_id} successfully")
        return project
    except Exception as e:
        logging_helper.log_error(f"An error occurred while adding tenants to project ID {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/projects/{project_id}/employees", response_model=ProjectOut)
def add_employees_to_project(project_id: int, employee_ids: List[int], db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user), _=Depends(role_checker(['super_admin', 'tenant_admin']))):
    logging_helper.log_info(f"User {current_user.username} is adding employees to project ID {project_id}")
    repo = ProjectRepository(db)
    try:
        project = repo.add_employees_to_project(project_id, employee_ids)
        if not project:
            logging_helper.log_warning(f"Project with ID {project_id} not found")
            raise HTTPException(status_code=404, detail="Project not found")
        changes = {"action": "ADD_EMPLOYEES_TO_PROJECT", "project_id": project_id, "employee_ids": employee_ids}
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, 'Project', project_id, changes)
        logging_helper.log_info(f"Employees added to project ID {project_id} successfully")
        return project
    except Exception as e:
        logging_helper.log_error(f"An error occurred while adding employees to project ID {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from models.all_models import ActionEnum
from repositories.project_component_repository import ProjectComponentRepository
from schemas.project_component_shemas import (
    ProjectComponentCreate,
    ProjectComponentUpdate,
    ProjectComponentOut,
)
from auth.dependencies import get_current_user, role_checker
from schemas.user_schemas import UserRead
from logging_helpers import logging_helper

router = APIRouter()


@router.get(
    "/project_components/{id}",
    response_model=ProjectComponentOut,
    dependencies=[Depends(role_checker(["super_admin"]))],
)
def get_project_component(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
):
    repo = ProjectComponentRepository(db)
    logging_helper.log_info(
        f"User {current_user.username} is fetching project component with id {id}"
    )
    try:
        project_component = repo.get_project_component(id)
        if not project_component:
            logging_helper.log_warning(f"Project component with id {id} not found")
            raise HTTPException(status_code=404, detail="Project component not found")
        return project_component
    except Exception as e:
        logging_helper.log_error(
            f"An error occurred while fetching project component with id {id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get(
    "/project_components",
    response_model=List[ProjectComponentOut],
    dependencies=[Depends(role_checker(["super_admin", "unit_member", "stl"]))],
)
def get_project_components(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
):
    repo = ProjectComponentRepository(db)
    logging_helper.log_info(
        f"User {current_user.username} is fetching project components with skip={skip} and limit={limit}"
    )
    try:
        return repo.get_project_components(skip=skip, limit=limit)
    except Exception as e:
        logging_helper.log_error(
            f"An error occurred while fetching project components: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post(
    "/project_components",
    response_model=ProjectComponentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(role_checker(["super_admin"]))],
)
def create_project_component(
    project_component: ProjectComponentCreate,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
):
    repo = ProjectComponentRepository(db)
    logging_helper.log_info(
        f"User {current_user.username} is creating a new project component"
    )
    try:
        new_component = repo.create_project_component(project_component)

        # Log the action
        changes = {
            "action": "CREATE_PROJECT_COMPONENT",
            "project_component": project_component.dict(),
        }
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.CREATE,
            "ProjectComponent",
            new_component.id,
            changes,
        )

        logging_helper.log_info(f"Project component created with id {new_component.id}")
        return new_component
    except Exception as e:
        logging_helper.log_error(
            f"An error occurred while creating project component: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.put(
    "/project_components/{id}",
    response_model=ProjectComponentOut,
    dependencies=[Depends(role_checker(["admin"]))],
)
def update_project_component(
    id: int,
    project_component: ProjectComponentUpdate,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
):
    repo = ProjectComponentRepository(db)
    logging_helper.log_info(
        f"User {current_user.username} is updating project component with id {id}"
    )
    try:
        updated_component = repo.update_project_component(id, project_component)
        if not updated_component:
            logging_helper.log_warning(f"Project component with id {id} not found")
            raise HTTPException(status_code=404, detail="Project component not found")

        # Log the action
        changes = {
            "action": "UPDATE_PROJECT_COMPONENT",
            "project_component": project_component.dict(exclude_unset=True),
        }
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.UPDATE, "ProjectComponent", id, changes
        )

        logging_helper.log_info(f"Project component with id {id} updated successfully")
        return updated_component
    except Exception as e:
        logging_helper.log_error(
            f"An error occurred while updating project component with id {id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.delete(
    "/project_components/{id}",
    response_model=ProjectComponentOut,
    dependencies=[Depends(role_checker(["super_admin"]))],
)
def delete_project_component(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
):
    repo = ProjectComponentRepository(db)
    logging_helper.log_info(
        f"User {current_user.username} is deleting project component with id {id}"
    )
    try:
        deleted_component = repo.delete_project_component(id)
        if not deleted_component:
            logging_helper.log_warning(f"Project component with id {id} not found")
            raise HTTPException(status_code=404, detail="Project component not found")

        # Log the action
        changes = {"action": "DELETE_PROJECT_COMPONENT", "project_component_id": id}
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.DELETE, "ProjectComponent", id, changes
        )

        logging_helper.log_info(f"Project component with id {id} deleted successfully")
        return deleted_component
    except Exception as e:
        logging_helper.log_error(
            f"An error occurred while deleting project component with id {id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

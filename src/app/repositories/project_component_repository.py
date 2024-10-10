from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.all_models import ProjectComponent, Project
from schemas.project_component_shemas import ProjectComponentCreate, ProjectComponentUpdate
from typing import List
from logging_helpers import logging_helper
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

class ProjectComponentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_project_component(self, id: int) -> ProjectComponent:
        logging_helper.log_info(f"Fetching project component with id={id}")
        try:
            component = self.db.query(ProjectComponent).filter(
                ProjectComponent.id == id,
                ProjectComponent.is_active == True
            ).first()
            if not component:
                logging_helper.log_warning(f"Project component with id={id} not found or inactive")
            return component
        except Exception as e:
            logging_helper.log_error(f"An error occurred while fetching project component with id={id}: {str(e)}")
            raise

    def get_project_components(self, skip: int = 0, limit: int = 100) -> List[ProjectComponent]:
        logging_helper.log_info(f"Fetching project components with skip={skip} and limit={limit}")
        try:
            components = self.db.query(ProjectComponent).filter(ProjectComponent.is_active == True).offset(skip).limit(limit).all()
            return components
        except Exception as e:
            logging_helper.log_error(f"An error occurred while fetching project components: {str(e)}")
            raise

    def create_project_component(self, project_component: ProjectComponentCreate) -> ProjectComponent:
        logging_helper.log_info(f"Creating project component with data: {project_component.dict()}")
        try:
            # Check if the project_id exists in the projects table
            project_exists = self.db.query(Project.id).filter(Project.id == project_component.project_id).first()
            if not project_exists:
                logging_helper.log_error(f"Project with id={project_component.project_id} does not exist")
                raise ValueError(f"Project with id={project_component.project_id} does not exist")

            db_project_component = ProjectComponent(**project_component.dict())
            self.db.add(db_project_component)
            self.db.commit()
            self.db.refresh(db_project_component)
            logging_helper.log_info(f"Created project component with id={db_project_component.id}")
            return db_project_component
        except IntegrityError as e:
            logging_helper.log_error(f"Integrity error while creating project component: {str(e)}")
            self.db.rollback()
            raise ValueError(f"Integrity error: {str(e)}")
        except SQLAlchemyError as e:
            logging_helper.log_error(f"SQLAlchemy error while creating project component: {str(e)}")
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"SQLAlchemy error: {str(e)}")
        except Exception as e:
            logging_helper.log_error(f"An unexpected error occurred while creating project component: {str(e)}")
            self.db.rollback()
            raise

    def update_project_component(self, id: int, project_component: ProjectComponentUpdate) -> ProjectComponent:
        logging_helper.log_info(f"Updating project component with id={id} and data: {project_component.dict(exclude_unset=True)}")
        try:
            db_project_component = self.get_project_component(id)
            if not db_project_component:
                logging_helper.log_warning(f"Project component with id={id} not found or inactive")
                return None
            for key, value in project_component.dict(exclude_unset=True).items():
                setattr(db_project_component, key, value)
            self.db.commit()
            self.db.refresh(db_project_component)
            logging_helper.log_info(f"Updated project component with id={db_project_component.id}")
            return db_project_component
        except SQLAlchemyError as e:
            logging_helper.log_error(f"SQLAlchemy error while updating project component with id={id}: {str(e)}")
            self.db.rollback()
            raise
        except Exception as e:
            logging_helper.log_error(f"An unexpected error occurred while updating project component with id={id}: {str(e)}")
            self.db.rollback()
            raise

    def delete_project_component(self, id: int) -> ProjectComponent:
        logging_helper.log_info(f"Deleting project component with id={id}")
        try:
            db_project_component = self.get_project_component(id)
            if not db_project_component:
                logging_helper.log_warning(f"Project component with id={id} not found or inactive")
                return None
            db_project_component.is_active = False
            self.db.commit()
            logging_helper.log_info(f"Deleted project component with id={db_project_component.id}")
            return db_project_component
        except SQLAlchemyError as e:
            logging_helper.log_error(f"SQLAlchemy error while deleting project component with id={id}: {str(e)}")
            self.db.rollback()
            raise
        except Exception as e:
            logging_helper.log_error(f"An unexpected error occurred while deleting project component with id={id}: {str(e)}")
            self.db.rollback()
            raise

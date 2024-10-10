import logging
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from models.all_models import Project, Funder, ProjectComponent, Employee,Tenancy
from schemas.project_schemas import ProjectCreate, ProjectUpdate  # Assuming you have Pydantic schemas for input validation
from typing import List, Optional

logger = logging.getLogger(__name__)

class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_project(self, project_id: int) -> Optional[Project]:
        try:
            logger.info(f"Fetching project with ID {project_id}")
            project = self.db.query(Project).filter(Project.id == project_id, Project.is_active == True).first()
            if project:
                logger.info(f"Project with ID {project_id} found")
            else:
                logger.warning(f"Project with ID {project_id} not found or inactive")
            return project
        except SQLAlchemyError as e:
            logger.error(f"Error fetching project with ID {project_id}: {e}")
            self.db.rollback()
            raise e

    def get_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        try:
            logger.info(f"Fetching projects with skip={skip} and limit={limit}")
            projects = self.db.query(Project).filter(Project.is_active == True).offset(skip).limit(limit).all()
            logger.info(f"Fetched {len(projects)} projects")
            return projects
        except SQLAlchemyError as e:
            logger.error(f"Error fetching projects: {e}")
            self.db.rollback()
            raise e

    def create_project(self, project: ProjectCreate) -> Project:
        try:
            logger.info(f"Creating project with name {project.name}")
            db_project = Project(
                name=project.name,
                description=project.description,
                start_date=project.start_date,
                end_date=project.end_date,
                project_sum=project.project_sum,
            )
            self.db.add(db_project)
            self.db.commit()
            self.db.refresh(db_project)
            logger.info(f"Project created with ID {db_project.id}")
            return db_project
        except SQLAlchemyError as e:
            logger.error(f"Error creating project: {e}")
            self.db.rollback()
            raise e

    def update_project(self, project_id: int, project: ProjectUpdate) -> Optional[Project]:
        try:
            logger.info(f"Updating project with ID {project_id}")
            db_project = self.db.query(Project).filter(Project.id == project_id, Project.is_active == True).first()
            if db_project is None:
                logger.warning(f"Project with ID {project_id} not found or inactive")
                return None

            for var, value in vars(project).items():
                setattr(db_project, var, value) if value else None

            self.db.commit()
            self.db.refresh(db_project)
            logger.info(f"Project with ID {project_id} updated successfully")
            return db_project
        except SQLAlchemyError as e:
            logger.error(f"Error updating project with ID {project_id}: {e}")
            self.db.rollback()
            raise e

    def delete_project(self, project_id: int) -> Optional[Project]:
        try:
            logger.info(f"Deleting project with ID {project_id}")
            db_project = self.db.query(Project).filter(Project.id == project_id, Project.is_active == True).first()
            if db_project is None:
                logger.warning(f"Project with ID {project_id} not found or inactive")
                return None

            db_project.is_active = False
            self.db.commit()
            self.db.refresh(db_project)
            logger.info(f"Project with ID {project_id} marked as inactive")
            return db_project
        except SQLAlchemyError as e:
            logger.error(f"Error deleting project with ID {project_id}: {e}")
            self.db.rollback()
            raise e

    def get_project_funders(self, project_id: int) -> List[Funder]:
        try:
            logger.info(f"Fetching funders for project ID {project_id}")
            project = self.get_project(project_id)
            if project:
                logger.info(f"Found {len(project.funders)} funders for project ID {project_id}")
                return project.funders
            logger.warning(f"No funders found for project ID {project_id}")
            return []
        except SQLAlchemyError as e:
            logger.error(f"Error fetching funders for project ID {project_id}: {e}")
            self.db.rollback()
            raise e

    def get_project_components(self, project_id: int) -> List[ProjectComponent]:
        try:
            logger.info(f"Fetching components for project ID {project_id}")
            project = self.get_project(project_id)
            if project:
                logger.info(f"Found {len(project.components)} components for project ID {project_id}")
                return project.components
            logger.warning(f"No components found for project ID {project_id}")
            return []
        except SQLAlchemyError as e:
            logger.error(f"Error fetching components for project ID {project_id}: {e}")
            self.db.rollback()
            raise e


    def get_project_employees(self, project_id: int):
        try:
            logger.info(f"Fetching employees for project ID {project_id}")
            project = self.db.query(Project).options(joinedload(Project.employees).joinedload(Employee.tenancy)).filter(Project.id == project_id, Project.is_active == True).first()
            if project:
                employees = [
                    {
                        "employee_id": emp.id,
                        "full_name": f"{emp.first_name} {emp.last_name}",
                        "email": emp.employee_email,
                        "phone_number": emp.phone_number,
                        "state": {
                            "tenancy_id": emp.tenancy.id,
                            "tenancy_name": emp.tenancy.name
                        } if emp.tenancy else None
                    } for emp in project.employees
                ]
                result = {
                    "project_id": project.id,
                    "project_name": project.name,
                    "employees": employees
                }
                logger.info(f"Found {len(project.employees)} employees for project ID {project_id}")
                return result
            logger.warning(f"No employees found for project ID {project_id}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error fetching employees for project ID {project_id}: {e}")
            self.db.rollback()
            raise e


    def add_tenants_to_project(self, project_id: int, tenancy_ids: List[int]) -> Optional[Project]:
        try:
            logger.info(f"Adding tenants to project with ID {project_id}")
            project = self.get_project(project_id)
            if not project:
                logger.warning(f"Project with ID {project_id} not found or inactive")
                return None

            for tenancy_id in tenancy_ids:
                tenant = self.db.query(Tenancy).filter(Tenancy.id == tenancy_id).first()
                if tenant:
                    project.tenancies.append(tenant)
                else:
                    logger.warning(f"Tenant with ID {tenancy_id} not found")

            self.db.commit()
            logger.info(f"Tenants added to project with ID {project_id}")
            return project
        except SQLAlchemyError as e:
            logger.error(f"Error adding tenants to project with ID {project_id}: {e}")
            self.db.rollback()
            raise e
        
    def add_employees_to_project(self, project_id: int, employee_ids: List[int]) -> Optional[Project]:
        try:
            logger.info(f"Adding employees to project with ID {project_id}")
            project = self.get_project(project_id)
            if not project:
                logger.warning(f"Project with ID {project_id} not found or inactive")
                return None

            for employee_id in employee_ids:
                employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
                if employee:
                    project.employees.append(employee)
                else:
                    logger.warning(f"Employee with ID {employee_id} not found")

            self.db.commit()
            logger.info(f"Employees added to project with ID {project_id}")
            return project
        except SQLAlchemyError as e:
            logger.error(f"Error adding employees to project with ID {project_id}: {e}")
            self.db.rollback()
            raise e
        

        # w=14ft=4m
        # l=18ft=6m
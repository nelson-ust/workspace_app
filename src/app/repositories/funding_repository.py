from sqlalchemy.orm import Session
from models.all_models import Funding
from schemas.funding_schemas import FundingCreate, FundingUpdate
from typing import List
from logging_helpers import logging_helper

class FundingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_funding(self, project_id: int, funder_id: int, component_id: int) -> Funding:
        try:
            logging_helper.log_info(f"Fetching funding for project_id={project_id}, funder_id={funder_id}, component_id={component_id}")
            funding = self.db.query(Funding).filter(
                Funding.project_id == project_id,
                Funding.funder_id == funder_id,
                Funding.component_id == component_id,
                Funding.is_active == True
            ).first()
            if not funding:
                logging_helper.log_warning(f"Funding not found for project_id={project_id}, funder_id={funder_id}, component_id={component_id}")
            return funding
        except Exception as e:
            logging_helper.log_error(f"An error occurred while fetching funding: {str(e)}")
            raise

    def get_fundings(self, skip: int = 0, limit: int = 100) -> List[Funding]:
        try:
            logging_helper.log_info(f"Fetching fundings with skip={skip}, limit={limit}")
            fundings = self.db.query(Funding).filter(Funding.is_active == True).offset(skip).limit(limit).all()
            logging_helper.log_info(f"Fetched {len(fundings)} fundings")
            return fundings
        except Exception as e:
            logging_helper.log_error(f"An error occurred while fetching fundings: {str(e)}")
            raise

    def create_funding(self, funding: FundingCreate) -> Funding:
        try:
            logging_helper.log_info(f"Creating new funding with data: {funding.dict()}")
            db_funding = Funding(**funding.dict())
            self.db.add(db_funding)
            self.db.commit()
            self.db.refresh(db_funding)
            logging_helper.log_info(f"Created funding with ID {db_funding.project_id}, {db_funding.funder_id}, {db_funding.component_id}")
            return db_funding
        except Exception as e:
            logging_helper.log_error(f"An error occurred while creating funding: {str(e)}")
            raise

    def update_funding(self, project_id: int, funder_id: int, component_id: int, funding: FundingUpdate) -> Funding:
        try:
            logging_helper.log_info(f"Updating funding for project_id={project_id}, funder_id={funder_id}, component_id={component_id} with data: {funding.dict(exclude_unset=True)}")
            db_funding = self.get_funding(project_id, funder_id, component_id)
            if not db_funding:
                logging_helper.log_warning(f"Funding not found for project_id={project_id}, funder_id={funder_id}, component_id={component_id}")
                return None
            for key, value in funding.dict(exclude_unset=True).items():
                setattr(db_funding, key, value)
            self.db.commit()
            self.db.refresh(db_funding)
            logging_helper.log_info(f"Updated funding for project_id={project_id}, funder_id={funder_id}, component_id={component_id}")
            return db_funding
        except Exception as e:
            logging_helper.log_error(f"An error occurred while updating funding: {str(e)}")
            raise

    def delete_funding(self, project_id: int, funder_id: int, component_id: int) -> Funding:
        try:
            logging_helper.log_info(f"Deleting funding for project_id={project_id}, funder_id={funder_id}, component_id={component_id}")
            db_funding = self.get_funding(project_id, funder_id, component_id)
            if not db_funding:
                logging_helper.log_warning(f"Funding not found for project_id={project_id}, funder_id={funder_id}, component_id={component_id}")
                return None
            db_funding.is_active = False
            self.db.commit()
            logging_helper.log_info(f"Deleted funding for project_id={project_id}, funder_id={funder_id}, component_id={component_id}")
            return db_funding
        except Exception as e:
            logging_helper.log_error(f"An error occurred while deleting funding: {str(e)}")
            raise

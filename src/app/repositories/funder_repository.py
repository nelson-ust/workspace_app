#repositories/funder_repository.py
from typing import List
from sqlalchemy.orm import Session
from models.all_models import Funder
from schemas.funder_schemas import FunderCreate, FunderUpdate
from logging_helpers import logging_helper  # Assuming this module handles logging

class FunderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_funder(self, funder_id: int) -> Funder:
        try:
            logging_helper.log_info(f"Fetching funder with ID {funder_id}")
            funder = self.db.query(Funder).filter(Funder.id == funder_id, Funder.is_active == True).first()
            if not funder:
                logging_helper.log_warning(f"Funder with ID {funder_id} not found or inactive")
            return funder
        except Exception as e:
            logging_helper.log_error(f"Error fetching funder with ID {funder_id}: {str(e)}")
            raise

    def get_funders(self, skip: int = 0, limit: int = 100) -> List[Funder]:
        try:
            logging_helper.log_info(f"Fetching funders with skip={skip} and limit={limit}")
            funders = self.db.query(Funder).filter(Funder.is_active == True).offset(skip).limit(limit).all()
            logging_helper.log_info(f"Retrieved {len(funders)} funders")
            return funders
        except Exception as e:
            logging_helper.log_error(f"Error fetching funders: {str(e)}")
            raise

    def create_funder(self, funder: FunderCreate) -> Funder:
        try:
            logging_helper.log_info(f"Creating new funder with data: {funder.dict()}")
            db_funder = Funder(**funder.dict())
            self.db.add(db_funder)
            self.db.commit()
            self.db.refresh(db_funder)
            logging_helper.log_info(f"Funder created with ID {db_funder.id}")
            return db_funder
        except Exception as e:
            logging_helper.log_error(f"Error creating funder: {str(e)}")
            self.db.rollback()
            raise

    def update_funder(self, funder_id: int, funder: FunderUpdate) -> Funder:
        try:
            logging_helper.log_info(f"Updating funder with ID {funder_id}")
            db_funder = self.db.query(Funder).filter(Funder.id == funder_id, Funder.is_active == True).first()
            if not db_funder:
                logging_helper.log_warning(f"Funder with ID {funder_id} not found or inactive")
                return None
            for key, value in funder.dict(exclude_unset=True).items():
                setattr(db_funder, key, value)
            self.db.commit()
            self.db.refresh(db_funder)
            logging_helper.log_info(f"Funder with ID {funder_id} updated successfully")
            return db_funder
        except Exception as e:
            logging_helper.log_error(f"Error updating funder with ID {funder_id}: {str(e)}")
            self.db.rollback()
            raise

    def delete_funder(self, funder_id: int) -> Funder:
        try:
            logging_helper.log_info(f"Deleting funder with ID {funder_id}")
            db_funder = self.db.query(Funder).filter(Funder.id == funder_id, Funder.is_active == True).first()
            if not db_funder:
                logging_helper.log_warning(f"Funder with ID {funder_id} not found or inactive")
                return None
            db_funder.is_active = False
            self.db.commit()
            logging_helper.log_info(f"Funder with ID {funder_id} marked as inactive")
            return db_funder
        except Exception as e:
            logging_helper.log_error(f"Error deleting funder with ID {funder_id}: {str(e)}")
            self.db.rollback()
            raise


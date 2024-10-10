# repositories/meeting_type_repository.py

from sqlalchemy.orm import Session
from models.all_models import MeetingType
from schemas.meeting_type_schemas import MeetingTypeCreate, MeetingTypeUpdate
from typing import List, Optional
from logging_helpers import logging_helper

class MeetingTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_meeting_type(self, meeting_type_id: int) -> Optional[MeetingType]:
        logging_helper.log_info(f"Fetching MeetingType with ID: {meeting_type_id}")
        meeting_type = self.db.query(MeetingType).filter(MeetingType.id == meeting_type_id, MeetingType.is_active == True).first()
        if meeting_type:
            logging_helper.log_info(f"Found MeetingType: {meeting_type}")
        else:
            logging_helper.log_warning(f"MeetingType with ID: {meeting_type_id} not found")
        return meeting_type

    def get_meeting_type_by_name(self, name: str) -> Optional[MeetingType]:
        logging_helper.log_info(f"Fetching MeetingType with name: {name}")
        meeting_type = self.db.query(MeetingType).filter(MeetingType.name == name, MeetingType.is_active == True).first()
        if meeting_type:
            logging_helper.log_info(f"Found MeetingType: {meeting_type}")
        else:
            logging_helper.log_warning(f"MeetingType with name: {name} not found")
        return meeting_type

    def get_meeting_types(self, skip: int = 0, limit: int = 100) -> List[MeetingType]:
        logging_helper.log_info(f"Fetching all MeetingTypes with skip: {skip}, limit: {limit}")
        meeting_types = self.db.query(MeetingType).filter(MeetingType.is_active == True).offset(skip).limit(limit).all()
        logging_helper.log_info(f"Found {len(meeting_types)} MeetingTypes")
        return meeting_types

    def create_meeting_type(self, meeting_type: MeetingTypeCreate) -> MeetingType:
        logging_helper.log_info(f"Creating new MeetingType with name: {meeting_type.name}")
        db_meeting_type = MeetingType(
            name=meeting_type.name,
        )
        self.db.add(db_meeting_type)
        self.db.commit()
        self.db.refresh(db_meeting_type)
        logging_helper.log_info(f"Created MeetingType: {db_meeting_type}")
        return db_meeting_type

    def update_meeting_type(self, meeting_type_id: int, meeting_type: MeetingTypeUpdate) -> Optional[MeetingType]:
        logging_helper.log_info(f"Updating MeetingType with ID: {meeting_type_id}")
        db_meeting_type = self.get_meeting_type(meeting_type_id)
        if db_meeting_type:
            for var, value in vars(meeting_type).items():
                if value is not None:
                    setattr(db_meeting_type, var, value)
            self.db.commit()
            self.db.refresh(db_meeting_type)
            logging_helper.log_info(f"Updated MeetingType: {db_meeting_type}")
        else:
            logging_helper.log_warning(f"MeetingType with ID: {meeting_type_id} not found for update")
        return db_meeting_type

    def delete_meeting_type(self, meeting_type_id: int) -> Optional[MeetingType]:
        logging_helper.log_info(f"Deleting (soft delete) MeetingType with ID: {meeting_type_id}")
        db_meeting_type = self.get_meeting_type(meeting_type_id)
        if db_meeting_type:
            db_meeting_type.is_active = False
            self.db.commit()
            self.db.refresh(db_meeting_type)
            logging_helper.log_info(f"Soft deleted MeetingType: {db_meeting_type}")
        else:
            logging_helper.log_warning(f"MeetingType with ID: {meeting_type_id} not found for deletion")
        return db_meeting_type

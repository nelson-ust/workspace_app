# #third_party_participant_repository.py
# from typing import Optional
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from models.all_models import ThirdPartyParticipant
# from schemas.company_schemas import ThirdPartyParticipantCreate
# from logging_helpers import logging_helper

# class ThirdPartyParticipantRepository:

#     def __init__(self, db_session: Session):
#         self.db_session = db_session

#     def add_third_party_participant(self, name: str, email: str, phone_number: Optional[str], company_id: Optional[int], site_id: Optional[int], meeting_id: Optional[int]):
#         try:
#             participant = ThirdPartyParticipant(
#                 name=name,
#                 email=email,
#                 phone_number=phone_number,
#                 company_id=company_id,
#                 site_id=site_id,
#                 meeting_id=meeting_id
#             )
#             self.db_session.add(participant)
#             self.db_session.commit()
#             logging_helper.log_info(f"Added third-party participant with ID: {participant.id} to company ID: {company_id}")
#             return participant
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error adding third-party participant: {e}")
#             raise e

#     def get_third_party_participant_by_id(self, participant_id: int):
#         try:
#             participant = self.db_session.query(ThirdPartyParticipant).filter(ThirdPartyParticipant.id == participant_id).first()
#             logging_helper.log_info(f"Fetched third-party participant with ID: {participant_id}")
#             return participant
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error fetching third-party participant with ID: {participant_id}: {e}")
#             raise e

#     def get_all_third_party_participants(self):
#         try:
#             participants = self.db_session.query(ThirdPartyParticipant).all()
#             logging_helper.log_info("Fetched all third-party participants")
#             return participants
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error fetching all third-party participants: {e}")
#             raise e

#     def update_third_party_participant(self, participant_id: int, **kwargs):
#         try:
#             participant = self.get_third_party_participant_by_id(participant_id)
#             if not participant:
#                 logging_helper.log_error(f"Third-party participant not found with ID: {participant_id}")
#                 return None
#             for key, value in kwargs.items():
#                 setattr(participant, key, value)
#             self.db_session.commit()
#             logging_helper.log_info(f"Updated third-party participant with ID: {participant_id}")
#             return participant
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error updating third-party participant with ID: {participant_id}: {e}")
#             raise e

#     def delete_third_party_participant(self, participant_id: int):
#         try:
#             participant = self.get_third_party_participant_by_id(participant_id)
#             if not participant:
#                 logging_helper.log_error(f"Third-party participant not found with ID: {participant_id}")
#                 return None
#             self.db_session.delete(participant)
#             self.db_session.commit()
#             logging_helper.log_info(f"Deleted third-party participant with ID: {participant_id}")
#             return participant
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error deleting third-party participant with ID: {participant_id}: {e}")
#             raise e



# repositories/third_party_participant_repository.py

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.all_models import ThirdPartyParticipant
from schemas.company_schemas import ThirdPartyParticipantCreate
from logging_helpers import logging_helper

class ThirdPartyParticipantRepository:

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def add_third_party_participant(self, name: str, email: str, phone_number: Optional[str], company_id: Optional[int], site_id: Optional[int], meeting_id: Optional[int]):
        try:
            participant = ThirdPartyParticipant(
                name=name,
                email=email,
                phone_number=phone_number,
                company_id=company_id,
                site_id=site_id,
                meeting_id=meeting_id
            )
            self.db_session.add(participant)
            self.db_session.commit()
            logging_helper.log_info(f"Added third-party participant with ID: {participant.id} to company ID: {company_id}")
            return participant
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error adding third-party participant: {e}")
            raise e

    def get_third_party_participant_by_id(self, participant_id: int):
        try:
            participant = self.db_session.query(ThirdPartyParticipant).filter(ThirdPartyParticipant.id == participant_id).first()
            logging_helper.log_info(f"Fetched third-party participant with ID: {participant_id}")
            return participant
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching third-party participant with ID: {participant_id}: {e}")
            raise e

    def get_all_third_party_participants(self):
        try:
            participants = self.db_session.query(ThirdPartyParticipant).all()
            logging_helper.log_info("Fetched all third-party participants")
            return participants
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching all third-party participants: {e}")
            raise e

    def update_third_party_participant(self, participant_id: int, **kwargs):
        try:
            participant = self.get_third_party_participant_by_id(participant_id)
            if not participant:
                logging_helper.log_error(f"Third-party participant not found with ID: {participant_id}")
                return None
            for key, value in kwargs.items():
                setattr(participant, key, value)
            self.db_session.commit()
            logging_helper.log_info(f"Updated third-party participant with ID: {participant_id}")
            return participant
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error updating third-party participant with ID: {participant_id}: {e}")
            raise e

    def delete_third_party_participant(self, participant_id: int):
        try:
            participant = self.get_third_party_participant_by_id(participant_id)
            if not participant:
                logging_helper.log_error(f"Third-party participant not found with ID: {participant_id}")
                return None
            self.db_session.delete(participant)
            self.db_session.commit()
            logging_helper.log_info(f"Deleted third-party participant with ID: {participant_id}")
            return participant
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error deleting third-party participant with ID: {participant_id}: {e}")
            raise e

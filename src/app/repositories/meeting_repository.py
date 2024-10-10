# # repositories/meeting_repository.py

# from sqlalchemy.orm import Session
# from models.all_models import (
#     Meeting, MeetingType, Company, ThirdPartyParticipant, MealCombination,
#     MealSelection, MeetingParticipant, MeetingAttendance, MeetingMinutes, Employee
# )
# from sqlalchemy.exc import SQLAlchemyError
# import datetime
# from logging_helpers import logging_helper

# class MeetingRepository:

#     def __init__(self, db_session: Session):
#         self.db_session = db_session


#     def create_meeting(self, name: str, date_start: datetime.datetime, date_end: datetime.datetime, meeting_type_id: int,
#                        organizer_id: int, meeting_category: str, is_meal_required: bool,
#                        is_third_party_required: bool):
#         try:
#             meeting = Meeting(
#                 name=name,
#                 date_start=date_start,
#                 date_end=date_end,
#                 meeting_type_id=meeting_type_id,
#                 organizer_id=organizer_id,
#                 meeting_category=meeting_category,
#                 is_meal_required=is_meal_required,
#                 is_third_party_required=is_third_party_required
#             )
#             self.db_session.add(meeting)
#             self.db_session.commit()
#             logging_helper.log_info(f"Created meeting with ID: {meeting.id}")
#             return meeting
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error creating meeting: {e}")
#             raise e


#     def get_meeting_by_id(self, meeting_id: int):
#         try:
#             meeting = self.db_session.query(Meeting).filter(Meeting.id == meeting_id).first()
#             logging_helper.log_info(f"Fetched meeting with ID: {meeting_id}")
#             return meeting
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error fetching meeting with ID: {meeting_id}: {e}")
#             raise e

#     def get_all_meetings(self):
#         try:
#             meetings = self.db_session.query(Meeting).all()
#             logging_helper.log_info("Fetched all meetings")
#             return meetings
#         except SQLAlchemyError as e:
#             logging_helper.log_error("Error fetching all meetings: {e}")
#             raise e

#     def update_meeting(self, meeting_id: int, **kwargs):
#         try:
#             meeting = self.get_meeting_by_id(meeting_id)
#             if not meeting:
#                 logging_helper.log_error(f"Meeting not found with ID: {meeting_id}")
#                 return None
#             for key, value in kwargs.items():
#                 setattr(meeting, key, value)
#             self.db_session.commit()
#             logging_helper.log_info(f"Updated meeting with ID: {meeting_id}")
#             return meeting
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error updating meeting with ID: {meeting_id}: {e}")
#             raise e

#     def delete_meeting(self, meeting_id: int):
#         try:
#             meeting = self.get_meeting_by_id(meeting_id)
#             if not meeting:
#                 logging_helper.log_error(f"Meeting not found with ID: {meeting_id}")
#                 return None
#             self.db_session.delete(meeting)
#             self.db_session.commit()
#             logging_helper.log_info(f"Deleted meeting with ID: {meeting_id}")
#             return meeting
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error deleting meeting with ID: {meeting_id}: {e}")
#             raise e

#     def add_meal_selection(self, meeting_id: int, selection_type: str, meal_combination_id: int, employee_id: int = None, third_party_participant_id: int = None):
#         try:
#             meal_selection = MealSelection(
#                 meeting_id=meeting_id,
#                 selection_type=selection_type,
#                 meal_combination_id=meal_combination_id,
#                 employee_id=employee_id,
#                 third_party_participant_id=third_party_participant_id
#             )
#             self.db_session.add(meal_selection)
#             self.db_session.commit()
#             logging_helper.log_info(f"Added meal selection for meeting ID: {meeting_id}")
#             return meal_selection
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error adding meal selection for meeting ID: {meeting_id}: {e}")
#             raise e

#     def add_participant(self, meeting_id: int, participant_type: str, employee_id: int = None, third_party_participant_id: int = None):
#         try:
#             participant = MeetingParticipant(
#                 meeting_id=meeting_id,
#                 participant_type=participant_type,
#                 employee_id=employee_id,
#                 third_party_participant_id=third_party_participant_id
#             )
#             self.db_session.add(participant)
#             self.db_session.commit()
#             logging_helper.log_info(f"Added participant for meeting ID: {meeting_id}")
#             return participant
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error adding participant for meeting ID: {meeting_id}: {e}")
#             raise e

#     def add_meeting_minutes(self, meeting_id: int, content: str):
#         try:
#             minutes = MeetingMinutes(
#                 meeting_id=meeting_id,
#                 content=content
#             )
#             self.db_session.add(minutes)
#             self.db_session.commit()
#             logging_helper.log_info(f"Added minutes for meeting ID: {meeting_id}")
#             return minutes
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error adding minutes for meeting ID: {meeting_id}: {e}")
#             raise e

#     def add_attendance(self, meeting_id: int, participant_type: str, employee_id: int = None, third_party_participant_id: int = None, attended: bool = False):
#         try:
#             attendance = MeetingAttendance(
#                 meeting_id=meeting_id,
#                 participant_type=participant_type,
#                 employee_id=employee_id,
#                 third_party_participant_id=third_party_participant_id,
#                 attended=attended
#             )
#             self.db_session.add(attendance)
#             self.db_session.commit()
#             logging_helper.log_info(f"Added attendance for meeting ID: {meeting_id}")
#             return attendance
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error adding attendance for meeting ID: {meeting_id}: {e}")
#             raise e

#     # Additional methods to manage related entities like companies, meal combinations, etc.
#     def get_meeting_types(self):
#         try:
#             meeting_types = self.db_session.query(MeetingType).all()
#             logging_helper.log_info("Fetched all meeting types")
#             return meeting_types
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error fetching meeting types: {e}")
#             raise e

#     def get_companies(self):
#         try:
#             companies = self.db_session.query(Company).all()
#             logging_helper.log_info("Fetched all companies")
#             return companies
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error fetching companies: {e}")
#             raise e

#     def get_meal_combinations(self):
#         try:
#             meal_combinations = self.db_session.query(MealCombination).all()
#             logging_helper.log_info("Fetched all meal combinations")
#             return meal_combinations
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error fetching meal combinations: {e}")
#             raise e




# repositories/meeting_repository.py

from sqlalchemy.orm import Session
from models.all_models import (
    Meeting, MeetingType, Company, ThirdPartyParticipant, MealCombination,
    MealSelection, MeetingParticipant, MeetingAttendance, MeetingMinutes, Employee
)
from sqlalchemy.exc import SQLAlchemyError
import datetime
from logging_helpers import logging_helper

class MeetingRepository:

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_meeting(self, name: str, date_start: datetime.datetime, date_end: datetime.datetime, meeting_type_id: int,
                       organizer_id: int, meeting_category: str, is_meal_required: bool,
                       is_third_party_required: bool):
        try:
            meeting = Meeting(
                name=name,
                date_start=date_start,
                date_end=date_end,
                meeting_type_id=meeting_type_id,
                organizer_id=organizer_id,
                meeting_category=meeting_category,
                is_meal_required=is_meal_required,
                is_third_party_required=is_third_party_required
            )
            self.db_session.add(meeting)
            self.db_session.commit()
            logging_helper.log_info(f"Created meeting with ID: {meeting.id}")
            return meeting
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error creating meeting: {e}")
            raise e

    def get_meeting_by_id(self, meeting_id: int):
        try:
            meeting = self.db_session.query(Meeting).filter(Meeting.id == meeting_id).first()
            logging_helper.log_info(f"Fetched meeting with ID: {meeting_id}")
            return meeting
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching meeting with ID: {meeting_id}: {e}")
            raise e

    def get_all_meetings(self):
        try:
            meetings = self.db_session.query(Meeting).all()
            logging_helper.log_info("Fetched all meetings")
            return meetings
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching all meetings: {e}")
            raise e

    def update_meeting(self, meeting_id: int, **kwargs):
        try:
            meeting = self.get_meeting_by_id(meeting_id)
            if not meeting:
                logging_helper.log_error(f"Meeting not found with ID: {meeting_id}")
                return None
            for key, value in kwargs.items():
                setattr(meeting, key, value)
            self.db_session.commit()
            logging_helper.log_info(f"Updated meeting with ID: {meeting_id}")
            return meeting
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error updating meeting with ID: {meeting_id}: {e}")
            raise e

    def delete_meeting(self, meeting_id: int):
        try:
            meeting = self.get_meeting_by_id(meeting_id)
            if not meeting:
                logging_helper.log_error(f"Meeting not found with ID: {meeting_id}")
                return None
            self.db_session.delete(meeting)
            self.db_session.commit()
            logging_helper.log_info(f"Deleted meeting with ID: {meeting_id}")
            return meeting
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error deleting meeting with ID: {meeting_id}: {e}")
            raise e

    def add_meal_selection(self, meeting_id: int, selection_type: str, meal_combination_id: int, employee_id: int = None, third_party_participant_id: int = None):
        try:
            meal_selection = MealSelection(
                meeting_id=meeting_id,
                selection_type=selection_type,
                meal_combination_id=meal_combination_id,
                employee_id=employee_id,
                third_party_participant_id=third_party_participant_id
            )
            self.db_session.add(meal_selection)
            self.db_session.commit()
            logging_helper.log_info(f"Added meal selection for meeting ID: {meeting_id}")
            return meal_selection
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error adding meal selection for meeting ID: {meeting_id}: {e}")
            raise e

    def add_participant(self, meeting_id: int, participant_type: str, employee_id: int = None, third_party_participant_id: int = None):
        try:
            participant = MeetingParticipant(
                meeting_id=meeting_id,
                participant_type=participant_type,
                employee_id=employee_id,
                third_party_participant_id=third_party_participant_id
            )
            self.db_session.add(participant)
            self.db_session.commit()
            logging_helper.log_info(f"Added participant for meeting ID: {meeting_id}")
            return participant
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error adding participant for meeting ID: {meeting_id}: {e}")
            raise e

    def add_meeting_minutes(self, meeting_id: int, content: str):
        try:
            minutes = MeetingMinutes(
                meeting_id=meeting_id,
                content=content
            )
            self.db_session.add(minutes)
            self.db_session.commit()
            logging_helper.log_info(f"Added minutes for meeting ID: {meeting_id}")
            return minutes
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error adding minutes for meeting ID: {meeting_id}: {e}")
            raise e

    def add_attendance(self, meeting_id: int, participant_type: str, employee_id: int = None, third_party_participant_id: int = None, attended: bool = False):
        try:
            attendance = MeetingAttendance(
                meeting_id=meeting_id,
                participant_type=participant_type,
                employee_id=employee_id,
                third_party_participant_id=third_party_participant_id,
                attended=attended
            )
            self.db_session.add(attendance)
            self.db_session.commit()
            logging_helper.log_info(f"Added attendance for meeting ID: {meeting_id}")
            return attendance
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error adding attendance for meeting ID: {meeting_id}: {e}")
            raise e

    def add_coordinator(self, meeting_id: int, employee_id: int):
        try:
            meeting = self.get_meeting_by_id(meeting_id)
            if not meeting:
                logging_helper.log_error(f"Meeting not found with ID: {meeting_id}")
                return None
            employee = self.db_session.query(Employee).filter(Employee.id == employee_id).first()
            if not employee:
                logging_helper.log_error(f"Employee not found with ID: {employee_id}")
                return None
            meeting.coordinators.append(employee)
            self.db_session.commit()
            logging_helper.log_info(f"Added coordinator with ID: {employee_id} to meeting ID: {meeting_id}")
            return meeting
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error adding coordinator with ID: {employee_id} to meeting ID: {meeting_id}: {e}")
            raise e

    def add_moderator(self, meeting_id: int, employee_id: int):
        try:
            meeting = self.get_meeting_by_id(meeting_id)
            if not meeting:
                logging_helper.log_error(f"Meeting not found with ID: {meeting_id}")
                return None
            employee = self.db_session.query(Employee).filter(Employee.id == employee_id).first()
            if not employee:
                logging_helper.log_error(f"Employee not found with ID: {employee_id}")
                return None
            meeting.moderators.append(employee)
            self.db_session.commit()
            logging_helper.log_info(f"Added moderator with ID: {employee_id} to meeting ID: {meeting_id}")
            return meeting
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error adding moderator with ID: {employee_id} to meeting ID: {meeting_id}: {e}")
            raise e

    # Additional methods to manage related entities like companies, meal combinations, etc.
    def get_meeting_types(self):
        try:
            meeting_types = self.db_session.query(MeetingType).all()
            logging_helper.log_info("Fetched all meeting types")
            return meeting_types
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching meeting types: {e}")
            raise e

    def get_companies(self):
        try:
            companies = self.db_session.query(Company).all()
            logging_helper.log_info("Fetched all companies")
            return companies
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching companies: {e}")
            raise e

    def get_meal_combinations(self):
        try:
            meal_combinations = self.db_session.query(MealCombination).all()
            logging_helper.log_info("Fetched all meal combinations")
            return meal_combinations
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching meal combinations: {e}")
            raise e

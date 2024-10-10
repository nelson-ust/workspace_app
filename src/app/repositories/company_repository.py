# from typing import Optional
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from models.all_models import Company, ThirdPartyParticipant
# from schemas.company_schemas import CompanyCreate
# from logging_helpers import logging_helper

# class CompanyRepository:

#     def __init__(self, db_session: Session):
#         self.db_session = db_session

#     def create_company(self, company_data: CompanyCreate):
#         try:
#             company = Company(**company_data.dict())
#             self.db_session.add(company)
#             self.db_session.commit()
#             logging_helper.log_info(f"Created company with ID: {company.id}")
#             return company
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error creating company: {e}")
#             raise e

#     def get_company_by_id(self, company_id: int):
#         try:
#             company = self.db_session.query(Company).filter(Company.id == company_id).first()
#             logging_helper.log_info(f"Fetched company with ID: {company_id}")
#             return company
#         except SQLAlchemyError as e:
#             logging_helper.log_error(f"Error fetching company with ID: {company_id}: {e}")
#             raise e

#     def get_all_companies(self):
#         try:
#             companies = self.db_session.query(Company).all()
#             logging_helper.log_info("Fetched all companies")
#             return companies
#         except SQLAlchemyError as e:
#             logging_helper.log_error("Error fetching all companies: {e}")
#             raise e

#     def update_company(self, company_id: int, name: str = None):
#         try:
#             company = self.get_company_by_id(company_id)
#             if not company:
#                 logging_helper.log_error(f"Company not found with ID: {company_id}")
#                 return None
#             if name:
#                 company.name = name
#             self.db_session.commit()
#             logging_helper.log_info(f"Updated company with ID: {company_id}")
#             return company
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error updating company with ID: {company_id}: {e}")
#             raise e

#     def delete_company(self, company_id: int):
#         try:
#             company = self.get_company_by_id(company_id)
#             if not company:
#                 logging_helper.log_error(f"Company not found with ID: {company_id}")
#                 return None
#             self.db_session.delete(company)
#             self.db_session.commit()
#             logging_helper.log_info(f"Deleted company with ID: {company_id}")
#             return company
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error deleting company with ID: {company_id}: {e}")
#             raise e

#     def add_third_party_participant(self, name: str, email: str, phone_number: Optional[str], company_id: Optional[int], site_id: Optional[int]):
#         try:
#             participant = ThirdPartyParticipant(
#                 name=name,
#                 email=email,
#                 phone_number=phone_number,
#                 company_id=company_id,
#                 site_id=site_id
#             )
#             self.db_session.add(participant)
#             self.db_session.commit()
#             logging_helper.log_info(f"Added third-party participant with ID: {participant.id} to company ID: {company_id}")
#             return participant
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             logging_helper.log_error(f"Error adding third-party participant: {e}")
#             raise e



from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.all_models import Company, ThirdPartyParticipant
from schemas.company_schemas import CompanyCreate
from logging_helpers import logging_helper

class CompanyRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_company(self, company_data: CompanyCreate):
        """
        Create a new company record in the database.

        Args:
            company_data (CompanyCreate): The data for the new company.

        Returns:
            Company: The newly created company object.

        Raises:
            SQLAlchemyError: If there is an error during the creation process.
        """
        try:
            company = Company(**company_data.dict())
            self.db_session.add(company)
            self.db_session.commit()
            logging_helper.log_info(f"Created company with ID: {company.id}")
            return company
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error creating company: {e}")
            raise e

    def get_company_by_id(self, company_id: int):
        """
        Retrieve a company by its ID.

        Args:
            company_id (int): The ID of the company to retrieve.

        Returns:
            Company: The company object if found, else None.

        Raises:
            SQLAlchemyError: If there is an error during the retrieval process.
        """
        try:
            company = self.db_session.query(Company).filter(Company.id == company_id).first()
            logging_helper.log_info(f"Fetched company with ID: {company_id}")
            return company
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching company with ID: {company_id}: {e}")
            raise e

    def get_all_companies(self):
        """
        Retrieve all companies from the database.

        Returns:
            List[Company]: A list of all company objects.

        Raises:
            SQLAlchemyError: If there is an error during the retrieval process.
        """
        try:
            companies = self.db_session.query(Company).all()
            logging_helper.log_info("Fetched all companies")
            return companies
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching all companies: {e}")
            raise e

    def update_company(self, company_id: int, name: str = None):
        """
        Update a company's details.

        Args:
            company_id (int): The ID of the company to update.
            name (str, optional): The new name for the company.

        Returns:
            Company: The updated company object if found, else None.

        Raises:
            SQLAlchemyError: If there is an error during the update process.
        """
        try:
            company = self.get_company_by_id(company_id)
            if not company:
                logging_helper.log_error(f"Company not found with ID: {company_id}")
                return None
            if name:
                company.name = name
            self.db_session.commit()
            logging_helper.log_info(f"Updated company with ID: {company_id}")
            return company
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error updating company with ID: {company_id}: {e}")
            raise e

    def delete_company(self, company_id: int):
        """
        Delete a company from the database.

        Args:
            company_id (int): The ID of the company to delete.

        Returns:
            Company: The deleted company object if found, else None.

        Raises:
            SQLAlchemyError: If there is an error during the deletion process.
        """
        try:
            company = self.get_company_by_id(company_id)
            if not company:
                logging_helper.log_error(f"Company not found with ID: {company_id}")
                return None
            self.db_session.delete(company)
            self.db_session.commit()
            logging_helper.log_info(f"Deleted company with ID: {company_id}")
            return company
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error deleting company with ID: {company_id}: {e}")
            raise e

    def add_third_party_participant(self, name: str, email: str, phone_number: Optional[str], company_id: Optional[int], site_id: Optional[int]):
        """
        Add a third-party participant to a company or site.

        Args:
            name (str): The name of the participant.
            email (str): The email of the participant.
            phone_number (Optional[str]): The phone number of the participant.
            company_id (Optional[int]): The ID of the associated company.
            site_id (Optional[int]): The ID of the associated site.

        Returns:
            ThirdPartyParticipant: The newly created third-party participant object.

        Raises:
            SQLAlchemyError: If there is an error during the creation process.
        """
        try:
            participant = ThirdPartyParticipant(
                name=name,
                email=email,
                phone_number=phone_number,
                company_id=company_id,
                site_id=site_id
            )
            self.db_session.add(participant)
            self.db_session.commit()
            logging_helper.log_info(f"Added third-party participant with ID: {participant.id} to company ID: {company_id}")
            return participant
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error adding third-party participant: {e}")
            raise e

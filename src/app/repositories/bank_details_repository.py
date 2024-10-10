from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.all_models import BankDetail, Employee, Project, Tenancy
from fastapi import HTTPException
from typing import List, Optional
import logging


class BankDetailsRepository:
    def __init__(self, db_session: Session):
        """
        Initialize the BankDetailsRepository with a database session.

        Args:
            db_session (Session): SQLAlchemy session object.
        """
        self.db_session = db_session

    # def create_bank_detail(
    #     self, employee_id: int, bank_name: str, account_number: str, ifsc_code: Optional[str] = None
    # ) -> BankDetail:
    #     """
    #     Create a new bank detail record for an employee.

    #     Args:
    #         employee_id (int): The ID of the employee.
    #         bank_name (str): The name of the bank.
    #         account_number (str): The account number of the employee.
    #         ifsc_code (Optional[str]): The IFSC code of the bank.

    #     Returns:
    #         BankDetail: The created bank detail record.

    #     Raises:
    #         HTTPException: If there is any error during the process.
    #     """
    #     try:
    #         new_bank_detail = BankDetail(
    #             employee_id=employee_id,
    #             bank_name=bank_name,
    #             account_number=account_number,
    #             ifsc_code=ifsc_code,
    #         )
    #         self.db_session.add(new_bank_detail)
    #         self.db_session.commit()
    #         self.db_session.refresh(new_bank_detail)
    #         return new_bank_detail
    #     except SQLAlchemyError as e:
    #         self.db_session.rollback()
    #         logging.error(f"Database error occurred: {str(e)}")
    #         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    def create_bank_detail(
        self, employee_id: int, bank_name: str, account_number: str, ifsc_code: Optional[str] = None
    ) -> BankDetail:
        """
        Create a new bank detail record for an employee.

        Args:
            employee_id (int): The ID of the employee.
            bank_name (str): The name of the bank.
            account_number (str): The account number of the employee.
            ifsc_code (Optional[str]): The IFSC code of the bank.

        Returns:
            BankDetail: The created bank detail record.

        Raises:
            HTTPException: If there is any error during the process or if the account number already exists.
        """
        try:
            # Check if account number already exists
            existing_detail = self.db_session.query(BankDetail).filter_by(account_number=account_number).first()
            if existing_detail:
                raise HTTPException(status_code=400, detail="Account number already exists.")

            new_bank_detail = BankDetail(
                employee_id=employee_id,
                bank_name=bank_name,
                account_number=account_number,
                ifsc_code=ifsc_code,
            )
            self.db_session.add(new_bank_detail)
            self.db_session.commit()
            self.db_session.refresh(new_bank_detail)
            return new_bank_detail
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging.error(f"Database error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



    def get_bank_details_by_employee(self, employee_id: int) -> List[BankDetail]:
        """
        Retrieve all bank details for a specific employee.

        Args:
            employee_id (int): The ID of the employee.

        Returns:
            List[BankDetail]: A list of bank detail records for the employee.

        Raises:
            HTTPException: If there is any error during the process.
        """
        try:
            bank_details = (
                self.db_session.query(BankDetail).filter_by(employee_id=employee_id).all()
            )
            return bank_details
        except SQLAlchemyError as e:
            logging.error(f"Database error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def get_bank_detail_by_id(self, bank_detail_id: int) -> Optional[BankDetail]:
        """
        Retrieve a specific bank detail record by its ID.

        Args:
            bank_detail_id (int): The ID of the bank detail record.

        Returns:
            Optional[BankDetail]: The bank detail record if found, otherwise None.

        Raises:
            HTTPException: If there is any error during the process.
        """
        try:
            bank_detail = (
                self.db_session.query(BankDetail).filter_by(id=bank_detail_id).first()
            )
            return bank_detail
        except SQLAlchemyError as e:
            logging.error(f"Database error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def delete_bank_detail(self, bank_detail_id: int) -> None:
        """
        Delete a specific bank detail record by its ID.

        Args:
            bank_detail_id (int): The ID of the bank detail record to delete.

        Raises:
            HTTPException: If the bank detail record is not found or if there is any error during the process.
        """
        try:
            bank_detail = (
                self.db_session.query(BankDetail).filter_by(id=bank_detail_id).first()
            )
            if not bank_detail:
                raise HTTPException(status_code=404, detail="Bank detail not found.")

            self.db_session.delete(bank_detail)
            self.db_session.commit()
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging.error(f"Database error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def update_bank_detail(
        self,
        bank_detail_id: int,
        bank_name: Optional[str] = None,
        account_number: Optional[str] = None,
        ifsc_code: Optional[str] = None,
    ) -> BankDetail:
        """
        Update an existing bank detail record.

        Args:
            bank_detail_id (int): The ID of the bank detail record to update.
            bank_name (Optional[str]): The updated bank name.
            account_number (Optional[str]): The updated account number.
            ifsc_code (Optional[str]): The updated IFSC code.

        Returns:
            BankDetail: The updated bank detail record.

        Raises:
            HTTPException: If the bank detail record is not found or if there is any error during the process.
        """
        try:
            bank_detail = (
                self.db_session.query(BankDetail).filter_by(id=bank_detail_id).first()
            )
            if not bank_detail:
                raise HTTPException(status_code=404, detail="Bank detail not found.")

            if bank_name is not None:
                bank_detail.bank_name = bank_name
            if account_number is not None:
                bank_detail.account_number = account_number
            if ifsc_code is not None:
                bank_detail.ifsc_code = ifsc_code

            self.db_session.commit()
            self.db_session.refresh(bank_detail)
            return bank_detail
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging.error(f"Database error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def get_all_bank_details(self) -> List[BankDetail]:
        """
        Retrieve all bank details records.

        Returns:
            List[BankDetail]: A list of all bank detail records.

        Raises:
            HTTPException: If there is any error during the process.
        """
        try:
            bank_details = self.db_session.query(BankDetail).all()
            return bank_details
        except SQLAlchemyError as e:
            logging.error(f"Database error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # def get_bank_details_by_project_or_tenancy(
    #     self, project_id: Optional[int] = None, tenancy_id: Optional[int] = None
    # ) -> List[BankDetail]:
    #     """
    #     Retrieve bank details for all employees associated with a specific project or tenancy.

    #     Args:
    #         project_id (Optional[int]): The ID of the project.
    #         tenancy_id (Optional[int]): The ID of the tenancy.

    #     Returns:
    #         List[BankDetail]: A list of bank detail records for the employees associated with the project or tenancy.

    #     Raises:
    #         HTTPException: If there is any error during the process.
    #     """
    #     try:
    #         if project_id:
    #             employees = (
    #                 self.db_session.query(Employee)
    #                 .join(Employee.projects)
    #                 .filter(Project.id == project_id)
    #                 .all()
    #             )
    #         elif tenancy_id:
    #             employees = (
    #                 self.db_session.query(Employee)
    #                 .filter(Employee.tenancy_id == tenancy_id)
    #                 .all()
    #             )
    #         else:
    #             raise HTTPException(
    #                 status_code=400, detail="Project ID or Tenancy ID must be provided."
    #             )

    #         if not employees:
    #             return []

    #         employee_ids = [employee.id for employee in employees]

    #         bank_details = (
    #             self.db_session.query(BankDetail)
    #             .filter(BankDetail.employee_id.in_(employee_ids))
    #             .all()
    #         )

    #         return bank_details
    #     except SQLAlchemyError as e:
    #         logging.error(f"Database error occurred: {str(e)}")
    #         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def get_bank_details_by_project_or_tenancy(
        self, project_ids: Optional[List[int]] = None, tenancy_ids: Optional[List[int]] = None
    ) -> List[BankDetail]:
        """
        Retrieve bank details for all employees associated with specific projects or tenancies.

        Args:
            project_ids (Optional[List[int]]): List of project IDs.
            tenancy_ids (Optional[List[int]]): List of tenancy IDs.

        Returns:
            List[BankDetail]: A list of bank detail records for the employees associated with the projects or tenancies.

        Raises:
            HTTPException: If there is any error during the process.
        """
        try:
            if project_ids:
                employees = (
                    self.db_session.query(Employee)
                    .join(Employee.projects)
                    .filter(Project.id.in_(project_ids))
                    .all()
                )
            elif tenancy_ids:
                employees = (
                    self.db_session.query(Employee)
                    .filter(Employee.tenancy_id.in_(tenancy_ids))
                    .all()
                )
            else:
                raise HTTPException(
                    status_code=400, detail="Project IDs or Tenancy IDs must be provided."
                )

            if not employees:
                return []

            employee_ids = [employee.id for employee in employees]

            bank_details = (
                self.db_session.query(BankDetail)
                .filter(BankDetail.employee_id.in_(employee_ids))
                .all()
            )

            return bank_details
        except SQLAlchemyError as e:
            logging.error(f"Database error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# # repositories/employee_routes.py
# from schemas.employee_schemas import EmployeeCreate, EmployeeUpdate
# from repositories.base_repository import BaseRepository
# from models.all_models import SRT, Department, Employee as EmployeeModel, Unit, employee_srt_association
# from sqlalchemy import func, or_
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from typing import Any, Dict, List, Optional
# from fastapi import HTTPException
# from sqlalchemy.orm import joinedload


# class EmployeeRepository(BaseRepository[EmployeeModel, EmployeeCreate, EmployeeUpdate]):
#     def __init__(self, db_session: Session):
#         super().__init__(EmployeeModel, db_session)

#     def _fetch_srts_by_ids(self, srt_ids: List[int]) -> List[SRT]:
#         """Fetches SRT records by their IDs."""
#         return self.db_session.query(SRT).filter(SRT.id.in_(srt_ids)).all()
    
#     def get_all_employees(self, skip: int = 0, limit: int = 100) -> List[EmployeeModel]:
#         """Fetches all employee records with optional pagination."""
#         return self.db_session.query(EmployeeModel).offset(skip).limit(limit).all()
   
#     def create_employee(self, employee_data: EmployeeCreate) -> EmployeeModel:
#         # Create the employee without immediately linking to SRT, department, or unit
#         employee = EmployeeModel(
#             first_name=employee_data.first_name,
#             last_name=employee_data.last_name,
#             phone_number=employee_data.phone_number,
#             department_id= employee_data.department_id,
#             unit_id =employee_data.unit_id,
#             staff_code =employee_data.staff_code,
#             employee_email = employee_data.employee_email,
#             address=employee_data.address,
#             state_origin =employee_data.state_origin,
#             lga_origin =employee_data.lga_origin,
#             designation_id=employee_data.designation_id,
#             tenancy_id=employee_data.tenancy_id


#             # Initially, do not assign department_id or unit_id
#             # These can be added later as part of an update operation
#         )
        
#         self.db_session.add(employee)
#         try:
#             self.db_session.commit()
#             return employee
#         except Exception as e:
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Failed to create employee: {str(e)}")      
    

#     def update_employee(self, employee_id: int, employee_data: EmployeeUpdate) -> Optional[EmployeeModel]:
#         """Updates an employee record including SRT assignments."""
#         employee = self.get_employee_by_id(employee_id)
#         if not employee:
#             return None
#         # Fetch and update SRT associations if srt_ids is provided in employee_data
#         if 'srt_ids' in employee_data.dict():
#             srts = self._fetch_srts_by_ids(employee_data.srt_ids)
#             employee.srts = srts
#         # Update other fields as before
#         for attr, value in employee_data.dict(exclude={'srt_ids'}).items():
#             setattr(employee, attr, value)
#         try:
#             self.db_session.commit()
#             return employee
#         except SQLAlchemyError as e:
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=str(e))


#     def find_employees_without_department(self) -> List[EmployeeModel]:
#         return self.db_session.query(EmployeeModel).filter(EmployeeModel.department_id == None).all()

#     def count_employees_by_department(self) -> List[Dict[str, Any]]:
#         return self.db_session.query(
#             Department.name, func.count(EmployeeModel.id).label('employee_count')
#         ).join(EmployeeModel.department).group_by(Department.name).all()

#     def update_employee_department(self, employee_id: int, department_id: int) -> Optional[EmployeeModel]:
#         employee = self.get_employee_by_id(employee_id)
#         if employee:
#             employee.department_id = department_id
#             self.db_session.commit()
#             return employee
#         return None

#     def find_employees_by_name(self, name: str) -> List[EmployeeModel]:
#         return self.db_session.query(EmployeeModel).filter(
#             or_(
#                 EmployeeModel.first_name.ilike(f"%{name}%"), 
#                 EmployeeModel.last_name.ilike(f"%{name}%")
#             )
#         ).all()

#     def get_employee_by_id(self, employee_id: int) -> Optional[EmployeeModel]:
#         return self.db_session.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()

#     def get_employees_by_unit_name(self, unit_name: str) -> List[EmployeeModel]:
#         return self.db_session.query(EmployeeModel).join(EmployeeModel.unit).filter(Unit.name == unit_name).all()

#     def get_employees_by_department_name(self, department_name: str) -> List[EmployeeModel]:
#         return self.db_session.query(EmployeeModel).join(EmployeeModel.department).filter(Department.name == department_name).all()

#     def assign_employee_to_srt(self, employee_id: int, srt_ids: List[int]):
#         """
#         Assigns an employee to specified SRTs by their IDs.
#         """
#         # Fetch the employee
#         employee = self.db_session.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
#         if not employee:
#             raise HTTPException(status_code=404, detail="Employee not found")

#         # Fetch SRTs by IDs
#         srts = self.db_session.query(SRT).filter(SRT.id.in_(srt_ids)).all()
#         if len(srts) != len(srt_ids):
#             # This means one or more SRTs were not found
#             raise HTTPException(status_code=404, detail="One or more SRTs not found")

#         # Assign the SRTs to the employee
#         employee.srts = srts
#         try:
#             self.db_session.commit()
#         except Exception as e:
#             self.db_session.rollback()
#             raise HTTPException(status_code=500, detail=f"Failed to assign SRTs: {str(e)}")

#         return {"detail": "SRTs assigned successfully"}


#     def find_employees_by_srt_name(self, srt_name: str) -> List[EmployeeModel]:
#         """
#         Finds employees assigned to a specific SRT by the SRT's name.
#         """
#         return self.db_session.query(EmployeeModel)\
#             .join(EmployeeModel.srts)\
#             .filter(SRT.name == srt_name)\
#             .all()

#     def remove_employee_from_srt(self, employee_id: int, srt_id: int):
#         """
#         Remove an employee from a specific SRT.
#         """
#         employee = self.get_employee_by_id(employee_id)
#         if not employee:
#             raise HTTPException(status_code=404, detail="Employee not found")

#         srt = self.db_session.query(SRT).filter(SRT.id == srt_id).first()
#         if not srt:
#             raise HTTPException(status_code=404, detail="SRT not found")

#         if srt not in employee.srts:
#             raise HTTPException(status_code=400, detail="Employee is not assigned to the specified SRT")

#         employee.srts.remove(srt)
#         self.db_session.commit()

#     def get_employees_with_no_srt(self) -> List[EmployeeModel]:
#         """
#         Retrieves employees who are not assigned to any SRT.
#         """
#         return self.db_session.query(EmployeeModel)\
#             .filter(~EmployeeModel.srts.any())\
#             .all()

#     def assign_employee_to_department_and_unit(self, employee_id: int, department_id: int, unit_id: Optional[int] = None):
#         """
#         Assign an employee to a department and optionally to a unit.
#         """
#         employee = self.get_employee_by_id(employee_id)
#         if not employee:
#             raise HTTPException(status_code=404, detail="Employee not found")

#         department = self.db_session.query(Department).filter(Department.id == department_id).first()
#         if not department:
#             raise HTTPException(status_code=404, detail="Department not found")

#         unit = None
#         if unit_id:
#             unit = self.db_session.query(Unit).filter(Unit.id == unit_id).first()
#             if not unit:
#                 raise HTTPException(status_code=404, detail="Unit not found")

#         employee.department_id = department_id
#         employee.unit_id = unit_id
#         self.db.commit()




# repositories/employee_repository.py
#import datetime
from datetime import datetime
from schemas.employee_schemas import EmployeeCreate, EmployeeUpdate, Department_and_Unit_Update
from repositories.base_repository import BaseRepository
from models.all_models import SRT, Department, Designation, Employee as EmployeeModel, Project, Unit, User, employee_srt_association,project_employee_association
from sqlalchemy import extract, func, insert, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Any, Dict, List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload
from logging_helpers import logging_helper
# from pyspark.sql import Row


class EmployeeRepository(BaseRepository[EmployeeModel, EmployeeCreate, EmployeeUpdate]):
    def __init__(self, db_session: Session):
        super().__init__(EmployeeModel, db_session)

    def _fetch_srts_by_ids(self, srt_ids: List[int]) -> List[SRT]:
        """
        Fetches SRT records by their IDs.

        Args:
            srt_ids (List[int]): List of SRT IDs to fetch.

        Returns:
            List[SRT]: List of SRT records.
        """
        return self.db_session.query(SRT).filter(SRT.id.in_(srt_ids)).all()
    

    def get_all_employees(self, limit: int = 100, cursor: Optional[int] = None, tenancy_id: Optional[int] = None) -> List[Dict]:
        """
        Fetches all employee records with optional pagination, including the associated user ID.

        Args:
            limit (int): Number of records to return.
            cursor (Optional[int]): Cursor for pagination.
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Returns:
            List[Dict]: List of employee records with associated user ID.
        """
        query = self.db_session.query(
            EmployeeModel.id.label("employee_id"),
            EmployeeModel.first_name,
            EmployeeModel.last_name,
            EmployeeModel.employee_email.label("email"),
            EmployeeModel.phone_number,
            EmployeeModel.gender,
            EmployeeModel.department_id,
            EmployeeModel.unit_id,
            EmployeeModel.is_active,
            EmployeeModel.staff_code,
            EmployeeModel.address,
            EmployeeModel.state_origin,
            EmployeeModel.lga_origin,
            EmployeeModel.designation_id,
            User.id.label("user_id"),  # Extract the user ID
            EmployeeModel.tenancy_id
        ).outerjoin(
            User, EmployeeModel.user  # Join with the User table on the existing relationship
        )

        if tenancy_id:
            query = query.filter(EmployeeModel.tenancy_id == tenancy_id, EmployeeModel.is_active == True)
        else:
            query = query.filter(EmployeeModel.is_active == True)

        if cursor:
            query = query.filter(EmployeeModel.id > cursor)

        employees = query.order_by(EmployeeModel.id).limit(limit).all()

        # Transform result into a list of dictionaries to include all required fields
        return [
            {
                "employee_id": emp_id,
                "first_name": first_name,
                "last_name": last_name,
                "employee_email": email,
                "phone_number": phone_number,
                "gender": gender,
                "department_id": department_id,
                "unit_id": unit_id,
                "is_active": is_active,
                "staff_code": staff_code,
                "address": address,
                "state_origin": state_origin,
                "lga_origin": lga_origin,
                "designation_id": designation_id,
                "user_id": user_id,  # Now properly handles None as null in JSON
                "tenancy_id": tenancy_id
            } for emp_id, first_name, last_name, email, phone_number,gender, department_id, unit_id, is_active, staff_code, address, state_origin, lga_origin, designation_id, user_id, tenancy_id in employees
        ]

    def create_employee(self, employee_data: EmployeeCreate) -> EmployeeModel:
        """
        Creates a new employee.

        Args:
            employee_data (EmployeeCreate): Data for the new employee.

        Returns:
            EmployeeModel: The created employee record.

        Raises:
            HTTPException: If employee creation fails or if the phone number or staff code already exists.
        """
        #check for employee exixtence using phone number, staff code
        phone_existence = self.db_session.query(EmployeeModel).filter(EmployeeModel.phone_number == employee_data.phone_number).first()
        if phone_existence:
            logging_helper.log_error(f"The Phone_number '{employee_data.phone_number}' supplied for {employee_data.first_name} {employee_data.last_name} already exists")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The Phone_number '{employee_data.phone_number}' supplied for {employee_data.first_name} {employee_data.last_name} already exists ")
        staff_code_existence = self.db_session.query(EmployeeModel).filter(EmployeeModel.staff_code == employee_data.staff_code).first()
        
        if staff_code_existence:
            logging_helper.log_error(f"The Staff Code '{employee_data.staff_code}' supplied for {employee_data.first_name} {employee_data.last_name} already exists ")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The Staff Code '{employee_data.staff_code}' supplied for {employee_data.first_name} {employee_data.last_name} already exists ")

        # Create the employee without immediately linking to SRT, department, or unit
        employee = EmployeeModel(
            first_name=employee_data.first_name.capitalize(),
            last_name=employee_data.last_name.capitalize(),
            phone_number=employee_data.phone_number,
            department_id= employee_data.department_id,
            unit_id =employee_data.unit_id,
            staff_code =employee_data.staff_code,
            employee_email = employee_data.employee_email,
            address=employee_data.address,
            state_origin =employee_data.state_origin,
            lga_origin =employee_data.lga_origin,
            designation_id=employee_data.designation_id,
            tenancy_id=employee_data.tenancy_id,
            date_of_birth=employee_data.date_of_birth,
            gender=employee_data.gender

            # Initially, do not assign department_id or unit_id
            # These can be added later as part of an update operation
        )
        self.db_session.add(employee)
        try:
            self.db_session.commit()
            logging_helper.log_info(f"The new employee with name: {employee.first_name} {employee.last_name} and staff_code : {employee.staff_code} created successfully")
            return employee
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Failed to create employee: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create employee: {str(e)}")      
    

    def update_employee(self, employee_id: int, employee_data: EmployeeUpdate, tenancy_id:Optional[int]=None) -> Optional[EmployeeModel]:
        """
        Updates an employee record.

        Args:
            employee_id (int): ID of the employee to update.
            employee_data (EmployeeUpdate): Updated data for the employee.
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Returns:
            Optional[EmployeeModel]: The updated employee record or None if not found.

        Raises:
            HTTPException: If employee update fails or if the employee does not exist.
        """
        try:
            if tenancy_id: 
                employee = self.get_employee_by_id(employee_id=employee_id, tenancy_id=tenancy_id)
                if not employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or not in your state")
            else:
                employee = self.get_employee_by_id(employee_id)
                if not employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist")
            
            for attr, value in employee_data.model_dump().items():
                setattr(employee, attr, value)

                self.db_session.commit()
                logging_helper.log_info(f"Employee with staff_code{employee.staff_code} updated successfully")
                return employee
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        

    def delete_employee(self, employee_id:int, tenancy_id:Optional[int]=None)->Optional[int]:
        """
        Soft delete an employee.

        Args:
            employee_id (int): ID of the employee to delete.
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Returns:
            Optional[int]: The ID of the deleted employee.

        Raises:
            HTTPException: If employee deletion fails or if the employee does not exist.
        """
        try:
            if tenancy_id:
            #check employee existence 
                employee = self.get_employee_by_id(employee_id=employee_id, tenancy_id=tenancy_id)
                if not employee:
                    logging_helper.log_error(f"The Employee with id {employee_id} does not exist or not in your state")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or not in your state")
            else:
                employee = self.get_employee_by_id(employee_id)
                if not employee:
                    logging_helper.log_error(f"The Employee with id {employee_id} does not exist, so cannot be deleted")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist")
            self.db_session.delete(employee)
            self.db_session.commit()
            logging_helper.log_info(f"Employee with Id: {employee.id} deleted successfully")
            return employee_id
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Encountered an error deleteing the Employee with id:{employee.id} : {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


    def find_employees_without_department(self, tenancy_id:Optional[int]=None) -> List[EmployeeModel]:
        """
        Finds employees without a department.

        Args:
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Returns:
            List[EmployeeModel]: List of employees without a department.
        """        
        if tenancy_id:
            employees = self.db_session.query(EmployeeModel).filter(EmployeeModel.tenancy_id==tenancy_id, EmployeeModel.is_active==True, EmployeeModel.department_id == None).all()
            return employees
        else:
            employees = self.db_session.query(EmployeeModel).filter(EmployeeModel.is_active==True, EmployeeModel.department_id == None).all()
            return employees
        
        
    def convert_to_dict(self, outcome_list: List[List[Tuple[str, int]]]) -> List[Dict[str, int]]:
        """
        Converts a list of lists of tuples into a list of dictionaries.

        Args:
            outcome_list (List[List[Tuple[str, int]]]): List of lists of tuples to convert.

        Returns:
            List[Dict[str, int]]: List of dictionaries.
        """
        result_list = []
        for row in outcome_list:
            row_dict = {}
            for key, value in row:
                row_dict[key] = value
            result_list.append(row_dict)
        return result_list
    


    def change_employee_department_and_unit(self, employee_id: int, department_unit: Department_and_Unit_Update, tenancy_id:Optional[int]=None) -> Optional[EmployeeModel]:
        """
        Changes the department and unit of an employee.

        Args:
            employee_id (int): ID of the employee to update.
            department_unit (Department_and_Unit_Update): New department and unit data.
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Returns:
            Optional[EmployeeModel]: The updated employee record or None if not found.

        Raises:
            HTTPException: If the update fails or if the department/unit does not exist.
        """        
        try:

            #check department existence 
            department = self.db_session.query(Department).filter(Department.id == department_unit.department_id, Department.is_active==True).first()
            if not department:
                logging_helper.log_error(f"Department ID: {department.id} does not exist!!!")
                raise HTTPException(status_code=404, detail="Department ID provided does not exist!!!")

            #check department existence 
            unit = None
            if department_unit.unit_id:
                unit = self.db_session.query(Unit).filter(Unit.id == department_unit.unit_id).first()
                if not unit:
                    logging_helper.log_error(f" Selected Unit ID: {unit.id} to be updated for the employee: {employee.id} does not exist")
                    raise HTTPException(status_code=404, detail="Unit ID provided does not exist")
                

            #Unit ID match with Department ID
            unit_existence = self.db_session.query(Unit).filter(Unit.is_active==True, Unit.department_id==department_unit.department_id, Unit.id==department_unit.unit_id ).first()
            if not unit_existence:
                logging_helper.log_error(f"The Unit ID does not belong to the Department ID")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The Unit ID does not belong to the Department ID")
            
            if tenancy_id:
                employee = self.get_employee_by_id(employee_id=employee_id, tenancy_id=tenancy_id)
                if employee:
                    for attr, value in department_unit.model_dump().items():
                        setattr(employee, attr, value)
                    self.db_session.commit()
                    return employee
            else:
                employee = self.get_employee_by_id(employee_id=employee_id)
                if employee:
                    for attr, value in department_unit.model_dump().items():
                        setattr(employee, attr, value)
                    self.db_session.commit()
                    return employee
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error encountered changing Emoloyee department and unit: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


    def find_employees_by_name(self, name: str, tenancy_id:Optional[int]=None) -> List[EmployeeModel]:
        """
        Finds employees by their name.

        Args:
            name (str): Name of the employee to search for.
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Returns:
            List[EmployeeModel]: List of employees with the specified name.
        """
        try:
            if tenancy_id:
                employees = self.db_session.query(EmployeeModel).filter(EmployeeModel.tenancy_id==tenancy_id, EmployeeModel.is_active==True,
                or_(
                    EmployeeModel.first_name.ilike(f"%{name}%"), 
                    EmployeeModel.last_name.ilike(f"%{name}%")
                )
            ).all()
                return employees
            else:
                employees = self.db_session.query(EmployeeModel).filter(EmployeeModel.is_active==True,
                or_(
                    EmployeeModel.first_name.ilike(f"%{name}%"), 
                    EmployeeModel.last_name.ilike(f"%{name}%")
                )
            ).all()
                return employees
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error finding the Employee with name: {name}")
            raise HTTPException(f"Error finding the Employee with name: {name}: {str(e)}")

    def get_employee_by_id(self, employee_id: int, tenancy_id:Optional[int]=None) -> Optional[EmployeeModel]:
        """
        Fetches an employee by their ID.

        Args:
            employee_id (int): ID of the employee to fetch.
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Returns:
            Optional[EmployeeModel]: The employee record or None if not found.

        Raises:
            HTTPException: If the fetch fails.
        """
        try:

            if tenancy_id:
                employee = self.db_session.query(EmployeeModel).filter(EmployeeModel.tenancy_id==tenancy_id, EmployeeModel.is_active==True, EmployeeModel.id == employee_id).first()
                logging_helper.log_info(f"The Employee with {employee.id} was sucessfully searched")
                return employee
            else:
                employee = self.db_session.query(EmployeeModel).filter(EmployeeModel.is_active==True, EmployeeModel.id == employee_id).first()
                logging_helper.log_info(f"The Employee with {employee.id} was sucessfully searched")  
                return employee
            
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching the Employee with id: {employee_id} : {str(e)}")
            raise HTTPException(f"Error fetching the Employee with id: {employee_id} : {str(e)}")


    def get_employees_by_unit_name(self, unit_name: str, tenancy_id:Optional[int]=None) -> List[EmployeeModel]:
        """
        Fetches employees by their unit name.

        Args:
            unit_name (str): Name of the unit to search for.
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Returns:
            List[EmployeeModel]: List of employees in the specified unit.
        """
        try:

            if tenancy_id:
                employees = self.db_session.query(EmployeeModel).join(EmployeeModel.unit).filter(Unit.name == unit_name, EmployeeModel.tenancy_id==tenancy_id).all()
                return employees
            else:
                employees = self.db_session.query(EmployeeModel).join(EmployeeModel.unit).filter(Unit.name == unit_name).all()
                return employees
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching the Employees with unit name : {unit_name}. : {str(e)}")
            raise HTTPException(f"Error fetching the Employees with unit name : {unit_name}. : {str(e)}")    

    def get_employees_by_department_name(self, department_name: str, tenancy_id:Optional[int]=None) -> List[EmployeeModel]:
        """
        Fetches employees by their department name.

        Args:
            department_name (str): Name of the department to search for.
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Returns:
            List[EmployeeModel]: List of employees in the specified department.
        """
        try:

            if tenancy_id:
                employees = self.db_session.query(EmployeeModel).join(EmployeeModel.department).filter(Department.name == department_name, EmployeeModel.tenancy_id==tenancy_id).all()
                return employees
            else:
                employees = self.db_session.query(EmployeeModel).join(EmployeeModel.department).filter(Department.name == department_name).all()
                return employees
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Errot fetching employees with the department name {department_name}: {str(e)}")
            raise HTTPException(f"Errot fetching employees with the department name {department_name}: {str(e)}")

    def assign_employee_to_srt(self, employee_id: int, srt_ids: List[int], tenancy_id:Optional[int]=None):
        """
        Assigns an employee to specified SRTs by their IDs.

        Args:
            employee_id (int): ID of the employee to assign.
            srt_ids (List[int]): List of SRT IDs to assign.
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Returns:
            dict: A message indicating the result of the assignment.

        Raises:
            HTTPException: If the assignment fails or if the employee/SRT does not exist.
        """
        try:
            if tenancy_id:
            #check employee existence 
                employee = self.get_employee_by_id(employee_id=employee_id, tenancy_id=tenancy_id)
                if not employee:
                    logging_helper.log_error(f"The Employee with id {employee_id} does not exist or not in your state")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or not in your state")
            else:
                employee = self.get_employee_by_id(employee_id)
                if not employee:
                    logging_helper.log_error(f"The Employee with id {employee_id} does not exist")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist")

            # Fetch SRTs by IDs
            if tenancy_id:
                srts = self.db_session.query(SRT).filter(SRT.id.in_(srt_ids), SRT.tenancy_id==tenancy_id).all()
                if len(srts) != len(srt_ids):
                    # This means one or more SRTs were not found
                    logging_helper.log_error("One or more SRTs not found, Please ensure to put SRT IDs that belong to your state")
                    raise HTTPException(status_code=404, detail="One or more SRTs not found, Please ensure to put SRT IDs that belong to your state")
            else:
                srts = self.db_session.query(SRT).filter(SRT.id.in_(srt_ids), SRT.tenancy_id==employee.tenancy_id).all()
                if len(srts) != len(srt_ids):
                    # This means one or more SRTs were not found
                    logging_helper.log_error("One or more SRTs not found, Please ensure to put SRT IDs that belong to the employee state")
                    raise HTTPException(status_code=404, detail="One or more SRTs not found, Please ensure to put SRT IDs that belong to the employee state")

            # Assign the SRTs to the employee
            employee.srts = srts
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Failed to assign SRTs: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to assign SRTs: {str(e)}")

        return {"detail": "SRTs assigned successfully"}


    def find_employees_by_srt_name(self, srt_name: str, tenancy_id:Optional[int]=None) -> List[EmployeeModel]:
        """
        Finds employees assigned to a specific SRT by the SRT's name.

        Args:
            srt_name (str): Name of the SRT to search for.
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Returns:
            List[EmployeeModel]: List of employees in the specified SRT.

        Raises:
            HTTPException: If the fetch fails.
        """
        try:

            if tenancy_id:
                employees = self.db_session.query(EmployeeModel)\
                .join(EmployeeModel.srts)\
                .filter(SRT.name == srt_name, EmployeeModel.tenancy_id==tenancy_id)\
                .all()
                return employees
            else:
                employees = self.db_session.query(EmployeeModel)\
                .join(EmployeeModel.srts)\
                .filter(SRT.name == srt_name)\
                .all()
                return employees
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching the employees in {srt_name} : {str(e)}")
            raise(f"Error fetching the employees in {srt_name} : {str(e)}")
        except Exception as e:
            logging_helper.log_error(f"Error fetching the employees in {srt_name} : {str(e)}")
            raise HTTPException(f"Error fetching the employees in {srt_name} : {str(e)}")

    def remove_employee_from_srt(self, employee_id: int, srt_id: int, tenancy_id:Optional[int]=None):
        """
        Removes an employee from a specific SRT.

        Args:
            employee_id (int): ID of the employee to remove.
            srt_id (int): ID of the SRT to remove the employee from.
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Returns:
            int: The ID of the removed employee.

        Raises:
            HTTPException: If the removal fails or if the employee/SRT does not exist.
        """
        try:
            if tenancy_id:
            #check employee existence 
                employee = self.get_employee_by_id(employee_id=employee_id, tenancy_id=tenancy_id)
                if not employee:
                    logging_helper.log_error(f"The Employee with id {employee_id} does not exist or not in your state")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or not in your state")
            else:
                employee = self.get_employee_by_id(employee_id)
                if not employee:
                    logging_helper.log_error(f"The Employee with id {employee_id} does not exist")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist")

            #check SRT existence 
            if tenancy_id:
                srt = self.db_session.query(SRT).filter(SRT.id == srt_id, SRT.tenancy_id==tenancy_id).first()
                if not srt:
                    logging_helper.log_error("SRT ID provided is not found within your state or does not exist")
                    raise HTTPException(status_code=404, detail="SRT ID provided is not found within your state or does not exist")
            else:
                srt = self.db_session.query(SRT).filter(SRT.id == srt_id).first()
                if not srt:
                    logging_helper.log_error("SRT ID provided does not exist")
                    raise HTTPException(status_code=404, detail="SRT ID provided does not exist")

            if srt not in employee.srts:
                logging_helper.log_error("Employee is not assigned to the specified SRT")
                raise HTTPException(status_code=400, detail="Employee is not assigned to the specified SRT")

            employee.srts.remove(srt)
            self.db_session.commit()
            logging_helper.log_info(f"The Employee with ID: {employee.id} was sucessully removed from {srt.name}")
            return employee_id
        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Failed to Remove Employee from SRTs: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to Remove Employee from SRTs: {str(e)}")


    def get_employees_with_no_srt(self, tenancy_id:Optional[int]=None) -> List[EmployeeModel]:
        """
        Retrieves employees who are not assigned to any SRT.

        Args:
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Returns:
            List[EmployeeModel]: List of employees with no SRT assignments.
        """
        try:

            if tenancy_id:
                employees = self.db_session.query(EmployeeModel)\
                .filter(~EmployeeModel.srts.any(), EmployeeModel.tenancy_id==tenancy_id)\
                .all()
                return employees
            else:
                employees = self.db_session.query(EmployeeModel)\
                .filter(~EmployeeModel.srts.any())\
                .all()
                return employees
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching the employees not mapped to an SRT: {str(e)}")
            raise HTTPException(f"Error fetching the employees not mapped to an SRT: {str(e)}")
        except Exception as e:
            logging_helper.log_error(f"An unexpected error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


    def assign_employee_to_department_and_unit(self, employee_id: int, department_id: int, unit_id: Optional[int] = None, tenancy_id:Optional[int]=None):
        """
        Assigns an employee to a department and optionally to a unit.

        Args:
            employee_id (int): ID of the employee to assign.
            department_id (int): ID of the department to assign.
            unit_id (Optional[int]): ID of the unit to assign.
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Raises:
            HTTPException: If the assignment fails or if the employee/department/unit does not exist.
        """
        try:
            if tenancy_id:
            #check employee existence 
                employee = self.get_employee_by_id(employee_id=employee_id, tenancy_id=tenancy_id)
                if not employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or not in your state")
            else:
                employee = self.get_employee_by_id(employee_id)
                if not employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist")


            #check department existence 
            department = self.db_session.query(Department).filter(Department.id == department_id, Department.is_active==True).first()
            if not department:
                raise HTTPException(status_code=404, detail="Department ID provided does not exist!!!")

            #check department existence 
            unit = None
            if unit_id:
                unit = self.db_session.query(Unit).filter(Unit.id == unit_id).first()
                if not unit:
                    raise HTTPException(status_code=404, detail="Unit not found")
                
            #Unit ID match with Department ID
            unit_existence = self.db_session.query(Unit).filter(Unit.is_active==True, Unit.department_id==department_id, Unit.id==unit_id ).first()
            if not unit_existence:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The Unit ID does not belong to the Department ID ")


            employee.department_id = department_id
            employee.unit_id = unit_id
            self.db.commit()

        except Exception as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Failed to Assign Employee Department and Unit: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to Assign Employee Department and Unit: {str(e)}")
        
    def get_employees_with_birthdays_in_current_month(self):
        """
        Retrieves employees with birthdays in the current month.

        Returns:
            List[Dict]: List of employees with birthdays in the current month.
        """
        current_month = datetime.now().month
        try:
            employees_with_birthdays = (
                self.db_session.query(
                    EmployeeModel.id,
                    func.concat(EmployeeModel.first_name, ' ', EmployeeModel.last_name).label('full_name'),
                    Unit.name.label('unit_name'),
                    EmployeeModel.employee_email,
                    EmployeeModel.phone_number,
                    EmployeeModel.date_of_birth,
                    EmployeeModel.gender,
                    EmployeeModel.tenancy_id
                )
                .join(Unit, EmployeeModel.unit_id == Unit.id, isouter=True)
                .filter(extract('month', EmployeeModel.date_of_birth) == current_month)
                .all()
            )

            if not employees_with_birthdays:
                logging_helper.log_info("No employees with birthdays in the current month found.")
                # raise HTTPException(status_code=404, detail="No employees with birthdays in the current month found.")

            return [
                {
                    "tenancy_id":emp.tenancy_id,
                    "employee_id": emp.id,
                    "full_name": emp.full_name,
                    "unit_name": emp.unit_name,
                    "email": emp.employee_email,
                    "phone_number": emp.phone_number,
                    "birth_date":emp.date_of_birth,
                    "gender":emp.gender
                }
                for emp in employees_with_birthdays
            ]

        except SQLAlchemyError as e:
            logging_helper.log_error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            logging_helper.log_error(f"An unexpected error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


    def get_all_employees_with_birth_date(self, tenancy_id: int = None):
        """
        Gets all employees with optional tenancy_id filter.

        Args:
            tenancy_id (int): Tenancy ID for filtering.

        Returns:
            List[Dict]: List of employees with birth dates.
        """
        try:
            query = self.db_session.query(
                EmployeeModel.id,
                func.concat(EmployeeModel.first_name, ' ', EmployeeModel.last_name).label('full_name'),
                Unit.name.label('unit_name'),
                EmployeeModel.employee_email,
                EmployeeModel.phone_number,
                EmployeeModel.date_of_birth,
                EmployeeModel.gender,
                EmployeeModel.tenancy_id,
                Designation.name.label('designation_name')
            ).join(Unit, EmployeeModel.unit_id == Unit.id, isouter=True
            ).join(Designation, EmployeeModel.designation_id == Designation.id, isouter=True)

            if tenancy_id:
                query = query.filter(EmployeeModel.tenancy_id == tenancy_id)

            employees = query.all()

            if not employees:
                raise HTTPException(status_code=404, detail="No employees found.")

            return [
                {
                    "tenancy_id": emp.tenancy_id,
                    "employee_id": emp.id,
                    "full_name": emp.full_name,
                    "unit_name": emp.unit_name,
                    "email": emp.employee_email,
                    "phone_number": emp.phone_number,
                    "birth_date": emp.date_of_birth,
                    "gender": emp.gender,
                    "designation_name": emp.designation_name
                }
                for emp in employees
            ]

        except SQLAlchemyError as e:
            logging_helper.log_error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            logging_helper.log_error(f"An unexpected error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
        
    def get_employees_with_today_birthday(self, tenancy_id: int = None):
        """
        Gets employees whose birthday is today with optional tenancy_id filter.

        Args:
            tenancy_id (int): Tenancy ID for filtering.

        Returns:
            List[Dict]: List of employees with birthdays today.
        """
        try:
            today = datetime.now()
            query = self.db_session.query(
                EmployeeModel.id.label('employee_id'),
                EmployeeModel.date_of_birth,
                func.concat(EmployeeModel.first_name, ' ', EmployeeModel.last_name).label('full_name'),
                EmployeeModel.gender,
                EmployeeModel.tenancy_id
            ).filter(
                func.extract('month', EmployeeModel.date_of_birth) == today.month,
                func.extract('day', EmployeeModel.date_of_birth) == today.day
            )

            if tenancy_id:
                query = query.filter(EmployeeModel.tenancy_id == tenancy_id)

            employees = query.all()

            if not employees:
                logging_helper.log_info("No Birthday celebrant found for Today")
                #raise HTTPException(status_code=404, detail="No employees with birthdays today found.")

            return [
                {
                    "employee_id": emp.employee_id,
                    "full_name": emp.full_name,
                    "date_of_birth": emp.date_of_birth,
                    "gender":emp.gender,
                    "tenancy_id": emp.tenancy_id
                }
                for emp in employees
            ]

        except SQLAlchemyError as e:
            logging_helper.log_error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            logging_helper.log_error(f"An unexpected error occurred fetching birthday celebrant for the Today: {str(e)}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred fetching Birthday celebrants for the Today: {str(e)}")
        


    def add_employee_to_project(self, employee_id: int, project_id: int) -> None:
        """
        Adds an employee to a project.

        Args:
            employee_id (int): ID of the employee to add.
            project_id (int): ID of the project to add the employee to.

        Raises:
            ValueError: If the employee or project does not exist or is inactive.
            SQLAlchemyError: If a database error occurs.
            Exception: If any other error occurs.
        """
        logging_helper.log_info(f"Attempting to add employee {employee_id} to project {project_id}")
        try:
            employee = self.get_all_employees(employee_id)
            project = self.db_session.query(Project).filter(Project.id == project_id, Project.is_active == True).first()

            if not employee or not project:
                logging_helper.log_info(f"Either the employee {employee_id} or the project {project_id} does not exist or is inactive")
                raise ValueError("Either the employee or the project does not exist or is inactive")

            self.db_session.execute(
                insert(project_employee_association).values(
                    employee_id=employee_id,
                    project_id=project_id
                )
            )
            self.db_session.commit()
            logging_helper.log_info(f"Successfully added employee {employee_id} to project {project_id}")
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Database error while adding employee {employee_id} to project {project_id}: {str(e)}")
            self.db_session.rollback()
            raise
        except Exception as e:
            logging_helper.log_error(f"An error occurred while adding employee {employee_id} to project {project_id}: {str(e)}")
            raise

    def add_group_of_employees_to_project(self, employee_ids: List[int], project_id: int) -> None:
        """
        Adds a group of employees to a project.

        Args:
            employee_ids (List[int]): List of employee IDs to add.
            project_id (int): ID of the project to add the employees to.

        Raises:
            ValueError: If the project does not exist or is inactive.
            SQLAlchemyError: If a database error occurs.
            Exception: If any other error occurs.
        """
        logging_helper.log_info(f"Attempting to add employees {employee_ids} to project {project_id}")
        try:
            project = self.db_session.query(Project).filter(Project.id == project_id, Project.is_active == True).first()

            if not project:
                logging_helper.log_error(f"The project {project_id} does not exist or is inactive")
                raise ValueError("The project does not exist or is inactive")

            # Remove duplicate employee IDs
            unique_employee_ids = list(set(employee_ids))

            employees = self.db_session.query(EmployeeModel).filter(EmployeeModel.id.in_(unique_employee_ids), EmployeeModel.is_active == True).all()

            if not employees:
                logging_helper.log_error(f"None of the employees {unique_employee_ids} exist or are inactive")
                raise ValueError("None of the employees exist or are inactive")

            # Check for employees already assigned to the project
            existing_assignments = self.db_session.query(project_employee_association).filter(
                project_employee_association.c.project_id == project_id,
                project_employee_association.c.employee_id.in_(unique_employee_ids)
            ).all()

            already_assigned_employee_ids = {assignment.employee_id for assignment in existing_assignments}

            # Filter out already assigned employees
            new_employee_ids = [emp_id for emp_id in unique_employee_ids if emp_id not in already_assigned_employee_ids]

            if not new_employee_ids:
                logging_helper.log_info(f"All employees {unique_employee_ids} are already assigned to project {project_id}")
                return

            self.db_session.execute(
                insert(project_employee_association).values(
                    [{'employee_id': employee_id, 'project_id': project_id} for employee_id in new_employee_ids]
                )
            )
            self.db_session.commit()
            logging_helper.log_info(f"Successfully added employees {new_employee_ids} to project {project_id}")
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Database error while adding employees {employee_ids} to project {project_id}: {str(e)}")
            self.db_session.rollback()
            raise
        except Exception as e:
            logging_helper.log_error(f"An error occurred while adding employees {employee_ids} to project {project_id}: {str(e)}")
            raise


    def set_supervisor(self, employee_id: int, supervisor_id: Optional[int], tenancy_id: Optional[int] = None) -> Optional[EmployeeModel]:
        """
        Sets or updates the supervisor for an employee.

        Args:
            employee_id (int): ID of the employee to update.
            supervisor_id (Optional[int]): ID of the new supervisor.
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Returns:
            Optional[EmployeeModel]: The updated employee record or None if not found.

        Raises:
            HTTPException: If the update fails or if the employee/supervisor does not exist.
        """
        try:
            if tenancy_id:
                employee = self.get_employee_by_id(employee_id=employee_id, tenancy_id=tenancy_id)
                if not employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist or is not in your state")
            else:
                employee = self.get_employee_by_id(employee_id)
                if not employee:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist")

            if supervisor_id:
                supervisor = self.get_employee_by_id(supervisor_id, tenancy_id)
                if not supervisor:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Supervisor with id {supervisor_id} does not exist or is not in your state")

            employee.supervisor_id = supervisor_id
            self.db_session.commit()
            logging_helper.log_info(f"Employee with ID {employee_id} was assigned to Supervisor with ID {supervisor_id}")
            return employee
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Failed to set supervisor: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        
    def get_supervised_employees(self, supervisor_id: int, tenancy_id: Optional[int] = None) -> List[EmployeeModel]:
        """
        Retrieves all employees supervised by a specific supervisor.

        Args:
            supervisor_id (int): ID of the supervisor.
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Returns:
            List[EmployeeModel]: List of supervised employees.

        Raises:
            HTTPException: If the retrieval fails or if the supervisor does not exist.
        """
        try:
            if tenancy_id:
                supervised_employees = self.db_session.query(EmployeeModel).filter(
                    EmployeeModel.supervisor_id == supervisor_id,
                    EmployeeModel.tenancy_id == tenancy_id,
                    EmployeeModel.is_active == True
                ).all()
            else:
                supervised_employees = self.db_session.query(EmployeeModel).filter(
                    EmployeeModel.supervisor_id == supervisor_id,
                    EmployeeModel.is_active == True
                ).all()
            
            if not supervised_employees:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No supervised employees found")

            return supervised_employees
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error retrieving supervised employees: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


    def get_employee_hierarchy(self, employee_id: int, tenancy_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Retrieves the employee hierarchy starting from a specific employee.

        Args:
            employee_id (int): ID of the employee to start the hierarchy.
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Returns:
            Dict[str, Any]: Hierarchical structure of employees.

        Raises:
            HTTPException: If the retrieval fails or if the employee does not exist.
        """
        def build_hierarchy(employee: EmployeeModel) -> Dict[str, Any]:
            """
            Builds the hierarchical structure for a given employee.

            Args:
                employee (EmployeeModel): The employee to build the hierarchy for.

            Returns:
                Dict[str, Any]: Hierarchical structure of the employee.
            """
            hierarchy = {
                "employee_id": employee.id,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "supervisor_id": employee.supervisor_id,
                "subordinates": []
            }

            subordinates = self.db_session.query(EmployeeModel).filter(
                EmployeeModel.supervisor_id == employee.id,
                EmployeeModel.is_active == True
            ).all()

            for subordinate in subordinates:
                hierarchy["subordinates"].append(build_hierarchy(subordinate))

            return hierarchy

        def fetch_supervisor_details(supervisor_id: int) -> Optional[Dict[str, Any]]:
            """
            Fetches the details of the supervisor.

            Args:
                supervisor_id (int): ID of the supervisor.

            Returns:
                Optional[Dict[str, Any]]: Details of the supervisor or None if not found.
            """
            supervisor = self.db_session.query(EmployeeModel).filter(
                EmployeeModel.id == supervisor_id,
                EmployeeModel.is_active == True
            ).first()
            
            if supervisor:
                return {
                    "supervisor_id": supervisor.id,
                    "first_name": supervisor.first_name,
                    "last_name": supervisor.last_name
                }
            return None

        try:
            if tenancy_id:
                employee = self.db_session.query(EmployeeModel).filter(
                    EmployeeModel.id == employee_id,
                    EmployeeModel.tenancy_id == tenancy_id,
                    EmployeeModel.is_active == True
                ).first()
            else:
                employee = self.db_session.query(EmployeeModel).filter(
                    EmployeeModel.id == employee_id,
                    EmployeeModel.is_active == True
                ).first()

            if not employee:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Employee with id {employee_id} does not exist")

            hierarchy = build_hierarchy(employee)

            if employee.supervisor_id:
                hierarchy["supervisor"] = fetch_supervisor_details(employee.supervisor_id)

            return hierarchy
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error retrieving employee hierarchy: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))



    def get_full_hierarchy(self, tenancy_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieves the full employee hierarchy starting from top-level employees.

        Args:
            tenancy_id (Optional[int]): Tenancy ID for filtering.

        Returns:
            List[Dict[str, Any]]: List of hierarchical structures of employees.

        Raises:
            HTTPException: If the retrieval fails.
        """
        def build_hierarchy(employee: EmployeeModel) -> Dict[str, Any]:
            """
            Builds the hierarchical structure for a given employee.

            Args:
                employee (EmployeeModel): The employee to build the hierarchy for.

            Returns:
                Dict[str, Any]: Hierarchical structure of the employee.
            """
            hierarchy = {
                "employee_id": employee.id,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "supervisor_id": employee.supervisor_id,
                "subordinates": []
            }

            subordinates = self.db_session.query(EmployeeModel).filter(
                EmployeeModel.supervisor_id == employee.id,
                EmployeeModel.is_active == True
            ).all()

            for subordinate in subordinates:
                hierarchy["subordinates"].append(build_hierarchy(subordinate))

            return hierarchy

        try:
            if tenancy_id:
                top_level_employees = self.db_session.query(EmployeeModel).filter(
                    EmployeeModel.supervisor_id == None,
                    EmployeeModel.tenancy_id == tenancy_id,
                    EmployeeModel.is_active == True
                ).all()
            else:
                top_level_employees = self.db_session.query(EmployeeModel).filter(
                    EmployeeModel.supervisor_id == None,
                    EmployeeModel.is_active == True
                ).all()

            if not top_level_employees:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No top-level employees found")

            full_hierarchy = [build_hierarchy(employee) for employee in top_level_employees]
            return full_hierarchy
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error retrieving full employee hierarchy: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
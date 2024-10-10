# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List

# from db.database import get_db  # Assuming get_db is a dependency that provides a database session
# from schemas.holiday_schemas import HolidayCreate, HolidayUpdate, HolidayResponse  # Assuming you have these schemas
# from repositories.holiday_repository import HolidayRepository

# router = APIRouter()

# @router.post("/holidays/", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
# def create_holiday(holiday_data: HolidayCreate, db: Session = Depends(get_db)):
#     """
#     Create a new holiday and send email notifications.
    
#     Args:
#         holiday_data (HolidayCreate): Data for creating the holiday.
#         db (Session): SQLAlchemy session object.
        
#     Returns:
#         PublicHoliday: The created holiday object.
#     """
#     try:
#         holiday_repo = HolidayRepository(db)
#         new_holiday = holiday_repo.create_holiday(holiday_data.dict())
#         return new_holiday
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# @router.get("/holidays/", response_model=List[HolidayResponse])
# def get_all_holidays(db: Session = Depends(get_db)):
#     """
#     Retrieve all holidays.
    
#     Args:
#         db (Session): SQLAlchemy session object.
        
#     Returns:
#         list[PublicHoliday]: List of all holidays.
#     """
#     try:
#         holiday_repo = HolidayRepository(db)
#         holidays = holiday_repo.get_all_holidays()
#         return holidays
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# @router.delete("/holidays/{holiday_id}/", status_code=status.HTTP_204_NO_CONTENT)
# def delete_holiday(holiday_id: int, db: Session = Depends(get_db)):
#     """
#     Soft delete a holiday by ID.
    
#     Args:
#         holiday_id (int): ID of the holiday to delete.
#         db (Session): SQLAlchemy session object.
        
#     Returns:
#         bool: True if the holiday was soft-deleted, False if not found.
#     """
#     try:
#         holiday_repo = HolidayRepository(db)
#         success = holiday_repo.delete_holiday(holiday_id)
#         if not success:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holiday not found or already deleted")
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# @router.put("/holidays/{holiday_id}/", response_model=HolidayResponse)
# def update_holiday(holiday_id: int, update_data: HolidayUpdate, db: Session = Depends(get_db)):
#     """
#     Update a holiday by ID.
    
#     Args:
#         holiday_id (int): ID of the holiday to update.
#         update_data (HolidayUpdate): Data for updating the holiday.
#         db (Session): SQLAlchemy session object.
        
#     Returns:
#         PublicHoliday: The updated holiday object.
#     """
#     try:
#         holiday_repo = HolidayRepository(db)
#         updated_holiday = holiday_repo.update_holiday(holiday_id, update_data.dict(exclude_unset=True))
#         if not updated_holiday:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holiday not found")
#         return updated_holiday
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


#routes/holiday_routes.py
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db  
from schemas.holiday_schemas import HolidayCreate, HolidayUpdate, HolidayResponse  
from repositories.holiday_repository import HolidayRepository
from auth.email import notify_holiday_creation  # Import the email notification function

router = APIRouter()

# @router.post("/holidays/", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
# async def create_holiday(holiday_data: HolidayCreate, db: Session = Depends(get_db)):
#     """
#     Create a new holiday and send email notifications.
    
#     Args:
#         holiday_data (HolidayCreate): Data for creating the holiday.
#         db (Session): SQLAlchemy session object.
        
#     Returns:
#         PublicHoliday: The created holiday object.
#     """
#     try:
#         holiday_repo = HolidayRepository(db)
#         new_holiday = holiday_repo.create_holiday(holiday_data.dict())

#         # Fetch employees and CEO
#         employees, ceo = holiday_repo.get_employees_and_ceo()
#         ceo_email = ceo.employee_email

#         # Prepare the list of recipient emails
#         email_recipients = [(employee.first_name, employee.employee_email) for employee in employees]

#         # Call the email notification function asynchronously using asyncio.create_task
#         asyncio.create_task(
#             notify_holiday_creation(
#                 recipients=email_recipients,
#                 holiday_name=new_holiday.name,
#                 holiday_date=new_holiday.date,
#                 holiday_description=new_holiday.description,
#                 ceo_email=ceo_email,
#                 holiday_type_id=new_holiday.holiday_type_id
#             )
#         )

#         return new_holiday
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/holidays/", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
async def create_holiday(holiday_data: HolidayCreate, db: Session = Depends(get_db)):
    """
    Create a new holiday and send email notifications.
    
    Args:
        holiday_data (HolidayCreate): Data for creating the holiday.
        db (Session): SQLAlchemy session object.
        
    Returns:
        PublicHoliday: The created holiday object.
    """
    try:
        holiday_repo = HolidayRepository(db)
        new_holiday = holiday_repo.create_holiday(holiday_data.dict())

        # Fetch employees and CEO
        employees, ceo = holiday_repo.get_employees_and_ceo()
        ceo_email = ceo.employee_email

        # Prepare the list of recipient emails
        email_recipients = [(employee.first_name, employee.employee_email) for employee in employees]

        # Call the email notification function asynchronously using asyncio.create_task
        await notify_holiday_creation(
            recipients=email_recipients,
            holiday_name=new_holiday.name,
            holiday_date=new_holiday.date,
            holiday_description=new_holiday.description,
            ceo_email=ceo_email,
            holiday_type_id=new_holiday.holiday_type_id
        )

        return new_holiday
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))




@router.get("/holidays/", response_model=List[HolidayResponse])
def get_all_holidays(db: Session = Depends(get_db)):
    """
    Retrieve all holidays.
    
    Args:
        db (Session): SQLAlchemy session object.
        
    Returns:
        list[PublicHoliday]: List of all holidays.
    """
    try:
        holiday_repo = HolidayRepository(db)
        holidays = holiday_repo.get_all_holidays()
        return holidays
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/holidays/{holiday_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_holiday(holiday_id: int, db: Session = Depends(get_db)):
    """
    Soft delete a holiday by ID.
    
    Args:
        holiday_id (int): ID of the holiday to delete.
        db (Session): SQLAlchemy session object.
        
    Returns:
        bool: True if the holiday was soft-deleted, False if not found.
    """
    try:
        holiday_repo = HolidayRepository(db)
        success = holiday_repo.delete_holiday(holiday_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holiday not found or already deleted")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/holidays/{holiday_id}/", response_model=HolidayResponse)
def update_holiday(holiday_id: int, update_data: HolidayUpdate, db: Session = Depends(get_db)):
    """
    Update a holiday by ID.
    
    Args:
        holiday_id (int): ID of the holiday to update.
        update_data (HolidayUpdate): Data for updating the holiday.
        db (Session): SQLAlchemy session object.
        
    Returns:
        PublicHoliday: The updated holiday object.
    """
    try:
        holiday_repo = HolidayRepository(db)
        updated_holiday = holiday_repo.update_holiday(holiday_id, update_data.dict(exclude_unset=True))
        if not updated_holiday:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holiday not found")
        return updated_holiday
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

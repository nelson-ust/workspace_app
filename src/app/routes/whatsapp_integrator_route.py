# from fastapi import APIRouter, Request, Depends
# from sqlalchemy.orm import Session
# from twilio.twiml.messaging_response import MessagingResponse
# from db.database import get_db
# from logging_config import logger

# router = APIRouter()

# # Twilio WhatsApp webhook handler
# @router.post("/whatsapp/webhook")
# async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
#     form_data = await request.form()
#     incoming_message = form_data.get('Body', '').strip().lower()
#     from_number = form_data.get('From')

#     response = MessagingResponse()

#     # Command processing based on incoming message
#     if incoming_message == '1':
#         message_body = await get_unit_info(db)
#     elif incoming_message == '2':
#         message_body = await get_department_info(db)
#     elif incoming_message == '3':
#         message_body = await get_tenancy_info(db)
#     elif incoming_message == '4':
#         message_body = await get_user_role_info(db)
#     elif incoming_message == '5':
#         message_body = await get_user_info(db)
#     elif incoming_message == '6':
#         message_body = await get_employee_info(db)
#     elif incoming_message == '7':
#         message_body = await get_location_info(db)
#     elif incoming_message == '8':
#         message_body = await get_trip_report(db)
#     else:
#         message_body = send_whatsapp_menu()

#     response.message(message_body)
#     return str(response)

# def send_whatsapp_menu():
#     menu_text = (
#         "1 Get Unit Information\n"
#         "2 Get Department Information\n"
#         "3 Get Tenancy Information\n"
#         "4 Get User Role Information\n"
#         "5 Get User Information\n"
#         "6 Get Employee Information\n"
#         "7 Get Location Information\n"
#         "8 Get Trip Report\n"
#         # Add more options as needed...
#         "Enter any Number or Keyword above to get started."
#     )
#     return menu_text

# async def get_unit_info(db: Session):
#     # Here you call the actual endpoint or query the database to fetch the data
#     # Example: return await some_function_from_your_routes_module()
#     return "Here is the unit information..."

# async def get_department_info(db: Session):
#     return "Here is the department information..."

# async def get_tenancy_info(db: Session):
#     return "Here is the tenancy information..."

# async def get_user_role_info(db: Session):
#     return "Here is the user role information..."

# async def get_user_info(db: Session):
#     return "Here is the user information..."

# async def get_employee_info(db: Session):
#     return "Here is the employee information..."

# async def get_location_info(db: Session):
#     return "Here is the location information..."

# async def get_trip_report(db: Session):
#     return "Here is the trip report..."


from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse
from db.database import get_db
from logging_config import logger
from repositories.department_repository import DepartmentRepository  # Import the repository

router = APIRouter()

# Twilio WhatsApp webhook handler
@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    incoming_message = form_data.get('Body', '').strip().lower()
    from_number = form_data.get('From')

    response = MessagingResponse()

    try:
        # Command processing based on incoming message
        if incoming_message == '0':
            message_body = send_whatsapp_menu()
        elif incoming_message == '1':
            message_body = await get_all_departments(db)
        elif incoming_message == '2':
            message_body = await get_department_by_id(db, department_id=1)  # Example: get department with ID 1
        # Add more options as needed...
        else:
            message_body = "Invalid option. Please try again.\n\n" + send_whatsapp_menu()

        # Respond back to the user on WhatsApp
        response.message(message_body)

    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {e}")
        response.message("Sorry, something went wrong.")

    return str(response)

def send_whatsapp_menu():
    menu_text = (
        "Welcome to the WorkPlan Management System WhatsApp Integration.\n\n"
        "Please choose an option:\n"
        "1. Get All Departments Information\n"
        "2. Get Department Information by ID\n"
        # Add more options as needed...
        "0. Return to Main Menu\n"
        "Enter any number or keyword above to get started."
    )
    return menu_text

# Define async functions to integrate with the department repository
async def get_all_departments(db: Session):
    department_repo = DepartmentRepository(db)
    departments = department_repo.get_departments()
    if departments:
        department_list = "\n".join([f"{dept.id}: {dept.name}" for dept in departments])
        return f"Departments:\n{department_list}"
    return "No departments found."

async def get_department_by_id(db: Session, department_id: int):
    department_repo = DepartmentRepository(db)
    department = department_repo.get_department_by_id(department_id)
    if department:
        return f"Department ID: {department.id}\nName: {department.name}"
    return f"No department found with ID {department_id}."



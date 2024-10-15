#app/auth/email.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Tuple
from datetime import datetime
import zipfile
from dotenv import load_dotenv
from sqlalchemy import func
from sqlalchemy.orm import Session
from email.mime.image import MIMEImage

from models.all_models import Employee
from logging_helpers import logging_helper


load_dotenv()  # This loads the environment variables from .env

# Load SMTP configuration from environment variables
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.mail.yahoo.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '465'))  # SSL port for secure email
SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'nelson_ust@yahoo.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'olpbcmuclaqaqzcd')
FROM_EMAIL = SMTP_USERNAME  # Typically the same as the SMTP username

# Directory containing the logs
base_dir = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(base_dir, 'workplanlogs')


# def send_email(email_to: str, subject: str, html_content: str, attachments: List[str] = None, images: List[Tuple[str, str]] = None, message_id: str = None, in_reply_to: str = None, references: str = None):
#     """Generalized email sending function with optional attachments and inline images."""
#     try:
#         msg = MIMEMultipart('alternative')
#         msg['Subject'] = subject
#         msg['From'] = FROM_EMAIL
#         msg['To'] = email_to

#         if message_id:
#             msg['Message-ID'] = message_id
#         if in_reply_to:
#             msg['In-Reply-To'] = in_reply_to
#         if references:
#             msg['References'] = references

#         part_html = MIMEText(html_content, 'html')
#         msg.attach(part_html)

#         if attachments:
#             for attachment in attachments:
#                 part = MIMEBase('application', 'octet-stream')
#                 with open(attachment, 'rb') as file:
#                     part.set_payload(file.read())
#                 encoders.encode_base64(part)
#                 part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment)}')
#                 msg.attach(part)

#         if images:
#             for image_path, image_cid in images:
#                 with open(image_path, 'rb') as img_file:
#                     img = MIMEImage(img_file.read())
#                     img.add_header('Content-ID', f'<{image_cid}>')
#                     img.add_header('Content-Disposition', 'inline', filename=image_path)
#                     msg.attach(img)

#         with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
#             server.login(SMTP_USERNAME, SMTP_PASSWORD)
#             server.sendmail(FROM_EMAIL, email_to, msg.as_string())

#         print("Email sent successfully!")
#         return True
#     except Exception as e:
#         print(f"Failed to send email: {e}")
#         return False

def send_email(email_to: str, subject: str, html_content: str, attachments: List[str] = None, images: List[Tuple[str, str]] = None, message_id: str = None, in_reply_to: str = None, references: str = None, cc: Optional[str] = None):
    """Generalized email sending function with optional attachments and inline images."""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = email_to

        if cc:
            msg['Cc'] = cc

        if message_id:
            msg['Message-ID'] = message_id
        if in_reply_to:
            msg['In-Reply-To'] = in_reply_to
        if references:
            msg['References'] = references

        part_html = MIMEText(html_content, 'html')
        msg.attach(part_html)

        if attachments:
            for attachment in attachments:
                part = MIMEBase('application', 'octet-stream')
                with open(attachment, 'rb') as file:
                    part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment)}')
                msg.attach(part)

        if images:
            for image_path, image_cid in images:
                with open(image_path, 'rb') as img_file:
                    img = MIMEImage(img_file.read())
                    img.add_header('Content-ID', f'<{image_cid}>')
                    img.add_header('Content-Disposition', 'inline', filename=image_path)
                    msg.attach(img)

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, [email_to] + ([cc] if cc else []), msg.as_string())

        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def generate_message_id() -> str:
    from uuid import uuid4
    return f"<{uuid4()}@yourdomain.com>"


def zip_logs():
    """Zip the log files."""
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    zip_filename = f"logs_{datetime.now().strftime('%Y-%m-%d')}.zip"
    zip_filepath = os.path.join(logs_dir, zip_filename)
    
    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
        for root, _, files in os.walk(logs_dir):
            for file in files:
                if file.endswith(".log"):
                    log_file_path = os.path.join(root, file)
                    zipf.write(log_file_path, os.path.basename(log_file_path))
    return zip_filepath


def send_log_files_email():
    """Send email with log files attached."""
    zip_filepath = zip_logs()
    
    subject = "Daily Log Files"
    html_content = """
    <html>
        <body>
            <p>Hi,<br>
               Please find attached the daily log files.<br>
               <p>Regards,<br>Your System</p>
            </p>
        </body>
    </html>
    """
    if send_email(FROM_EMAIL, subject, html_content, [zip_filepath]):
        delete_logs()


def delete_logs():
    """Delete the log files after emailing."""
    for root, _, files in os.walk(logs_dir):
        for file in files:
            if file.endswith(".log") or file.endswith(".zip"):
                os.remove(os.path.join(root, file))


def send_reset_password_email(email_to: str, token: str):
    """Send a password reset email."""
    subject = "CCFN Workplan - Password Reset Request"
    html_content = f"""
    <html>
        <body>
            <p>Hi,<br>
               To reset your password, please click on the following link or copy and paste it into your browser:<br>
               <a href="http://localhost:3000/password-reset?token={token}">Reset Password</a>
               <p>Regards,<br>CCFN Health Informatics Team</p>
            </p>
        </body>
    </html>
    """
    send_email(email_to, subject, html_content)


def notify_initiator_about_work_plan(email_to: str, initiator_name: str, work_plan_title: str, work_plan_status: str, message_id: str):
    """Notify the initiator about the work plan creation and its status."""
    subject = "Work Plan Creation Update"
    html_content = f"""
    <html>
        <body>
            <p>Hi {initiator_name},<br>
               You have successfully created a new work plan titled '<strong>{work_plan_title}</strong>'.
              <br>
               Current Status: <strong>{work_plan_status}</strong><br>
               You can track the progress and approvals related to this work plan in the system.
               <p>Regards,<br>CCFN Health Informatics Team</p>
            </p>
        </body>
    </html>
    """
    send_email(email_to, subject, html_content, message_id=message_id)


def notify_work_plan_creation(recipients: List[tuple], work_plan_title: str, initiator_name: str, work_plan_status: str, message_id: str):
    """Notify associated employees of a new work plan creation, addressing them by their first name and including the initiator's name and status."""
    subject = "New Work Plan Created"
    for first_name, email in recipients:
        html_content = f"""
        <html> 
            <body>
                <p>Hi {first_name},<br>
                   You have been added to a new work plan created by {initiator_name}, with Activity Title 
                   <strong>'{work_plan_title}'</strong>.<br>
                   Current Status: <strong>{work_plan_status}</strong><br>
                   Please login to the work plan platform for details.
                   <p>Regards,<br>CCFN Health Informatics Team</p>
                </p>
            </body>
        </html>
        """
        send_email(email, subject, html_content, message_id=message_id)


def notify_work_plan_approval(recipients: List[tuple], work_plan_title: str, work_plan_code: str, activity_date: datetime.date, activity_start_time: datetime.time, work_plan_status: str, message_id: str, in_reply_to: str = None, references: str = None):
    """Notify associated employees that a work plan has been approved, including the status."""
    date_formatted = activity_date.strftime('%Y-%m-%d')
    time_formatted = activity_start_time.strftime('%H:%M %p')
    subject = "Work Plan Approved"
    
    for first_name, email in recipients:
        html_content = f"""
        <html>
            <body>
                <p>Hi {first_name},<br>
                The work plan titled '{work_plan_title}' with Workplan code <strong>{work_plan_code}</strong> has been approved.<br>
                Current Status: <strong>{work_plan_status}</strong><br>
                <strong>Details:</strong>
                <ul>
                    <li>Activity Date: {date_formatted}</li>
                    <li>Activity Start Time: {time_formatted}</li>
                </ul>
                Please login to the Workplan Platform to access the approved plan. Thereafter you can proceed accordingly.
                <p>Regards,<br>Programs Team</p>
                </p>
            </body>
        </html>
        """
        send_email(email, subject, html_content, message_id=message_id, in_reply_to=in_reply_to, references=references)


def notify_work_plan_denial(recipients: List[tuple], work_plan_title: str, work_plan_code: str, denial_reason: str, work_plan_status: str, message_id: str, in_reply_to: str = None, references: str = None):
    """Notify associated employees of a work plan denial, including the status, by addressing them by their first name."""
    subject = "Work Plan Denied Notification"
    for first_name, email in recipients:
        html_content = f"""
        <html>
            <body>
                <p>Hi {first_name},<br>
                Unfortunately, the work plan titled '<strong>{work_plan_title}</strong>' with code '{work_plan_code}' has been denied.<br>
                Reason for denial: {denial_reason}<br>
                Current Status: <strong>{work_plan_status}</strong><br>
                Please review the details and make necessary adjustments as required.
                <p>Regards,<br>Programs Team</p>
                </p>
            </body>
        </html>
        """
        send_email(email, subject, html_content, message_id=message_id, in_reply_to=in_reply_to, references=references)


def notify_work_plan_reschedule(recipients: List[Tuple[str, str]], work_plan_title: str, work_plan_code: str, reason: str, new_date: str, message_id: str, in_reply_to: str = None, references: str = None):
    """Notify associated employees of a work plan rescheduling, addressing them by their first name."""
    subject = "Work Plan Rescheduling Notification"
    for first_name, email in recipients:
        html_content = f"""
        <html>
            <body>
                <p>Hi {first_name},<br>
                The work plan titled '<strong>{work_plan_title}</strong>' with code <strong>{work_plan_code}</strong> has been rescheduled.<br>
                New Date: {new_date}<br>
                Reason for Rescheduling: {reason}
                <p>Please update your schedules accordingly.</p>
                <p>Regards,<br>Programs Team</p>
                </p>
            </body>
        </html>
        """
        send_email(email, subject, html_content, message_id=message_id, in_reply_to=in_reply_to, references=references)    


def notify_work_plan_updates(recipients: List[tuple], work_plan_title: str, changes: dict, message_id: str, in_reply_to: str = None, references: str = None):
    """Notify associated employees of updates to a work plan."""
    subject = "Update to Work Plan"
    for first_name, email in recipients:
        changes_html = ''.join(f"<li>{field}: {value}</li>" for field, value in changes.items())
        html_content = f"""
        <html>
            <body>
                <p>Hi {first_name},<br>
                   The work plan titled '<strong>{work_plan_title}</strong>' has been updated with the following changes:<br>
                   <ul>{changes_html}</ul><br>
                   Please login to the work plan platform for detailed information.
                   <p>Regards,<br>CCFN Health Informatics Team</p>
                </p>
            </body>
        </html>
        """
        send_email(email, subject, html_content, message_id=message_id, in_reply_to=in_reply_to, references=references)


def notify_employees_about_trip(recipients, details):
    """Notify associated employees about the trip details."""
    subject = "Trip Details Notification"
    for first_name, email in recipients:
        html_content = f"""
        <html>
            <body>
                <p>Hi {first_name},<br>
                   You are scheduled for a trip today. Here are the details:<br>
                   <ul>
                       <li>Departure Time: {details['take_off_time']}</li>
                       <li>Pilot: {details['driver_name']}</li>
                       <li>Vehicle Details: {details['vehicle_info']}</li>
                   </ul>
                   Please be on time and have a safe trip.
                   <p>Regards,<br>Your Transport and Logistics Team</p>
                </p>
            </body>
        </html>
        """
        send_email(email, subject, html_content)


def notify_trip_creation(recipients, start_time, driver_full_name, driver_licence, vehicle_name, vehicle_plate, location_details, activity_date):
    subject = "Trip Scheduled"
    for first_name, email in recipients:
        html_content = f"""
        <html>
            <body>
                <p>Hi {first_name},<br>
                Your trip is scheduled to start at {start_time.strftime('%H:%M %p')} on {activity_date}.<br>
                <!--Site(s) To Cover: {location_details}<br>-->
                Activity Title: {location_details}<br>
                Pilot: {driver_full_name} With Driver Licence: {driver_licence})<br>
                Vehicle Details: {vehicle_name} - {vehicle_plate}<br>
                <p>Please be prepared to leave on time.</p>
                <p>Regards,<br>Transport and Logistics Team</p>
                </p>
            </body>
        </html>
        """
        send_email(email, subject, html_content)


def send_driver_trip_details(email_to, driver_name, vehicle_name, vehicle_plate, passengers, take_off_time, location_details, activity_date):
    """Sends an email to the driver with detailed information about the trip they will conduct."""
    subject = "Trip Assignment Details"
    html_content = f"""
    <html>
        <body>
            <p>Hi {driver_name},<br>
            You are scheduled to pilot the {vehicle_name} (Plate: {vehicle_plate}) on {activity_date}.<br>
            Location: {location_details}<br>
            The passengers for this trip will be: {passengers}.<br>
            Please ensure to be ready by {take_off_time}.</p>
            <p>Regards,<br>Transport and Logistics Team</p>
        </body>
    </html>
    """
    send_email(email_to, subject, html_content)


def notify_driver_about_trip_assignment(email_to: str, vehicle_name: str, vehicle_plate: str, employee_names: List[str]):
    """Send email to the driver with details about the trip assignment."""
    subject = "Your Trip Assignment"
    employee_list = ', '.join(employee_names)  # Creating a comma-separated string of employee names
    html_content = f"""
    <html>
        <body>
            <p>Hi,<br>
            You have been assigned to drive the following vehicle:<br>
            <strong>Vehicle:</strong> {vehicle_name} - {vehicle_plate}<br>
            <strong>Passengers:</strong> {employee_list}<br>
            Please review the passenger list and be prepared for the trip.<br>
            Thank you for your service.<br>
            <p>Regards,<br>Transport and Logistics Team</p>
            </p>
        </body>
    </html>
    """
    send_email(email_to, subject, html_content)


async def send_reminder_email(email: str, driver_name: str, trip_code: str):
    subject = "Reminder: Trip Not Yet Completed"
    content = f"""
    <html>
        <body>
            <p>Dear {driver_name},</p>
            <p>Your trip with the code <b>{trip_code}</b> is still marked as 'Trip Started'. Please remember to update the trip status by the end of your day.</p>
            <p>Regards,<br>Your Logistics Team</p>
        </body>
    </html>
    """
    await send_email(email, subject, content)


def send_birthday_emails(db_session: Session):
    """Send birthday emails to employees whose birthday is today."""
    today = datetime.now()
    employees_with_birthday = db_session.query(Employee).filter(
        func.extract('month', Employee.date_of_birth) == today.month,
        func.extract('day', Employee.date_of_birth) == today.day
    ).all()

    for employee in employees_with_birthday:
        subject = "Happy Birthday!"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="text-align: center;">
                        <img src="cid:birthday_image" alt="Happy Birthday!" style="width: 100%; max-width: 400px; border-radius: 10px;" />
                    </div>
                    <h1 style="color: #333333;">Happy Birthday, {employee.first_name} {employee.last_name}!</h1>
                    <p style="color: #555555; font-size: 16px;">
                        On behalf of everyone at Caritas Nigeria, we want to wish you a very Happy Birthday! 🎉
                    </p>
                    <p style="color: #555555; font-size: 16px;">
                        Your hard work and dedication are truly appreciated, and we're grateful to have you as part of our team. Today, we celebrate you and the unique contributions you bring to our company.
                    </p>
                    <p style="color: #555555; font-size: 16px;">
                        May your special day be filled with joy, laughter, and wonderful moments. Take some time to relax and enjoy the celebration with your loved ones.
                    </p>
                    <p style="color: #555555; font-size: 16px;">
                        Happy Birthday once again! Here's to a fantastic year ahead, both professionally and personally.
                    </p>
                    <p style="color: #555555; font-size: 16px;">
                        Best wishes,<br>Caritas Nigeria
                    </p>
                </div>
            </body>
        </html>
        """

        images = [
            ("images/happy_birthday.png", "birthday_image")
        ]

        send_email(employee.employee_email, subject, html_content, images=images)



def notify_employees_about_issue_logs(focal_persons:List[tuple], issue_initiator:str, issue:str, issue_description:str, recommendation:Optional[str]=None, time_line_date:str=None):
    for first_name, email in focal_persons:
        subject = "Issue Log Notification"
        content = f"""
        <html>
            <body>
                <p>Dear {first_name},</p>
                <p>Your name has been mentioned as the responsible person for an Issue Log raised by {issue_initiator}. </p>
                <strong>See the Issue Log details below</strong><br>
                <ul>
                    <li><strong>Issue:</strong> {issue}</li>
                    <li><strong>Issue Description:</strong> {issue_description}</li>
                    <li><strong>Recommendation:</strong> {recommendation}</li>
                    <li><strong>Timeline:</strong> {time_line_date}</li>
                </ul>
                Please login to the Workplan Platform to see more details about the Issue Log.
                <p>Regards,<br>CCFN Workplan System</p>
            </body?
        </html>
        """
        # Remove recommendation if there is none
        if recommendation is None or recommendation==f"<li><strong>Recommendation:</strong>None</li>":
            counter =0
            recommendation = f"<li><strong>Recommendation:</strong> {recommendation}</li>"
            content = ' '.join(content.split())
            content = content.replace(recommendation, "")
            counter+=1

        send_email(email_to=email, subject=subject, html_content=content)


def notify_employees_about_update_on_issue_logs(focal_persons:List[tuple], issue_initiator:str, issue:str, issue_description:str, recommendation:Optional[str], time_line_date:str):
    for first_name, email in focal_persons:
        subject = "Issue Log Update Notification"

        content = f"""
        <html>
            <body>
                <p>Dear {first_name},</p>
                <p>There has been an update on Issue Log raised by {issue_initiator}. </p>
                <strong>See the Updated Issue Log details below</strong><br>
                <ul>
                    <li><strong>Issue:</strong> {issue}</li>
                    <li><strong>Issue Description:</strong> {issue_description}</li>
                    <li><strong>Recommendation:</strong> {recommendation}</li>
                    <li><strong>Timeline:</strong> {time_line_date}</li>
                </ul>
                Please login to the Workplan Platform to see more details about the Issue Log.
                <p>Regards,<br>CCFN Workplan System</p>
            </body?
        </html>
        """
        # Remove recommendation if there is none
        if recommendation is None or recommendation==f"<li><strong>Recommendation:</strong>None</li>":
            counter =0
            recommendation = f"<li><strong>Recommendation:</strong> {recommendation}</li>"
            content = ' '.join(content.split())
            content = content.replace(recommendation, "")
            counter+=1

        send_email(email_to=email, subject=subject, html_content=content)


def notify_employees_about_completed_issue_logs(focal_persons:List[tuple], issue_initiator:str, issue:str, issue_description:str, notes_on_closure:Optional[str]=None, close_date:str=None):
    for first_name, email in focal_persons:
        subject = "Issue Log Completion Notification"
        content = f"""
        <html>
            <body>
                <p>Dear {first_name},</p>
                <p>This is to kindly notify you that Issue Log raised by {issue_initiator} has been completed successfully. </p>
                <strong>See the details below</strong><br>
                <ul>
                    <li><strong>Date of Completion:</strong> {close_date}</li>
                     <li><strong>Note on Closure:</strong> {notes_on_closure}</li>
                    <li><strong>Issue:</strong> {issue}</li>
                    <li><strong>Issue Description:</strong> {issue_description}</li>
                </ul>
                Please login to the Workplan Platform to see more details about the completed Issue Log.
                <p>Regards,<br>CCFN Workplan System</p>
            </body?
        </html>
        """
        # Remove recommendation if there is none
        if notes_on_closure is None or notes_on_closure==f"<li><strong>Note on Closure:</strong>None</li>":
            counter =0
            notes_on_closure = f"<li><strong>Note on Closure:</strong> {notes_on_closure}</li>"
            content = ' '.join(content.split())
            content = content.replace(notes_on_closure, "")
            counter+=1

        send_email(email_to=email, subject=subject, html_content=content)

    
def notify_initiator_about_issue_logs(focal_persons_names:tuple, initiator_first_name, initiator_email, issue:str, issue_description:str, recommendation:Optional[str]=None, time_line_date:str=None):
    subject = "Issue Log Notification"
    content = f"""
    <html>
        <body>
            <p>Dear {initiator_first_name},</p>
            <p>You have created an issue log successfully. </p>
            <strong>See the Issue Log details below</strong><br>
            <ul>
                <li><strong>Issue:</strong> {issue}</li>
                <li><strong>Issue Description:</strong> {issue_description}</li>
                <li><strong>Recommendation:</strong> {recommendation}</li>
                <li><strong>Timeline:</strong> {time_line_date}</li>
                <li><strong>Focal Person(s):</strong> {focal_persons_names}</li>
            </ul>
            Please login to the Workplan Platform to see more details about the Issue Log.
            <p>Regards,<br>CCFN Workplan System</p>
        </body?
    </html>
    """
    # Remove recommendation if there is none
    if recommendation is None or recommendation==f"<li><strong>Recommendation:</strong>None</li>":
        counter =0
        recommendation = f"<li><strong>Recommendation:</strong> {recommendation}</li>"
        content = ' '.join(content.split())
        content = content.replace(recommendation, "")
        counter+=1

    send_email(email_to=initiator_email, subject=subject, html_content=content)




def notify_initiator_about_completed_issue_logs(first_name, email:str, issue:str, issue_description:str, notes_on_closure:Optional[str]=None, close_date:str=None):

    subject = "Issue Log Completion Notification"
    content = f"""
    <html>
        <body>
            <p>Dear {first_name},</p>
            <p>This is to kindly notify you that the Issue Log you raised has been completed successfully. </p>
            <strong>See the details below</strong><br>
            <ul>
                <li><strong>Date of Completion:</strong> {close_date}</li>
                    <li><strong>Note on Closure:</strong> {notes_on_closure}</li>
                <li><strong>Issue:</strong> {issue}</li>
                <li><strong>Issue Description:</strong> {issue_description}</li>
            </ul>
            Please login to the Workplan Platform to see more details about the completed Issue Log.
            <p>Regards,<br>CCFN Workplan System</p>
        </body?
    </html>
    """
    # Remove recommendation if there is none
    if notes_on_closure is None or notes_on_closure==f"<li><strong>Note on Closure:</strong>None</li>":
        counter =0
        notes_on_closure = f"<li><strong>Note on Closure:</strong> {notes_on_closure}</li>"
        content = ' '.join(content.split())
        content = content.replace(notes_on_closure, "")
        counter+=1

    send_email(email_to=email, subject=subject, html_content=content)
    

def notify_assignment_creation(recipients, assignment_name, initiator_name):
    subject = "New Assignment Created"
    recipient_emails = [email for _, email in recipients]
    recipient_names = ", ".join(first_name for first_name, _ in recipients)
    
    html_content = f"""
    <html>
        <body>
            <p>Hi {recipient_names},<br>
               You have been assigned to a new assignment created by {initiator_name}, with the name 
               <strong>'{assignment_name}'</strong>.<br>
               Please login to the platform for more details.
               <p>Regards,<br>Workplan System</p>
            </p>
        </body>
    </html>
    """
    send_email(", ".join(recipient_emails), subject, html_content)

def notify_initiator_about_assignment(email_to, initiator_name, assignment_name, assignment_status):
    subject = "Assignment Creation Update"
    html_content = f"""
    <html>
        <body>
            <p>Hi {initiator_name},<br>
               You have successfully created a new assignment titled '<strong>{assignment_name}</strong>'.
               <br>
               Current Status: <strong>{assignment_status}</strong><br>
               You can track the progress and updates related to this assignment in the system.
               <p>Regards,<br>Workplan System</p>
            </p>
        </body>
    </html>
    """
    send_email(email_to, subject, html_content)


def notify_stage_email(stage: str, employee_email: str, supervisor_email: str):
    """
    Send an email notification when a leave request progresses to a new stage.
    
    Args:
        stage (str): The current stage of the leave request.
        employee_email (str): The email address of the employee.
        supervisor_email (str): The email address of the supervisor.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    subject = f"Leave Request: Progress to {stage}"
    html_content = f"""
    <html>
        <body>
            <p>Dear Employee,</p>
            <p>Your leave request has progressed to the <strong>{stage}</strong> stage.</p>
            <p>Please take the necessary actions to move forward with the leave process.</p>
            <p>Regards,<br>CCFN Workspace Team</p>
        </body>
    </html>
    """
    if send_email(employee_email, subject, html_content) and send_email(supervisor_email, subject, html_content):
        return True
    return False




# def notify_holiday_creation(recipients: List[str], holiday_name: str, holiday_date: datetime.date, holiday_description: str, ceo_email: str):
#     """
#     Notify all employees and the CEO about a new public holiday creation.

#     Args:
#         recipients (List[str]): List of employee email addresses.
#         holiday_name (str): Name of the holiday.
#         holiday_date (datetime.date): Date of the holiday.
#         holiday_description (str): Description of the holiday.
#         ceo_email (str): Email address of the CEO.
#     """
#     subject = f"New Public Holiday Announcement: {holiday_name}"
#     body = (
#         f"Dear All,\n\n"
#         f"We are pleased to announce that {holiday_date.strftime('%Y-%m-%d')} has been declared as a public holiday.\n\n"
#         f"Holiday: {holiday_name}\n"
#         f"Description: {holiday_description}\n\n"
#         f"Best regards,\n"
#         f"Management"
#     )

#     # Add CEO's email to the recipient list if it's not already included
#     if ceo_email not in recipients:
#         recipients.append(ceo_email)

#     # Send email to all recipients
#     for email in recipients:
#         send_email(email_to=email, subject=subject, html_content=body)
    
#     print("Holiday announcement email sent to all employees with the CEO in copy.")




def get_greeting_based_on_time():
    """Determine the appropriate greeting based on the current time."""
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

# def notify_holiday_creation(recipients: List[Tuple[str, str]], holiday_name: str, holiday_date: datetime.date, holiday_description: str, ceo_email: str, holiday_type_id: int):
#     """
#     Notify all employees and the CEO about a new public holiday creation.

#     Args:
#         recipients (List[Tuple[str, str]]): List of tuples containing employee first names and email addresses.
#         holiday_name (str): Name of the holiday.
#         holiday_date (datetime.date): Date of the holiday.
#         holiday_description (str): Description of the holiday.
#         ceo_email (str): Email address of the CEO.
#         holiday_type_id (int): Type of the holiday.
#     """
#     greeting = get_greeting_based_on_time()

#     if holiday_type_id == 1:
#         body_template = (
#             f"Dear All,\n\n"
#             f"{greeting}.\n\n"
#             f"We are pleased to inform you that the Executive Management has approved {holiday_date.strftime('%A, %B %d, %Y')}, as a public holiday in line with the Federal Government's declaration to mark the {holiday_name}.\n\n"
#             "Best regards,"
#         )
#     else:
#         body_template = (
#             f"Dear All,\n\n"
#             f"{greeting}.\n\n"
#             f"We are pleased to inform you that the Executive Management has approved {holiday_date.strftime('%A, %B %d, %Y')}, the {holiday_name}, as a public holiday.\n\n"
#             "Best regards,\n"
#             "Management"
#         )

#     # Prepare the subject and email content
#     subject = f"New Public Holiday Announcement: {holiday_name}"
#     recipient_emails = [email for _, email in recipients]
#     recipient_names = ", ".join(first_name for first_name, _ in recipients)

#     html_content = f"""
#     <html>
#         <body>
#             <p>{body_template}</p>
#         </body>
#     </html>
#     """

#     # Send the email to all recipients at once with the CEO copied
#     send_email(email_to=", ".join(recipient_emails), subject=subject, html_content=html_content, cc=ceo_email)
    
#     logging_helper.log_info("Holiday announcement email sent to all employees with the CEO in copy.")


import asyncio

async def notify_holiday_creation(recipients: List[Tuple[str, str]], holiday_name: str, holiday_date: datetime.date, holiday_description: str, ceo_email: str, holiday_type_id: int):
    """
    Notify all employees and the CEO about a new public holiday creation.

    Args:
        recipients (List[Tuple[str, str]]): List of tuples containing employee first names and email addresses.
        holiday_name (str): Name of the holiday.
        holiday_date (datetime.date): Date of the holiday.
        holiday_description (str): Description of the holiday.
        ceo_email (str): Email address of the CEO.
        holiday_type_id (int): Type of the holiday.
    """
    greeting = get_greeting_based_on_time()

    if holiday_type_id == 1:
        body_template = (
            f"Dear All,\n\n"
            f"{greeting}.\n\n"
            f"We are pleased to inform you that the Executive Management has approved {holiday_date.strftime('%A, %B %d, %Y')}, as a public holiday in line with the Federal Government's declaration to mark the {holiday_name}.\n\n"
            "Best regards,"
        )
    else:
        body_template = (
            f"Dear All,\n\n"
            f"{greeting}.\n\n"
            f"We are pleased to inform you that the Executive Management has approved {holiday_date.strftime('%A, %B %d, %Y')}, the {holiday_name}, as a public holiday.\n\n"
            "Best regards,\n"
            "Management"
        )

    # Prepare the subject and email content
    subject = f"New Public Holiday Announcement: {holiday_name}"
    recipient_emails = [email for _, email in recipients]

    html_content = f"""
    <html>
        <body>
            <p>{body_template}</p>
        </body>
    </html>
    """

    # Send the email to all recipients at once with the CEO copied
    await asyncio.to_thread(send_email, email_to=", ".join(recipient_emails), subject=subject, html_content=html_content, cc=ceo_email)
    
    logging_helper.log_info("Holiday announcement email sent to all employees with the CEO in copy.")



#email notification to the next person in the person in the Approval flow
def notify_next_approval_step(email_to: str, employee_name: str, flow_name: str, request_link: str):
    """
    Notify the next approver about a pending approval step.
    
    Args:
        email_to (str): The email address of the next approver.
        employee_name (str): The name of the employee involved in the request.
        flow_name (str): The name of the approval flow.
        request_link (str): The URL link to the approval request.
    """
    subject = "Approval Required for Next Step"
    html_content = f"""
    <html>
        <body>
            <p>Dear {employee_name},</p>
            <p>You have a pending approval step in the '{flow_name}' approval flow. Please review the request and take the necessary action.</p>
            <p><a href="{request_link}">Click here to view and approve the request</a></p>
            <p>Regards,<br>Your Approval Management Team</p>
        </body>
    </html>
    """
    send_email(email_to=email_to, subject=subject, html_content=html_content)

# def notify_request_initiator(email_to: str, initiator_name: str, flow_name: str, step_description: str, request_link: str):
#     """
#     Notify the request initiator about the current step in the approval flow.

#     Args:
#         email_to (str): The email address of the initiator.
#         initiator_name (str): The name of the initiator.
#         flow_name (str): The name of the approval flow.
#         step_description (str): Description of the current approval step.
#         request_link (str): The URL link to view the approval request.
#     """
#     subject = "Your Request is Moving Through the Approval Process"
#     html_content = f"""
#     <html>
#         <body>
#             <p>Dear {initiator_name},</p>
#             <p>Your request in the '{flow_name}' approval flow has advanced to the following step:</p>
#             <p><strong>Current Step:</strong> {step_description}</p>
#             <p>You can follow the progress by <a href="{request_link}">clicking here to view your request</a>.</p>
#             <p>Regards,<br>Your Approval Management Team</p>
#         </body>
#     </html>
#     """
#     send_email(email_to=email_to, subject=subject, html_content=html_content)


# def notify_request_initiator_of_rejection(email_to: str, employee_name: str, approver_name: str, rejection_comment: str, request_link: str):
#     """
#     Send an email to the initiator notifying them of the rejection with a comment.

#     Args:
#         email_to (str): Email of the initiator.
#         employee_name (str): Name of the employee whose review was rejected.
#         approver_name (str): Name of the approver who rejected the review.
#         rejection_comment (str): The comment explaining the rejection.
#         request_link (str): The link to view the performance review.
#     """
#     subject = f"Performance Review Rejected by {approver_name}"
#     html_content = f"""
#     <html>
#         <body>
#             <p>Hi {employee_name},</p>
#             <p>Your performance review has been rejected by {approver_name} with the following comment:</p>
#             <blockquote>{rejection_comment}</blockquote>
#             <p>You can view the review by following this <a href="{request_link}">link</a>.</p>
#             <p>Regards,<br>Your Performance Review System</p>
#         </body>
#     </html>
    # """
    # send_email(email_to, subject, html_content)



def notify_request_initiator_of_approval(email_to: str, initiator_name: str, approver_name: str, request_type: str, request_link: str):
    """
    Send an email to the initiator notifying them of the approval.

    Args:
        email_to (str): Email of the initiator.
        initiator_name (str): Name of the initiator.
        approver_name (str): Name of the approver who approved the request.
        request_type (str): Type of the request (e.g., "Performance Review", "Leave Request").
        request_link (str): The link to view the request.
    """
    subject = f"{request_type} Approved by {approver_name}"
    html_content = f"""
    <html>
        <body>
            <p>Hi {initiator_name},</p>
            <p>Your {request_type} has been approved by {approver_name}. You can view the details by following this <a href="{request_link}">link</a>.</p>
            <p>Regards,<br>Your System Team</p>
        </body>
    </html>
    """
    send_email(email_to, subject, html_content)


def notify_request_initiator_of_rejection(email_to: str, initiator_name: str, approver_name: str, request_type: str, rejection_reason: str, request_link: str):
    """
    Send an email to the initiator notifying them of the rejection and providing the reason.

    Args:
        email_to (str): Email of the initiator.
        initiator_name (str): Name of the initiator.
        approver_name (str): Name of the approver who rejected the request.
        request_type (str): Type of the request (e.g., "Performance Review", "Leave Request").
        rejection_reason (str): Reason for the rejection.
        request_link (str): The link to view the request.
    """
    subject = f"{request_type} Rejected by {approver_name}"
    html_content = f"""
    <html>
        <body>
            <p>Hi {initiator_name},</p>
            <p>Your {request_type} has been rejected by {approver_name} for the following reason:</p>
            <blockquote>{rejection_reason}</blockquote>
            <p>You can view the details by following this <a href="{request_link}">link</a>.</p>
            <p>Regards,<br>Your System Team</p>
        </body>
    </html>
    """
    send_email(email_to, subject, html_content)

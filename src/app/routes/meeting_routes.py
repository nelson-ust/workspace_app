# from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, Response
# from sqlalchemy.orm import Session
# from typing import List, Dict, Any
# from db.database import get_db
# from repositories.meeting_repository import MeetingRepository
# from logging_helpers import logging_helper
# from auth.security import get_current_user
# from models.all_models import User, ActionEnum
# from schemas.meeting_schemas import MeetingCreate, MeetingUpdate, MealSelectionCreate, ParticipantCreate, MeetingMinutesCreate, AttendanceCreate
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# from auth.third_party_template_generator import generate_template
# import json

# limiter = Limiter(key_func=get_remote_address)

# router = APIRouter()

# @router.get("/meetings/third-party-participants/template", status_code=status.HTTP_200_OK)
# @limiter.limit("10/minute")
# async def download_template(request: Request,file_type: str = Query(..., description="File type can be 'csv' or 'excel'")):
#     logging_helper.log_info("Accessing - Download Template - Endpoint")
#     try:
#         file_content, content_type = generate_template(file_type)
#         file_extension = "csv" if file_type == "csv" else "xlsx"
#         file_name = f"third_party_participants_template.{file_extension}"
        
#         headers = {
#             "Content-Disposition": f"attachment; filename={file_name}"
#         }
        
#         return Response(content=file_content, media_type=content_type, headers=headers)
#     except HTTPException as e:
#         logging_helper.log_error(f"Failed to generate template: {e.detail}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Failed to generate template: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate template")


# @router.post("/meetings/", status_code=status.HTTP_201_CREATED)
# @limiter.limit("5/minute")
# async def create_meeting(request: Request, meeting: MeetingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info("Accessing - Create Meeting - Endpoint")
#     meeting_repo = MeetingRepository(db)
#     try:
#         new_meeting = meeting_repo.create_meeting(**meeting.dict())
#         logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "Meeting", new_meeting.id, json.dumps(meeting.dict(), default=str))
#         # return new_meeting
#         return {"message": f"Meeting created Successfully"}
#     except Exception as e:
#         logging_helper.log_error(f"Failed to create meeting: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create meeting")

# @router.get("/meetings/{meeting_id}", status_code=status.HTTP_200_OK)
# @limiter.limit("10/minute")
# async def get_meeting_by_id(request: Request, meeting_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info(f"Accessing - Get Meeting by ID - Endpoint for meeting ID: {meeting_id}")
#     meeting_repo = MeetingRepository(db)
#     try:
#         meeting = meeting_repo.get_meeting_by_id(meeting_id)
#         if not meeting:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
#         logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Meeting", meeting_id, None)
#         return meeting
#     except Exception as e:
#         logging_helper.log_error(f"Failed to fetch meeting with ID: {meeting_id}: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch meeting")

# @router.get("/meetings/", status_code=status.HTTP_200_OK)
# @limiter.limit("10/minute")
# async def get_all_meetings(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info("Accessing - Get All Meetings - Endpoint")
#     meeting_repo = MeetingRepository(db)
#     try:
#         meetings = meeting_repo.get_all_meetings()
#         logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Meeting", None, None)
#         return meetings
#     except Exception as e:
#         logging_helper.log_error(f"Failed to fetch all meetings: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch meetings")

# @router.put("/meetings/{meeting_id}", status_code=status.HTTP_200_OK)
# @limiter.limit("5/minute")
# async def update_meeting(request: Request, meeting_id: int, meeting: MeetingUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info(f"Accessing - Update Meeting - Endpoint for meeting ID: {meeting_id}")
#     meeting_repo = MeetingRepository(db)
#     try:
#         updated_meeting = meeting_repo.update_meeting(meeting_id, **meeting.dict())
#         if not updated_meeting:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
#         logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "Meeting", meeting_id, json.dumps(meeting.dict(), default=str))
#         return updated_meeting
#     except Exception as e:
#         logging_helper.log_error(f"Failed to update meeting with ID: {meeting_id}: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update meeting")

# @router.delete("/meetings/{meeting_id}", status_code=status.HTTP_200_OK)
# @limiter.limit("5/minute")
# async def delete_meeting(request: Request, meeting_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info(f"Accessing - Delete Meeting - Endpoint for meeting ID: {meeting_id}")
#     meeting_repo = MeetingRepository(db)
#     try:
#         deleted_meeting = meeting_repo.delete_meeting(meeting_id)
#         if not deleted_meeting:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
#         logging_helper.log_audit(db, current_user.id, ActionEnum.DELETE, "Meeting", meeting_id, None)
#         return {"message": f"The Meeting with ID: {meeting_id} deleted successfully!"}
#     except Exception as e:
#         logging_helper.log_error(f"Failed to delete meeting with ID: {meeting_id}: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete meeting")

# @router.post("/meetings/{meeting_id}/meal-selections", status_code=status.HTTP_201_CREATED)
# @limiter.limit("5/minute")
# async def add_meal_selection(request: Request, meeting_id: int, meal_selection: MealSelectionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info(f"Accessing - Add Meal Selection - Endpoint for meeting ID: {meeting_id}")
#     meeting_repo = MeetingRepository(db)
#     try:
#         new_meal_selection = meeting_repo.add_meal_selection(meeting_id, **meal_selection.dict())
#         logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "MealSelection", new_meal_selection.id, json.dumps(meal_selection.dict(), default=str))
#         return new_meal_selection
#     except Exception as e:
#         logging_helper.log_error(f"Failed to add meal selection for meeting ID: {meeting_id}: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add meal selection")

# @router.post("/meetings/{meeting_id}/participants", status_code=status.HTTP_201_CREATED)
# @limiter.limit("5/minute")
# async def add_participant(request: Request, meeting_id: int, participant: ParticipantCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info(f"Accessing - Add Participant - Endpoint for meeting ID: {meeting_id}")
#     meeting_repo = MeetingRepository(db)
#     try:
#         new_participant = meeting_repo.add_participant(meeting_id, **participant.dict())
#         logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "Participant", new_participant.id, json.dumps(participant.dict(), default=str))
#         return new_participant
#     except Exception as e:
#         logging_helper.log_error(f"Failed to add participant for meeting ID: {meeting_id}: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add participant")

# @router.post("/meetings/{meeting_id}/minutes", status_code=status.HTTP_201_CREATED)
# @limiter.limit("5/minute")
# async def add_meeting_minutes(request: Request, meeting_id: int, minutes: MeetingMinutesCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info(f"Accessing - Add Meeting Minutes - Endpoint for meeting ID: {meeting_id}")
#     meeting_repo = MeetingRepository(db)
#     try:
#         new_minutes = meeting_repo.add_meeting_minutes(meeting_id, **minutes.dict())
#         logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "Minutes", new_minutes.id, json.dumps(minutes.dict(), default=str))
#         return new_minutes
#     except Exception as e:
#         logging_helper.log_error(f"Failed to add minutes for meeting ID: {meeting_id}: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add minutes")

# @router.post("/meetings/{meeting_id}/attendances", status_code=status.HTTP_201_CREATED)
# @limiter.limit("5/minute")
# async def add_attendance(request: Request, meeting_id: int, attendance: AttendanceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info(f"Accessing - Add Attendance - Endpoint for meeting ID: {meeting_id}")
#     meeting_repo = MeetingRepository(db)
#     try:
#         new_attendance = meeting_repo.add_attendance(meeting_id, **attendance.dict())
#         logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "Attendance", new_attendance.id, json.dumps(attendance.dict(), default=str))
#         return new_attendance
#     except Exception as e:
#         logging_helper.log_error(f"Failed to add attendance for meeting ID: {meeting_id}: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add attendance")

# @router.get("/meetings/types", status_code=status.HTTP_200_OK)
# @limiter.limit("10/minute")
# async def get_meeting_types(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info("Accessing - Get Meeting Types - Endpoint")
#     meeting_repo = MeetingRepository(db)
#     try:
#         meeting_types = meeting_repo.get_meeting_types()
#         logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "MeetingType", None, None)
#         return meeting_types
#     except Exception as e:
#         logging_helper.log_error(f"Failed to fetch meeting types: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch meeting types")

# @router.get("/companies", status_code=status.HTTP_200_OK)
# @limiter.limit("10/minute")
# async def get_companies(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info("Accessing - Get Companies - Endpoint")
#     meeting_repo = MeetingRepository(db)
#     try:
#         companies = meeting_repo.get_companies()
#         logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Company", None, None)
#         return companies
#     except Exception as e:
#         logging_helper.log_error(f"Failed to fetch companies: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch companies")

# @router.get("/meal-combinations", status_code=status.HTTP_200_OK)
# @limiter.limit("10/minute")
# async def get_meal_combinations(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info("Accessing - Get Meal Combinations - Endpoint")
#     meeting_repo = MeetingRepository(db)
#     try:
#         meal_combinations = meeting_repo.get_meal_combinations()
#         logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "MealCombination", None, None)
#         return meal_combinations
#     except Exception as e:
#         logging_helper.log_error(f"Failed to fetch meal combinations: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch meal combinations")






from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, Response
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from db.database import get_db
from repositories.meeting_repository import MeetingRepository
from logging_helpers import logging_helper
from auth.security import get_current_user
from models.all_models import User, ActionEnum
from schemas.meeting_schemas import MeetingCreate, MeetingUpdate, MealSelectionCreate, ParticipantCreate, MeetingMinutesCreate, AttendanceCreate
from slowapi import Limiter
from slowapi.util import get_remote_address
from auth.third_party_template_generator import generate_template
import json

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

@router.get("/meetings/third-party-participants/template", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def download_template(request: Request, file_type: str = Query(..., description="File type can be 'csv' or 'excel'")):
    logging_helper.log_info("Accessing - Download Template - Endpoint")
    try:
        file_content, content_type = generate_template(file_type)
        file_extension = "csv" if file_type == "csv" else "xlsx"
        file_name = f"third_party_participants_template.{file_extension}"
        
        headers = {
            "Content-Disposition": f"attachment; filename={file_name}"
        }
        
        return Response(content=file_content, media_type=content_type, headers=headers)
    except HTTPException as e:
        logging_helper.log_error(f"Failed to generate template: {e.detail}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Failed to generate template: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate template")

@router.post("/meetings/", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_meeting(request: Request, meeting: MeetingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Create Meeting - Endpoint")
    meeting_repo = MeetingRepository(db)
    try:
        new_meeting = meeting_repo.create_meeting(**meeting.dict())
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "Meeting", new_meeting.id, json.dumps(meeting.dict(), default=str))
        return {"message": f"Meeting created Successfully"}
    except Exception as e:
        logging_helper.log_error(f"Failed to create meeting: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create meeting")

@router.get("/meetings/{meeting_id}", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def get_meeting_by_id(request: Request, meeting_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info(f"Accessing - Get Meeting by ID - Endpoint for meeting ID: {meeting_id}")
    meeting_repo = MeetingRepository(db)
    try:
        meeting = meeting_repo.get_meeting_by_id(meeting_id)
        if not meeting:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Meeting", meeting_id, None)
        return meeting
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch meeting with ID: {meeting_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch meeting")

@router.get("/meetings/", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def get_all_meetings(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Get All Meetings - Endpoint")
    meeting_repo = MeetingRepository(db)
    try:
        meetings = meeting_repo.get_all_meetings()
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Meeting", None, None)
        return meetings
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch all meetings: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch meetings")

@router.put("/meetings/{meeting_id}", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def update_meeting(request: Request, meeting_id: int, meeting: MeetingUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info(f"Accessing - Update Meeting - Endpoint for meeting ID: {meeting_id}")
    meeting_repo = MeetingRepository(db)
    try:
        updated_meeting = meeting_repo.update_meeting(meeting_id, **meeting.dict())
        if not updated_meeting:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
        logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "Meeting", meeting_id, json.dumps(meeting.dict(), default=str))
        return updated_meeting
    except Exception as e:
        logging_helper.log_error(f"Failed to update meeting with ID: {meeting_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update meeting")

@router.delete("/meetings/{meeting_id}", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def delete_meeting(request: Request, meeting_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info(f"Accessing - Delete Meeting - Endpoint for meeting ID: {meeting_id}")
    meeting_repo = MeetingRepository(db)
    try:
        deleted_meeting = meeting_repo.delete_meeting(meeting_id)
        if not deleted_meeting:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
        logging_helper.log_audit(db, current_user.id, ActionEnum.DELETE, "Meeting", meeting_id, None)
        return {"message": f"The Meeting with ID: {meeting_id} deleted successfully!"}
    except Exception as e:
        logging_helper.log_error(f"Failed to delete meeting with ID: {meeting_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete meeting")

@router.post("/meetings/{meeting_id}/meal-selections", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def add_meal_selection(request: Request, meeting_id: int, meal_selection: MealSelectionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info(f"Accessing - Add Meal Selection - Endpoint for meeting ID: {meeting_id}")
    meeting_repo = MeetingRepository(db)
    try:
        new_meal_selection = meeting_repo.add_meal_selection(meeting_id, **meal_selection.dict())
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "MealSelection", new_meal_selection.id, json.dumps(meal_selection.dict(), default=str))
        return new_meal_selection
    except Exception as e:
        logging_helper.log_error(f"Failed to add meal selection for meeting ID: {meeting_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add meal selection")

@router.post("/meetings/{meeting_id}/participants", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def add_participant(request: Request, meeting_id: int, participant: ParticipantCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info(f"Accessing - Add Participant - Endpoint for meeting ID: {meeting_id}")
    meeting_repo = MeetingRepository(db)
    try:
        new_participant = meeting_repo.add_participant(meeting_id, **participant.dict())
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "Participant", new_participant.id, json.dumps(participant.dict(), default=str))
        return new_participant
    except Exception as e:
        logging_helper.log_error(f"Failed to add participant for meeting ID: {meeting_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add participant")

@router.post("/meetings/{meeting_id}/minutes", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def add_meeting_minutes(request: Request, meeting_id: int, minutes: MeetingMinutesCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info(f"Accessing - Add Meeting Minutes - Endpoint for meeting ID: {meeting_id}")
    meeting_repo = MeetingRepository(db)
    try:
        new_minutes = meeting_repo.add_meeting_minutes(meeting_id, **minutes.dict())
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "Minutes", new_minutes.id, json.dumps(minutes.dict(), default=str))
        return new_minutes
    except Exception as e:
        logging_helper.log_error(f"Failed to add minutes for meeting ID: {meeting_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add minutes")

@router.post("/meetings/{meeting_id}/attendances", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def add_attendance(request: Request, meeting_id: int, attendance: AttendanceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info(f"Accessing - Add Attendance - Endpoint for meeting ID: {meeting_id}")
    meeting_repo = MeetingRepository(db)
    try:
        new_attendance = meeting_repo.add_attendance(meeting_id, **attendance.dict())
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "Attendance", new_attendance.id, json.dumps(attendance.dict(), default=str))
        return new_attendance
    except Exception as e:
        logging_helper.log_error(f"Failed to add attendance for meeting ID: {meeting_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add attendance")

@router.get("/meetings/types", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def get_meeting_types(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Get Meeting Types - Endpoint")
    meeting_repo = MeetingRepository(db)
    try:
        meeting_types = meeting_repo.get_meeting_types()
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "MeetingType", None, None)
        return meeting_types
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch meeting types: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch meeting types")

@router.get("/companies", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def get_companies(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Get Companies - Endpoint")
    meeting_repo = MeetingRepository(db)
    try:
        companies = meeting_repo.get_companies()
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Company", None, None)
        return companies
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch companies: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch companies")

@router.get("/meal-combinations", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def get_meal_combinations(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Get Meal Combinations - Endpoint")
    meeting_repo = MeetingRepository(db)
    try:
        meal_combinations = meeting_repo.get_meal_combinations()
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "MealCombination", None, None)
        return meal_combinations
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch meal combinations: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch meal combinations")

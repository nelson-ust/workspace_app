# routes/third_party_participant_routes.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request, Response, Query
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from repositories.third_party_participant_repository import ThirdPartyParticipantRepository
from logging_helpers import logging_helper
from auth.security import get_current_user
from models.all_models import User, ActionEnum
from schemas.company_schemas import ThirdPartyParticipantCreate, ThirdPartyParticipantUpdate, ThirdPartyParticipantResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import json
import pandas as pd
from io import BytesIO
import re

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return bool(pattern.match(email))

def validate_phone_number(phone_number: str) -> bool:
    """Validate phone number format."""
    pattern = re.compile(r"^(?:\+234|0)\d{10}$")
    return bool(pattern.match(phone_number))

@router.post("/third_party_participants/", response_model=ThirdPartyParticipantResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def add_third_party_participant(request: Request, participant: ThirdPartyParticipantCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logging_helper.log_info("Accessing - Create Third-Party Participant - Endpoint")
    participant_repo = ThirdPartyParticipantRepository(db)
    try:
        new_participant = participant_repo.add_third_party_participant(
            name=participant.name,
            email=participant.email,
            phone_number=participant.phone_number,
            company_id=participant.company_id,
            site_id=participant.site_id,
            meeting_id=participant.meeting_id
        )
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "ThirdPartyParticipant", new_participant.id, json.dumps(new_participant, default=str))
        return ThirdPartyParticipantResponse.from_orm(new_participant)
    except Exception as e:
        logging_helper.log_error(f"Failed to create third-party participant: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create third-party participant")

@router.get("/third_party_participants/{participant_id}", status_code=status.HTTP_200_OK, response_model=ThirdPartyParticipantResponse)
@limiter.limit("10/minute")
async def read_participant(request: Request, participant_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Read Third-Party Participant - Endpoint")
    participant_repo = ThirdPartyParticipantRepository(db)
    try:
        participant = participant_repo.get_third_party_participant_by_id(participant_id)
        if not participant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Third-party participant not found")
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "ThirdPartyParticipant", participant_id, None)
        return ThirdPartyParticipantResponse.from_orm(participant)
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch third-party participant: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch third-party participant")

@router.get("/third_party_participants/", status_code=status.HTTP_200_OK, response_model=List[ThirdPartyParticipantResponse])
@limiter.limit("10/minute")
async def read_participants(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Read All Third-Party Participants - Endpoint")
    participant_repo = ThirdPartyParticipantRepository(db)
    try:
        participants = participant_repo.get_all_third_party_participants()
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "ThirdPartyParticipant", None, "Read all third-party participants")
        return participants
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch third-party participants: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch third-party participants")

@router.put("/third_party_participants/{participant_id}", status_code=status.HTTP_200_OK, response_model=ThirdPartyParticipantResponse)
@limiter.limit("5/minute")
async def update_participant(request: Request, participant_id: int, participant: ThirdPartyParticipantUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Update Third-Party Participant - Endpoint")
    participant_repo = ThirdPartyParticipantRepository(db)
    try:
        updated_participant = participant_repo.update_third_party_participant(participant_id, **participant.dict(exclude_unset=True))
        if not updated_participant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Third-party participant not found")
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.UPDATE, "ThirdPartyParticipant", participant_id, json.dumps(updated_participant, default=str)
        )
        return ThirdPartyParticipantResponse.from_orm(updated_participant)
    except Exception as e:
        logging_helper.log_error(f"Failed to update third-party participant: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update third-party participant")

@router.delete("/third_party_participants/{participant_id}", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def delete_participant(request: Request, participant_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Delete Third-Party Participant - Endpoint")
    participant_repo = ThirdPartyParticipantRepository(db)
    try:
        deleted_participant = participant_repo.delete_third_party_participant(participant_id)
        if not deleted_participant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Third-party participant not found")
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.DELETE, "ThirdPartyParticipant", participant_id, json.dumps(deleted_participant, default=str)
        )
        return {"message": f"The Third-Party Participant with ID: {participant_id} deleted successfully!"}
    except Exception as e:
        logging_helper.log_error(f"Failed to delete third-party participant: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete third-party participant")

# Endpoint to download the template
@router.get("/third_party_participants/template", status_code=status.HTTP_200_OK)
async def download_template(request: Request, meeting_id: int = Query(...), format: str = Query("csv"), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        logging_helper.log_info("Accessing - Download Third-Party Participant Template - Endpoint")
        data = {
            "name": [""],
            "email": [""],
            "phone_number": [""],
            "company_id": [""],
            "site_id": [""],
            "meeting_id": [meeting_id]  # Auto populate the meeting_id column
        }

        df = pd.DataFrame(data)

        output = BytesIO()
        if format == "xlsx":
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            writer.save()
            output.seek(0)
            filename = "third_party_participants_template.xlsx"
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            df.to_csv(output, index=False)
            output.seek(0)
            filename = "third_party_participants_template.csv"
            media_type = "text/csv"

        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "ThirdPartyParticipantTemplate", None, f"Downloaded template for meeting_id: {meeting_id}")
        return Response(content=output.getvalue(), media_type=media_type, headers={"Content-Disposition": f"attachment; filename={filename}"})
    except Exception as e:
        logging_helper.log_error(f"Failed to generate template: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate template")

@router.post("/third_party_participants/bulk", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def bulk_insert_third_party_participants(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logging_helper.log_info("Accessing - Bulk Insert Third-Party Participants - Endpoint")
    participant_repo = ThirdPartyParticipantRepository(db)
    try:
        if file.content_type not in ["text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file format. Only CSV and XLSX files are supported.")

        df = pd.read_csv(file.file) if file.content_type == "text/csv" else pd.read_excel(file.file)

        required_columns = {"name", "email", "phone_number", "company_id", "site_id", "meeting_id"}
        if not required_columns.issubset(df.columns):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"CSV file must contain the following columns: {', '.join(required_columns)}")

        participants_to_add = []
        for _, row in df.iterrows():
            if not row["name"] or not row["email"] or not row["meeting_id"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name, email, and meeting_id are required for all participants.")
            if not validate_email(row["email"]):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid email format: {row['email']}")
            if not validate_phone_number(row["phone_number"]):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid phone number format: {row['phone_number']}")

            new_participant = participant_repo.add_third_party_participant(
                name=row["name"],
                email=row["email"],
                phone_number=row["phone_number"],
                company_id=row.get("company_id"),
                site_id=row.get("site_id"),
                meeting_id=row["meeting_id"]
            )
            participants_to_add.append(new_participant)

        db.commit()
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "ThirdPartyParticipant", None, "Bulk insert of third-party participants")
        return {"message": f"Successfully added {len(participants_to_add)} participants."}
    except Exception as e:
        db.rollback()
        logging_helper.log_error(f"Failed to bulk insert third-party participants: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to bulk insert third-party participants")

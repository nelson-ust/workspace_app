# Assuming your SQLAlchemy session and RequestStatus model are set up as follows:
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from models.all_models import RequestStatus
from schemas.requeststatus_schemas import RequestStatusCreate, RequestStatusUpdate

class RequestStatusRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_request_status_by_id(self, request_status_id: int) -> RequestStatus:
        try:
            request_status = self.db.query(RequestStatus).filter(RequestStatus.id == request_status_id).first()
            if not request_status:
                raise HTTPException(status_code=404, detail="RequestStatus not found")
            return request_status
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="An error occurred while fetching the RequestStatus.")

    def get_all_request_statuses(self) -> list[RequestStatus]:
        try:
            return self.db.query(RequestStatus).all()
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="An error occurred while fetching all RequestStatuses.")



def create_request_status(self, request_status_data: RequestStatusCreate) -> RequestStatus:
    try:
        # Check if a RequestStatus with the given name already exists
        existing_request_status = self.db.query(RequestStatus).filter(RequestStatus.name == request_status_data.name).first()
        if existing_request_status:
            raise HTTPException(status_code=400, detail=f"RequestStatus with name '{request_status_data.name}' already exists.")

        new_request_status = RequestStatus(**request_status_data.dict())
        self.db.add(new_request_status)
        self.db.commit()
        self.db.refresh(new_request_status)
        return new_request_status
    except SQLAlchemyError as e:
        self.db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred while creating the RequestStatus. Error: {str(e)}")

def update_request_status(self, request_status_id: int, request_status_update: RequestStatusUpdate) -> RequestStatus:
    try:
        db_request_status = self.db.query(RequestStatus).filter(RequestStatus.id == request_status_id).first()
        if not db_request_status:
            raise HTTPException(status_code=404, detail="RequestStatus not found")

        # Optional: Check if updating to a new name that already exists in another record
        if request_status_update.name:
            existing_request_status = self.db.query(RequestStatus).filter(RequestStatus.name == request_status_update.name, RequestStatus.id != request_status_id).first()
            if existing_request_status:
                raise HTTPException(status_code=400, detail=f"Another RequestStatus with name '{request_status_update.name}' already exists.")

        for var, value in request_status_update.dict(exclude_unset=True).items():
            setattr(db_request_status, var, value)
            
        self.db.commit()
        return db_request_status
    except SQLAlchemyError as e:
        self.db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred while updating the RequestStatus. Error: {str(e)}")

def delete_request_status(self, request_status_id: int):
    try:
        db_request_status = self.db.query(RequestStatus).filter(RequestStatus.id == request_status_id).first()
        if not db_request_status:
            raise HTTPException(status_code=404, detail="RequestStatus not found")

        # Check if it's already marked as inactive
        if not db_request_status.is_active:
            raise HTTPException(status_code=400, detail="RequestStatus is already deleted")

        # Mark as inactive instead of deleting
        db_request_status.is_active = False
        self.db.commit()
    except SQLAlchemyError as e:
        self.db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred while deleting the RequestStatus. Error: {str(e)}")
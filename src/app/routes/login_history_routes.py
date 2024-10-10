# routes/login_history_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from auth.security import get_current_user
from schemas.login_history_schemas import LoginHistoryRead
from repositories.login_history_repository import LoginHistoryRepository
from models.all_models import User
from logging_helpers import logging_helper

router = APIRouter()

@router.get("/login-history/", response_model=List[LoginHistoryRead], status_code=status.HTTP_200_OK)
async def read_login_history(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info(f"User {current_user.username} accessing login history")
    login_history_repo = LoginHistoryRepository(db)
    try:
        #login_history = login_history_repo.get_login_history(user_id=current_user.id, skip=skip, limit=limit)
        login_history = login_history_repo.get_login_history( skip=skip, limit=limit)
        return login_history
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch login history: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch login history")


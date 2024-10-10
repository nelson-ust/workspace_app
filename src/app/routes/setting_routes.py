from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from repositories.setting_repository import SettingRepository, SettingError

router = APIRouter()

@router.get("/settings/{setting_name}", response_model=str)
def read_setting(setting_name: str, db: Session = Depends(get_db)):
    try:
        setting_repo = SettingRepository(db)
        value = setting_repo.get_setting(setting_name)
        return value
    except SettingError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/settings/{setting_name}", response_model=str)
def create_or_update_setting(setting_name: str, value: str, db: Session = Depends(get_db)):
    try:
        setting_repo = SettingRepository(db)
        setting_repo.set_setting(setting_name, value)
        return value
    except SettingError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/settings/{setting_name}", response_model=str)
def update_existing_setting(setting_name: str, value: str, db: Session = Depends(get_db)):
    try:
        setting_repo = SettingRepository(db)
        setting_repo.update_setting(setting_name, value)
        return value
    except SettingError as e:
        raise HTTPException(status_code=404, detail=str(e))

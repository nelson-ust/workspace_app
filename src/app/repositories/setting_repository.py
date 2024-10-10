from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.all_models import Setting
from logging_helpers import logging_helper

class SettingError(Exception):
    """
    Custom exception class for setting-related errors.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class SettingRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_setting(self, setting_name: str) -> str:
        """
        Retrieve the value of a setting by its name.
        """
        try:
            setting = self.db_session.query(Setting).filter(Setting.setting_name == setting_name).first()
            if setting:
                logging_helper.log_info(f"Successfully fetched setting '{setting_name}' from the database")
                return setting.value
            raise SettingError(f"Setting '{setting_name}' not found")
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Database error fetching setting '{setting_name}': {str(e)}")
            raise SettingError(f"Database error: {str(e)}")

    def set_setting(self, setting_name: str, value: str):
        """
        Set the value of a setting. If the setting does not exist, it will be created.
        """
        try:
            setting = self.db_session.query(Setting).filter(Setting.setting_name == setting_name).first()
            if setting:
                setting.value = value
            else:
                setting = Setting(setting_name=setting_name, value=value)
                self.db_session.add(setting)
            self.db_session.commit()
            logging_helper.log_info(f"Successfully set setting '{setting_name}' in the database")
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Database error setting '{setting_name}': {str(e)}")
            raise SettingError(f"Database error: {str(e)}")

    def update_setting(self, setting_name: str, value: str):
        """
        Update the value of an existing setting. If the setting does not exist, an exception is raised.
        """
        try:
            setting = self.db_session.query(Setting).filter(Setting.setting_name == setting_name).first()
            if not setting:
                raise SettingError(f"Setting '{setting_name}' not found")
            setting.value = value
            self.db_session.commit()
            logging_helper.log_info(f"Successfully updated setting '{setting_name}' in the database")
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Database error updating setting '{setting_name}': {str(e)}")
            raise SettingError(f"Database error: {str(e)}")

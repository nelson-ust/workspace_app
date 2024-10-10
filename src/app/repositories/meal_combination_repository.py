# repositories/meal_combination_repository.py

from sqlalchemy.orm import Session
from models.all_models import MealCombination
from sqlalchemy.exc import SQLAlchemyError
from logging_helpers import logging_helper

class MealCombinationRepository:

    def __init__(self, db_session: Session):
        self.db_session = db_session

    # def create_meal_combination(self, name: str, description: str = None):
    #     try:
    #         meal_combination = MealCombination(
    #             name=name,
    #             description=description
    #         )
    #         self.db_session.add(meal_combination)
    #         self.db_session.commit()
    #         logging_helper.log_info(f"Created meal combination with ID: {meal_combination.id}")
    #         return meal_combination
    #     except SQLAlchemyError as e:
    #         self.db_session.rollback()
    #         logging_helper.log_error(f"Error creating meal combination: {e}")
    #         raise e


    def create_meal_combination(self, name: str, description: str = None):
        try:
            # Check for duplicate name
            existing_meal_combination = self.db_session.query(MealCombination).filter(MealCombination.name == name).first()
            if existing_meal_combination:
                logging_helper.log_error(f"Meal combination with name '{name}' already exists")
                raise ValueError(f"Meal combination with name '{name}' already exists")

            meal_combination = MealCombination(
                name=name,
                description=description
            )
            self.db_session.add(meal_combination)
            self.db_session.commit()
            logging_helper.log_info(f"Created meal combination with ID: {meal_combination.id}")
            return meal_combination
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error creating meal combination: {e}")
            raise e
        except ValueError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error creating meal combination: {e}")
            raise e



    def get_meal_combination_by_id(self, meal_combination_id: int):
        try:
            meal_combination = self.db_session.query(MealCombination).filter(MealCombination.id == meal_combination_id).first()
            logging_helper.log_info(f"Fetched meal combination with ID: {meal_combination_id}")
            return meal_combination
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching meal combination with ID: {meal_combination_id}: {e}")
            raise e

    def get_all_meal_combinations(self):
        try:
            meal_combinations = self.db_session.query(MealCombination).all()
            logging_helper.log_info("Fetched all meal combinations")
            return meal_combinations
        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error fetching all meal combinations: {e}")
            raise e

    def update_meal_combination(self, meal_combination_id: int, **kwargs):
        try:
            meal_combination = self.get_meal_combination_by_id(meal_combination_id)
            if not meal_combination:
                logging_helper.log_error(f"Meal combination not found with ID: {meal_combination_id}")
                return None
            for key, value in kwargs.items():
                setattr(meal_combination, key, value)
            self.db_session.commit()
            logging_helper.log_info(f"Updated meal combination with ID: {meal_combination_id}")
            return meal_combination
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error updating meal combination with ID: {meal_combination_id}: {e}")
            raise e

    def delete_meal_combination(self, meal_combination_id: int):
        try:
            meal_combination = self.get_meal_combination_by_id(meal_combination_id)
            if not meal_combination:
                logging_helper.log_error(f"Meal combination not found with ID: {meal_combination_id}")
                return None
            self.db_session.delete(meal_combination)
            self.db_session.commit()
            logging_helper.log_info(f"Deleted meal combination with ID: {meal_combination_id}")
            return meal_combination
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logging_helper.log_error(f"Error deleting meal combination with ID: {meal_combination_id}: {e}")
            raise e

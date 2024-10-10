
# # routes/meal_combination_routes.py

# from fastapi import APIRouter, Depends, HTTPException, Request, status
# from sqlalchemy.orm import Session
# from typing import List
# from db.database import get_db
# from repositories.meal_combination_repository import MealCombinationRepository
# from logging_helpers import logging_helper
# from auth.security import get_current_user
# from models.all_models import User, ActionEnum
# from schemas.meal_combination_schemas import MealCombinationCreate, MealCombinationUpdate, MealCombinationResponse
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# import json

# limiter = Limiter(key_func=get_remote_address)

# router = APIRouter()

# def serialize_model(model):
#     """Helper function to serialize SQLAlchemy model to dictionary."""
#     return {key: value for key, value in model.__dict__.items() if key != "_sa_instance_state"}

# @router.post("/meal_combinations/", response_model=MealCombinationResponse, status_code=status.HTTP_201_CREATED)
# @limiter.limit("5/minute")
# async def create_meal_combination(request: Request, meal_combination: MealCombinationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     logging_helper.log_info("Accessing - Create Meal Combination - Endpoint")
#     meal_combination_repo = MealCombinationRepository(db)
#     try:
#         new_meal_combination = meal_combination_repo.create_meal_combination(
#             name=meal_combination.name,
#             description=meal_combination.description
#         )
#         logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "MealCombination", new_meal_combination.id, json.dumps(serialize_model(new_meal_combination), default=str))
#         return MealCombinationResponse.from_orm(new_meal_combination)
#     except Exception as e:
#         logging_helper.log_error(f"Failed to create meal combination: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create meal combination")

# @router.get("/meal_combinations/{meal_combination_id}", response_model=MealCombinationResponse, status_code=status.HTTP_200_OK)
# @limiter.limit("10/minute")
# async def get_meal_combination(request: Request, meal_combination_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     logging_helper.log_info(f"Accessing - Get Meal Combination - Endpoint for ID: {meal_combination_id}")
#     meal_combination_repo = MealCombinationRepository(db)
#     try:
#         meal_combination = meal_combination_repo.get_meal_combination_by_id(meal_combination_id)
#         if not meal_combination:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal combination not found")
#         logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "MealCombination", meal_combination_id, None)
#         return MealCombinationResponse.from_orm(meal_combination)
#     except Exception as e:
#         logging_helper.log_error(f"Failed to fetch meal combination with ID: {meal_combination_id}: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch meal combination")

# @router.get("/meal_combinations/", response_model=List[MealCombinationResponse], status_code=status.HTTP_200_OK)
# @limiter.limit("10/minute")
# async def get_all_meal_combinations(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     logging_helper.log_info("Accessing - Get All Meal Combinations - Endpoint")
#     meal_combination_repo = MealCombinationRepository(db)
#     try:
#         meal_combinations = meal_combination_repo.get_all_meal_combinations()
#         logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "MealCombination", None, None)
#         return [MealCombinationResponse.from_orm(mc) for mc in meal_combinations]
#     except Exception as e:
#         logging_helper.log_error(f"Failed to fetch all meal combinations: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch meal combinations")

# @router.put("/meal_combinations/{meal_combination_id}", response_model=MealCombinationResponse, status_code=status.HTTP_200_OK)
# @limiter.limit("5/minute")
# async def update_meal_combination(request: Request, meal_combination_id: int, meal_combination: MealCombinationUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     logging_helper.log_info(f"Accessing - Update Meal Combination - Endpoint for ID: {meal_combination_id}")
#     meal_combination_repo = MealCombinationRepository(db)
#     try:
#         updated_meal_combination = meal_combination_repo.update_meal_combination(meal_combination_id, **meal_combination.dict(exclude_unset=True))
#         if not updated_meal_combination:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal combination not found")
#         logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "MealCombination", meal_combination_id, json.dumps(serialize_model(updated_meal_combination), default=str))
#         return MealCombinationResponse.from_orm(updated_meal_combination)
#     except Exception as e:
#         logging_helper.log_error(f"Failed to update meal combination with ID: {meal_combination_id}: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update meal combination")

# @router.delete("/meal_combinations/{meal_combination_id}", status_code=status.HTTP_200_OK)
# @limiter.limit("5/minute")
# async def delete_meal_combination(request: Request, meal_combination_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     logging_helper.log_info(f"Accessing - Delete Meal Combination - Endpoint for ID: {meal_combination_id}")
#     meal_combination_repo = MealCombinationRepository(db)
#     try:
#         deleted_meal_combination = meal_combination_repo.delete_meal_combination(meal_combination_id)
#         if not deleted_meal_combination:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal combination not found")
#         logging_helper.log_audit(db, current_user.id, ActionEnum.DELETE, "MealCombination", meal_combination_id, None)
#         return {"message": f"The Meal Combination with ID: {meal_combination_id} deleted successfully!"}
#     except Exception as e:
#         logging_helper.log_error(f"Failed to delete meal combination with ID: {meal_combination_id}: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete meal combination")



# routes/meal_combination_routes.py

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from repositories.meal_combination_repository import MealCombinationRepository
from logging_helpers import logging_helper
from auth.security import get_current_user
from models.all_models import User, ActionEnum
from schemas.meal_combination_schemas import MealCombinationCreate, MealCombinationUpdate, MealCombinationResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import json

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

@router.post("/meal_combinations/", response_model=MealCombinationResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_meal_combination(request: Request, meal_combination: MealCombinationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logging_helper.log_info("Accessing - Create Meal Combination - Endpoint")
    meal_combination_repo = MealCombinationRepository(db)
    try:
        new_meal_combination = meal_combination_repo.create_meal_combination(
            name=meal_combination.name,
            description=meal_combination.description
        )
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "MealCombination", new_meal_combination.id, json.dumps(MealCombinationResponse.from_orm(new_meal_combination).dict(), default=str))
        return MealCombinationResponse.from_orm(new_meal_combination)
    except ValueError as e:
        logging_helper.log_error(f"Failed to create meal combination: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logging_helper.log_error(f"Failed to create meal combination: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create meal combination")

@router.get("/meal_combinations/{meal_combination_id}", response_model=MealCombinationResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def get_meal_combination(request: Request, meal_combination_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logging_helper.log_info(f"Accessing - Get Meal Combination - Endpoint for ID: {meal_combination_id}")
    meal_combination_repo = MealCombinationRepository(db)
    try:
        meal_combination = meal_combination_repo.get_meal_combination_by_id(meal_combination_id)
        if not meal_combination:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal combination not found")
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "MealCombination", meal_combination_id, None)
        return MealCombinationResponse.from_orm(meal_combination)
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch meal combination with ID: {meal_combination_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch meal combination")

@router.get("/meal_combinations/", response_model=List[MealCombinationResponse], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def get_all_meal_combinations(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logging_helper.log_info("Accessing - Get All Meal Combinations - Endpoint")
    meal_combination_repo = MealCombinationRepository(db)
    try:
        meal_combinations = meal_combination_repo.get_all_meal_combinations()
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "MealCombination", None, None)
        return [MealCombinationResponse.from_orm(mc) for mc in meal_combinations]
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch all meal combinations: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch meal combinations")

@router.put("/meal_combinations/{meal_combination_id}", response_model=MealCombinationResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def update_meal_combination(request: Request, meal_combination_id: int, meal_combination: MealCombinationUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logging_helper.log_info(f"Accessing - Update Meal Combination - Endpoint for ID: {meal_combination_id}")
    meal_combination_repo = MealCombinationRepository(db)
    try:
        updated_meal_combination = meal_combination_repo.update_meal_combination(meal_combination_id, **meal_combination.dict(exclude_unset=True))
        if not updated_meal_combination:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal combination not found")
        logging_helper.log_audit(db, current_user.id, ActionEnum.UPDATE, "MealCombination", meal_combination_id, json.dumps(MealCombinationResponse.from_orm(updated_meal_combination).dict(), default=str))
        return MealCombinationResponse.from_orm(updated_meal_combination)
    except Exception as e:
        logging_helper.log_error(f"Failed to update meal combination with ID: {meal_combination_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update meal combination")

@router.delete("/meal_combinations/{meal_combination_id}", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def delete_meal_combination(request: Request, meal_combination_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logging_helper.log_info(f"Accessing - Delete Meal Combination - Endpoint for ID: {meal_combination_id}")
    meal_combination_repo = MealCombinationRepository(db)
    try:
        deleted_meal_combination = meal_combination_repo.delete_meal_combination(meal_combination_id)
        if not deleted_meal_combination:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal combination not found")
        logging_helper.log_audit(db, current_user.id, ActionEnum.DELETE, "MealCombination", meal_combination_id, None)
        return {"message": f"The Meal Combination with ID: {meal_combination_id} deleted successfully!"}
    except Exception as e:
        logging_helper.log_error(f"Failed to delete meal combination with ID: {meal_combination_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete meal combination")

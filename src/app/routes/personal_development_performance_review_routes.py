

# import os
# from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
# from sqlalchemy.orm import Session
# from typing import List, Optional
# from dotenv import load_dotenv

# from db.database import get_db
# from auth.dependencies import route_role_checker
# from auth.security import get_current_user
# from schemas.user_schemas import UserRead
# from repositories.personal_development_performance_review_repository import PersonalDevelopmentPerformanceReviewRepository
# from schemas.personal_development_performance_review_schemas import (
#     PersonalDevelopmentPerformanceReviewCreateSchema,
#     PersonalDevelopmentPerformanceReviewUpdateSchema,
#     PersonalDevelopmentPerformanceReviewDisplaySchema
# )
# from logging_helpers import logging_helper
# from models.all_models import ActionEnum

# # Load environment variables
# load_dotenv()
# BASE_URL = os.getenv("BASE_URL")

# router = APIRouter()

# @router.post(
#     "/personal-development-performance-reviews",
#     response_model=PersonalDevelopmentPerformanceReviewDisplaySchema,
#     status_code=status.HTTP_201_CREATED,
#     dependencies=[Depends(route_role_checker)]
# )
# def create_performance_review(
#     review_data: PersonalDevelopmentPerformanceReviewCreateSchema,
#     background_tasks: BackgroundTasks,
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Create a new personal development performance review and initiate the approval flow.
#     """
#     review_repo = PersonalDevelopmentPerformanceReviewRepository(db, base_url=BASE_URL)
#     try:
#         review = review_repo.create_performance_review(review_data, background_tasks)
#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.CREATE,
#             "PersonalDevelopmentPerformanceReview",
#             review.id,
#             {"data": review_data.dict()}
#         )
#         return review
#     except HTTPException as e:
#         logging_helper.log_error(f"Error creating performance review: {e.detail}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Unexpected error creating performance review: {str(e)}")
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the performance review.")

# @router.get(
#     "/personal-development-performance-reviews/{review_id}",
#     response_model=PersonalDevelopmentPerformanceReviewDisplaySchema,
#     dependencies=[Depends(route_role_checker)]
# )
# def get_performance_review(
#     review_id: int,
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Retrieve a specific personal development performance review by ID.
#     """
#     review_repo = PersonalDevelopmentPerformanceReviewRepository(db, base_url=BASE_URL)
#     try:
#         review = review_repo.get_performance_review_by_id(review_id)
#         return review
#     except HTTPException as e:
#         logging_helper.log_error(f"Error retrieving performance review {review_id}: {e.detail}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Unexpected error retrieving performance review {review_id}: {str(e)}")
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving the performance review.")

# @router.get(
#     "/personal-development-performance-reviews",
#     response_model=List[PersonalDevelopmentPerformanceReviewDisplaySchema],
#     dependencies=[Depends(route_role_checker)]
# )
# def list_performance_reviews(
#     employee_id: Optional[int] = None,
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     List all personal development performance reviews, optionally filtered by employee ID.
#     """
#     review_repo = PersonalDevelopmentPerformanceReviewRepository(db, base_url=BASE_URL)
#     try:
#         reviews = review_repo.list_performance_reviews(employee_id)
#         return reviews
#     except HTTPException as e:
#         logging_helper.log_error(f"Error listing performance reviews: {e.detail}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Unexpected error listing performance reviews: {str(e)}")
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while listing the performance reviews.")

# @router.put(
#     "/personal-development-performance-reviews/{review_id}",
#     response_model=PersonalDevelopmentPerformanceReviewDisplaySchema,
#     dependencies=[Depends(route_role_checker)]
# )
# def update_performance_review(
#     review_id: int,
#     update_data: PersonalDevelopmentPerformanceReviewUpdateSchema,
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Update an existing personal development performance review.
#     """
#     review_repo = PersonalDevelopmentPerformanceReviewRepository(db, base_url=BASE_URL)
#     try:
#         updated_review = review_repo.update_performance_review(review_id, update_data)
#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.UPDATE,
#             "PersonalDevelopmentPerformanceReview",
#             review_id,
#             {"data": update_data.dict()}
#         )
#         return updated_review
#     except HTTPException as e:
#         logging_helper.log_error(f"Error updating performance review {review_id}: {e.detail}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Unexpected error updating performance review {review_id}: {str(e)}")
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the performance review.")

# @router.delete(
#     "/personal-development-performance-reviews/{review_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     dependencies=[Depends(route_role_checker)]
# )
# def delete_performance_review(
#     review_id: int,
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Delete a personal development performance review.
#     """
#     review_repo = PersonalDevelopmentPerformanceReviewRepository(db, base_url=BASE_URL)
#     try:
#         review_repo.delete_performance_review(review_id)
#         logging_helper.log_audit(
#             db,
#             current_user.id,
#             ActionEnum.DELETE,
#             "PersonalDevelopmentPerformanceReview",
#             review_id,
#             {}
#         )
#     except HTTPException as e:
#         logging_helper.log_error(f"Error deleting performance review {review_id}: {e.detail}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Unexpected error deleting performance review {review_id}: {str(e)}")
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the performance review.")

# @router.post(
#     "/personal-development-performance-reviews/{review_id}/advance",
#     response_model=bool,
#     status_code=status.HTTP_200_OK,
#     dependencies=[Depends(route_role_checker)]
# )
# def advance_performance_review_approval(
#     review_id: int,
#     background_tasks: BackgroundTasks,
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Advance the approval flow for a specific performance review.
#     """
#     review_repo = PersonalDevelopmentPerformanceReviewRepository(db, base_url=BASE_URL)
#     try:
#         result = review_repo.advance_performance_review_approval(review_id, background_tasks)
#         if result:
#             logging_helper.log_info(f"Approval process advanced for review {review_id}.")
#         else:
#             logging_helper.log_info(f"Approval process completed for review {review_id}.")
#         return result
#     except HTTPException as e:
#         logging_helper.log_error(f"Error advancing approval for performance review {review_id}: {e.detail}")
#         raise e
#     except Exception as e:
#         logging_helper.log_error(f"Unexpected error advancing approval for performance review {review_id}: {str(e)}")
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while advancing the approval.")


import os
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from dotenv import load_dotenv

from db.database import get_db
from auth.dependencies import role_required
from auth.security import get_current_user
from schemas.user_schemas import UserRead
from repositories.personal_development_performance_review_repository import PersonalDevelopmentPerformanceReviewRepository
from schemas.personal_development_performance_review_schemas import (
    PersonalDevelopmentPerformanceReviewCreateSchema,
    PersonalDevelopmentPerformanceReviewUpdateSchema,
    PersonalDevelopmentPerformanceReviewDisplaySchema
)
from logging_helpers import logging_helper
from models.all_models import ActionEnum

# Load environment variables
load_dotenv()
BASE_URL = os.getenv("BASE_URL")

router = APIRouter()

@router.post(
    "/personal-development-performance-reviews",
    response_model=PersonalDevelopmentPerformanceReviewDisplaySchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(role_required(["unit_member", "super_admin"]))]
)
def create_performance_review(
    review_data: PersonalDevelopmentPerformanceReviewCreateSchema,
    background_tasks: BackgroundTasks,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new personal development performance review and initiate the approval flow.
    
    Roles: unit_member, super_admin
    """
    review_repo = PersonalDevelopmentPerformanceReviewRepository(db, base_url=BASE_URL)
    try:
        review = review_repo.create_performance_review(review_data, background_tasks)
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.CREATE,
            "PersonalDevelopmentPerformanceReview",
            review.id,
            {"data": review_data.dict()}
        )
        return review
    except HTTPException as e:
        logging_helper.log_error(f"Error creating performance review: {e.detail}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error creating performance review: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the performance review.")

@router.get(
    "/personal-development-performance-reviews/{review_id}",
    response_model=PersonalDevelopmentPerformanceReviewDisplaySchema,
    dependencies=[Depends(role_required(["super_admin", "unit_member", "hr"]))]
)
def get_performance_review(
    review_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific personal development performance review by ID.
    
    Roles: super_admin, unit_member, hr
    """
    review_repo = PersonalDevelopmentPerformanceReviewRepository(db, base_url=BASE_URL)
    try:
        review = review_repo.get_performance_review_by_id(review_id)
        return review
    except HTTPException as e:
        logging_helper.log_error(f"Error retrieving performance review {review_id}: {e.detail}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error retrieving performance review {review_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while retrieving the performance review.")

@router.get(
    "/personal-development-performance-reviews",
    response_model=List[PersonalDevelopmentPerformanceReviewDisplaySchema],
    dependencies=[Depends(role_required(["admin", "manager", "hr"]))]
)
def list_performance_reviews(
    employee_id: Optional[int] = None,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all personal development performance reviews, optionally filtered by employee ID.
    
    Roles: admin, manager, hr
    """
    review_repo = PersonalDevelopmentPerformanceReviewRepository(db, base_url=BASE_URL)
    try:
        reviews = review_repo.list_performance_reviews(employee_id)
        return reviews
    except HTTPException as e:
        logging_helper.log_error(f"Error listing performance reviews: {e.detail}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error listing performance reviews: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while listing the performance reviews.")

@router.put(
    "/personal-development-performance-reviews/{review_id}",
    response_model=PersonalDevelopmentPerformanceReviewDisplaySchema,
    dependencies=[Depends(role_required(["super_admin", "hr"]))]
)
def update_performance_review(
    review_id: int,
    update_data: PersonalDevelopmentPerformanceReviewUpdateSchema,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing personal development performance review.
    
    Roles: super_admin, hr
    """
    review_repo = PersonalDevelopmentPerformanceReviewRepository(db, base_url=BASE_URL)
    try:
        updated_review = review_repo.update_performance_review(review_id, update_data)
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.UPDATE,
            "PersonalDevelopmentPerformanceReview",
            review_id,
            {"data": update_data.dict()}
        )
        return updated_review
    except HTTPException as e:
        logging_helper.log_error(f"Error updating performance review {review_id}: {e.detail}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error updating performance review {review_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the performance review.")

@router.delete(
    "/personal-development-performance-reviews/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(role_required(["super_admin"]))]
)
def delete_performance_review(
    review_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a personal development performance review.
    
    Roles: super_admin
    """
    review_repo = PersonalDevelopmentPerformanceReviewRepository(db, base_url=BASE_URL)
    try:
        review_repo.delete_performance_review(review_id)
        logging_helper.log_audit(
            db,
            current_user.id,
            ActionEnum.DELETE,
            "PersonalDevelopmentPerformanceReview",
            review_id,
            {}
        )
    except HTTPException as e:
        logging_helper.log_error(f"Error deleting performance review {review_id}: {e.detail}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error deleting performance review {review_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the performance review.")

@router.post(
    "/personal-development-performance-reviews/{review_id}/advance",
    response_model=bool,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(role_required(["unit_member", "super_admin"]))]
)
def advance_performance_review_approval(
    review_id: int,
    background_tasks: BackgroundTasks,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Advance the approval flow for a specific performance review.
    
    Roles: unit_member, super_admin
    """
    review_repo = PersonalDevelopmentPerformanceReviewRepository(db, base_url=BASE_URL)
    try:
        result = review_repo.advance_performance_review_approval(review_id, background_tasks)
        if result:
            logging_helper.log_info(f"Approval process advanced for review {review_id}.")
        else:
            logging_helper.log_info(f"Approval process completed for review {review_id}.")
        return result
    except HTTPException as e:
        logging_helper.log_error(f"Error advancing approval for performance review {review_id}: {e.detail}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Unexpected error advancing approval for performance review {review_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while advancing the approval.")

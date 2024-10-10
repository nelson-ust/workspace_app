# routes/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db.database import get_db
from auth.security import verify_password, create_access_token
from repositories.user_repository import UserRepository
from logging_helpers import logging_helper

# router = APIRouter(tags=["Authentication"])
router = APIRouter()

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    logging_helper.log_info("Accessing - Login - Endpoint")
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# # Create a new user
# @router.post("/users/", response_model=UserRead)
# def create_user(user: UserCreate, db: Session = Depends(get_db)):
#     user_repo = UserRepository(db)
#     db_user = user_repo.get_user_by_email(email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return user_repo.create_user(user=user)


# from schemas.user_schemas import UserCreate

# @router.post("/register")
# def register(user: UserCreate, db: Session = Depends(get_db)):
#     user_repo = UserRepository(db)
#     db_user = user_repo.get_user_by_email(email=user.email)
#     if db_user:
#         raise HTTPException(
#             status_code=400,
#             detail="Email already registered"
#         )
#     user_repo.create_user(user=user)
#     return {"message": "User created successfully."}

from datetime import datetime, timedelta
import os
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from repositories.user_repository import UserRepository
from models.all_models import User

# Load environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "YOUR_SECRET_KEY_HERE")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

oauth_scheme = OAuth2PasswordBearer(tokenUrl='/token')

# Function to create access JWT
def create_access_jwt(data: dict):
    data['exp'] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data['mode'] = 'access_token'  # Explicitly setting mode
    return jwt.encode(data, SECRET_KEY, ALGORITHM)

# Function to create refresh JWT
def create_refresh_jwt(data: dict):
    data['exp'] = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    data['mode'] = 'refresh_token'  # Explicitly setting mode
    return jwt.encode(data, SECRET_KEY, ALGORITHM)

# Authorization function
async def authorize(token: str = Depends(oauth_scheme)) -> dict:
    # Validate the JWT
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload['mode'] != 'refresh_token':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authorization credentials')

        user_repo = UserRepository(Session())  # Adjust according to your database session management
        user = user_repo.get_user_by_email(payload['user_name'])
        if not user or token != user.refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authorization credentials')

        # Refresh the tokens
        data = {'user_name': user.email}
        refresh_tkn = create_refresh_jwt(data)
        access_tkn = create_access_jwt(data)
        return {'access_token': access_tkn, 'refresh_token': refresh_tkn, 'type': 'bearer'}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authorization credentials')

# Function to verify access JWT and fetch user
async def verified_user(token: str = Depends(oauth_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload['mode'] != 'access_token':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authorization credentials')

        user_repo = UserRepository(Session())
        return await user_repo.get_user_by_email(payload['user_name'])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authorization credentials')

# Function to get current user with detailed information
async def get_current_user(token: str = Depends(oauth_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload['mode'] != 'access_token':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

        user_repo = UserRepository(Session())
        user_data = user_repo.get_user_details_by_email(payload['user_name'])
        if user_data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return user_data
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('mode') != 'refresh_token':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        return payload['sub']
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

def authenticate_user(db: Session, username: str, password: str):
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(username)
    if not user or not user_repo.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    return user






# from datetime import datetime, timedelta
# import os
# from jose import JWTError, jwt
# from fastapi import HTTPException, status, Depends
# from fastapi.security import OAuth2PasswordBearer
# from sqlalchemy.orm import Session
# from repositories.user_repository import UserRepository
# from passlib.context import CryptContext
# from typing import Optional

# # Load environment variables
# SECRET_KEY = os.getenv("SECRET_KEY", "YOUR_SECRET_KEY_HERE")
# ALGORITHM = os.getenv("ALGORITHM", "HS256")
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
# REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# oauth_scheme = OAuth2PasswordBearer(tokenUrl='/token')
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # Function to create access JWT
# def create_access_jwt(user_email: str):
#     claims = {
#         'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
#         'sub': user_email,
#         'mode': 'access_token'
#     }
#     return jwt.encode(claims, SECRET_KEY, ALGORITHM)

# # Function to create refresh JWT
# def create_refresh_jwt(user_email: str):
#     claims = {
#         'exp': datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
#         'sub': user_email,
#         'mode': 'refresh_token'
#     }
#     return jwt.encode(claims, SECRET_KEY, ALGORITHM)

# # Function to authenticate user credentials
# def authenticate_user(db: Session, username: str, password: str):
#     user_repo = UserRepository(db)
#     user = user_repo.get_user_by_email(username)
#     if not user or not pwd_context.verify(password, user.hashed_password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
#     return user

# # Function to decode and validate access JWT and get current user
# async def get_current_user(token: str = Depends(oauth_scheme), db: Session = Depends()):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         if payload.get('mode') != 'access_token':
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
#         user_repo = UserRepository(db)
#         user = user_repo.get_user_by_email(payload['sub'])
#         if not user:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#         return user
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

# # Function to refresh tokens
# async def refresh_tokens(token: str, db: Session = Depends()):
#     try: 
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         if payload.get('mode') != 'refresh_token':
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
#         user_repo = UserRepository(db)
#         user = user_repo.get_user_by_email(payload['sub'])
#         if not user:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#         new_access_token = create_access_jwt(user.email)
#         new_refresh_token = create_refresh_jwt(user.email)
#         return {
#             "access_token": new_access_token,
#             "refresh_token": new_refresh_token,
#             "token_type": "bearer"
#         }
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate refresh token")

# # Function to verify refresh token validity
# def verify_refresh_token(token: str):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         if payload.get('mode') != 'refresh_token':
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
#         return payload['sub']
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

# # Function to authenticate user and create tokens
# def authorize(db: Session, username: str, password: str):
#     user = authenticate_user(db, username, password)
#     access_token = create_access_jwt(user.email)
#     refresh_token = create_refresh_jwt(user.email)
#     return {
#         'access_token': access_token,
#         'refresh_token': refresh_token,
#         'token_type': 'bearer'
#     }

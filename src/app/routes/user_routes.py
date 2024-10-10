# #routes/user_routes.py
# from fastapi import APIRouter, Depends, HTTPException, Query, Response,  BackgroundTasks, Request
# from fastapi.security import OAuth2PasswordRequestForm
# from sqlalchemy.orm import Session
# from typing import List

# from db.database import get_db
# from auth.dependencies import role_checker # get_current_user, role_checker

# from auth.security import authenticate_user, create_access_token, create_refresh_token, get_current_user, verify_refresh_token
# from auth.email import send_reset_password_email
# from schemas.user_schemas import PasswordResetConfirm, UserCreate, UserRead, Token, PasswordReset, UserReadWithEmployee, UserUpdate, RoleAssignment
# from repositories.user_repository import UserRepository
# from fastapi import BackgroundTasks
# from logging_helpers import logging_helper

# router = APIRouter()


# #Remove this route later, it's for testing the response for the active user
# @router.get("/users/details-by-email", response_model=UserRead)
# def get_user_details(email: str, db: Session = Depends(get_db)):
#     """
#     Fetches detailed user information by email. This endpoint extracts the email from the query parameters.
#     """

#     logging_helper.log_info("Accessing - Get User Details - Endpoint")
#     user_repo = UserRepository(db)
#     user_data = user_repo.get_user_details_by_email(email)
#     if not user_data:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user_data

# # # Create a new user
# # @router.post("/users/", response_model=UserRead)
# # def create_user(user: UserCreate, db: Session = Depends(get_db)): # , _=Depends(role_checker(['programs-lead', 'tech-lead', 'stl', 'tenant_admin']))):
# #     user_repo = UserRepository(db)
# #     db_user = user_repo.get_user_by_email(email=user.email)
# #     if db_user:
# #         raise HTTPException(status_code=400, detail="Email already registered")
# #     return user_repo.create_user(db,user)

# @router.post("/users/", response_model=UserRead)
# def create_user(user: UserCreate, db: Session = Depends(get_db), background_tasks: BackgroundTasks = BackgroundTasks()):  # , _=Depends(role_checker(['programs-lead', 'tech-lead', 'stl', 'tenant_admin']))):
    
#     logging_helper.log_info("Accessing - Create User - Endpoint")
#     user_repo = UserRepository(db)
#     # Check if the user already exists
#     db_user = user_repo.get_user_by_email(email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     # Create the user
#     db_user = user_repo.create_user(db, user)
#     if db_user:
#         # Generate the reset token
#         token_info = user_repo.create_password_reset_token(user.email)
#         if token_info:
#             # Send the reset email as a background task
#             background_tasks.add_task(send_reset_password_email, db_user.email, token_info['reset_token'])
#             return db_user
#         else:
#             raise HTTPException(status_code=500, detail="Failed to generate password reset token")
#     else:
#         raise HTTPException(status_code=500, detail="Failed to create user")

# # Get current user
# @router.get("/users/me", response_model=UserRead)
# def read_users_me(current_user: UserRead = Depends(get_current_user)):
    
#     logging_helper.log_info("Accessing - Read User Me - Endpoint")
#     return current_user

# # Get a specific user by ID
# @router.get("/users/{user_id}", response_model=UserRead)
# def read_user(user_id: int, db: Session = Depends(get_db)): # , _=Depends(role_checker(['programs_lead', 'tech_lead', 'stl', 'tenant_admin','unit_member','unit_lead','dept_lead']))):
    
#     logging_helper.log_info("Accessing - Read User - Endpoint")
#     user_repo = UserRepository(db)
#     db_user = user_repo.get_user_by_id(user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user

# # Update user details
# @router.put("/users/{user_id}", response_model=UserRead)
# def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db), _=Depends(role_checker(['programs_lead', 'technical_lead', 'stl', 'tenant_admin','unit_member','unit_lead','dept_lead']))):
    
#     logging_helper.log_info("Accessing - Update User - Endpoint")
#     user_repo = UserRepository(db)
#     updated_user = user_repo.update_user(user_id=user_id, user=user)
#     if not updated_user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return updated_user

# # Delete a user
# @router.delete("/users/{user_id}") #, status_code=status.HTTP_204_NO_CONTENT)
# def delete_user(user_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['programs-lead', 'tech-lead', 'stl', 'tenant_admin','unit_member','unit_lead','dept_lead']))):
    
#     logging_helper.log_info("Accessing - Delete User - Endpoint")
#     user_repo = UserRepository(db)
#     success = user_repo.delete_user(user_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {"message": "User deleted successfully"}

# # List all users
# @router.get("/users/", response_model=List[UserRead])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin','super_admin']))):
#     logging_helper.log_info("Accessing - Read Users -Endpoint")
#     users = UserRepository(db).get_users(skip=skip, limit=limit)
#     return users

# # Assign roles to a user
# @router.post("/users/{user_id}/roles")
# async def assign_roles(user_id: int, role_assignment: RoleAssignment, db: Session = Depends(get_db)): #,_=Depends(role_checker(['tech-lead', 'stl', 'tenant_admin','super_admin']))):
    
#     logging_helper.log_info("Accessing - Assign Roles - Endpoint")
#     user_repo = UserRepository(db)
#     try:
#         result = user_repo.assign_roles(user_id, role_assignment.roles)
#         return {"message": "Roles assigned successfully", "data": result}
#     except AttributeError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # # Login for access token
# # @router.post("/token", response_model=Token)
# # def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
# #     # Implementation similar to the previously provided snippet
# #     pass


# # @router.post("/refresh-token", response_model=Token)
# # def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
# #     user_email = verify_refresh_token(refresh_token)
# #     if not user_email:
# #         raise HTTPException(
# #             status_code=status.HTTP_401_UNAUTHORIZED,
# #             detail="Invalid refresh token",
# #             headers={"WWW-Authenticate": "Bearer"},
# #         )

# #     # Assuming you have a function to fetch user roles or any necessary claims for the token
# #     user_repo = UserRepository(db)
# #     user = user_repo.get_user_by_email(user_email)
# #     if not user:
# #         raise HTTPException(status_code=404, detail="User not found")

# #     access_token = create_access_token(data={"sub": user.email})
# #     return {"access_token": access_token, "token_type": "bearer"}


# @router.post("/refresh-token", response_model=Token)
# def refresh_access_token(db: Session = Depends(get_db), user: UserRead = Depends(get_current_user)):
    
#     logging_helper.log_info("Accessing - Refresh Access Token - Endpoint")
#     refresh_token = create_refresh_token(data={"sub": user.email})
#     access_token = create_access_token(data={"sub": user.email})
#     return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

# @router.post("/token", response_model=Token)
# async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
#     logging_helper.log_info("Accessing - Loging for Access Token - Endpoint")
#     user = authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(status_code=401, detail="Incorrect username or password")
    
#     access_token = create_access_token(data={"sub": user.email})
#     refresh_token = create_refresh_token(data={"sub": user.email})

#     # Ensure you're returning a dictionary matching the Token schema
#     return {"access_token": access_token, "token_type": "bearer","refresh_token":refresh_token}



# @router.post("/password-reset/", status_code=202)
# async def request_password_reset(password_reset: PasswordReset, db: Session = Depends(get_db), background_tasks: BackgroundTasks = BackgroundTasks()):
    
#     logging_helper.log_info("Accessing - Request Password Reset - Endpoint")
#     user_repo = UserRepository(db)
#     user = user_repo.get_user_by_email(password_reset.email)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     token_info = user_repo.create_password_reset_token(password_reset.email)
#     if not token_info:
#         raise HTTPException(status_code=404, detail="Failed to create reset token")

#     # Here, we ensure we are sending the correct email and token to the send_reset_password_email function
#     background_tasks.add_task(send_reset_password_email, user.email, token_info['reset_token'])
#     return {"message": "If your account exists, a reset link has been sent to your email."}


# # Verify password reset token and reset password
# @router.post("/password-reset/confirm/") #, response_model=UserRead)
# def reset_password(reset_details: PasswordResetConfirm, db: Session = Depends(get_db)):
    
#     logging_helper.log_info("Accessing - Reset Password - Endpoint")
#     user_repo = UserRepository(db)
#     user = user_repo.reset_password(reset_details.reset_token, reset_details.new_password)
#     if not user:
#         raise HTTPException(status_code=400, detail="Invalid or expired reset token")
#     return {"mesage":"The Password has been reset succsessfully"}










# # Add refresh token and also functionality for refreshing the authentication token based on the auth/securty.py , auth/dependencies.py, repositories/user_repository.py and routes/user_repository.py below:


# #For testing

# # @router.get("/users/details-by-email", response_model=UserRead)
# # def get_user_details(email: str = Query(..., alias="email"), db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin', 'super_admin']))):
# #     """
# #     Fetches detailed user information by email. Access restricted to admin and super_admin roles.
# #     """
# #     user_repo = UserRepository(db)
# #     user_data = user_repo.get_user_details_by_email(email)
# #     if not user_data:
# #         raise HTTPException(status_code=404, detail="User not found")
# #     return user_data








# # from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
# # from sqlalchemy.orm import Session
# # from fastapi.security import OAuth2PasswordRequestForm
# # from typing import List

# # from db.database import get_db
# # from auth.auth import get_current_user, create_access_jwt, create_refresh_jwt, authorize, verify_refresh_token, oauth_scheme, authenticate_user
# # from schemas.user_schemas import UserCreate, UserRead, Token, UserUpdate, RoleAssignment
# # from repositories.user_repository import UserRepository

# # router = APIRouter()

# # # Create a new user
# # @router.post("/users/", response_model=UserRead)
# # def create_user(user: UserCreate, db: Session = Depends(get_db)):
# #     user_repo = UserRepository(db)
# #     if user_repo.get_user_by_email(user.email):
# #         raise HTTPException(status_code=400, detail="Email already registered")
# #     return user_repo.create_user(db, user)

# # # Get current user details
# # @router.get("/users/me", response_model=UserRead)
# # async def read_users_me(current_user: UserRead = Depends(get_current_user)):
# #     return current_user

# # # Get specific user by ID
# # @router.get("/users/{user_id}", response_model=UserRead)
# # def read_user(user_id: int, db: Session = Depends(get_db)):
# #     user_repo = UserRepository(db)
# #     user = user_repo.get_user_by_id(user_id)
# #     if not user:
# #         raise HTTPException(status_code=404, detail="User not found")
# #     return user

# # # Update user details
# # @router.put("/users/{user_id}", response_model=UserRead)
# # def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
# #     user_repo = UserRepository(db)
# #     updated_user = user_repo.update_user(user_id, user)
# #     if not updated_user:
# #         raise HTTPException(status_code=404, detail="User not found")
# #     return updated_user

# # # Delete a user
# # @router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# # def delete_user(user_id: int, db: Session = Depends(get_db)):
# #     user_repo = UserRepository(db)
# #     if not user_repo.delete_user(user_id):
# #         raise HTTPException(status_code=404, detail="User not found")
# #     return Response(status_code=status.HTTP_204_NO_CONTENT)

# # # List all users
# # @router.get("/users/", response_model=List[UserRead])
# # def read_users(skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
# #     users = UserRepository(db).get_users(skip=skip, limit=limit)
# #     return users

# # # Assign roles to a user
# # @router.post("/users/{user_id}/roles")
# # def assign_roles(user_id: int, role_assignment: RoleAssignment, db: Session = Depends(get_db)):
# #     user_repo = UserRepository(db)
# #     result = user_repo.assign_roles(user_id, role_assignment.roles)
# #     return {"message": "Roles assigned successfully", "data": result}

# # # # Login for access token
# # # @router.post("/token", response_model=Token)
# # # def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
# # #     user = authorize(form_data.username, form_data.password, db)
# # #     access_token = create_access_jwt({"sub": user.email})
# # #     refresh_token = create_refresh_jwt({"sub": user.email})
# # #     return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

# # # Refresh access token
# # @router.post("/refresh-token", response_model=Token)
# # def refresh_access_token(db: Session = Depends(get_db), token: str = Depends(oauth_scheme)):
# #     user_email = verify_refresh_token(token)
# #     user_repo = UserRepository(db)
# #     user = user_repo.get_user_by_email(user_email)
# #     if not user:
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

# #     access_token = create_access_jwt({"sub": user.email})
# #     new_refresh_token = create_refresh_jwt({"sub": user.email})
# #     return {"access_token": access_token, "token_type": "bearer", "refresh_token": new_refresh_token}



# # # In user_routes.py
# # #from auth import create_access_token, create_refresh_token, authenticate_user

# # @router.post("/token", response_model=Token)
# # async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
# #     user = authenticate_user(db, form_data.username, form_data.password)
# #     access_token = create_access_jwt(data={"sub": user.email, "user_name": user.email})
# #     refresh_token = create_refresh_jwt(data={"sub": user.email, "user_name": user.email})
# #     return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


# # @router.post("/refresh-token")
# # def refresh_access_token(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):
# #     # Implementation of the refresh token logic
# #     user_email = verify_refresh_token(token)
# #     new_access_token = create_access_jwt({"sub": user_email})
# #     new_refresh_token = create_refresh_jwt({"sub": user_email})
# #     return {"access_token": new_access_token, "token_type": "bearer", "refresh_token": new_refresh_token}






from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Response, BackgroundTasks, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from auth.dependencies import role_checker
from auth.security import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, create_refresh_token, get_current_user, verify_refresh_token
from auth.email import send_reset_password_email
from models.all_models import InvalidToken, LoginHistory
from schemas.user_schemas import PasswordResetConfirm, UserCreate, UserRead, Token, PasswordReset, UserReadWithEmployee, UserUpdate, RoleAssignment
from repositories.user_repository import UserRepository
from logging_helpers import logging_helper

router = APIRouter()

# Remove this route later, it's for testing the response for the active user
@router.get("/users/details-by-email", response_model=UserRead)
def get_user_details(email: str, db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Get User Details - Endpoint")
    user_repo = UserRepository(db)
    user_data = user_repo.get_user_details_by_email(email)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return user_data

@router.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db), background_tasks: BackgroundTasks = BackgroundTasks()):
    logging_helper.log_info("Accessing - Create User - Endpoint")
    user_repo = UserRepository(db)
    # Check if the user already exists
    db_user = user_repo.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Create the user
    db_user = user_repo.create_user(db, user)
    if db_user:
        # Generate the reset token
        token_info = user_repo.create_password_reset_token(user.email)
        if token_info:
            # Send the reset email as a background task
            background_tasks.add_task(send_reset_password_email, db_user.email, token_info['reset_token'])
            return db_user
        else:
            raise HTTPException(status_code=500, detail="Failed to generate password reset token")
    else:
        raise HTTPException(status_code=500, detail="Failed to create user")

@router.get("/users/me", response_model=UserRead)
def read_users_me(current_user: UserRead = Depends(get_current_user)):
    logging_helper.log_info("Accessing - Read User Me - Endpoint")
    return current_user

@router.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Read User - Endpoint")
    user_repo = UserRepository(db)
    db_user = user_repo.get_user_by_id(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db), _=Depends(role_checker(['programs_lead', 'technical_lead', 'stl', 'tenant_admin','unit_member','unit_lead','dept_lead']))):
    logging_helper.log_info("Accessing - Update User - Endpoint")
    user_repo = UserRepository(db)
    updated_user = user_repo.update_user(user_id=user_id, user=user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), _=Depends(role_checker(['programs-lead', 'tech-lead', 'stl', 'tenant_admin','unit_member','unit_lead','dept_lead']))):
    logging_helper.log_info("Accessing - Delete User - Endpoint")
    user_repo = UserRepository(db)
    success = user_repo.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@router.get("/users/", response_model=List[UserRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(role_checker(['tenant_admin','super_admin']))):
    logging_helper.log_info("Accessing - Read Users -Endpoint")
    users = UserRepository(db).get_users(skip=skip, limit=limit)
    return users

@router.post("/users/{user_id}/roles")
async def assign_roles(user_id: int, role_assignment: RoleAssignment, db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Assign Roles - Endpoint")
    user_repo = UserRepository(db)
    try:
        result = user_repo.assign_roles(user_id, role_assignment.roles)
        return {"message": "Roles assigned successfully", "data": result}
    except AttributeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh-token", response_model=Token)
def refresh_access_token(db: Session = Depends(get_db), user: UserRead = Depends(get_current_user)):
    logging_helper.log_info("Accessing - Refresh Access Token - Endpoint")
    refresh_token = create_refresh_token(data={"sub": user.email})
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@router.post("/token", response_model=Token)
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Login for Access Token - Endpoint")
    user = authenticate_user(db, form_data.username, form_data.password, request)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@router.post("/password-reset/", status_code=202)
async def request_password_reset(password_reset: PasswordReset, db: Session = Depends(get_db), background_tasks: BackgroundTasks = BackgroundTasks()):
    logging_helper.log_info("Accessing - Request Password Reset - Endpoint")
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(password_reset.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token_info = user_repo.create_password_reset_token(password_reset.email)
    if not token_info:
        raise HTTPException(status_code=404, detail="Failed to create reset token")

    background_tasks.add_task(send_reset_password_email, user.email, token_info['reset_token'])
    return {"message": "If your account exists, a reset link has been sent to your email."}


@router.post("/password-reset/confirm/")
def reset_password(reset_details: PasswordResetConfirm, db: Session = Depends(get_db)):
    logging_helper.log_info("Accessing - Reset Password - Endpoint")
    user_repo = UserRepository(db)
    user = user_repo.reset_password(reset_details.reset_token, reset_details.new_password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    return {"mesage":"The Password has been reset successfully"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, current_user: UserRead = Depends(get_current_user), db: Session = Depends(get_db)):
    logging_helper.log_info(f"User {current_user.email} logging out")
    token = request.headers.get('authorization').split()[1]
    user_repo = UserRepository(db)
    try:
        user_repo.logout_user(current_user.id, token)
        logging_helper.log_info(f"User {current_user.email} logged out successfully")
    except HTTPException as e:
        logging_helper.log_error(f"Error during logout for user {current_user.email}: {str(e.detail)}")
        raise e
    except Exception as e:
        logging_helper.log_error(f"Error during logout for user {current_user.email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error during logout")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


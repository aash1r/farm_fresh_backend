from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.token import Token, TokenWithUser
from app.schemas.user import User as UserSchema, UserCreate

router = APIRouter(prefix="/auth")

# @router.post("/register", response_model=UserSchema)
# def register_user(*, db: Session = Depends(get_db), user_in: UserCreate) -> Any:
#     """Register a new user"""
#     # Check if user with this email exists
#     user = db.query(User).filter(User.email == user_in.email).first()
#     if user:
#         raise HTTPException(
#             status_code=400,
#             detail="A user with this email already exists",
#         )
#     # Check if user with this username exists
#     user = db.query(User).filter(User.username == user_in.username).first()
#     if user:
#         raise HTTPException(
#             status_code=400,
#             detail="A user with this username already exists",
#         )
#     # Create new user
#     db_user = User(
#         email=user_in.email,
#         username=user_in.username,
#         hashed_password=get_password_hash(user_in.password),
#         address=user_in.address,
#         is_admin=False,
#     )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# @router.post("/login", response_model=TokenWithUser)
# def login_access_token(
#     db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
# ) -> Any:
#     """OAuth2 compatible token login, get an access token for future requests"""
#     # Try to authenticate with username
#     user = db.query(User).filter(User.username == form_data.username).first()
#     # If not found, try with email
#     if not user:
#         user = db.query(User).filter(User.email == form_data.username).first()
#     if not user or not verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     return {
#         "access_token": create_access_token(
#             user.id, expires_delta=access_token_expires
#         ),
#         "token_type": "bearer",
#         "user": user
#     }



@router.post("/register", response_model=TokenWithUser)
def register_user(*, db: Session = Depends(get_db), user_in: UserCreate) -> Any:
    """Register a new user"""
    # Check if user with this email exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists",
        )
    # Check if user with this username exists
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this username already exists",
        )
    # Create new user
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        address=user_in.address,
        is_admin=user_in.is_admin,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        db_user.id, expires_delta=access_token_expires
    )
    print("Access token:", access_token)
    
    # Return token and user
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserSchema.model_validate(db_user)
    }

@router.post("/login")
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """OAuth2 compatible token login, get an access token for future requests"""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        user.id, expires_delta=access_token_expires
    )
    print("Access token:", access_token)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserSchema.model_validate(user)  # or db_user
    }

@router.post("/test-token", response_model=UserSchema)
def test_token(current_user: User = Depends(get_current_user)) -> Any:
    """Test access token"""
    return current_user

from datetime import timedelta, datetime, timezone
from typing import Any
import random
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.token import Token, TokenWithUser
from app.schemas.user import User as UserSchema, UserCreate
from app.core.email_utils import send_otp_email
from pydantic import BaseModel
from app.services.payment import payment_service


router = APIRouter(prefix="/auth")


def generate_otp() -> str:
    return str(random.randint(10000, 99999))


@router.post("/register")
def register_user(*, db: Session = Depends(get_db), user_in: UserCreate) -> Any:
    """Register a new user"""
    # Check if user with this email exists
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    # Create new user
    otp = generate_otp()
    otp_expires = datetime.now(timezone.utc) + timedelta(minutes=10)

    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        address=user_in.address,
        is_admin=user_in.is_admin,
        is_verified=False,
        otp=otp,
        otp_expires_at=otp_expires,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    send_otp_email(db_user.email, otp)
    
    return {"message": "OTP sent to your email."}
    
    # Generate access token
    

@router.post("/verify-otp",response_model=TokenWithUser)
def verify_otp(email: str = Body(...), otp: str = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or user.otp != otp or not user.otp_expires_at or user.otp_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user.is_verified = True
    user.otp = None
    user.otp_expires_at = None
    db.commit()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        user.id, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserSchema.model_validate(user),
        "message": "Account verified successfully"
    }


@router.post("/login")
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """OAuth2 compatible token login, get an access token for future requests"""
    user = db.query(User).filter(User.username == form_data.username, User.is_archived == False).first()
    if not user:
        user = db.query(User).filter(User.email == form_data.username, User.is_archived == False).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not user.is_verified:
        otp = generate_otp()
        user.otp = otp
        user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        db.commit()
        send_otp_email(user.email, otp)
        raise HTTPException(status_code=200, detail="Otp Sent.")


    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        user.id, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserSchema.model_validate(user),
        "message":"Login successful"  # or db_user
    }

class ForgotPasswordRequest(BaseModel):
    email: str

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    print("Email:", request.email)
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = generate_otp()
    user.otp = otp
    user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.commit()

    send_otp_email(user.email, otp)
    return {"message": "OTP sent to your email"}

@router.post("/reset-password")
def reset_password(email: str = Body(...), otp: str = Body(...), new_password: str = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or user.otp != otp or user.otp_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user.hashed_password = get_password_hash(new_password)
    user.otp = None
    user.otp_expires_at = None
    db.commit()
    return {"message": "Password updated successfully"}

@router.post("/change-password")
def change_password(
    old_password: str = Body(...),
    new_password: str = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    return {"message": "Password changed successfully"}

@router.delete("/delete-account")
def delete_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.is_archived = True
    current_user.email = ""
    current_user.username = ""
    db.commit()
    print("Account deleted successfully")
    return {"message": "Account has been archived (soft deleted)"}


@router.post("/test-token", response_model=UserSchema)
def test_token(current_user: User = Depends(get_current_user)) -> Any:
    """Test access token"""
    return current_user


# Add this to your FastAPI app temporarily
@app.get("/test-auth-net")
async def test_authorize_net():
    try:
        success, message = payment_service.test_api_credentials()
        return {"success": success, "message": message}
    except Exception as e:
        return {"success": False, "message": str(e)}

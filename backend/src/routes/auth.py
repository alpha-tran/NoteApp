import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from datetime import timedelta
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, Annotated
from jose import JWTError, jwt

from database import DataBase
from models.user import User, UserCreate, UserInDB
from schemas.user import UserOut, LoginCredentials, UserResponse, Token
from security.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    oauth2_scheme,
    authenticate_user
)
from config import settings
from services.user_service import UserService
from infrastructure.database import get_user_repository
from services.user import create_user, get_user_by_email, get_user_by_username

router = APIRouter(tags=["auth"])  # Remove prefix since it's handled in main.py
logger = logging.getLogger(__name__)

ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/register", response_model=User, status_code=status.HTTP_200_OK)
async def register(user_data: UserCreate):
    # Check if email already exists
    if await get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    if await get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user object
    user_in_db = UserInDB(
        **user_data.dict(exclude={"password"}),
        hashed_password=hashed_password
    )
    
    # Save user to database
    user = await create_user(user_in_db)
    
    # Generate access token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        **user.dict(),
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/login", response_model=Token)
async def login(credentials: LoginCredentials):
    user = await get_user_by_email(credentials.username)  # Using username field for email
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user)):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email
    )

@router.post("/logout")
async def logout():
    # Note: Token invalidation not implemented
    # Client should remove token from storage
    return {"message": "Successfully logged out"}

# Separate OPTIONS handler no longer needed as it's handled by the global options handler
# in main.py and by CORS middleware
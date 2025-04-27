import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from datetime import timedelta

from app.database import get_mongo_db
from app.models.user import User, UserCreate, UserInDB # Import MongoDB models
from app.schemas.user import AuthResponse, UserOut # Keep existing response schemas if suitable
from app.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    oauth2_scheme # Import oauth2_scheme if needed here
)
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate, 
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Register a new user.
    """
    # Check if user already exists
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        logger.warning(f"Registration attempt for existing email: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
        
    hashed_password = get_password_hash(user.password)
    # Create UserInDB object (prepare for DB insertion)
    user_in_db = UserInDB(
        email=user.email, 
        hashed_password=hashed_password
        # username=user.username # Add if username field is kept
    )
    
    try:
        # Insert user into database
        # .dict() deprecated, use .model_dump()
        new_user = await db["users"].insert_one(user_in_db.model_dump(by_alias=True))
        logger.info(f"User registered successfully: {user.email}, ID: {new_user.inserted_id}")
        
        # Find the created user to return data (excluding password)
        # It's often better to fetch it again to ensure consistency and get the _id
        created_user_data = await db["users"].find_one({"_id": new_user.inserted_id})
        if created_user_data:
             # Use UserOut schema if it excludes password, otherwise use User model
            return UserOut(**created_user_data)
        else:
             # Should not happen, but handle defensively
             logger.error(f"Could not retrieve newly registered user: {user.email}")
             raise HTTPException(status_code=500, detail="User registration failed unexpectedly")

    except DuplicateKeyError: # Should be caught by find_one check, but as safeguard
        logger.warning(f"Duplicate key error during registration for email: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered (concurrent request?)"
        )
    except Exception as e:
        logger.exception(f"Error during user registration for {user.email}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during registration")

@router.post("/login", response_model=AuthResponse)
async def login(
    response: Response, # Inject Response object to set cookie
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Authenticate user and return JWT token.
    Uses standard OAuth2PasswordRequestForm.
    Sets token in an HTTP-only cookie.
    """
    logger.debug(f"Login attempt for user: {form_data.username}")
    user_data = await db["users"].find_one({"email": form_data.username}) # username is the email here
    
    if not user_data or not verify_password(form_data.password, user_data["hashed_password"]):
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}, # Keep Bearer for potential non-cookie clients
        )
    
    logger.info(f"User authenticated successfully: {form_data.username}")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data["email"]}, expires_delta=access_token_expires
    )
    
    # Set the token in an HTTP-only cookie for security
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True, 
        max_age=int(access_token_expires.total_seconds()),
        samesite="lax", # Consider 'strict' if applicable
        secure=not settings.is_development() # Set Secure flag in production (requires HTTPS)
    )

    # Also return the token in the response body for flexibility
    return {"access_token": access_token, "token_type": "bearer"}


# Modified oauth2_scheme to potentially read from cookie
# This is a more advanced topic, potentially requiring a custom dependency
# For now, get_current_user relies on the Authorization header
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False) 

@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    """Get current logged-in user information."""
    # UserOut should ideally be used to filter fields sent to client
    return UserOut(**current_user.model_dump())

@router.post("/logout")
async def logout(response: Response):
    """
    Logout user by clearing the access token cookie.
    """
    logger.info("User logging out")
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out"}
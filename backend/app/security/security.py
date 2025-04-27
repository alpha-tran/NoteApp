from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings
from app.models.user import UserInDB
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_mongo_db

# Remove SECRET_KEY from __all__ for security
__all__ = [
    'oauth2_scheme',
    'pwd_context',
    'verify_password',
    'get_password_hash',
    'create_access_token',
    'get_current_user',
]

# Enhanced password context with explicit settings
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Explicit work factor
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add standard JWT claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": "noteapp-api",
        "aud": ["noteapp-client"]
    })
    
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Explicit verification of token expiration and claims
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience=["noteapp-client"],
            issuer="noteapp-api"
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Query MongoDB instead of SQLAlchemy
        user_data = await db["users"].find_one({"email": username})
        
    except JWTError as e:
        # More specific error handling
        if "expired" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise credentials_exception
    
    if user_data is None:
        # Generic error to prevent user enumeration
        raise credentials_exception
    
    # Validate user data with Pydantic model
    try:
        user = UserInDB(**user_data)
    except Exception:
        # Handle potential validation errors if DB data doesn't match model
        raise credentials_exception 
        
    return user 
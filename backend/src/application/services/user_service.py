from datetime import datetime
from typing import Optional, List
from passlib.context import CryptContext

from domain.models.user import User
from domain.repositories.user_repository import UserRepository
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = await self.user_repository.get_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def create_user(self, username: str, email: str, password: str) -> User:
        # Check password policy
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            raise ValueError(f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long")
        if settings.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if settings.PASSWORD_REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            raise ValueError("Password must contain at least one lowercase letter")
        if settings.PASSWORD_REQUIRE_DIGITS and not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one number")
        if settings.PASSWORD_REQUIRE_SPECIAL and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            raise ValueError("Password must contain at least one special character")

        # Check if user exists
        existing_user = await self.user_repository.get_by_username(username)
        if existing_user:
            raise ValueError("Username already exists")
        
        existing_email = await self.user_repository.get_by_email(email)
        if existing_email:
            raise ValueError("Email already registered")

        # Create user
        hashed_password = self.get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        return await self.user_repository.create(user)

    async def get_user(self, user_id: str) -> Optional[User]:
        return await self.user_repository.get_by_id(user_id)

    async def update_user(self, user_id: str, username: Optional[str] = None, 
                         email: Optional[str] = None, password: Optional[str] = None) -> Optional[User]:
        user = await self.get_user(user_id)
        if not user:
            return None

        if username and username != user.username:
            existing_user = await self.user_repository.get_by_username(username)
            if existing_user:
                raise ValueError("Username already exists")
            user.username = username

        if email and email != user.email:
            existing_email = await self.user_repository.get_by_email(email)
            if existing_email:
                raise ValueError("Email already registered")
            user.email = email

        if password:
            user.hashed_password = self.get_password_hash(password)

        user.updated_at = datetime.utcnow()
        return await self.user_repository.update(user)

    async def delete_user(self, user_id: str) -> bool:
        return await self.user_repository.delete(user_id)

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return await self.user_repository.list_all(skip, limit)

    async def count_users(self) -> int:
        return await self.user_repository.count() 
"""
Authentication service for user registration, login, and session management.

Handles password hashing, JWT token generation, and user management.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import jwt
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import User, UserProfile
from schemas.user import UserCreate, UserResponse
from utils.errors import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from utils.logger import setup_logging
from config import settings

logger = setup_logging(__name__)


class AuthService:
    """Authentication service using JWT tokens and password hashing."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password for storage.

        In production, use bcrypt or argon2:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

        For this implementation, we'll use a simple placeholder.
        """
        # TODO: Implement proper password hashing with bcrypt
        # For now, return a dummy hash prefixed with method
        import hashlib
        import secrets

        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), 100000
        )
        return f"pbkdf2_sha256${100000}${salt}${hashed.hex()}"

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.

        In production:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(password, password_hash)
        """
        # TODO: Implement proper password verification with bcrypt
        # For now, simple verification
        if not password_hash.startswith("pbkdf2_sha256$"):
            return False

        try:
            parts = password_hash.split("$")
            if len(parts) != 4:
                return False

            iterations = int(parts[1])
            salt = parts[2]

            import hashlib
            hashed = hashlib.pbkdf2_hmac(
                "sha256", password.encode(), salt.encode(), iterations
            )
            return hashed.hex() == parts[3]
        except Exception:
            return False

    @staticmethod
    def create_access_token(user_id: str) -> Tuple[str, int]:
        """
        Create a JWT access token for a user.

        Returns:
            Tuple of (token, expires_in_seconds)
        """
        now = datetime.utcnow()
        expires = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": user_id,
            "iat": now,
            "exp": expires,
            "type": "access",
        }

        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        expires_in = int(
            (expires - now).total_seconds()
        )  # Convert to seconds

        return token, expires_in

    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """
        Verify a JWT token and return the user ID.

        Args:
            token: JWT token string

        Returns:
            User ID if valid, None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )

            if payload.get("type") != "access":
                return None

            user_id = payload.get("sub")
            if not user_id:
                return None

            return user_id
        except jwt.ExpiredSignatureError:
            logger.debug("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.debug("Invalid token")
            return None

    @staticmethod
    async def register_user(
        user_data: UserCreate, session: AsyncSession
    ) -> Tuple[User, str, int]:
        """
        Register a new user.

        Args:
            user_data: User registration data (email, password, name)
            session: Database session

        Returns:
            Tuple of (user, access_token, expires_in_seconds)

        Raises:
            ConflictError: If email already exists
            ValidationError: If data is invalid
        """
        # Check if email already exists
        stmt = select(User).where(User.email == user_data.email)
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            raise ConflictError(
                message=f"Email {user_data.email} is already registered",
                details={"email": "already_exists"},
            )

        # Validate password length
        if len(user_data.password) < 8:
            raise ValidationError(
                "Password must be at least 8 characters",
                details={"password": "too_short"},
            )

        # Create user
        user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            password_hash=AuthService.hash_password(user_data.password),
            name=user_data.name,
            is_active=True,
            is_admin=False,
        )

        session.add(user)
        await session.flush()  # Flush to get ID

        # Create user profile automatically
        profile = UserProfile(
            id=str(uuid.uuid4()),
            user_id=user.id,
        )
        session.add(profile)

        # Generate token
        access_token, expires_in = AuthService.create_access_token(user.id)

        await session.commit()

        logger.info(f"User registered: {user.email} ({user.id})")

        return user, access_token, expires_in

    @staticmethod
    async def login_user(
        email: str, password: str, session: AsyncSession
    ) -> Tuple[User, str, int]:
        """
        Authenticate a user and return access token.

        Args:
            email: User email
            password: User password
            session: Database session

        Returns:
            Tuple of (user, access_token, expires_in_seconds)

        Raises:
            AuthenticationError: If credentials are invalid
        """
        # Find user by email
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not AuthService.verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("Account is inactive")

        # Update last login
        user.last_login = datetime.utcnow()
        await session.commit()

        # Generate token
        access_token, expires_in = AuthService.create_access_token(user.id)

        logger.info(f"User logged in: {user.email}")

        return user, access_token, expires_in

    @staticmethod
    async def get_user_by_id(
        user_id: str, session: AsyncSession
    ) -> Optional[User]:
        """Get a user by ID."""
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_user_profile(
        user_id: str,
        language_preference: Optional[str] = None,
        theme: Optional[str] = None,
        session: Optional[AsyncSession] = None,
    ) -> User:
        """Update user preferences."""
        if not session:
            raise ValueError("Session is required")

        user = await AuthService.get_user_by_id(user_id, session)
        if not user:
            raise NotFoundError("User", user_id)

        if language_preference:
            user.language_preference = language_preference
        if theme:
            user.theme = theme

        user.updated_at = datetime.utcnow()
        await session.commit()

        return user

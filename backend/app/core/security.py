"""
Security utilities: JWT, password hashing, encryption
"""
import base64
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import UUID

from cryptography.fernet import Fernet
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.core.exceptions import AuthenticationError

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})

    # Convert UUID to string if present
    if "sub" in to_encode and isinstance(to_encode["sub"], UUID):
        to_encode["sub"] = str(to_encode["sub"])
    if "organization_id" in to_encode and isinstance(to_encode["organization_id"], UUID):
        to_encode["organization_id"] = str(to_encode["organization_id"])

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})

    # Convert UUID to string if present
    if "sub" in to_encode and isinstance(to_encode["sub"], UUID):
        to_encode["sub"] = str(to_encode["sub"])
    if "organization_id" in to_encode and isinstance(to_encode["organization_id"], UUID):
        to_encode["organization_id"] = str(to_encode["organization_id"])

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise AuthenticationError(detail=f"Invalid token: {str(e)}")


def get_encryption_key() -> bytes:
    """Get or generate encryption key for storing DSP credentials"""
    if settings.ENCRYPTION_KEY:
        return base64.b64decode(settings.ENCRYPTION_KEY)
    else:
        # Development fallback - DO NOT USE IN PRODUCTION
        return Fernet.generate_key()


def encrypt_credentials(credentials: str) -> str:
    """Encrypt credentials for storage"""
    fernet = Fernet(get_encryption_key())
    encrypted = fernet.encrypt(credentials.encode())
    return base64.b64encode(encrypted).decode()


def decrypt_credentials(encrypted_credentials: str) -> str:
    """Decrypt stored credentials"""
    fernet = Fernet(get_encryption_key())
    decrypted = fernet.decrypt(base64.b64decode(encrypted_credentials))
    return decrypted.decode()

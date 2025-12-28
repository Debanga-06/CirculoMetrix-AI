"""
Security utilities for authentication and authorization
JWT token handling, password hashing, and security middleware
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
import secrets
import hashlib
import logging

from core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# ==========================================
# Password Hashing Configuration
# ==========================================

# Password context for hashing and verification
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS
)


def hash_password(password: str) -> str:
    """
    Hash a plain password
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Previously hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False


# ==========================================
# JWT Token Management
# ==========================================

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")
http_bearer = HTTPBearer()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Data to encode in token
        expires_delta: Custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create JWT refresh token with longer expiration
    
    Args:
        data: Data to encode in token
        
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Verify token type
        if payload.get("type") not in ["access", "refresh"]:
            raise credentials_exception
        
        return payload
        
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise credentials_exception


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """
    Extract user ID from JWT token
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User ID string
        
    Raises:
        HTTPException: If token is invalid
    """
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    return user_id


def verify_token_type(token: str, expected_type: str = "access") -> bool:
    """
    Verify token type (access or refresh)
    
    Args:
        token: JWT token string
        expected_type: Expected token type
        
    Returns:
        True if token type matches
    """
    try:
        payload = decode_token(token)
        return payload.get("type") == expected_type
    except:
        return False


# ==========================================
# API Key Management
# ==========================================

def generate_api_key() -> str:
    """
    Generate a secure random API key
    
    Returns:
        API key string
    """
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for secure storage
    
    Args:
        api_key: Plain API key
        
    Returns:
        Hashed API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """
    Verify an API key against its hash
    
    Args:
        plain_key: Plain API key to verify
        hashed_key: Previously hashed API key
        
    Returns:
        True if API key matches
    """
    return hash_api_key(plain_key) == hashed_key


# ==========================================
# Security Utilities
# ==========================================

def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token
    
    Args:
        length: Token length
        
    Returns:
        Secure random token
    """
    return secrets.token_urlsafe(length)


def generate_verification_code(length: int = 6) -> str:
    """
    Generate a numeric verification code
    
    Args:
        length: Code length
        
    Returns:
        Numeric verification code
    """
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])


def check_password_strength(password: str) -> Dict[str, Any]:
    """
    Check password strength and return feedback
    
    Args:
        password: Password to check
        
    Returns:
        Dictionary with strength info and suggestions
    """
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    score = 0
    suggestions = []
    
    if length >= 8:
        score += 1
    else:
        suggestions.append("Use at least 8 characters")
    
    if length >= 12:
        score += 1
    
    if has_upper:
        score += 1
    else:
        suggestions.append("Include uppercase letters")
    
    if has_lower:
        score += 1
    else:
        suggestions.append("Include lowercase letters")
    
    if has_digit:
        score += 1
    else:
        suggestions.append("Include numbers")
    
    if has_special:
        score += 1
    else:
        suggestions.append("Include special characters")
    
    strength_labels = ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong"]
    strength = strength_labels[min(score, len(strength_labels) - 1)]
    
    return {
        "score": score,
        "max_score": 6,
        "strength": strength,
        "is_strong": score >= 4,
        "suggestions": suggestions
    }


# ==========================================
# Request Validation
# ==========================================

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", ';', '\\', '`']
    sanitized = text
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()


def validate_email(email: str) -> bool:
    """
    Basic email validation
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# ==========================================
# Rate Limiting Helper
# ==========================================

from collections import defaultdict
from time import time

# Simple in-memory rate limiter (for production, use Redis)
_rate_limit_data = defaultdict(list)


def check_rate_limit(identifier: str, max_requests: int = None, period: int = None) -> bool:
    """
    Check if request is within rate limit
    
    Args:
        identifier: Unique identifier (IP, user_id, etc.)
        max_requests: Maximum requests allowed
        period: Time period in seconds
        
    Returns:
        True if within limit, False otherwise
    """
    if max_requests is None:
        max_requests = settings.RATE_LIMIT_REQUESTS
    if period is None:
        period = settings.RATE_LIMIT_PERIOD_SECONDS
    
    now = time()
    cutoff = now - period
    
    # Clean old requests
    _rate_limit_data[identifier] = [
        req_time for req_time in _rate_limit_data[identifier]
        if req_time > cutoff
    ]
    
    # Check limit
    if len(_rate_limit_data[identifier]) >= max_requests:
        return False
    
    # Add current request
    _rate_limit_data[identifier].append(now)
    return True


# ==========================================
# Security Headers Middleware
# ==========================================

def get_security_headers() -> Dict[str, str]:
    """
    Get recommended security headers
    
    Returns:
        Dictionary of security headers
    """
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }
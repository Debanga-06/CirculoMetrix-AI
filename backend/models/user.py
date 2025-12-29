"""
User Database Model for MongoDB
Document model for user management and authentication
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, timedelta
from bson import ObjectId
import enum


# ==========================================
# PyObjectId Handler for MongoDB
# ==========================================

class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# ==========================================
# User Role Enumeration
# ==========================================

class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


# ==========================================
# User Document Model
# ==========================================

class UserDocument(BaseModel):
    """
    User document model for MongoDB
    Handles authentication and authorization
    """
    
    # MongoDB ID
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    # User Information
    email: EmailStr = Field(..., description="User email address (unique)")
    username: str = Field(..., min_length=3, max_length=100, description="Username (unique)")
    full_name: Optional[str] = Field(None, max_length=255)
    
    # Authentication
    hashed_password: str = Field(..., description="Bcrypt hashed password")
    
    # Role and Permissions
    role: UserRole = Field(default=UserRole.USER, description="User role")
    is_active: bool = Field(default=True, description="Account active status")
    is_verified: bool = Field(default=False, description="Email verification status")
    
    # Company Information
    company_name: Optional[str] = Field(None, max_length=255)
    company_industry: Optional[str] = Field(None, max_length=100)
    
    # API Access
    api_key: Optional[str] = Field(None, description="API key for programmatic access")
    api_key_created_at: Optional[datetime] = None
    
    # Subscription/Plan
    subscription_tier: str = Field(default="free", max_length=50, description="Subscription tier")
    subscription_expires_at: Optional[datetime] = None
    
    # Usage Tracking
    total_lca_calculations: int = Field(default=0, ge=0)
    total_reports_generated: int = Field(default=0, ge=0)
    last_login_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "role": "user",
                "is_active": True,
                "is_verified": True,
                "company_name": "Green Industries Inc.",
                "company_industry": "Manufacturing",
                "subscription_tier": "free"
            }
        }
    
    def to_dict(self, include_sensitive: bool = False):
        """
        Convert user document to dictionary
        
        Args:
            include_sensitive: Whether to include sensitive fields like hashed_password
        """
        data = self.dict(by_alias=True, exclude_none=True)
        
        # Convert ObjectId to string
        if "_id" in data:
            data["id"] = str(data["_id"])
            del data["_id"]
        
        # Convert datetime to ISO format
        for field in ["created_at", "updated_at", "last_login_at", "api_key_created_at", "subscription_expires_at"]:
            if field in data and isinstance(data[field], datetime):
                data[field] = data[field].isoformat()
        
        # Remove sensitive fields unless explicitly requested
        if not include_sensitive:
            data.pop("hashed_password", None)
            data.pop("api_key", None)
        
        return data
    
    def to_public_dict(self):
        """Convert to public-safe dictionary (no sensitive data)"""
        return {
            "id": str(self.id),
            "username": self.username,
            "full_name": self.full_name,
            "company_name": self.company_name,
            "subscription_tier": self.subscription_tier,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_premium(self) -> bool:
        """Check if user has active premium subscription"""
        if not self.subscription_expires_at:
            return False
        return datetime.utcnow() < self.subscription_expires_at
    
    def increment_lca_count(self):
        """Increment LCA calculation count"""
        self.total_lca_calculations += 1
        self.updated_at = datetime.utcnow()
    
    def increment_report_count(self):
        """Increment report generation count"""
        self.total_reports_generated += 1
        self.updated_at = datetime.utcnow()
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


# ==========================================
# Pydantic Schemas for API
# ==========================================

class UserCreateSchema(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    company_industry: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if not v.isalnum() and '_' not in v and '-' not in v:
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "SecurePassword123!",
                "full_name": "John Doe",
                "company_name": "Green Industries Inc.",
                "company_industry": "Manufacturing"
            }
        }


class UserLoginSchema(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!"
            }
        }


class UserUpdateSchema(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = Field(None, max_length=255)
    company_name: Optional[str] = Field(None, max_length=255)
    company_industry: Optional[str] = Field(None, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "company_name": "Green Industries Inc.",
                "company_industry": "Manufacturing"
            }
        }


class UserResponseSchema(BaseModel):
    """Schema for user response"""
    id: str
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    company_name: Optional[str]
    company_industry: Optional[str]
    subscription_tier: str
    total_lca_calculations: int
    total_reports_generated: int
    created_at: str
    last_login_at: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "role": "user",
                "is_active": True,
                "is_verified": True,
                "company_name": "Green Industries Inc.",
                "company_industry": "Manufacturing",
                "subscription_tier": "free",
                "total_lca_calculations": 42,
                "total_reports_generated": 15,
                "created_at": "2024-01-15T10:30:00",
                "last_login_at": "2024-01-20T14:25:00"
            }
        }


class TokenSchema(BaseModel):
    """Schema for authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class PasswordChangeSchema(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "OldPassword123!",
                "new_password": "NewSecurePassword456!"
            }
        }


class PasswordResetRequestSchema(BaseModel):
    """Schema for password reset request"""
    email: EmailStr
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordResetSchema(BaseModel):
    """Schema for password reset with token"""
    token: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "reset_token_abc123",
                "new_password": "NewSecurePassword456!"
            }
        }


class APIKeyResponseSchema(BaseModel):
    """Schema for API key response"""
    api_key: str
    created_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "api_key": "cmx_1234567890abcdef",
                "created_at": "2024-01-15T10:30:00"
            }
        }


# ==========================================
# MongoDB Collection Helper
# ==========================================

def get_users_collection(db):
    """
    Get users collection with indexes
    
    Args:
        db: MongoDB database instance
        
    Returns:
        MongoDB collection
    """
    collection = db.users
    
    # Create unique indexes
    collection.create_index("email", unique=True)
    collection.create_index("username", unique=True)
    collection.create_index("api_key", unique=True, sparse=True)
    
    # Create other indexes
    collection.create_index("role")
    collection.create_index("subscription_tier")
    collection.create_index("is_active")
    collection.create_index("created_at")
    
    return collection


# ==========================================
# CRUD Helper Functions
# ==========================================

def user_document_helper(user) -> dict:
    """
    Convert MongoDB user document to dictionary
    
    Args:
        user: MongoDB document
        
    Returns:
        Dictionary representation (without sensitive data)
    """
    if not user:
        return None
    
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "username": user["username"],
        "full_name": user.get("full_name"),
        "role": user.get("role", "user"),
        "is_active": user.get("is_active", True),
        "is_verified": user.get("is_verified", False),
        "company_name": user.get("company_name"),
        "company_industry": user.get("company_industry"),
        "subscription_tier": user.get("subscription_tier", "free"),
        "total_lca_calculations": user.get("total_lca_calculations", 0),
        "total_reports_generated": user.get("total_reports_generated", 0),
        "created_at": user["created_at"].isoformat() if isinstance(user.get("created_at"), datetime) else user.get("created_at"),
        "last_login_at": user["last_login_at"].isoformat() if isinstance(user.get("last_login_at"), datetime) else user.get("last_login_at")
    }


def user_public_helper(user) -> dict:
    """
    Convert MongoDB user document to public dictionary
    
    Args:
        user: MongoDB document
        
    Returns:
        Public-safe dictionary
    """
    if not user:
        return None
    
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "full_name": user.get("full_name"),
        "company_name": user.get("company_name"),
        "subscription_tier": user.get("subscription_tier", "free"),
        "created_at": user["created_at"].isoformat() if isinstance(user.get("created_at"), datetime) else user.get("created_at")
    }
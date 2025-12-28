"""
User Database Model
SQLAlchemy model for user management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class User(Base):
    """
    User model for authentication and authorization
    """
    __tablename__ = "users"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # User Information
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    
    # Role and Permissions
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Company Information
    company_name = Column(String(255), nullable=True)
    company_industry = Column(String(100), nullable=True)
    
    # API Access
    api_key = Column(String(255), unique=True, nullable=True, index=True)
    api_key_created_at = Column(DateTime(timezone=True), nullable=True)
    
    # Subscription/Plan
    subscription_tier = Column(String(50), default="free", nullable=False)
    subscription_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Usage Tracking
    total_lca_calculations = Column(Integer, default=0, nullable=False)
    total_reports_generated = Column(Integer, default=0, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "role": self.role.value if self.role else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "company_name": self.company_name,
            "company_industry": self.company_industry,
            "subscription_tier": self.subscription_tier,
            "total_lca_calculations": self.total_lca_calculations,
            "total_reports_generated": self.total_reports_generated,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None
        }
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_premium(self) -> bool:
        """Check if user has premium subscription"""
        if not self.subscription_expires_at:
            return False
        return datetime.utcnow() < self.subscription_expires_at
    
    def increment_lca_count(self):
        """Increment LCA calculation count"""
        self.total_lca_calculations += 1
    
    def increment_report_count(self):
        """Increment report generation count"""
        self.total_reports_generated += 1
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login_at = datetime.utcnow()


# Pydantic schemas for API

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreateSchema(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    company_industry: Optional[str] = None
    
    class Config:
        schema_extra = {
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
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!"
            }
        }


class UserUpdateSchema(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    company_industry: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "full_name": "John Doe",
                "company_name": "Green Industries Inc.",
                "company_industry": "Manufacturing"
            }
        }


class UserResponseSchema(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    company_name: Optional[str]
    subscription_tier: str
    total_lca_calculations: int
    total_reports_generated: int
    created_at: str
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "role": "user",
                "is_active": True,
                "is_verified": True,
                "company_name": "Green Industries Inc.",
                "subscription_tier": "free",
                "total_lca_calculations": 42,
                "total_reports_generated": 15,
                "created_at": "2024-01-15T10:30:00"
            }
        }


class TokenSchema(BaseModel):
    """Schema for authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
    class Config:
        schema_extra = {
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
    
    class Config:
        schema_extra = {
            "example": {
                "current_password": "OldPassword123!",
                "new_password": "NewSecurePassword456!"
            }
        }
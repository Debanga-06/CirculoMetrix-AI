"""
Project Database Model
SQLAlchemy model for storing LCA projects and calculations
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from core.database import Base


class Project(Base):
    """
    Project model for storing LCA calculations and analysis
    """
    __tablename__ = "projects"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Project Information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Material Information
    material = Column(String(50), nullable=False, index=True)
    production_type = Column(String(50), nullable=False)
    quantity = Column(Float, nullable=False)
    
    # Energy and Transport
    energy_source = Column(String(50), nullable=False)
    transport_distance = Column(Float, nullable=True)
    transport_mode = Column(String(50), nullable=True)
    
    # Circularity Metrics
    recycled_content = Column(Float, default=0.0, nullable=False)
    end_of_life_recycling_rate = Column(Float, default=0.0, nullable=False)
    
    # LCA Results
    total_co2_emissions = Column(Float, nullable=True)
    co2_per_unit = Column(Float, nullable=True)
    energy_consumption = Column(Float, nullable=True)
    water_usage = Column(Float, nullable=True)
    
    # Circularity Score
    mci_score = Column(Float, nullable=True)
    circularity_level = Column(String(50), nullable=True)
    
    # Complete Results (JSON)
    lca_results = Column(JSON, nullable=True)
    circularity_results = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    
    # Status and Tags
    status = Column(String(50), default="draft", nullable=False)  # draft, completed, archived
    tags = Column(JSON, nullable=True)  # Array of tags
    
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
    user = relationship("User", back_populates="projects")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, material={self.material})>"
    
    def to_dict(self):
        """Convert project to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "material": self.material,
            "production_type": self.production_type,
            "quantity": self.quantity,
            "energy_source": self.energy_source,
            "transport_distance": self.transport_distance,
            "transport_mode": self.transport_mode,
            "recycled_content": self.recycled_content,
            "end_of_life_recycling_rate": self.end_of_life_recycling_rate,
            "total_co2_emissions": self.total_co2_emissions,
            "co2_per_unit": self.co2_per_unit,
            "energy_consumption": self.energy_consumption,
            "water_usage": self.water_usage,
            "mci_score": self.mci_score,
            "circularity_level": self.circularity_level,
            "lca_results": self.lca_results,
            "circularity_results": self.circularity_results,
            "recommendations": self.recommendations,
            "status": self.status,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_summary(self):
        """Convert project to summary dictionary (without full results)"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "material": self.material,
            "production_type": self.production_type,
            "quantity": self.quantity,
            "total_co2_emissions": self.total_co2_emissions,
            "mci_score": self.mci_score,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


# Pydantic schemas for API

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ProjectCreateSchema(BaseModel):
    """Schema for creating a new project"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    material: str
    production_type: str
    quantity: float = Field(..., gt=0)
    energy_source: str
    transport_distance: Optional[float] = Field(default=0, ge=0)
    transport_mode: Optional[str] = "truck"
    recycled_content: float = Field(default=0, ge=0, le=100)
    end_of_life_recycling_rate: float = Field(default=0, ge=0, le=100)
    tags: Optional[List[str]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Aluminum Production Q1 2024",
                "description": "LCA for aluminum production facility",
                "material": "aluminium",
                "production_type": "secondary",
                "quantity": 10000,
                "energy_source": "renewable",
                "transport_distance": 500,
                "transport_mode": "truck",
                "recycled_content": 75,
                "end_of_life_recycling_rate": 80,
                "tags": ["Q1", "aluminum", "renewable"]
            }
        }


class ProjectUpdateSchema(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Updated Project Name",
                "description": "Updated description",
                "status": "completed",
                "tags": ["Q1", "completed"]
            }
        }


class ProjectResponseSchema(BaseModel):
    """Schema for project response"""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    material: str
    production_type: str
    quantity: float
    energy_source: str
    transport_distance: Optional[float]
    transport_mode: Optional[str]
    recycled_content: float
    end_of_life_recycling_rate: float
    total_co2_emissions: Optional[float]
    co2_per_unit: Optional[float]
    energy_consumption: Optional[float]
    water_usage: Optional[float]
    mci_score: Optional[float]
    circularity_level: Optional[str]
    lca_results: Optional[Dict[str, Any]]
    circularity_results: Optional[Dict[str, Any]]
    recommendations: Optional[Dict[str, Any]]
    status: str
    tags: Optional[List[str]]
    created_at: str
    updated_at: str
    
    class Config:
        orm_mode = True


class ProjectSummarySchema(BaseModel):
    """Schema for project summary (list view)"""
    id: int
    name: str
    description: Optional[str]
    material: str
    production_type: str
    quantity: float
    total_co2_emissions: Optional[float]
    mci_score: Optional[float]
    status: str
    created_at: str
    updated_at: str
    
    class Config:
        orm_mode = True


class ProjectStatsSchema(BaseModel):
    """Schema for project statistics"""
    total_projects: int
    completed_projects: int
    draft_projects: int
    total_co2_calculated: float
    average_mci_score: float
    materials_analyzed: Dict[str, int]
    
    class Config:
        schema_extra = {
            "example": {
                "total_projects": 25,
                "completed_projects": 18,
                "draft_projects": 7,
                "total_co2_calculated": 125000.50,
                "average_mci_score": 0.72,
                "materials_analyzed": {
                    "aluminium": 12,
                    "copper": 8,
                    "steel": 5
                }
            }
        }
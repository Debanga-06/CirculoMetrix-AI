"""
Project Database Model for MongoDB
Document model for storing LCA projects and calculations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId


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
# Project Document Model
# ==========================================

class ProjectDocument(BaseModel):
    """
    Project document model for MongoDB
    Represents LCA calculations and analysis
    """
    
    # MongoDB ID
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    # Foreign Key (User reference)
    user_id: str = Field(..., description="Reference to user document ID")
    
    # Project Information
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    
    # Material Information
    material: str = Field(..., min_length=1, max_length=50)
    production_type: str = Field(..., min_length=1, max_length=50)
    quantity: float = Field(..., gt=0)
    
    # Energy and Transport
    energy_source: str = Field(..., min_length=1, max_length=50)
    transport_distance: Optional[float] = Field(default=0, ge=0)
    transport_mode: Optional[str] = Field(default="truck", max_length=50)
    
    # Circularity Metrics
    recycled_content: float = Field(default=0.0, ge=0, le=100)
    end_of_life_recycling_rate: float = Field(default=0.0, ge=0, le=100)
    
    # LCA Results
    total_co2_emissions: Optional[float] = None
    co2_per_unit: Optional[float] = None
    energy_consumption: Optional[float] = None
    water_usage: Optional[float] = None
    
    # Circularity Score
    mci_score: Optional[float] = Field(default=None, ge=0, le=1)
    circularity_level: Optional[str] = Field(default=None, max_length=50)
    
    # Complete Results (Nested documents)
    lca_results: Optional[Dict[str, Any]] = None
    circularity_results: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    
    # Status and Tags
    status: str = Field(default="draft", max_length=50)  # draft, completed, archived
    tags: Optional[List[str]] = Field(default_factory=list)
    
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
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
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
                "status": "draft",
                "tags": ["Q1", "aluminum", "renewable"]
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert project document to dictionary"""
        data = self.dict(by_alias=True)
        # Convert ObjectId to string
        if "_id" in data:
            data["id"] = str(data["_id"])
            del data["_id"]
        # Convert datetime to ISO format
        if "created_at" in data and isinstance(data["created_at"], datetime):
            data["created_at"] = data["created_at"].isoformat()
        if "updated_at" in data and isinstance(data["updated_at"], datetime):
            data["updated_at"] = data["updated_at"].isoformat()
        return data
    
    def to_summary(self) -> Dict[str, Any]:
        """Convert project to summary dictionary (without full results)"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "material": self.material,
            "production_type": self.production_type,
            "quantity": self.quantity,
            "total_co2_emissions": self.total_co2_emissions,
            "mci_score": self.mci_score,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# ==========================================
# Pydantic Schemas for API
# ==========================================

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
        json_schema_extra = {
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
    
    # Allow updating results
    total_co2_emissions: Optional[float] = None
    co2_per_unit: Optional[float] = None
    energy_consumption: Optional[float] = None
    water_usage: Optional[float] = None
    mci_score: Optional[float] = None
    circularity_level: Optional[str] = None
    lca_results: Optional[Dict[str, Any]] = None
    circularity_results: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Project Name",
                "description": "Updated description",
                "status": "completed",
                "tags": ["Q1", "completed"]
            }
        }


class ProjectResponseSchema(BaseModel):
    """Schema for project response"""
    id: str
    user_id: str
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
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "name": "Aluminum Production Q1 2024",
                "material": "aluminium",
                "production_type": "secondary",
                "quantity": 10000,
                "total_co2_emissions": 5000.0,
                "mci_score": 0.75,
                "status": "completed",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T14:20:00"
            }
        }


class ProjectSummarySchema(BaseModel):
    """Schema for project summary (list view)"""
    id: str
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
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Aluminum Production Q1 2024",
                "material": "aluminium",
                "status": "completed",
                "created_at": "2024-01-15T10:30:00"
            }
        }


class ProjectStatsSchema(BaseModel):
    """Schema for project statistics"""
    total_projects: int
    completed_projects: int
    draft_projects: int
    total_co2_calculated: float
    average_mci_score: float
    materials_analyzed: Dict[str, int]
    
    class Config:
        json_schema_extra = {
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


# ==========================================
# MongoDB Collection Helper
# ==========================================

def get_projects_collection(db):
    """
    Get projects collection with indexes
    
    Args:
        db: MongoDB database instance
        
    Returns:
        MongoDB collection
    """
    collection = db.projects
    
    # Create indexes for better query performance
    collection.create_index("user_id")
    collection.create_index("material")
    collection.create_index("status")
    collection.create_index("created_at")
    collection.create_index([("user_id", 1), ("created_at", -1)])
    collection.create_index([("user_id", 1), ("status", 1)])
    
    return collection


# ==========================================
# CRUD Operations Helper Functions
# ==========================================

def project_document_helper(project) -> dict:
    """
    Convert MongoDB document to dictionary
    
    Args:
        project: MongoDB document
        
    Returns:
        Dictionary representation
    """
    if not project:
        return None
    
    return {
        "id": str(project["_id"]),
        "user_id": project["user_id"],
        "name": project["name"],
        "description": project.get("description"),
        "material": project["material"],
        "production_type": project["production_type"],
        "quantity": project["quantity"],
        "energy_source": project["energy_source"],
        "transport_distance": project.get("transport_distance", 0),
        "transport_mode": project.get("transport_mode", "truck"),
        "recycled_content": project.get("recycled_content", 0),
        "end_of_life_recycling_rate": project.get("end_of_life_recycling_rate", 0),
        "total_co2_emissions": project.get("total_co2_emissions"),
        "co2_per_unit": project.get("co2_per_unit"),
        "energy_consumption": project.get("energy_consumption"),
        "water_usage": project.get("water_usage"),
        "mci_score": project.get("mci_score"),
        "circularity_level": project.get("circularity_level"),
        "lca_results": project.get("lca_results"),
        "circularity_results": project.get("circularity_results"),
        "recommendations": project.get("recommendations"),
        "status": project.get("status", "draft"),
        "tags": project.get("tags", []),
        "created_at": project["created_at"].isoformat() if isinstance(project.get("created_at"), datetime) else project.get("created_at"),
        "updated_at": project["updated_at"].isoformat() if isinstance(project.get("updated_at"), datetime) else project.get("updated_at")
    }


def project_summary_helper(project) -> dict:
    """
    Convert MongoDB document to summary dictionary
    
    Args:
        project: MongoDB document
        
    Returns:
        Summary dictionary
    """
    if not project:
        return None
    
    return {
        "id": str(project["_id"]),
        "name": project["name"],
        "description": project.get("description"),
        "material": project["material"],
        "production_type": project["production_type"],
        "quantity": project["quantity"],
        "total_co2_emissions": project.get("total_co2_emissions"),
        "mci_score": project.get("mci_score"),
        "status": project.get("status", "draft"),
        "created_at": project["created_at"].isoformat() if isinstance(project.get("created_at"), datetime) else project.get("created_at"),
        "updated_at": project["updated_at"].isoformat() if isinstance(project.get("updated_at"), datetime) else project.get("updated_at")
    }
"""
Pydantic schemas for request/response validation
Data models for API endpoints - MongoDB compatible
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
from bson import ObjectId


# ==========================================
# MongoDB ObjectId Validator
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
# Enums
# ==========================================

class MaterialType(str, Enum):
    """Supported material types"""
    ALUMINIUM = "aluminium"
    ALUMINUM = "aluminum"
    COPPER = "copper"
    STEEL = "steel"


class ProductionType(str, Enum):
    """Production process types"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    RECYCLED = "recycled"
    VIRGIN = "virgin"


class EnergySource(str, Enum):
    """Energy source types"""
    RENEWABLE = "renewable"
    FOSSIL = "fossil"
    GRID_AVERAGE = "grid_average"
    NUCLEAR = "nuclear"
    HYDRO = "hydro"
    SOLAR = "solar"
    WIND = "wind"


class TransportMode(str, Enum):
    """Transport modes"""
    TRUCK = "truck"
    RAIL = "rail"
    SHIP = "ship"
    AIR = "air"


# ==========================================
# LCA Input Schemas
# ==========================================

class LCAInputSchema(BaseModel):
    """
    Input schema for LCA calculation
    """
    material: MaterialType = Field(..., description="Material type")
    production_type: ProductionType = Field(..., description="Production process type")
    quantity: float = Field(..., gt=0, description="Quantity in kg")
    energy_source: EnergySource = Field(default=EnergySource.GRID_AVERAGE, description="Energy source")
    transport_distance: float = Field(default=0, ge=0, description="Transport distance in km")
    transport_mode: TransportMode = Field(default=TransportMode.TRUCK, description="Transport mode")
    recycled_content: float = Field(default=0, ge=0, le=100, description="Recycled content percentage (0-100)")
    end_of_life_recycling_rate: float = Field(default=0, ge=0, le=100, description="End-of-life recycling rate (0-100)")
    
    class Config:
        use_enum_values = True  # Use enum values instead of enum objects
        json_schema_extra = {
            "example": {
                "material": "aluminium",
                "production_type": "secondary",
                "quantity": 1000,
                "energy_source": "renewable",
                "transport_distance": 500,
                "transport_mode": "truck",
                "recycled_content": 75,
                "end_of_life_recycling_rate": 80
            }
        }
    
    @validator('material')
    def normalize_material(cls, v):
        """Normalize aluminum spelling"""
        if v == MaterialType.ALUMINUM or v == "aluminum":
            return MaterialType.ALUMINIUM
        return v


# ==========================================
# LCA Output Schemas
# ==========================================

class LCABreakdownSchema(BaseModel):
    """LCA emissions breakdown by lifecycle stage"""
    raw_material_extraction: float = Field(..., description="Emissions from raw material extraction")
    production: float = Field(..., description="Emissions from production")
    transport: float = Field(..., description="Emissions from transport")
    end_of_life: float = Field(..., description="Emissions from end-of-life")
    
    class Config:
        json_schema_extra = {
            "example": {
                "raw_material_extraction": 300.5,
                "production": 750.0,
                "transport": 150.0,
                "end_of_life": 50.0
            }
        }


class LCAResultSchema(BaseModel):
    """
    Output schema for LCA calculation results
    """
    total_co2_emissions: float = Field(..., description="Total CO2 emissions in kg")
    co2_per_unit: float = Field(..., description="CO2 emissions per kg of material")
    energy_consumption: float = Field(..., description="Total energy consumption in MJ")
    energy_per_unit: float = Field(..., description="Energy consumption per kg")
    water_usage: float = Field(..., description="Total water usage in liters")
    water_per_unit: float = Field(..., description="Water usage per kg")
    breakdown: LCABreakdownSchema = Field(..., description="Emissions breakdown")
    carbon_savings: Optional[float] = Field(None, description="Carbon savings vs virgin material")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_co2_emissions": 1250.5,
                "co2_per_unit": 1.25,
                "energy_consumption": 8500.2,
                "energy_per_unit": 8.5,
                "water_usage": 15000,
                "water_per_unit": 15,
                "breakdown": {
                    "raw_material_extraction": 300.5,
                    "production": 750.0,
                    "transport": 150.0,
                    "end_of_life": 50.0
                },
                "carbon_savings": 500.5
            }
        }


# ==========================================
# Circularity Schemas
# ==========================================

class CircularityInputSchema(BaseModel):
    """
    Input schema for circularity metrics calculation
    """
    material: MaterialType = Field(..., description="Material type")
    virgin_material_input: float = Field(..., ge=0, description="Virgin material input in kg")
    recycled_material_input: float = Field(..., ge=0, description="Recycled material input in kg")
    waste_generated: float = Field(..., ge=0, description="Waste generated in kg")
    waste_recycled: float = Field(..., ge=0, description="Waste recycled in kg")
    product_lifespan: float = Field(..., gt=0, description="Product lifespan in years")
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "material": "aluminium",
                "virgin_material_input": 250,
                "recycled_material_input": 750,
                "waste_generated": 100,
                "waste_recycled": 80,
                "product_lifespan": 20
            }
        }


class CircularityResultSchema(BaseModel):
    """
    Output schema for circularity metrics
    """
    mci_score: float = Field(..., ge=0, le=1, description="Material Circularity Indicator (0-1)")
    recycled_content_rate: float = Field(..., ge=0, le=100, description="Recycled content rate (%)")
    end_of_life_recycling_rate: float = Field(..., ge=0, le=100, description="End-of-life recycling rate (%)")
    waste_reduction: float = Field(..., ge=0, le=100, description="Waste reduction rate (%)")
    circularity_level: str = Field(..., description="Circularity level (Low/Medium/High/Excellent)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mci_score": 0.78,
                "recycled_content_rate": 75.0,
                "end_of_life_recycling_rate": 80.0,
                "waste_reduction": 20.0,
                "circularity_level": "High"
            }
        }


# ==========================================
# AI Prediction Schemas
# ==========================================

class AIPredictionInputSchema(BaseModel):
    """
    Input schema for AI prediction
    """
    material: MaterialType = Field(..., description="Material type")
    production_volume: float = Field(..., gt=0, description="Production volume in kg")
    energy_source: EnergySource = Field(..., description="Energy source")
    recycled_content: float = Field(..., ge=0, le=100, description="Recycled content percentage")
    process_efficiency: float = Field(default=85, ge=0, le=100, description="Process efficiency (%)")
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "material": "copper",
                "production_volume": 5000,
                "energy_source": "renewable",
                "recycled_content": 60,
                "process_efficiency": 85
            }
        }


class AIPredictionResultSchema(BaseModel):
    """
    Output schema for AI predictions
    """
    predicted_co2_emissions: float = Field(..., description="Predicted CO2 emissions")
    predicted_energy_consumption: float = Field(..., description="Predicted energy consumption")
    confidence_score: float = Field(..., ge=0, le=1, description="Prediction confidence (0-1)")
    prediction_range: Dict[str, float] = Field(..., description="Prediction range (min/max)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "predicted_co2_emissions": 3500.5,
                "predicted_energy_consumption": 25000.0,
                "confidence_score": 0.92,
                "prediction_range": {
                    "co2_min": 3200.0,
                    "co2_max": 3800.0,
                    "energy_min": 23000.0,
                    "energy_max": 27000.0
                }
            }
        }


# ==========================================
# Recommendation Schemas
# ==========================================

class RecommendationSchema(BaseModel):
    """
    Individual recommendation
    """
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed description")
    impact: str = Field(..., description="Expected impact (Low/Medium/High)")
    category: str = Field(..., description="Category (Energy/Material/Process/Transport)")
    estimated_savings: Dict[str, Union[float, str]] = Field(..., description="Estimated savings")
    implementation_difficulty: str = Field(..., description="Difficulty (Easy/Medium/Hard)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Switch to Renewable Energy",
                "description": "Replace fossil fuel energy with solar/wind power",
                "impact": "High",
                "category": "Energy",
                "estimated_savings": {
                    "co2_reduction": 500.0,
                    "cost_savings": 5000.0
                },
                "implementation_difficulty": "Medium"
            }
        }


class RecommendationsResultSchema(BaseModel):
    """
    Output schema for recommendations
    """
    recommendations: List[RecommendationSchema] = Field(..., description="List of recommendations")
    total_estimated_savings: Dict[str, float] = Field(..., description="Total estimated savings")
    priority_actions: List[str] = Field(..., description="Priority actions to take")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommendations": [],
                "total_estimated_savings": {
                    "co2_reduction": 1200.0,
                    "energy_savings": 8000.0,
                    "cost_savings": 15000.0
                },
                "priority_actions": [
                    "Increase recycled content to 80%",
                    "Switch to renewable energy",
                    "Optimize transport routes"
                ]
            }
        }


# ==========================================
# What-If Analysis Schemas
# ==========================================

class WhatIfScenarioSchema(BaseModel):
    """
    What-if scenario parameters
    """
    scenario_name: str = Field(..., description="Scenario name")
    base_input: LCAInputSchema = Field(..., description="Base case input")
    changes: Dict[str, Any] = Field(..., description="Parameters to change")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenario_name": "Increase Recycled Content to 90%",
                "base_input": {
                    "material": "aluminium",
                    "production_type": "secondary",
                    "quantity": 1000,
                    "energy_source": "grid_average",
                    "transport_distance": 500,
                    "recycled_content": 75
                },
                "changes": {
                    "recycled_content": 90,
                    "energy_source": "renewable"
                }
            }
        }


class WhatIfResultSchema(BaseModel):
    """
    What-if analysis results
    """
    scenario_name: str = Field(..., description="Scenario name")
    base_case: LCAResultSchema = Field(..., description="Base case results")
    scenario_case: LCAResultSchema = Field(..., description="Scenario results")
    improvements: Dict[str, float] = Field(..., description="Improvements (percentage)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenario_name": "Increase Recycled Content",
                "base_case": {},
                "scenario_case": {},
                "improvements": {
                    "co2_reduction": 15.5,
                    "energy_savings": 12.3,
                    "water_savings": 8.7
                }
            }
        }


# ==========================================
# Report Schemas
# ==========================================

class ReportRequestSchema(BaseModel):
    """
    Request schema for report generation
    """
    project_id: Optional[str] = Field(None, description="Existing project ID (MongoDB ObjectId)")
    project_name: str = Field(..., description="Project name")
    lca_input: LCAInputSchema = Field(..., description="LCA input data")
    include_recommendations: bool = Field(default=True, description="Include recommendations")
    include_comparisons: bool = Field(default=True, description="Include industry comparisons")
    format: str = Field(default="pdf", description="Report format (pdf/html)")
    
    @validator('project_id')
    def validate_project_id(cls, v):
        """Validate MongoDB ObjectId format"""
        if v is not None and not ObjectId.is_valid(v):
            raise ValueError("Invalid project ID format")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "507f1f77bcf86cd799439011",
                "project_name": "Aluminum Production Q1 2024",
                "lca_input": {
                    "material": "aluminium",
                    "production_type": "secondary",
                    "quantity": 1000,
                    "energy_source": "renewable",
                    "transport_distance": 500,
                    "recycled_content": 75
                },
                "include_recommendations": True,
                "include_comparisons": True,
                "format": "pdf"
            }
        }


class ReportResponseSchema(BaseModel):
    """
    Response schema for report generation
    """
    report_id: str = Field(..., description="Unique report ID (MongoDB ObjectId)")
    report_url: str = Field(..., description="Download URL")
    generated_at: datetime = Field(..., description="Generation timestamp")
    file_size: int = Field(..., description="File size in bytes")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "report_id": "507f1f77bcf86cd799439011",
                "report_url": "/api/v1/reports/download/507f1f77bcf86cd799439011",
                "generated_at": "2024-01-15T10:30:00",
                "file_size": 524288
            }
        }


# ==========================================
# Pagination Schemas
# ==========================================

class PaginationParams(BaseModel):
    """
    Pagination parameters for list endpoints
    """
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=20, ge=1, le=100, description="Number of records to return")
    sort_by: Optional[str] = Field(default="created_at", description="Field to sort by")
    sort_order: Optional[str] = Field(default="desc", description="Sort order (asc/desc)")
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        """Validate sort order"""
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "skip": 0,
                "limit": 20,
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        }


class PaginatedResponseSchema(BaseModel):
    """
    Generic paginated response wrapper
    """
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items per page")
    has_more: bool = Field(..., description="Whether there are more items")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "skip": 0,
                "limit": 20,
                "has_more": True
            }
        }


# ==========================================
# Error Response Schemas
# ==========================================

class ErrorResponseSchema(BaseModel):
    """
    Standard error response
    """
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input data",
                "details": {
                    "field": "quantity",
                    "issue": "must be greater than 0"
                },
                "timestamp": "2024-01-15T10:30:00"
            }
        }


# ==========================================
# Health Check Schema
# ==========================================

class HealthCheckSchema(BaseModel):
    """
    Health check response
    """
    status: str = Field(..., description="Service status")
    database: str = Field(..., description="Database status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: str = Field(..., description="API version")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "database": "connected",
                "timestamp": "2024-01-15T10:30:00",
                "version": "1.0.0"
            }
        }
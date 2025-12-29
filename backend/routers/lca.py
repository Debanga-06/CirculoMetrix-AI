"""
LCA API Router
Endpoints for Life Cycle Assessment calculations
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import logging

from models.schemas import LCAInputSchema, LCAResultSchema
from services.lca_engine import get_lca_engine
from core.database import get_db 
from fastapi import Depends
from core.utils import success_response, error_response

lca_engine = get_lca_engine()

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/calculate", response_model=Dict[str, Any])
async def calculate_lca(input_data: LCAInputSchema,db=Depends(get_db)):
    """
    Calculate Life Cycle Assessment for given input
    
    **Parameters:**
    - material: Material type (aluminium, copper, steel)
    - production_type: Production process (primary, secondary)
    - quantity: Quantity in kg
    - energy_source: Energy source type
    - transport_distance: Distance in km
    - transport_mode: Transport method
    - recycled_content: Percentage of recycled content (0-100)
    - end_of_life_recycling_rate: EOL recycling rate (0-100)
    
    **Returns:**
    - Complete LCA results with breakdown and carbon savings
    """
    try:
        logger.info(f"LCA calculation request: {input_data.material} - {input_data.quantity}kg")
        
        # Validate input
        if input_data.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than 0"
            )
        
        # Calculate LCA
        result = lca_engine.calculate_lca(input_data)
        
        # Return success response
        return success_response(
            data=result.dict(),
            message="LCA calculation completed successfully"
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error calculating LCA: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating LCA. Please check your input and try again."
        )


@router.post("/compare", response_model=Dict[str, Any])
async def compare_scenarios(
    base_scenario: LCAInputSchema,
    alternative_scenario: LCAInputSchema
):
    """
    Compare two LCA scenarios
    
    **Parameters:**
    - base_scenario: Base case input parameters
    - alternative_scenario: Alternative scenario parameters
    
    **Returns:**
    - Comparison results with improvements
    """
    try:
        logger.info("LCA comparison request")
        
        # Compare scenarios
        comparison = lca_engine.compare_scenarios(base_scenario, alternative_scenario)
        
        return success_response(
            data=comparison,
            message="Scenario comparison completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error comparing scenarios: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error comparing scenarios. Please check your input and try again."
        )


@router.get("/emission-factors", response_model=Dict[str, Any])
async def get_emission_factors():
    """
    Get available emission factors
    
    **Returns:**
    - List of emission factors by material and production type
    """
    try:
        # Convert DataFrame to dictionary
        factors = lca_engine.emission_factors.to_dict(orient='records')
        
        return success_response(
            data=factors,
            message="Emission factors retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving emission factors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving emission factors"
        )


@router.get("/transport-factors", response_model=Dict[str, Any])
async def get_transport_factors():
    """
    Get available transport emission factors
    
    **Returns:**
    - List of transport factors by mode
    """
    try:
        # Convert DataFrame to dictionary
        factors = lca_engine.transport_factors.to_dict(orient='records')
        
        return success_response(
            data=factors,
            message="Transport factors retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving transport factors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving transport factors"
        )


@router.post("/batch-calculate", response_model=Dict[str, Any])
async def batch_calculate_lca(inputs: list[LCAInputSchema]):
    """
    Calculate LCA for multiple inputs in batch
    
    **Parameters:**
    - inputs: List of LCA input parameters
    
    **Returns:**
    - List of LCA results
    """
    try:
        logger.info(f"Batch LCA calculation request: {len(inputs)} items")
        
        if len(inputs) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 100 items allowed per batch"
            )
        
        results = []
        for input_data in inputs:
            result = lca_engine.calculate_lca(input_data)
            results.append(result.dict())
        
        return success_response(
            data={
                "count": len(results),
                "results": results
            },
            message=f"Batch LCA calculation completed for {len(results)} items"
        )
        
    except Exception as e:
        logger.error(f"Error in batch calculation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error in batch calculation"
        )


@router.get("/breakdown/{material}/{production_type}", response_model=Dict[str, Any])
async def get_typical_breakdown(material: str, production_type: str):
    """
    Get typical LCA breakdown for material and production type
    
    **Parameters:**
    - material: Material type
    - production_type: Production process type
    
    **Returns:**
    - Typical breakdown percentages
    """
    try:
        # Create a sample input for typical breakdown
        sample_input = LCAInputSchema(
            material=material,
            production_type=production_type,
            quantity=1000,  # 1 ton
            energy_source="grid_average",
            transport_distance=500,
            transport_mode="truck",
            recycled_content=0 if production_type == "primary" else 80,
            end_of_life_recycling_rate=70
        )
        
        result = lca_engine.calculate_lca(sample_input)
        
        # Calculate percentages
        total = result.total_co2_emissions
        breakdown_pct = {
            "raw_material_extraction": round((result.breakdown.raw_material_extraction / total) * 100, 1),
            "production": round((result.breakdown.production / total) * 100, 1),
            "transport": round((result.breakdown.transport / total) * 100, 1),
            "end_of_life": round((result.breakdown.end_of_life / total) * 100, 1)
        }
        
        return success_response(
            data={
                "material": material,
                "production_type": production_type,
                "breakdown_percentages": breakdown_pct,
                "total_co2_per_ton": round(result.total_co2_emissions, 2)
            },
            message="Typical breakdown retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting typical breakdown: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving typical breakdown"
        )


@router.post("/carbon-savings", response_model=Dict[str, Any])
async def calculate_carbon_savings(
    current: LCAInputSchema,
    target_recycled_content: float
):
    """
    Calculate potential carbon savings with increased recycled content
    
    **Parameters:**
    - current: Current LCA parameters
    - target_recycled_content: Target recycled content percentage
    
    **Returns:**
    - Potential carbon savings
    """
    try:
        if not 0 <= target_recycled_content <= 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target recycled content must be between 0 and 100"
            )
        
        # Calculate current emissions
        current_result = lca_engine.calculate_lca(current)
        
        # Create target scenario
        target = current.copy()
        target.recycled_content = target_recycled_content
        target.production_type = "secondary" if target_recycled_content > 50 else current.production_type
        
        target_result = lca_engine.calculate_lca(target)
        
        # Calculate savings
        savings = current_result.total_co2_emissions - target_result.total_co2_emissions
        savings_pct = (savings / current_result.total_co2_emissions) * 100
        
        return success_response(
            data={
                "current_emissions": round(current_result.total_co2_emissions, 2),
                "target_emissions": round(target_result.total_co2_emissions, 2),
                "carbon_savings": round(savings, 2),
                "savings_percentage": round(savings_pct, 2),
                "current_recycled_content": current.recycled_content,
                "target_recycled_content": target_recycled_content
            },
            message="Carbon savings calculated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error calculating carbon savings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating carbon savings"
        )


@router.get("/benchmarks/{material}", response_model=Dict[str, Any])
async def get_industry_benchmarks(material: str):
    """
    Get industry benchmark data for material
    
    **Parameters:**
    - material: Material type
    
    **Returns:**
    - Industry benchmark emissions data
    """
    try:
        # Industry benchmarks (kg CO2 per kg material)
        benchmarks = {
            "aluminium": {
                "primary_best_practice": 8.5,
                "primary_average": 11.5,
                "secondary_best_practice": 0.4,
                "secondary_average": 0.6,
                "global_average": 7.5
            },
            "aluminum": {
                "primary_best_practice": 8.5,
                "primary_average": 11.5,
                "secondary_best_practice": 0.4,
                "secondary_average": 0.6,
                "global_average": 7.5
            },
            "copper": {
                "primary_best_practice": 2.0,
                "primary_average": 3.2,
                "secondary_best_practice": 0.8,
                "secondary_average": 1.2,
                "global_average": 2.5
            },
            "steel": {
                "primary_best_practice": 1.5,
                "primary_average": 2.8,
                "secondary_best_practice": 0.3,
                "secondary_average": 0.5,
                "global_average": 2.0
            }
        }
        
        material_lower = material.lower()
        if material_lower not in benchmarks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Benchmarks not available for material: {material}"
            )
        
        return success_response(
            data={
                "material": material,
                "benchmarks": benchmarks[material_lower],
                "unit": "kg CO2 per kg material"
            },
            message="Industry benchmarks retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving benchmarks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving industry benchmarks"
        )
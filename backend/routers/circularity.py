"""
Circularity API Router
Endpoints for circular economy metrics and Material Circularity Indicator (MCI)
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import logging

from models.schemas import CircularityInputSchema, CircularityResultSchema
from services.circularity_engine import circularity_engine
from core.utils import success_response

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/calculate", response_model=Dict[str, Any])
async def calculate_circularity(input_data: CircularityInputSchema):
    """
    Calculate circular economy metrics including MCI
    
    **Parameters:**
    - material: Material type
    - virgin_material_input: Virgin material in kg
    - recycled_material_input: Recycled material in kg
    - waste_generated: Waste generated in kg
    - waste_recycled: Waste recycled in kg
    - product_lifespan: Product lifespan in years
    
    **Returns:**
    - Circularity metrics including MCI score and levels
    """
    try:
        logger.info(f"Circularity calculation request: {input_data.material}")
        
        # Validate input
        if input_data.waste_recycled > input_data.waste_generated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Waste recycled cannot exceed waste generated"
            )
        
        # Calculate circularity metrics
        result = circularity_engine.calculate_circularity_metrics(input_data)
        
        return success_response(
            data=result.dict(),
            message="Circularity metrics calculated successfully"
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error calculating circularity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating circularity metrics"
        )


@router.post("/material-flow", response_model=Dict[str, Any])
async def analyze_material_flow(input_data: CircularityInputSchema):
    """
    Perform material flow analysis
    
    **Parameters:**
    - CircularityInputSchema parameters
    
    **Returns:**
    - Detailed material flow analysis with inputs, outputs, and efficiency
    """
    try:
        logger.info("Material flow analysis request")
        
        # Calculate flow analysis
        flow_analysis = circularity_engine.calculate_material_flow_analysis(input_data)
        
        return success_response(
            data=flow_analysis,
            message="Material flow analysis completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error in material flow analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing material flow analysis"
        )


@router.post("/sankey", response_model=Dict[str, Any])
async def generate_sankey_diagram(input_data: CircularityInputSchema):
    """
    Generate Sankey diagram data for material flows
    
    **Parameters:**
    - CircularityInputSchema parameters
    
    **Returns:**
    - Sankey diagram nodes and links data
    """
    try:
        logger.info("Sankey diagram generation request")
        
        # Generate Sankey data
        sankey_data = circularity_engine.generate_sankey_data(input_data)
        
        return success_response(
            data=sankey_data,
            message="Sankey diagram data generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating Sankey diagram: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating Sankey diagram data"
        )


@router.post("/benchmark", response_model=Dict[str, Any])
async def benchmark_circularity(
    input_data: CircularityInputSchema
):
    """
    Benchmark MCI score against industry averages
    
    **Parameters:**
    - CircularityInputSchema parameters
    
    **Returns:**
    - Benchmarking results with industry comparison
    """
    try:
        logger.info("Circularity benchmarking request")
        
        # Calculate MCI
        result = circularity_engine.calculate_circularity_metrics(input_data)
        
        # Benchmark against industry
        benchmark = circularity_engine.benchmark_against_industry(
            result.mci_score,
            input_data.material.value
        )
        
        return success_response(
            data={
                "circularity_metrics": result.dict(),
                "benchmark": benchmark
            },
            message="Benchmarking completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error in benchmarking: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing benchmark analysis"
        )


@router.post("/gap-analysis", response_model=Dict[str, Any])
async def analyze_circularity_gap(
    input_data: CircularityInputSchema,
    target_mci: float = 0.9
):
    """
    Analyze gap between current and target circularity
    
    **Parameters:**
    - input_data: Current circularity parameters
    - target_mci: Target MCI score (default: 0.9)
    
    **Returns:**
    - Gap analysis with required improvements
    """
    try:
        if not 0 <= target_mci <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target MCI must be between 0 and 1"
            )
        
        logger.info(f"Gap analysis request: target MCI = {target_mci}")
        
        # Calculate gap
        gap_analysis = circularity_engine.calculate_circularity_gap(
            input_data,
            target_mci
        )
        
        return success_response(
            data=gap_analysis,
            message="Gap analysis completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in gap analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing gap analysis"
        )


@router.get("/mci-explanation", response_model=Dict[str, Any])
async def get_mci_explanation():
    """
    Get detailed explanation of MCI calculation methodology
    
    **Returns:**
    - MCI methodology explanation
    """
    try:
        explanation = {
            "name": "Material Circularity Indicator (MCI)",
            "description": "The MCI measures how restorative material flows are in a product or company, scored from 0 (linear) to 1 (fully circular)",
            "methodology": "Based on Ellen MacArthur Foundation methodology",
            "formula": "MCI = (1 - LFI) × F(X,W)",
            "components": {
                "LFI": {
                    "name": "Linear Flow Index",
                    "description": "Proportion of material flowing linearly",
                    "calculation": "(Virgin Material Fraction + Waste Fraction) / 2"
                },
                "F(X,W)": {
                    "name": "Utility Factor",
                    "description": "Accounts for product lifespan and functional uses",
                    "factors": ["Product lifespan", "Number of functional uses"]
                }
            },
            "score_interpretation": {
                "0.9 - 1.0": "Excellent - Highly circular",
                "0.7 - 0.9": "High - Strong circularity",
                "0.5 - 0.7": "Medium - Moderate circularity",
                "0.3 - 0.5": "Low - Limited circularity",
                "0.0 - 0.3": "Very Low - Mostly linear"
            },
            "improvement_strategies": [
                "Increase recycled content in materials",
                "Improve end-of-life recycling rates",
                "Extend product lifespan",
                "Design for disassembly and recycling",
                "Implement take-back programs"
            ]
        }
        
        return success_response(
            data=explanation,
            message="MCI explanation retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving MCI explanation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving explanation"
        )


@router.get("/industry-averages", response_model=Dict[str, Any])
async def get_industry_averages():
    """
    Get industry average MCI scores by material
    
    **Returns:**
    - Industry average MCI scores
    """
    try:
        averages = {
            "aluminium": {
                "industry_average": 0.65,
                "best_in_class": 0.90,
                "worst_case": 0.30,
                "typical_range": [0.50, 0.75]
            },
            "copper": {
                "industry_average": 0.70,
                "best_in_class": 0.92,
                "worst_case": 0.35,
                "typical_range": [0.55, 0.80]
            },
            "steel": {
                "industry_average": 0.60,
                "best_in_class": 0.85,
                "worst_case": 0.25,
                "typical_range": [0.45, 0.70]
            }
        }
        
        return success_response(
            data=averages,
            message="Industry averages retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving industry averages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving industry averages"
        )


@router.post("/improvement-potential", response_model=Dict[str, Any])
async def calculate_improvement_potential(input_data: CircularityInputSchema):
    """
    Calculate improvement potential for circularity metrics
    
    **Parameters:**
    - CircularityInputSchema parameters
    
    **Returns:**
    - Improvement potential analysis
    """
    try:
        logger.info("Improvement potential analysis request")
        
        # Calculate current metrics
        current = circularity_engine.calculate_circularity_metrics(input_data)
        
        # Calculate potential with improvements
        improved_input = input_data.copy()
        improved_input.recycled_material_input = (
            improved_input.virgin_material_input + improved_input.recycled_material_input
        ) * 0.95
        improved_input.virgin_material_input = (
            improved_input.virgin_material_input + input_data.recycled_material_input
        ) * 0.05
        improved_input.waste_recycled = improved_input.waste_generated * 0.95
        
        improved = circularity_engine.calculate_circularity_metrics(improved_input)
        
        # Calculate potential improvements
        potential = {
            "current": {
                "mci_score": current.mci_score,
                "recycled_content_rate": current.recycled_content_rate,
                "eol_recycling_rate": current.end_of_life_recycling_rate
            },
            "achievable": {
                "mci_score": improved.mci_score,
                "recycled_content_rate": improved.recycled_content_rate,
                "eol_recycling_rate": improved.end_of_life_recycling_rate
            },
            "improvements": {
                "mci_increase": round(improved.mci_score - current.mci_score, 3),
                "recycled_content_increase": round(
                    improved.recycled_content_rate - current.recycled_content_rate, 2
                ),
                "eol_recycling_increase": round(
                    improved.end_of_life_recycling_rate - current.end_of_life_recycling_rate, 2
                )
            },
            "recommendations": [
                "Increase recycled content to 95%",
                "Achieve 95% end-of-life recycling rate",
                "Minimize virgin material input"
            ]
        }
        
        return success_response(
            data=potential,
            message="Improvement potential calculated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error calculating improvement potential: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating improvement potential"
        )
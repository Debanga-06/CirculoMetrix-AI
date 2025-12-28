"""
What-If Analysis API Router
Endpoints for scenario analysis and optimization
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Dict, Any, List
import logging

from models.schemas import (
    LCAInputSchema,
    WhatIfScenarioSchema,
    WhatIfResultSchema
)
from services.scenario_engine import scenario_engine
from core.utils import success_response

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_scenario(scenario: WhatIfScenarioSchema):
    """
    Analyze a what-if scenario
    
    **Parameters:**
    - scenario_name: Name of the scenario
    - base_input: Base case LCA parameters
    - changes: Dictionary of parameters to change
    
    **Returns:**
    - Scenario analysis with improvements
    """
    try:
        logger.info(f"Analyzing scenario: {scenario.scenario_name}")
        
        # Analyze scenario
        result = scenario_engine.analyze_scenario(
            scenario.base_input,
            scenario.changes,
            scenario.scenario_name
        )
        
        return success_response(
            data=result.dict(),
            message="Scenario analysis completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error analyzing scenario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing scenario"
        )


@router.post("/compare-multiple", response_model=Dict[str, Any])
async def compare_multiple_scenarios(
    base_input: LCAInputSchema,
    scenarios: List[Dict[str, Any]]
):
    """
    Compare multiple scenarios at once
    
    **Parameters:**
    - base_input: Base case parameters
    - scenarios: List of scenario configurations
    
    **Returns:**
    - Comparison of all scenarios
    """
    try:
        if len(scenarios) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 scenarios allowed for comparison"
            )
        
        logger.info(f"Comparing {len(scenarios)} scenarios")
        
        # Compare scenarios
        results = scenario_engine.compare_multiple_scenarios(base_input, scenarios)
        
        # Generate summary
        summary = scenario_engine.generate_scenario_summary(results)
        
        return success_response(
            data={
                "scenarios": [r.dict() for r in results],
                "summary": summary
            },
            message=f"Compared {len(scenarios)} scenarios successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing scenarios: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error comparing scenarios"
        )


@router.get("/predefined", response_model=Dict[str, Any])
async def list_predefined_scenarios():
    """
    List all available predefined scenarios
    
    **Returns:**
    - List of predefined scenario templates
    """
    try:
        scenarios = scenario_engine.list_predefined_scenarios()
        
        return success_response(
            data=scenarios,
            message=f"Retrieved {len(scenarios)} predefined scenarios"
        )
        
    except Exception as e:
        logger.error(f"Error listing scenarios: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving predefined scenarios"
        )


@router.post("/predefined/{scenario_key}", response_model=Dict[str, Any])
async def analyze_predefined_scenario(
    scenario_key: str,
    base_input: LCAInputSchema
):
    """
    Analyze a predefined scenario
    
    **Parameters:**
    - scenario_key: Key of predefined scenario
    - base_input: Base case parameters
    
    **Returns:**
    - Scenario analysis results
    """
    try:
        logger.info(f"Analyzing predefined scenario: {scenario_key}")
        
        # Get predefined scenario
        scenario_config = scenario_engine.get_predefined_scenario(scenario_key)
        
        if not scenario_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Predefined scenario '{scenario_key}' not found"
            )
        
        # Analyze scenario
        result = scenario_engine.analyze_scenario(
            base_input,
            scenario_config["changes"],
            scenario_config["name"]
        )
        
        return success_response(
            data={
                "scenario": result.dict(),
                "description": scenario_config["description"]
            },
            message=f"Analyzed predefined scenario: {scenario_config['name']}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing predefined scenario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing predefined scenario"
        )


@router.post("/sensitivity", response_model=Dict[str, Any])
async def perform_sensitivity_analysis(
    base_input: LCAInputSchema,
    parameter: str = Query(..., description="Parameter to analyze"),
    min_value: float = Query(..., description="Minimum value"),
    max_value: float = Query(..., description="Maximum value"),
    steps: int = Query(default=5, description="Number of steps")
):
    """
    Perform sensitivity analysis on a parameter
    
    **Parameters:**
    - base_input: Base case parameters
    - parameter: Parameter to vary (recycled_content, transport_distance, etc.)
    - min_value: Minimum value
    - max_value: Maximum value
    - steps: Number of steps in range
    
    **Returns:**
    - Sensitivity analysis results
    """
    try:
        if steps > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 steps allowed"
            )
        
        # Validate parameter
        valid_params = [
            "recycled_content",
            "transport_distance",
            "end_of_life_recycling_rate",
            "quantity"
        ]
        
        if parameter not in valid_params:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid parameter. Must be one of: {', '.join(valid_params)}"
            )
        
        logger.info(f"Sensitivity analysis on {parameter}")
        
        # Generate values
        import numpy as np
        values = np.linspace(min_value, max_value, steps).tolist()
        
        # Perform sensitivity analysis
        result = scenario_engine.sensitivity_analysis(
            base_input,
            parameter,
            values
        )
        
        return success_response(
            data=result,
            message="Sensitivity analysis completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in sensitivity analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing sensitivity analysis"
        )


@router.post("/optimize", response_model=Dict[str, Any])
async def optimize_parameters(
    base_input: LCAInputSchema,
    goal: str = Query(
        default="minimize_co2",
        description="Optimization goal: minimize_co2, minimize_energy, or maximize_circularity"
    )
):
    """
    Get optimal parameter suggestions based on goal
    
    **Parameters:**
    - base_input: Base case parameters
    - goal: Optimization objective
    
    **Returns:**
    - Optimal parameter suggestions and expected improvements
    """
    try:
        valid_goals = ["minimize_co2", "minimize_energy", "maximize_circularity"]
        
        if goal not in valid_goals:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid goal. Must be one of: {', '.join(valid_goals)}"
            )
        
        logger.info(f"Optimizing for: {goal}")
        
        # Get optimization suggestions
        optimization = scenario_engine.optimize_parameters(base_input, goal)
        
        return success_response(
            data=optimization,
            message=f"Optimization completed for {goal}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in optimization: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing optimization"
        )


@router.post("/target-achievement", response_model=Dict[str, Any])
async def calculate_target_achievement(
    base_input: LCAInputSchema,
    target_reduction_percent: float = Query(..., description="Target CO2 reduction percentage")
):
    """
    Calculate what changes are needed to achieve target reduction
    
    **Parameters:**
    - base_input: Base case parameters
    - target_reduction_percent: Desired CO2 reduction (percentage)
    
    **Returns:**
    - Suggested changes to achieve target
    """
    try:
        from services.lca_engine import lca_engine
        
        if not 0 <= target_reduction_percent <= 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target reduction must be between 0 and 100 percent"
            )
        
        logger.info(f"Calculating path to {target_reduction_percent}% reduction")
        
        # Calculate base emissions
        base_result = lca_engine.calculate_lca(base_input)
        target_emissions = base_result.total_co2_emissions * (1 - target_reduction_percent / 100)
        
        # Suggest changes
        suggestions = []
        
        # Try increasing recycled content
        if base_input.recycled_content < 90:
            new_recycled = min(95, base_input.recycled_content + 20)
            test_input = base_input.copy()
            test_input.recycled_content = new_recycled
            test_input.production_type = "secondary"
            test_result = lca_engine.calculate_lca(test_input)
            
            suggestions.append({
                "change": f"Increase recycled content to {new_recycled}%",
                "potential_emissions": test_result.total_co2_emissions,
                "reduction_achieved": round(
                    ((base_result.total_co2_emissions - test_result.total_co2_emissions) / 
                     base_result.total_co2_emissions) * 100, 2
                )
            })
        
        # Try switching to renewable energy
        if base_input.energy_source != "renewable":
            test_input = base_input.copy()
            test_input.energy_source = "renewable"
            test_result = lca_engine.calculate_lca(test_input)
            
            suggestions.append({
                "change": "Switch to renewable energy",
                "potential_emissions": test_result.total_co2_emissions,
                "reduction_achieved": round(
                    ((base_result.total_co2_emissions - test_result.total_co2_emissions) / 
                     base_result.total_co2_emissions) * 100, 2
                )
            })
        
        # Try combined approach
        test_input = base_input.copy()
        test_input.recycled_content = min(95, base_input.recycled_content + 20)
        test_input.production_type = "secondary"
        test_input.energy_source = "renewable"
        test_input.transport_distance = base_input.transport_distance * 0.7
        test_result = lca_engine.calculate_lca(test_input)
        
        combined_reduction = round(
            ((base_result.total_co2_emissions - test_result.total_co2_emissions) / 
             base_result.total_co2_emissions) * 100, 2
        )
        
        return success_response(
            data={
                "current_emissions": round(base_result.total_co2_emissions, 2),
                "target_emissions": round(target_emissions, 2),
                "target_reduction_percent": target_reduction_percent,
                "individual_suggestions": suggestions,
                "combined_approach": {
                    "changes": [
                        f"Recycled content: {min(95, base_input.recycled_content + 20)}%",
                        "Energy source: Renewable",
                        "Transport distance: -30%"
                    ],
                    "potential_emissions": round(test_result.total_co2_emissions, 2),
                    "reduction_achieved": combined_reduction,
                    "target_met": combined_reduction >= target_reduction_percent
                },
                "feasibility": "Achievable" if combined_reduction >= target_reduction_percent else "Additional measures needed"
            },
            message="Target achievement analysis completed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in target achievement calculation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating target achievement"
        )


@router.post("/scenario-builder", response_model=Dict[str, Any])
async def build_custom_scenario(
    base_input: LCAInputSchema,
    recycled_content: float = Query(default=None),
    energy_source: str = Query(default=None),
    transport_distance_reduction: float = Query(default=None),
    transport_mode: str = Query(default=None)
):
    """
    Build and analyze a custom scenario with specified parameters
    
    **Parameters:**
    - base_input: Base case parameters
    - recycled_content: Target recycled content (optional)
    - energy_source: Target energy source (optional)
    - transport_distance_reduction: Distance reduction percentage (optional)
    - transport_mode: Target transport mode (optional)
    
    **Returns:**
    - Custom scenario analysis
    """
    try:
        logger.info("Building custom scenario")
        
        # Build changes dictionary
        changes = {}
        
        if recycled_content is not None:
            if not 0 <= recycled_content <= 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Recycled content must be between 0 and 100"
                )
            changes["recycled_content"] = recycled_content
        
        if energy_source is not None:
            changes["energy_source"] = energy_source
        
        if transport_distance_reduction is not None:
            if not 0 <= transport_distance_reduction <= 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Transport distance reduction must be between 0 and 100 percent"
                )
            multiplier = 1 - (transport_distance_reduction / 100)
            changes["transport_distance"] = f"multiply:{multiplier}"
        
        if transport_mode is not None:
            changes["transport_mode"] = transport_mode
        
        if not changes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one parameter change must be specified"
            )
        
        # Analyze custom scenario
        result = scenario_engine.analyze_scenario(
            base_input,
            changes,
            "Custom Scenario"
        )
        
        return success_response(
            data={
                "scenario": result.dict(),
                "changes_applied": changes
            },
            message="Custom scenario analyzed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error building custom scenario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error building custom scenario"
        )
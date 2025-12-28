"""
AI Prediction API Router
Endpoints for AI-powered environmental impact predictions
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List
import logging

from models.schemas import AIPredictionInputSchema, AIPredictionResultSchema
from services.ai_engine import ai_engine
from core.utils import success_response

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/predict", response_model=Dict[str, Any])
async def predict_environmental_impact(input_data: AIPredictionInputSchema):
    """
    Predict environmental impact using AI/ML models
    
    **Parameters:**
    - material: Material type
    - production_volume: Production volume in kg
    - energy_source: Energy source type
    - recycled_content: Recycled content percentage
    - process_efficiency: Process efficiency percentage
    
    **Returns:**
    - Predicted CO2 emissions, energy consumption, and confidence scores
    """
    try:
        logger.info(f"AI prediction request: {input_data.material} - {input_data.production_volume}kg")
        
        # Validate input
        if input_data.production_volume <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Production volume must be greater than 0"
            )
        
        if not 0 <= input_data.recycled_content <= 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recycled content must be between 0 and 100"
            )
        
        if not 0 <= input_data.process_efficiency <= 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Process efficiency must be between 0 and 100"
            )
        
        # Make prediction
        result = ai_engine.predict(input_data)
        
        return success_response(
            data=result.dict(),
            message="Prediction completed successfully",
            meta={
                "model_status": "trained" if ai_engine.is_trained else "heuristic",
                "confidence_level": "high" if result.confidence_score > 0.85 else "medium"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error making prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error making prediction. Please check your input and try again."
        )


@router.post("/batch-predict", response_model=Dict[str, Any])
async def batch_predict(inputs: List[AIPredictionInputSchema]):
    """
    Make batch predictions for multiple inputs
    
    **Parameters:**
    - inputs: List of prediction input parameters
    
    **Returns:**
    - List of prediction results
    """
    try:
        logger.info(f"Batch prediction request: {len(inputs)} items")
        
        if len(inputs) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 50 items allowed per batch prediction"
            )
        
        # Make batch predictions
        results = ai_engine.batch_predict(inputs)
        
        # Convert to dict
        results_dict = [r.dict() for r in results]
        
        return success_response(
            data={
                "count": len(results_dict),
                "predictions": results_dict
            },
            message=f"Batch prediction completed for {len(results_dict)} items"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error in batch prediction"
        )


@router.get("/model-info", response_model=Dict[str, Any])
async def get_model_info():
    """
    Get information about the AI/ML models
    
    **Returns:**
    - Model information including status and features
    """
    try:
        info = {
            "model_type": "Random Forest Regressor",
            "is_trained": ai_engine.is_trained,
            "features": ai_engine.feature_columns if ai_engine.feature_columns else [],
            "target_variables": [
                "CO2 emissions (kg)",
                "Energy consumption (MJ)"
            ],
            "prediction_method": "ML-based" if ai_engine.is_trained else "Heuristic-based",
            "average_confidence": 0.85 if ai_engine.is_trained else 0.75,
            "supported_materials": ["aluminium", "aluminum", "copper", "steel"],
            "supported_energy_sources": [
                "renewable", "fossil", "grid_average", 
                "nuclear", "hydro", "solar", "wind"
            ]
        }
        
        return success_response(
            data=info,
            message="Model information retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving model info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving model information"
        )


@router.post("/compare-predictions", response_model=Dict[str, Any])
async def compare_predictions(
    scenarios: List[AIPredictionInputSchema]
):
    """
    Compare predictions for multiple scenarios
    
    **Parameters:**
    - scenarios: List of scenarios to compare (max 5)
    
    **Returns:**
    - Comparison of predictions across scenarios
    """
    try:
        if len(scenarios) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 5 scenarios allowed for comparison"
            )
        
        logger.info(f"Comparing {len(scenarios)} prediction scenarios")
        
        # Make predictions for all scenarios
        predictions = []
        for i, scenario in enumerate(scenarios):
            result = ai_engine.predict(scenario)
            predictions.append({
                "scenario_index": i + 1,
                "material": scenario.material.value,
                "production_volume": scenario.production_volume,
                "energy_source": scenario.energy_source.value,
                "recycled_content": scenario.recycled_content,
                "predicted_co2": result.predicted_co2_emissions,
                "predicted_energy": result.predicted_energy_consumption,
                "confidence": result.confidence_score
            })
        
        # Find best and worst scenarios
        best_co2 = min(predictions, key=lambda x: x["predicted_co2"])
        worst_co2 = max(predictions, key=lambda x: x["predicted_co2"])
        
        comparison = {
            "scenarios": predictions,
            "summary": {
                "best_scenario": {
                    "index": best_co2["scenario_index"],
                    "co2_emissions": best_co2["predicted_co2"]
                },
                "worst_scenario": {
                    "index": worst_co2["scenario_index"],
                    "co2_emissions": worst_co2["predicted_co2"]
                },
                "potential_savings": round(
                    worst_co2["predicted_co2"] - best_co2["predicted_co2"], 2
                ),
                "savings_percentage": round(
                    ((worst_co2["predicted_co2"] - best_co2["predicted_co2"]) / 
                     worst_co2["predicted_co2"]) * 100, 2
                )
            }
        }
        
        return success_response(
            data=comparison,
            message="Scenario comparison completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing predictions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error comparing predictions"
        )


@router.post("/sensitivity-analysis", response_model=Dict[str, Any])
async def sensitivity_analysis(
    base_input: AIPredictionInputSchema,
    parameter: str,
    range_min: float,
    range_max: float,
    steps: int = 5
):
    """
    Perform sensitivity analysis on a parameter
    
    **Parameters:**
    - base_input: Base prediction input
    - parameter: Parameter to analyze (recycled_content or process_efficiency)
    - range_min: Minimum value for parameter
    - range_max: Maximum value for parameter
    - steps: Number of steps in range (default: 5)
    
    **Returns:**
    - Sensitivity analysis results
    """
    try:
        if parameter not in ["recycled_content", "process_efficiency"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parameter must be 'recycled_content' or 'process_efficiency'"
            )
        
        if steps > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 steps allowed"
            )
        
        logger.info(f"Sensitivity analysis on {parameter}")
        
        # Generate parameter values
        import numpy as np
        values = np.linspace(range_min, range_max, steps)
        
        results = []
        for value in values:
            # Create modified input
            test_input = base_input.copy()
            setattr(test_input, parameter, float(value))
            
            # Make prediction
            prediction = ai_engine.predict(test_input)
            
            results.append({
                f"{parameter}_value": round(float(value), 2),
                "predicted_co2": prediction.predicted_co2_emissions,
                "predicted_energy": prediction.predicted_energy_consumption
            })
        
        # Calculate sensitivity (change per unit)
        if len(results) > 1:
            co2_change = results[-1]["predicted_co2"] - results[0]["predicted_co2"]
            param_change = results[-1][f"{parameter}_value"] - results[0][f"{parameter}_value"]
            sensitivity = co2_change / param_change if param_change != 0 else 0
        else:
            sensitivity = 0
        
        return success_response(
            data={
                "parameter": parameter,
                "range": [range_min, range_max],
                "results": results,
                "sensitivity": round(sensitivity, 4),
                "interpretation": (
                    f"For every 1 unit increase in {parameter}, "
                    f"CO2 emissions change by {abs(round(sensitivity, 2))} kg"
                )
            },
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


@router.get("/confidence-factors", response_model=Dict[str, Any])
async def get_confidence_factors():
    """
    Get information about prediction confidence factors
    
    **Returns:**
    - Explanation of confidence scoring
    """
    try:
        factors = {
            "confidence_scoring": {
                "description": "Confidence score indicates the reliability of predictions",
                "range": "0.0 to 1.0",
                "interpretation": {
                    "0.9 - 1.0": "Very High - Highly reliable prediction",
                    "0.8 - 0.9": "High - Reliable prediction",
                    "0.7 - 0.8": "Medium - Moderately reliable",
                    "< 0.7": "Low - Use with caution"
                }
            },
            "factors_affecting_confidence": [
                "Material type commonness",
                "Typical range of recycled content",
                "Process efficiency normality",
                "Model training status",
                "Historical data availability"
            ],
            "improving_confidence": [
                "Use common materials (aluminium, steel, copper)",
                "Stay within typical parameter ranges",
                "Provide accurate input data",
                "Use for similar production scales as training data"
            ],
            "prediction_range": {
                "description": "Min/max range represents uncertainty interval",
                "calculation": "Based on confidence score and historical variance"
            }
        }
        
        return success_response(
            data=factors,
            message="Confidence factors retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving confidence factors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving confidence factors"
        )
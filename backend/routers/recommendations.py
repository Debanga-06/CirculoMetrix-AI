"""
Recommendations API Router
Endpoints for generating AI-powered sustainability recommendations
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Dict, Any, Optional
import logging

from models.schemas import (
    LCAInputSchema,
    CircularityInputSchema,
    RecommendationsResultSchema
)
from services.lca_engine import lca_engine
from services.circularity_engine import circularity_engine
from services.recommendation_engine import recommendation_engine
from core.utils import success_response

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/generate", response_model=Dict[str, Any])
async def generate_recommendations(
    lca_input: LCAInputSchema,
    include_circularity: bool = Query(default=False, description="Include circularity recommendations")
):
    """
    Generate comprehensive sustainability recommendations
    
    **Parameters:**
    - lca_input: LCA input parameters
    - include_circularity: Whether to include circularity analysis
    
    **Returns:**
    - List of prioritized recommendations with estimated savings
    """
    try:
        logger.info("Generating recommendations")
        
        # Calculate LCA
        lca_result = lca_engine.calculate_lca(lca_input)
        
        # Calculate circularity if requested
        circularity_result = None
        if include_circularity:
            # Create circularity input from LCA input
            total_input = lca_input.quantity
            recycled_input = total_input * (lca_input.recycled_content / 100)
            virgin_input = total_input - recycled_input
            
            circularity_input = CircularityInputSchema(
                material=lca_input.material,
                virgin_material_input=virgin_input,
                recycled_material_input=recycled_input,
                waste_generated=total_input * 0.1,  # Assume 10% waste
                waste_recycled=total_input * 0.1 * (lca_input.end_of_life_recycling_rate / 100),
                product_lifespan=20  # Default lifespan
            )
            circularity_result = circularity_engine.calculate_circularity_metrics(circularity_input)
        
        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(
            lca_input,
            lca_result,
            circularity_result
        )
        
        return success_response(
            data=recommendations.dict(),
            message=f"Generated {len(recommendations.recommendations)} recommendations"
        )
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating recommendations"
        )


@router.post("/filter", response_model=Dict[str, Any])
async def filter_recommendations(
    lca_input: LCAInputSchema,
    category: Optional[str] = Query(default=None, description="Filter by category"),
    impact_level: Optional[str] = Query(default=None, description="Filter by impact level"),
    difficulty: Optional[str] = Query(default=None, description="Filter by difficulty")
):
    """
    Generate filtered recommendations
    
    **Parameters:**
    - lca_input: LCA input parameters
    - category: Filter by category (Energy, Material, Transport, Process, Circularity)
    - impact_level: Filter by impact (High, Medium, Low)
    - difficulty: Filter by difficulty (Easy, Medium, Hard)
    
    **Returns:**
    - Filtered list of recommendations
    """
    try:
        logger.info(f"Generating filtered recommendations: {category}, {impact_level}, {difficulty}")
        
        # Calculate LCA
        lca_result = lca_engine.calculate_lca(lca_input)
        
        # Generate all recommendations
        all_recommendations = recommendation_engine.generate_recommendations(
            lca_input,
            lca_result,
            None
        )
        
        # Apply filters
        filtered = all_recommendations.recommendations
        
        if category:
            filtered = [r for r in filtered if r.category.lower() == category.lower()]
        
        if impact_level:
            filtered = [r for r in filtered if r.impact.lower() == impact_level.lower()]
        
        if difficulty:
            filtered = [r for r in filtered if r.implementation_difficulty.lower() == difficulty.lower()]
        
        # Recalculate totals for filtered recommendations
        total_savings = recommendation_engine._calculate_total_savings(filtered)
        priority_actions = [r.title for r in filtered[:3]]
        
        return success_response(
            data={
                "recommendations": [r.dict() for r in filtered],
                "total_estimated_savings": total_savings,
                "priority_actions": priority_actions,
                "filters_applied": {
                    "category": category,
                    "impact_level": impact_level,
                    "difficulty": difficulty
                },
                "count": len(filtered)
            },
            message=f"Found {len(filtered)} recommendations matching filters"
        )
        
    except Exception as e:
        logger.error(f"Error filtering recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error filtering recommendations"
        )


@router.get("/categories", response_model=Dict[str, Any])
async def get_recommendation_categories():
    """
    Get available recommendation categories
    
    **Returns:**
    - List of recommendation categories with descriptions
    """
    try:
        categories = {
            "Energy": {
                "description": "Recommendations related to energy sources and efficiency",
                "typical_impact": "High",
                "examples": [
                    "Switch to renewable energy",
                    "Improve energy efficiency",
                    "Optimize heating/cooling systems"
                ]
            },
            "Material": {
                "description": "Recommendations for material selection and sourcing",
                "typical_impact": "High",
                "examples": [
                    "Increase recycled content",
                    "Material substitution",
                    "Local material sourcing"
                ]
            },
            "Transport": {
                "description": "Recommendations for transportation and logistics",
                "typical_impact": "Medium",
                "examples": [
                    "Switch to rail/ship transport",
                    "Optimize routes",
                    "Local sourcing to reduce distance"
                ]
            },
            "Process": {
                "description": "Recommendations for process optimization",
                "typical_impact": "Medium",
                "examples": [
                    "Lean manufacturing",
                    "Waste reduction",
                    "Process automation"
                ]
            },
            "Circularity": {
                "description": "Recommendations for circular economy practices",
                "typical_impact": "High",
                "examples": [
                    "Design for recyclability",
                    "Take-back programs",
                    "Product life extension"
                ]
            }
        }
        
        return success_response(
            data=categories,
            message="Recommendation categories retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving categories"
        )


@router.post("/prioritize", response_model=Dict[str, Any])
async def prioritize_recommendations(
    lca_input: LCAInputSchema,
    priority_criteria: str = Query(
        default="impact",
        description="Prioritization criteria: impact, cost, ease, or balanced"
    )
):
    """
    Generate recommendations with custom prioritization
    
    **Parameters:**
    - lca_input: LCA input parameters
    - priority_criteria: Prioritization method
    
    **Returns:**
    - Prioritized recommendations
    """
    try:
        logger.info(f"Generating recommendations with {priority_criteria} prioritization")
        
        # Calculate LCA
        lca_result = lca_engine.calculate_lca(lca_input)
        
        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(
            lca_input,
            lca_result,
            None
        )
        
        # Apply custom prioritization
        recs = recommendations.recommendations
        
        if priority_criteria == "impact":
            # Prioritize by impact level
            impact_order = {"High": 3, "Medium": 2, "Low": 1}
            recs = sorted(recs, key=lambda r: impact_order.get(r.impact, 0), reverse=True)
        
        elif priority_criteria == "cost":
            # Prioritize by potential cost savings
            recs = sorted(
                recs,
                key=lambda r: r.estimated_savings.get("cost_savings_annual", 0),
                reverse=True
            )
        
        elif priority_criteria == "ease":
            # Prioritize by ease of implementation
            difficulty_order = {"Easy": 3, "Medium": 2, "Hard": 1}
            recs = sorted(
                recs,
                key=lambda r: difficulty_order.get(r.implementation_difficulty, 0),
                reverse=True
            )
        
        elif priority_criteria == "balanced":
            # Balanced scoring: impact × ease
            def balanced_score(rec):
                impact_scores = {"High": 3, "Medium": 2, "Low": 1}
                ease_scores = {"Easy": 3, "Medium": 2, "Hard": 1}
                return (impact_scores.get(rec.impact, 0) * 
                       ease_scores.get(rec.implementation_difficulty, 0))
            
            recs = sorted(recs, key=balanced_score, reverse=True)
        
        return success_response(
            data={
                "recommendations": [r.dict() for r in recs],
                "prioritization": priority_criteria,
                "top_3": [r.title for r in recs[:3]]
            },
            message=f"Recommendations prioritized by {priority_criteria}"
        )
        
    except Exception as e:
        logger.error(f"Error prioritizing recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error prioritizing recommendations"
        )


@router.post("/quick-wins", response_model=Dict[str, Any])
async def get_quick_wins(lca_input: LCAInputSchema):
    """
    Get quick win recommendations (high impact, easy implementation)
    
    **Parameters:**
    - lca_input: LCA input parameters
    
    **Returns:**
    - Quick win recommendations
    """
    try:
        logger.info("Getting quick win recommendations")
        
        # Calculate LCA
        lca_result = lca_engine.calculate_lca(lca_input)
        
        # Generate all recommendations
        all_recs = recommendation_engine.generate_recommendations(
            lca_input,
            lca_result,
            None
        )
        
        # Filter for quick wins (High/Medium impact + Easy implementation)
        quick_wins = [
            r for r in all_recs.recommendations
            if r.impact in ["High", "Medium"] and r.implementation_difficulty == "Easy"
        ]
        
        return success_response(
            data={
                "quick_wins": [r.dict() for r in quick_wins],
                "count": len(quick_wins),
                "message": "These are high-value, easy-to-implement recommendations"
            },
            message=f"Found {len(quick_wins)} quick win opportunities"
        )
        
    except Exception as e:
        logger.error(f"Error getting quick wins: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting quick wins"
        )


@router.post("/action-plan", response_model=Dict[str, Any])
async def generate_action_plan(
    lca_input: LCAInputSchema,
    timeframe_months: int = Query(default=12, description="Implementation timeframe in months")
):
    """
    Generate phased action plan for recommendations
    
    **Parameters:**
    - lca_input: LCA input parameters
    - timeframe_months: Total timeframe for implementation
    
    **Returns:**
    - Phased action plan
    """
    try:
        logger.info(f"Generating {timeframe_months}-month action plan")
        
        # Calculate LCA
        lca_result = lca_engine.calculate_lca(lca_input)
        
        # Generate recommendations
        all_recs = recommendation_engine.generate_recommendations(
            lca_input,
            lca_result,
            None
        )
        
        # Phase recommendations
        immediate = []  # 0-3 months
        short_term = []  # 3-6 months
        medium_term = []  # 6-12 months
        long_term = []  # 12+ months
        
        for rec in all_recs.recommendations:
            if rec.implementation_difficulty == "Easy" and rec.impact == "High":
                immediate.append(rec)
            elif rec.implementation_difficulty == "Easy":
                short_term.append(rec)
            elif rec.implementation_difficulty == "Medium":
                medium_term.append(rec)
            else:
                long_term.append(rec)
        
        action_plan = {
            "immediate_actions": {
                "timeframe": "0-3 months",
                "actions": [r.dict() for r in immediate[:3]],
                "focus": "Quick wins and high-impact changes"
            },
            "short_term_actions": {
                "timeframe": "3-6 months",
                "actions": [r.dict() for r in short_term[:3]],
                "focus": "Easy-to-implement improvements"
            },
            "medium_term_actions": {
                "timeframe": "6-12 months",
                "actions": [r.dict() for r in medium_term[:3]],
                "focus": "Moderate complexity initiatives"
            },
            "long_term_actions": {
                "timeframe": "12+ months",
                "actions": [r.dict() for r in long_term[:2]],
                "focus": "Strategic transformations"
            },
            "summary": {
                "total_recommendations": len(all_recs.recommendations),
                "estimated_total_savings": all_recs.total_estimated_savings,
                "implementation_timeframe": f"{timeframe_months} months"
            }
        }
        
        return success_response(
            data=action_plan,
            message="Action plan generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating action plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating action plan"
        )
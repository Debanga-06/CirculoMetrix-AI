"""
Recommendation Engine
Generates AI-powered sustainability recommendations based on LCA and circularity analysis
"""

from typing import List, Dict, Any
import logging

from models.schemas import (
    LCAInputSchema,
    LCAResultSchema,
    CircularityResultSchema,
    RecommendationSchema,
    RecommendationsResultSchema
)

# Configure logging
logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Smart recommendation engine for sustainability improvements
    Analyzes current performance and suggests actionable improvements
    """
    
    def __init__(self):
        """Initialize recommendation engine"""
        logger.info("Recommendation Engine initialized successfully")
    
    def generate_recommendations(
        self,
        lca_input: LCAInputSchema,
        lca_result: LCAResultSchema,
        circularity_result: CircularityResultSchema = None
    ) -> RecommendationsResultSchema:
        """
        Generate comprehensive sustainability recommendations
        
        Args:
            lca_input: LCA input parameters
            lca_result: LCA calculation results
            circularity_result: Optional circularity metrics
            
        Returns:
            Complete recommendations with priority actions
        """
        try:
            logger.info("Generating recommendations...")
            
            recommendations = []
            
            # Energy-related recommendations
            recommendations.extend(self._generate_energy_recommendations(lca_input, lca_result))
            
            # Material-related recommendations
            recommendations.extend(self._generate_material_recommendations(lca_input, lca_result))
            
            # Transport-related recommendations
            recommendations.extend(self._generate_transport_recommendations(lca_input, lca_result))
            
            # Process-related recommendations
            recommendations.extend(self._generate_process_recommendations(lca_input, lca_result))
            
            # Circularity recommendations
            if circularity_result:
                recommendations.extend(
                    self._generate_circularity_recommendations(lca_input, circularity_result)
                )
            
            # Sort by impact
            recommendations = self._sort_by_priority(recommendations)
            
            # Calculate total savings
            total_savings = self._calculate_total_savings(recommendations)
            
            # Generate priority actions
            priority_actions = self._generate_priority_actions(recommendations[:3])
            
            result = RecommendationsResultSchema(
                recommendations=recommendations,
                total_estimated_savings=total_savings,
                priority_actions=priority_actions
            )
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return result
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise
    
    def _generate_energy_recommendations(
        self,
        lca_input: LCAInputSchema,
        lca_result: LCAResultSchema
    ) -> List[RecommendationSchema]:
        """Generate energy-related recommendations"""
        recommendations = []
        
        # Recommendation: Switch to renewable energy
        if lca_input.energy_source.value != 'renewable':
            # Calculate potential savings
            current_emissions = lca_result.breakdown.production
            potential_reduction = current_emissions * 0.7  # 70% reduction with renewables
            
            recommendations.append(RecommendationSchema(
                title="Switch to Renewable Energy Sources",
                description=(
                    f"Transitioning from {lca_input.energy_source.value} to renewable energy "
                    f"(solar, wind, hydro) can significantly reduce your carbon footprint. "
                    f"This is one of the most impactful changes you can make."
                ),
                impact="High",
                category="Energy",
                estimated_savings={
                    "co2_reduction": round(potential_reduction, 2),
                    "percentage_reduction": 70.0,
                    "cost_savings_annual": round(potential_reduction * 50, 2)  # $50 per ton CO2
                },
                implementation_difficulty="Medium"
            ))
        
        # Recommendation: Energy efficiency improvements
        if lca_result.energy_consumption > lca_input.quantity * 50:  # High energy intensity
            energy_reduction = lca_result.energy_consumption * 0.15
            co2_reduction = energy_reduction * 0.05  # Approximate CO2 factor
            
            recommendations.append(RecommendationSchema(
                title="Improve Energy Efficiency",
                description=(
                    "Invest in energy-efficient equipment, optimize production processes, "
                    "and implement energy management systems. Consider heat recovery systems "
                    "and modern insulation to reduce energy waste."
                ),
                impact="Medium",
                category="Energy",
                estimated_savings={
                    "co2_reduction": round(co2_reduction, 2),
                    "energy_savings_mj": round(energy_reduction, 2),
                    "percentage_reduction": 15.0,
                    "cost_savings_annual": round(energy_reduction * 0.02, 2)  # $0.02 per MJ
                },
                implementation_difficulty="Medium"
            ))
        
        return recommendations
    
    def _generate_material_recommendations(
        self,
        lca_input: LCAInputSchema,
        lca_result: LCAResultSchema
    ) -> List[RecommendationSchema]:
        """Generate material-related recommendations"""
        recommendations = []
        
        # Recommendation: Increase recycled content
        if lca_input.recycled_content < 75:
            target_content = min(90, lca_input.recycled_content + 20)
            improvement = target_content - lca_input.recycled_content
            
            # Estimate savings
            extraction_reduction = lca_result.breakdown.raw_material_extraction * (improvement / 100) * 0.8
            production_reduction = lca_result.breakdown.production * (improvement / 100) * 0.5
            total_reduction = extraction_reduction + production_reduction
            
            recommendations.append(RecommendationSchema(
                title=f"Increase Recycled Content to {target_content}%",
                description=(
                    f"Increasing recycled content from {lca_input.recycled_content}% to {target_content}% "
                    f"will significantly reduce the need for virgin material extraction and processing. "
                    f"This is especially effective for {lca_input.material.value}."
                ),
                impact="High",
                category="Material",
                estimated_savings={
                    "co2_reduction": round(total_reduction, 2),
                    "virgin_material_savings_kg": round(lca_input.quantity * improvement / 100, 2),
                    "percentage_reduction": round((total_reduction / lca_result.total_co2_emissions) * 100, 1)
                },
                implementation_difficulty="Easy" if improvement < 15 else "Medium"
            ))
        
        # Recommendation: Material substitution
        if lca_input.material.value in ['aluminium', 'aluminum'] and lca_input.production_type.value == 'primary':
            recommendations.append(RecommendationSchema(
                title="Consider Alternative Materials or Secondary Production",
                description=(
                    "Primary aluminum production is highly energy-intensive. Consider using "
                    "secondary (recycled) aluminum or exploring alternative materials for "
                    "non-critical applications where feasible."
                ),
                impact="High",
                category="Material",
                estimated_savings={
                    "co2_reduction": round(lca_result.total_co2_emissions * 0.6, 2),
                    "percentage_reduction": 60.0
                },
                implementation_difficulty="Hard"
            ))
        
        return recommendations
    
    def _generate_transport_recommendations(
        self,
        lca_input: LCAInputSchema,
        lca_result: LCAResultSchema
    ) -> List[RecommendationSchema]:
        """Generate transport-related recommendations"""
        recommendations = []
        
        # Recommendation: Optimize transport
        if lca_input.transport_distance > 500:
            # Suggest more efficient transport mode
            if lca_input.transport_mode.value == 'truck':
                potential_reduction = lca_result.breakdown.transport * 0.6  # 60% reduction with rail
                
                recommendations.append(RecommendationSchema(
                    title="Switch from Truck to Rail Transport",
                    description=(
                        f"Your current transport distance of {lca_input.transport_distance}km by truck "
                        f"generates significant emissions. Switching to rail transport can reduce "
                        f"transport emissions by up to 60%."
                    ),
                    impact="Medium",
                    category="Transport",
                    estimated_savings={
                        "co2_reduction": round(potential_reduction, 2),
                        "percentage_reduction": 60.0
                    },
                    implementation_difficulty="Medium"
                ))
            
            # Suggest local sourcing
            if lca_input.transport_distance > 1000:
                reduction = lca_result.breakdown.transport * 0.5
                
                recommendations.append(RecommendationSchema(
                    title="Source Materials Locally",
                    description=(
                        f"Consider sourcing materials from suppliers within 500km to reduce "
                        f"transport emissions. Local sourcing also improves supply chain resilience."
                    ),
                    impact="Medium",
                    category="Transport",
                    estimated_savings={
                        "co2_reduction": round(reduction, 2),
                        "distance_reduction_km": lca_input.transport_distance - 500
                    },
                    implementation_difficulty="Medium"
                ))
        
        return recommendations
    
    def _generate_process_recommendations(
        self,
        lca_input: LCAInputSchema,
        lca_result: LCAResultSchema
    ) -> List[RecommendationSchema]:
        """Generate process optimization recommendations"""
        recommendations = []
        
        # Recommendation: Process optimization
        if lca_result.breakdown.production > lca_result.total_co2_emissions * 0.5:
            reduction = lca_result.breakdown.production * 0.12
            
            recommendations.append(RecommendationSchema(
                title="Optimize Production Processes",
                description=(
                    "Implement lean manufacturing principles, reduce waste in production, "
                    "and optimize process parameters. Consider digital twins and IoT sensors "
                    "for real-time process monitoring and optimization."
                ),
                impact="Medium",
                category="Process",
                estimated_savings={
                    "co2_reduction": round(reduction, 2),
                    "efficiency_improvement": 12.0,
                    "waste_reduction_kg": round(lca_input.quantity * 0.05, 2)
                },
                implementation_difficulty="Medium"
            ))
        
        return recommendations
    
    def _generate_circularity_recommendations(
        self,
        lca_input: LCAInputSchema,
        circularity_result: CircularityResultSchema
    ) -> List[RecommendationSchema]:
        """Generate circularity-specific recommendations"""
        recommendations = []
        
        # Recommendation: Improve end-of-life recycling
        if circularity_result.end_of_life_recycling_rate < 80:
            target_rate = 90
            improvement = target_rate - circularity_result.end_of_life_recycling_rate
            
            recommendations.append(RecommendationSchema(
                title=f"Increase End-of-Life Recycling Rate to {target_rate}%",
                description=(
                    "Establish take-back programs, partner with recycling facilities, "
                    "and design products for easier disassembly. Implement material tracking "
                    "to ensure proper end-of-life handling."
                ),
                impact="High",
                category="Circularity",
                estimated_savings={
                    "mci_improvement": round(improvement * 0.003, 3),
                    "waste_diverted_kg": round(lca_input.quantity * improvement / 100, 2),
                    "circular_economy_benefit": "High"
                },
                implementation_difficulty="Medium"
            ))
        
        # Recommendation: Design for circularity
        if circularity_result.mci_score < 0.7:
            recommendations.append(RecommendationSchema(
                title="Implement Circular Design Principles",
                description=(
                    "Design products for longevity, repairability, and recyclability. "
                    "Use modular designs, avoid material mixing, and clearly label materials "
                    "for easier sorting at end-of-life."
                ),
                impact="High",
                category="Circularity",
                estimated_savings={
                    "mci_improvement": 0.15,
                    "product_lifespan_increase": "20-30%",
                    "long_term_impact": "Very High"
                },
                implementation_difficulty="Hard"
            ))
        
        return recommendations
    
    def _sort_by_priority(self, recommendations: List[RecommendationSchema]) -> List[RecommendationSchema]:
        """
        Sort recommendations by priority (impact and difficulty)
        
        Args:
            recommendations: List of recommendations
            
        Returns:
            Sorted list
        """
        # Priority scoring
        impact_scores = {"High": 3, "Medium": 2, "Low": 1}
        difficulty_scores = {"Easy": 3, "Medium": 2, "Hard": 1}
        
        def priority_score(rec):
            impact = impact_scores.get(rec.impact, 2)
            difficulty = difficulty_scores.get(rec.implementation_difficulty, 2)
            return impact * 2 + difficulty  # Weight impact more heavily
        
        return sorted(recommendations, key=priority_score, reverse=True)
    
    def _calculate_total_savings(self, recommendations: List[RecommendationSchema]) -> Dict[str, float]:
        """
        Calculate total estimated savings from all recommendations
        
        Args:
            recommendations: List of recommendations
            
        Returns:
            Total savings dictionary
        """
        total_co2 = 0
        total_energy = 0
        total_cost = 0
        
        for rec in recommendations:
            savings = rec.estimated_savings
            total_co2 += savings.get('co2_reduction', 0)
            total_energy += savings.get('energy_savings_mj', 0)
            total_cost += savings.get('cost_savings_annual', 0)
        
        return {
            "co2_reduction": round(total_co2, 2),
            "energy_savings": round(total_energy, 2),
            "cost_savings": round(total_cost, 2)
        }
    
    def _generate_priority_actions(self, top_recommendations: List[RecommendationSchema]) -> List[str]:
        """
        Generate concise priority action list
        
        Args:
            top_recommendations: Top 3 recommendations
            
        Returns:
            List of priority action strings
        """
        return [rec.title for rec in top_recommendations]


# Global recommendation engine instance
recommendation_engine = RecommendationEngine()
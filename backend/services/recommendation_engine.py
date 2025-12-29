"""
Recommendation Engine - MongoDB Integrated (FIXED)
Generates AI-powered sustainability recommendations with full tracking and analytics
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId

from models.schemas import (
    LCAInputSchema,
    LCAResultSchema,
    CircularityResultSchema,
    RecommendationSchema,
    RecommendationsResultSchema
)
from core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Smart recommendation engine with MongoDB integration
    - Generates sustainability recommendations
    - Tracks implementation progress
    - Analyzes prediction accuracy
    - Collects user feedback
    """
    
    def __init__(self, mongodb_uri: str = None, db_name: str = "sustainability_db"):
        """
        Initialize recommendation engine with MongoDB
        
        Args:
            mongodb_uri: MongoDB connection URI (defaults to settings.MONGODB_URI)
            db_name: Database name
        """
        try:
            # MongoDB setup
            self.mongodb_uri = mongodb_uri or getattr(settings, 'MONGODB_URI', 'mongodb://localhost:27017/')
            self.db_name = db_name
            self.client = MongoClient(self.mongodb_uri)
            self.db = self.client[self.db_name]
            
            # Collections
            self.recommendations_collection = self.db['recommendations']
            self.implementation_tracking = self.db['recommendation_implementations']
            self.recommendation_feedback = self.db['recommendation_feedback']
            
            # Create indexes for performance
            self._create_indexes()
            
            logger.info(f"Recommendation Engine initialized with MongoDB: {self.db_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB connection: {str(e)}")
            logger.info("Running in non-persistent mode (no MongoDB)")
            self.client = None
            self.db = None
    
    # ==================== HELPER METHOD (NEW) ====================
    
    @staticmethod
    def _get_value(field):
        """
        Safely extract value from field that might be Enum or string
        
        Args:
            field: Field that could be Enum or string
            
        Returns:
            String value
        """
        if hasattr(field, 'value'):
            return field.value
        return str(field)
    
    # ==================== REST OF THE CODE ====================
    
    def _create_indexes(self):
        """Create MongoDB indexes for efficient queries"""
        try:
            if not self.db:
                return
                
            # Recommendations collection
            self.recommendations_collection.create_index("recommendation_set_id", unique=True)
            self.recommendations_collection.create_index("project_name")
            self.recommendations_collection.create_index([("generated_at", DESCENDING)])
            self.recommendations_collection.create_index("category")
            self.recommendations_collection.create_index(
                [("project_name", ASCENDING), ("generated_at", DESCENDING)]
            )
            
            # Implementation tracking
            self.implementation_tracking.create_index("recommendation_id")
            self.implementation_tracking.create_index("project_name")
            self.implementation_tracking.create_index("status")
            self.implementation_tracking.create_index([("implemented_at", DESCENDING)])
            
            # Feedback collection
            self.recommendation_feedback.create_index("recommendation_id")
            self.recommendation_feedback.create_index("rating")
            
            logger.info("MongoDB indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Error creating indexes (may already exist): {str(e)}")
    
    def generate_recommendations(
        self,
        lca_input: LCAInputSchema,
        lca_result: LCAResultSchema,
        circularity_result: CircularityResultSchema = None,
        project_name: str = None,
        save_to_db: bool = True
    ) -> RecommendationsResultSchema:
        """
        Generate comprehensive sustainability recommendations
        
        Args:
            lca_input: LCA input parameters
            lca_result: LCA calculation results
            circularity_result: Optional circularity metrics
            project_name: Project identifier for tracking (required if save_to_db=True)
            save_to_db: Whether to save recommendations to MongoDB
            
        Returns:
            Complete recommendations with priority actions
        """
        try:
            logger.info("Generating recommendations...")
            
            recommendations = []
            
            # Generate recommendations by category
            recommendations.extend(self._generate_energy_recommendations(lca_input, lca_result))
            recommendations.extend(self._generate_material_recommendations(lca_input, lca_result))
            recommendations.extend(self._generate_transport_recommendations(lca_input, lca_result))
            recommendations.extend(self._generate_process_recommendations(lca_input, lca_result))
            
            # Add circularity recommendations if provided
            if circularity_result:
                recommendations.extend(
                    self._generate_circularity_recommendations(lca_input, circularity_result)
                )
            
            # Sort by priority (impact + ease of implementation)
            recommendations = self._sort_by_priority(recommendations)
            
            # Calculate total potential savings
            total_savings = self._calculate_total_savings(recommendations)
            
            # Generate top 3 priority actions
            priority_actions = self._generate_priority_actions(recommendations[:3])
            
            # Build result
            result = RecommendationsResultSchema(
                recommendations=recommendations,
                total_estimated_savings=total_savings,
                priority_actions=priority_actions
            )
            
            # Save to MongoDB if enabled
            recommendation_set_id = None
            if save_to_db and project_name and self.db:
                recommendation_set_id = self._save_recommendations(
                    project_name=project_name,
                    lca_input=lca_input,
                    lca_result=lca_result,
                    recommendations=result
                )
                logger.info(f"Recommendations saved: {recommendation_set_id}")
            elif save_to_db and not project_name:
                logger.warning("Cannot save to DB: project_name is required")
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return result
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise
    
    def _save_recommendations(
        self,
        project_name: str,
        lca_input: LCAInputSchema,
        lca_result: LCAResultSchema,
        recommendations: RecommendationsResultSchema
    ) -> str:
        """Save generated recommendations to MongoDB"""
        try:
            # Generate unique ID
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            recommendation_set_id = f"rec_{project_name.replace(' ', '_')}_{timestamp}"
            
            # Convert recommendations to dict format with unique IDs
            recs_list = []
            for i, rec in enumerate(recommendations.recommendations, 1):
                rec_dict = {
                    "recommendation_id": f"{recommendation_set_id}_item_{i}",
                    "title": rec.title,
                    "description": rec.description,
                    "impact": rec.impact,
                    "category": rec.category,
                    "estimated_savings": rec.estimated_savings,
                    "implementation_difficulty": rec.implementation_difficulty
                }
                recs_list.append(rec_dict)
            
            # Build document - FIXED: Use helper method
            document = {
                "recommendation_set_id": recommendation_set_id,
                "project_name": project_name,
                "generated_at": datetime.utcnow(),
                "lca_summary": {
                    "total_co2_emissions": lca_result.total_co2_emissions,
                    "co2_per_unit": lca_result.co2_per_unit,
                    "energy_consumption": lca_result.energy_consumption,
                    "water_usage": lca_result.water_usage,
                    "material": self._get_value(lca_input.material),
                    "quantity": lca_input.quantity,
                    "recycled_content": lca_input.recycled_content,
                    "energy_source": self._get_value(lca_input.energy_source)
                },
                "recommendations": recs_list,
                "total_estimated_savings": recommendations.total_estimated_savings,
                "priority_actions": recommendations.priority_actions,
                "recommendation_count": len(recs_list),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert into MongoDB
            self.recommendations_collection.insert_one(document)
            logger.info(f"Recommendations saved successfully: {recommendation_set_id}")
            
            return recommendation_set_id
            
        except Exception as e:
            logger.error(f"Error saving recommendations to MongoDB: {str(e)}")
            raise
    
    # ==================== QUERY METHODS ====================
    
    def get_recommendations_by_project(
        self,
        project_name: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recommendation history for a project"""
        try:
            if not self.db:
                logger.warning("MongoDB not available")
                return []
            
            recommendations = list(
                self.recommendations_collection
                .find({"project_name": project_name})
                .sort("generated_at", DESCENDING)
                .limit(limit)
            )
            
            for rec in recommendations:
                rec['_id'] = str(rec['_id'])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error retrieving recommendations: {str(e)}")
            return []
    
    def get_recommendation_by_id(
        self,
        recommendation_set_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get specific recommendation set by ID"""
        try:
            if not self.db:
                return None
            
            rec = self.recommendations_collection.find_one(
                {"recommendation_set_id": recommendation_set_id}
            )
            
            if rec:
                rec['_id'] = str(rec['_id'])
            
            return rec
            
        except Exception as e:
            logger.error(f"Error retrieving recommendation: {str(e)}")
            return None
    
    # ==================== IMPLEMENTATION TRACKING ====================
    
    def mark_recommendation_implemented(
        self,
        recommendation_id: str,
        project_name: str,
        actual_savings: Dict[str, float] = None,
        implementation_notes: str = None,
        status: str = "implemented"
    ) -> bool:
        """Track recommendation implementation"""
        try:
            if not self.db:
                logger.warning("MongoDB not available")
                return False
            
            implementation_doc = {
                "recommendation_id": recommendation_id,
                "project_name": project_name,
                "status": status,
                "implemented_at": datetime.utcnow(),
                "actual_savings": actual_savings or {},
                "implementation_notes": implementation_notes,
                "created_at": datetime.utcnow()
            }
            
            self.implementation_tracking.insert_one(implementation_doc)
            logger.info(f"Implementation tracked: {recommendation_id} - {status}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error marking recommendation: {str(e)}")
            return False
    
    def get_implementation_status(
        self,
        project_name: str = None,
        status: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get implementation status"""
        try:
            if not self.db:
                return []
            
            query = {}
            if project_name:
                query['project_name'] = project_name
            if status:
                query['status'] = status
            
            implementations = list(
                self.implementation_tracking
                .find(query)
                .sort("implemented_at", DESCENDING)
                .limit(limit)
            )
            
            for impl in implementations:
                impl['_id'] = str(impl['_id'])
            
            return implementations
            
        except Exception as e:
            logger.error(f"Error retrieving implementation status: {str(e)}")
            return []
    
    # ==================== FEEDBACK COLLECTION ====================
    
    def add_recommendation_feedback(
        self,
        recommendation_id: str,
        rating: int,
        feedback_text: str = None,
        was_useful: bool = None
    ) -> bool:
        """Collect user feedback on recommendations"""
        try:
            if not self.db:
                return False
            
            if not 1 <= rating <= 5:
                logger.warning(f"Invalid rating: {rating}. Must be 1-5")
                return False
            
            feedback_doc = {
                "recommendation_id": recommendation_id,
                "rating": rating,
                "feedback_text": feedback_text,
                "was_useful": was_useful,
                "created_at": datetime.utcnow()
            }
            
            self.recommendation_feedback.insert_one(feedback_doc)
            logger.info(f"Feedback added for: {recommendation_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding feedback: {str(e)}")
            return False
    
    # ==================== ANALYTICS ====================
    
    def get_recommendation_analytics(
        self,
        project_name: str = None,
        days: int = 90
    ) -> Dict[str, Any]:
        """Get comprehensive recommendation analytics"""
        try:
            if not self.db:
                return {"error": "MongoDB not available"}
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = {"generated_at": {"$gte": cutoff_date}}
            if project_name:
                query['project_name'] = project_name
            
            total_sets = self.recommendations_collection.count_documents(query)
            
            category_pipeline = [
                {"$match": query},
                {"$unwind": "$recommendations"},
                {"$group": {
                    "_id": "$recommendations.category",
                    "count": {"$sum": 1},
                    "avg_estimated_co2_savings": {
                        "$avg": "$recommendations.estimated_savings.co2_reduction"
                    }
                }},
                {"$sort": {"count": -1}}
            ]
            category_stats = list(
                self.recommendations_collection.aggregate(category_pipeline)
            )
            
            impl_query = {"implemented_at": {"$gte": cutoff_date}}
            if project_name:
                impl_query['project_name'] = project_name
            
            total_implementations = self.implementation_tracking.count_documents(impl_query)
            implemented_count = self.implementation_tracking.count_documents(
                {**impl_query, "status": "implemented"}
            )
            
            feedback_pipeline = [
                {"$match": {"created_at": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": None,
                    "avg_rating": {"$avg": "$rating"},
                    "total_feedback": {"$sum": 1}
                }}
            ]
            feedback_stats = list(
                self.recommendation_feedback.aggregate(feedback_pipeline)
            )
            
            avg_rating = None
            total_feedback = 0
            if feedback_stats:
                avg_rating = round(feedback_stats[0]['avg_rating'], 2)
                total_feedback = feedback_stats[0]['total_feedback']
            
            common_pipeline = [
                {"$match": query},
                {"$unwind": "$recommendations"},
                {"$group": {
                    "_id": "$recommendations.title",
                    "count": {"$sum": 1},
                    "avg_impact": {"$first": "$recommendations.impact"}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            common_recommendations = list(
                self.recommendations_collection.aggregate(common_pipeline)
            )
            
            analytics = {
                "period_days": days,
                "project_name": project_name,
                "total_recommendation_sets": total_sets,
                "total_implementations": total_implementations,
                "implemented_count": implemented_count,
                "implementation_rate": round(
                    (implemented_count / total_implementations * 100) 
                    if total_implementations > 0 else 0, 
                    1
                ),
                "category_breakdown": category_stats,
                "average_rating": avg_rating,
                "total_feedback": total_feedback,
                "most_common_recommendations": common_recommendations
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating analytics: {str(e)}")
            return {"error": str(e)}
    
    def compare_estimated_vs_actual(
        self,
        project_name: str = None
    ) -> Dict[str, Any]:
        """Compare estimated vs actual savings for accuracy analysis"""
        try:
            if not self.db:
                return {"error": "MongoDB not available"}
            
            query = {
                "actual_savings": {"$exists": True, "$ne": {}},
                "status": "implemented"
            }
            if project_name:
                query['project_name'] = project_name
            
            implementations = list(self.implementation_tracking.find(query))
            
            if not implementations:
                return {
                    "message": "No implementation data with actual savings available",
                    "project_name": project_name
                }
            
            total_estimated = 0
            total_actual = 0
            comparisons = []
            
            for impl in implementations:
                rec_id = impl['recommendation_id']
                
                parts = rec_id.split('_item_')
                if len(parts) != 2:
                    continue
                    
                set_id = parts[0]
                
                rec_set = self.recommendations_collection.find_one(
                    {"recommendation_set_id": set_id}
                )
                
                if not rec_set:
                    continue
                
                matching_rec = None
                for rec in rec_set.get('recommendations', []):
                    if rec.get('recommendation_id') == rec_id:
                        matching_rec = rec
                        break
                
                if not matching_rec:
                    continue
                
                estimated = matching_rec.get('estimated_savings', {}).get('co2_reduction', 0)
                actual = impl.get('actual_savings', {}).get('co2_reduction', 0)
                
                if estimated > 0:
                    total_estimated += estimated
                    total_actual += actual
                    
                    accuracy = round((actual / estimated * 100), 1) if estimated > 0 else None
                    
                    comparisons.append({
                        "recommendation": matching_rec['title'],
                        "category": matching_rec.get('category'),
                        "estimated_co2_reduction": round(estimated, 2),
                        "actual_co2_reduction": round(actual, 2),
                        "difference": round(actual - estimated, 2),
                        "accuracy_percent": accuracy
                    })
            
            overall_accuracy = None
            if total_estimated > 0:
                overall_accuracy = round((total_actual / total_estimated * 100), 1)
            
            return {
                "total_implementations_analyzed": len(comparisons),
                "total_estimated_savings": round(total_estimated, 2),
                "total_actual_savings": round(total_actual, 2),
                "overall_accuracy_percent": overall_accuracy,
                "comparisons": comparisons,
                "project_name": project_name
            }
            
        except Exception as e:
            logger.error(f"Error comparing savings: {str(e)}")
            return {"error": str(e)}
    
    # ==================== RECOMMENDATION GENERATION METHODS ====================
    
    def _generate_energy_recommendations(
        self,
        lca_input: LCAInputSchema,
        lca_result: LCAResultSchema
    ) -> List[RecommendationSchema]:
        """Generate energy-related recommendations"""
        recommendations = []
        
        # FIXED: Use helper method
        energy_source = self._get_value(lca_input.energy_source)
        
        if energy_source != 'renewable':
            current_emissions = lca_result.breakdown.production
            potential_reduction = current_emissions * 0.7
            
            recommendations.append(RecommendationSchema(
                title="Switch to Renewable Energy Sources",
                description=(
                    f"Transitioning from {energy_source} to renewable energy "
                    f"(solar, wind, hydro) can significantly reduce your carbon footprint. "
                    f"This is one of the most impactful changes you can make."
                ),
                impact="High",
                category="Energy",
                estimated_savings={
                    "co2_reduction": round(potential_reduction, 2),
                    "percentage_reduction": 70.0,
                    "cost_savings_annual": round(potential_reduction * 50, 2)
                },
                implementation_difficulty="Medium"
            ))
        
        if lca_result.energy_consumption > lca_input.quantity * 50:
            energy_reduction = lca_result.energy_consumption * 0.15
            co2_reduction = energy_reduction * 0.05
            
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
                    "cost_savings_annual": round(energy_reduction * 0.02, 2)
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
        
        # FIXED: Use helper method
        material = self._get_value(lca_input.material)
        production_type = self._get_value(lca_input.production_type)
        
        if lca_input.recycled_content < 75:
            target_content = min(90, lca_input.recycled_content + 20)
            improvement = target_content - lca_input.recycled_content
            
            extraction_reduction = lca_result.breakdown.raw_material_extraction * (improvement / 100) * 0.8
            production_reduction = lca_result.breakdown.production * (improvement / 100) * 0.5
            total_reduction = extraction_reduction + production_reduction
            
            recommendations.append(RecommendationSchema(
                title=f"Increase Recycled Content to {target_content}%",
                description=(
                    f"Increasing recycled content from {lca_input.recycled_content}% to {target_content}% "
                    f"will significantly reduce the need for virgin material extraction and processing. "
                    f"This is especially effective for {material}."
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
        
        if material in ['aluminium', 'aluminum'] and production_type == 'primary':
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
        
        # FIXED: Use helper method
        transport_mode = self._get_value(lca_input.transport_mode)
        
        if lca_input.transport_distance > 500:
            if transport_mode == 'truck':
                potential_reduction = lca_result.breakdown.transport * 0.6
                
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
        """Sort recommendations by priority"""
        impact_scores = {"High": 3, "Medium": 2, "Low": 1}
        difficulty_scores = {"Easy": 3, "Medium": 2, "Hard": 1}
        
        def priority_score(rec):
            impact = impact_scores.get(rec.impact, 2)
            difficulty = difficulty_scores.get(rec.implementation_difficulty, 2)
            return impact * 2 + difficulty
        
        return sorted(recommendations, key=priority_score, reverse=True)
    
    def _calculate_total_savings(self, recommendations: List[RecommendationSchema]) -> Dict[str, float]:
        """Calculate total estimated savings"""
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
        """Generate priority action list"""
        return [rec.title for rec in top_recommendations]
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global recommendation engine instance
recommendation_engine = RecommendationEngine()
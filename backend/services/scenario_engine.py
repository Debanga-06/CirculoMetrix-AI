"""
What-If Scenario Analysis Engine - MongoDB Integrated
Enables users to test different scenarios, compare impacts, and track analysis history
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from copy import deepcopy

from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId

from models.schemas import (
    LCAInputSchema,
    LCAResultSchema,
    WhatIfScenarioSchema,
    WhatIfResultSchema
)
from services.lca_engine import lca_engine

# Configure logging
logger = logging.getLogger(__name__)


class ScenarioEngine:
    """
    What-if scenario analysis engine with MongoDB tracking
    - Test different production scenarios
    - Compare environmental impacts
    - Track scenario analysis history
    - Share successful scenarios
    """
    
    def __init__(self, mongodb_uri: str = None, db_name: str = "sustainability_db"):
        """
        Initialize scenario engine with MongoDB
        
        Args:
            mongodb_uri: MongoDB connection URI
            db_name: Database name
        """
        try:
            # MongoDB setup
            from core.config import settings
            self.mongodb_uri = mongodb_uri or getattr(settings, 'MONGODB_URI', 'mongodb://localhost:27017/')
            self.db_name = db_name
            self.client = MongoClient(self.mongodb_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.db_name]
            
            # Test connection
            self.client.server_info()
            
            # Collections
            self.scenarios_collection = self.db['scenario_analyses']
            self.custom_scenarios = self.db['custom_scenarios']
            self.scenario_comparisons = self.db['scenario_comparisons']
            
            # Create indexes
            self._create_indexes()
            
            logger.info(f"Scenario Engine initialized with MongoDB: {self.db_name}")
            
        except Exception as e:
            logger.warning(f"MongoDB not available: {str(e)}. Running without persistence.")
            self.client = None
            self.db = None
        
        # Load predefined scenarios
        self.predefined_scenarios = self._load_predefined_scenarios()
    
    def _create_indexes(self):
        """Create MongoDB indexes for efficient queries"""
        try:
            if not self.db:
                return
            
            # Scenario analyses
            self.scenarios_collection.create_index("scenario_id", unique=True)
            self.scenarios_collection.create_index("project_name")
            self.scenarios_collection.create_index([("analyzed_at", DESCENDING)])
            self.scenarios_collection.create_index("scenario_type")
            self.scenarios_collection.create_index([("project_name", ASCENDING), ("analyzed_at", DESCENDING)])
            
            # Custom scenarios
            self.custom_scenarios.create_index("scenario_key", unique=True)
            self.custom_scenarios.create_index("created_by")
            self.custom_scenarios.create_index("is_public")
            
            # Comparisons
            self.scenario_comparisons.create_index("comparison_id", unique=True)
            self.scenario_comparisons.create_index("project_name")
            
            logger.info("Scenario indexes created successfully")
            
        except Exception as e:
            logger.debug(f"Index creation info: {str(e)}")
    
    def _load_predefined_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined scenario templates"""
        return {
            "increase_recycled_content": {
                "name": "Increase Recycled Content to 90%",
                "description": "See the impact of using 90% recycled materials",
                "changes": {
                    "recycled_content": 90,
                    "production_type": "secondary"
                }
            },
            "switch_renewable_energy": {
                "name": "Switch to 100% Renewable Energy",
                "description": "Calculate savings from using renewable energy sources",
                "changes": {
                    "energy_source": "renewable"
                }
            },
            "optimize_transport": {
                "name": "Optimize Transportation",
                "description": "Reduce transport distance by 50% and use rail",
                "changes": {
                    "transport_distance": "multiply:0.5",
                    "transport_mode": "rail"
                }
            },
            "best_case": {
                "name": "Best Case Scenario",
                "description": "Combine all sustainability best practices",
                "changes": {
                    "recycled_content": 95,
                    "production_type": "secondary",
                    "energy_source": "renewable",
                    "transport_distance": "multiply:0.3",
                    "transport_mode": "rail",
                    "end_of_life_recycling_rate": 95
                }
            },
            "circular_economy": {
                "name": "Full Circular Economy Model",
                "description": "Maximum circularity with closed-loop recycling",
                "changes": {
                    "recycled_content": 100,
                    "production_type": "secondary",
                    "energy_source": "renewable",
                    "transport_distance": "multiply:0.2",
                    "end_of_life_recycling_rate": 98
                }
            }
        }
    
    def analyze_scenario(
        self,
        base_input: LCAInputSchema,
        scenario_changes: Dict[str, Any],
        scenario_name: str = "Custom Scenario",
        project_name: str = None,
        save_to_db: bool = True
    ) -> WhatIfResultSchema:
        """
        Analyze a what-if scenario
        
        Args:
            base_input: Base case input parameters
            scenario_changes: Parameters to change
            scenario_name: Name of the scenario
            project_name: Project identifier for tracking
            save_to_db: Whether to save to MongoDB
            
        Returns:
            Scenario analysis results
        """
        try:
            logger.info(f"Analyzing scenario: {scenario_name}")
            
            # Calculate base case
            base_result = lca_engine.calculate_lca(base_input)
            
            # Apply changes to create scenario
            scenario_input = self._apply_changes(base_input, scenario_changes)
            
            # Calculate scenario case
            scenario_result = lca_engine.calculate_lca(scenario_input)
            
            # Calculate improvements
            improvements = self._calculate_improvements(base_result, scenario_result)
            
            result = WhatIfResultSchema(
                scenario_name=scenario_name,
                base_case=base_result,
                scenario_case=scenario_result,
                improvements=improvements
            )
            
            # Save to MongoDB
            if save_to_db and project_name and self.db:
                self._save_scenario_analysis(
                    project_name=project_name,
                    scenario_name=scenario_name,
                    base_input=base_input,
                    scenario_changes=scenario_changes,
                    result=result
                )
            
            logger.info(f"Scenario analysis completed: {improvements['co2_reduction']}% CO2 reduction")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing scenario: {str(e)}")
            raise
    
    def _save_scenario_analysis(
        self,
        project_name: str,
        scenario_name: str,
        base_input: LCAInputSchema,
        scenario_changes: Dict[str, Any],
        result: WhatIfResultSchema
    ) -> str:
        """Save scenario analysis to MongoDB"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            scenario_id = f"scenario_{project_name.replace(' ', '_')}_{timestamp}"
            
            document = {
                "scenario_id": scenario_id,
                "project_name": project_name,
                "scenario_name": scenario_name,
                "scenario_type": self._get_scenario_type(scenario_name),
                "analyzed_at": datetime.utcnow(),
                "base_input": base_input.dict(),
                "scenario_changes": scenario_changes,
                "base_case_summary": {
                    "total_co2_emissions": result.base_case.total_co2_emissions,
                    "energy_consumption": result.base_case.energy_consumption,
                    "water_usage": result.base_case.water_usage
                },
                "scenario_case_summary": {
                    "total_co2_emissions": result.scenario_case.total_co2_emissions,
                    "energy_consumption": result.scenario_case.energy_consumption,
                    "water_usage": result.scenario_case.water_usage
                },
                "improvements": result.improvements,
                "created_at": datetime.utcnow()
            }
            
            self.scenarios_collection.insert_one(document)
            logger.info(f"Scenario analysis saved: {scenario_id}")
            return scenario_id
            
        except Exception as e:
            logger.error(f"Error saving scenario: {str(e)}")
            return None
    
    def _get_scenario_type(self, scenario_name: str) -> str:
        """Determine scenario type from name"""
        name_lower = scenario_name.lower()
        if "energy" in name_lower or "renewable" in name_lower:
            return "energy"
        elif "recycled" in name_lower or "material" in name_lower:
            return "material"
        elif "transport" in name_lower:
            return "transport"
        elif "circular" in name_lower:
            return "circularity"
        elif "best" in name_lower or "optimal" in name_lower:
            return "optimization"
        else:
            return "custom"
    
    def _apply_changes(
        self,
        base_input: LCAInputSchema,
        changes: Dict[str, Any]
    ) -> LCAInputSchema:
        """Apply changes to base input to create scenario"""
        scenario_dict = base_input.dict()
        
        for key, value in changes.items():
            if key in scenario_dict:
                # Handle special operations
                if isinstance(value, str) and value.startswith("multiply:"):
                    multiplier = float(value.split(":")[1])
                    scenario_dict[key] = scenario_dict[key] * multiplier
                elif isinstance(value, str) and value.startswith("add:"):
                    addition = float(value.split(":")[1])
                    scenario_dict[key] = scenario_dict[key] + addition
                else:
                    scenario_dict[key] = value
        
        return LCAInputSchema(**scenario_dict)
    
    def _calculate_improvements(
        self,
        base_result: LCAResultSchema,
        scenario_result: LCAResultSchema
    ) -> Dict[str, float]:
        """Calculate improvements between base and scenario"""
        improvements = {}
        
        # CO2 reduction
        if base_result.total_co2_emissions > 0:
            co2_reduction = (
                (base_result.total_co2_emissions - scenario_result.total_co2_emissions) /
                base_result.total_co2_emissions * 100
            )
            improvements["co2_reduction"] = round(co2_reduction, 2)
            improvements["co2_absolute_reduction"] = round(
                base_result.total_co2_emissions - scenario_result.total_co2_emissions, 2
            )
        
        # Energy savings
        if base_result.energy_consumption > 0:
            energy_savings = (
                (base_result.energy_consumption - scenario_result.energy_consumption) /
                base_result.energy_consumption * 100
            )
            improvements["energy_savings"] = round(energy_savings, 2)
            improvements["energy_absolute_savings"] = round(
                base_result.energy_consumption - scenario_result.energy_consumption, 2
            )
        
        # Water savings
        if base_result.water_usage > 0:
            water_savings = (
                (base_result.water_usage - scenario_result.water_usage) /
                base_result.water_usage * 100
            )
            improvements["water_savings"] = round(water_savings, 2)
            improvements["water_absolute_savings"] = round(
                base_result.water_usage - scenario_result.water_usage, 2
            )
        
        # Breakdown improvements
        breakdown_improvements = {}
        if base_result.breakdown.raw_material_extraction > 0:
            extraction_reduction = (
                (base_result.breakdown.raw_material_extraction - 
                 scenario_result.breakdown.raw_material_extraction) /
                base_result.breakdown.raw_material_extraction * 100
            )
            breakdown_improvements["extraction"] = round(extraction_reduction, 2)
        
        if base_result.breakdown.production > 0:
            production_reduction = (
                (base_result.breakdown.production - scenario_result.breakdown.production) /
                base_result.breakdown.production * 100
            )
            breakdown_improvements["production"] = round(production_reduction, 2)
        
        if base_result.breakdown.transport > 0:
            transport_reduction = (
                (base_result.breakdown.transport - scenario_result.breakdown.transport) /
                base_result.breakdown.transport * 100
            )
            breakdown_improvements["transport"] = round(transport_reduction, 2)
        
        improvements["breakdown_improvements"] = breakdown_improvements
        
        return improvements
    
    # ==================== QUERY & ANALYTICS METHODS ====================
    
    def get_scenario_history(
        self,
        project_name: str = None,
        scenario_type: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get scenario analysis history
        
        Args:
            project_name: Filter by project (optional)
            scenario_type: Filter by type (optional)
            limit: Maximum results
            
        Returns:
            List of scenario analyses
        """
        if not self.db:
            return []
        
        try:
            query = {}
            if project_name:
                query['project_name'] = project_name
            if scenario_type:
                query['scenario_type'] = scenario_type
            
            scenarios = list(
                self.scenarios_collection
                .find(query)
                .sort("analyzed_at", DESCENDING)
                .limit(limit)
            )
            
            for scenario in scenarios:
                scenario['_id'] = str(scenario['_id'])
            
            return scenarios
            
        except Exception as e:
            logger.error(f"Error retrieving scenario history: {str(e)}")
            return []
    
    def get_scenario_analytics(
        self,
        project_name: str = None,
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Get scenario usage analytics
        
        Args:
            project_name: Filter by project (optional)
            days: Time period to analyze
            
        Returns:
            Analytics dictionary
        """
        if not self.db:
            return {"error": "MongoDB not available"}
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = {"analyzed_at": {"$gte": cutoff_date}}
            if project_name:
                query['project_name'] = project_name
            
            # Total scenarios analyzed
            total_scenarios = self.scenarios_collection.count_documents(query)
            
            # Scenario type breakdown
            type_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$scenario_type",
                    "count": {"$sum": 1},
                    "avg_co2_reduction": {"$avg": "$improvements.co2_reduction"},
                    "avg_energy_savings": {"$avg": "$improvements.energy_savings"}
                }},
                {"$sort": {"count": -1}}
            ]
            type_breakdown = list(self.scenarios_collection.aggregate(type_pipeline))
            
            # Most popular scenarios
            popular_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$scenario_name",
                    "count": {"$sum": 1},
                    "avg_improvement": {"$avg": "$improvements.co2_reduction"}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            popular_scenarios = list(self.scenarios_collection.aggregate(popular_pipeline))
            
            # Best performing scenarios
            best_pipeline = [
                {"$match": query},
                {"$sort": {"improvements.co2_reduction": -1}},
                {"$limit": 5},
                {"$project": {
                    "scenario_name": 1,
                    "co2_reduction": "$improvements.co2_reduction",
                    "scenario_type": 1
                }}
            ]
            best_scenarios = list(self.scenarios_collection.aggregate(best_pipeline))
            
            # Average improvements
            avg_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": None,
                    "avg_co2_reduction": {"$avg": "$improvements.co2_reduction"},
                    "avg_energy_savings": {"$avg": "$improvements.energy_savings"},
                    "avg_water_savings": {"$avg": "$improvements.water_savings"}
                }}
            ]
            avg_stats = list(self.scenarios_collection.aggregate(avg_pipeline))
            
            analytics = {
                "period_days": days,
                "project_name": project_name,
                "total_scenarios_analyzed": total_scenarios,
                "scenario_type_breakdown": type_breakdown,
                "most_popular_scenarios": popular_scenarios,
                "best_performing_scenarios": best_scenarios,
                "average_improvements": avg_stats[0] if avg_stats else {}
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating analytics: {str(e)}")
            return {"error": str(e)}
    
    def get_best_scenarios_for_goal(
        self,
        goal: str,
        project_name: str = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get best historical scenarios for a specific goal
        
        Args:
            goal: Goal (minimize_co2, minimize_energy, minimize_water)
            project_name: Filter by project (optional)
            limit: Maximum results
            
        Returns:
            List of best scenarios
        """
        if not self.db:
            return []
        
        try:
            query = {}
            if project_name:
                query['project_name'] = project_name
            
            # Determine sort field
            if goal == "minimize_co2":
                sort_field = "improvements.co2_reduction"
            elif goal == "minimize_energy":
                sort_field = "improvements.energy_savings"
            elif goal == "minimize_water":
                sort_field = "improvements.water_savings"
            else:
                sort_field = "improvements.co2_reduction"
            
            scenarios = list(
                self.scenarios_collection
                .find(query)
                .sort(sort_field, DESCENDING)
                .limit(limit)
            )
            
            for scenario in scenarios:
                scenario['_id'] = str(scenario['_id'])
            
            return scenarios
            
        except Exception as e:
            logger.error(f"Error retrieving best scenarios: {str(e)}")
            return []
    
    # ==================== CUSTOM SCENARIOS ====================
    
    def save_custom_scenario(
        self,
        scenario_key: str,
        scenario_name: str,
        description: str,
        changes: Dict[str, Any],
        created_by: str = None,
        is_public: bool = False,
        tags: List[str] = None
    ) -> bool:
        """
        Save a custom scenario template
        
        Args:
            scenario_key: Unique identifier
            scenario_name: Display name
            description: Description
            changes: Parameter changes
            created_by: Creator identifier
            is_public: Whether scenario is public
            tags: Category tags
            
        Returns:
            Success status
        """
        if not self.db:
            logger.warning("MongoDB not available")
            return False
        
        try:
            document = {
                "scenario_key": scenario_key,
                "name": scenario_name,
                "description": description,
                "changes": changes,
                "created_by": created_by,
                "is_public": is_public,
                "tags": tags or [],
                "usage_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Upsert (update if exists, insert if not)
            self.custom_scenarios.update_one(
                {"scenario_key": scenario_key},
                {"$set": document},
                upsert=True
            )
            
            logger.info(f"Custom scenario saved: {scenario_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving custom scenario: {str(e)}")
            return False
    
    def get_custom_scenarios(
        self,
        created_by: str = None,
        is_public: bool = None,
        tags: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get custom scenarios
        
        Args:
            created_by: Filter by creator (optional)
            is_public: Filter by visibility (optional)
            tags: Filter by tags (optional)
            
        Returns:
            List of custom scenarios
        """
        if not self.db:
            return []
        
        try:
            query = {}
            if created_by:
                query['created_by'] = created_by
            if is_public is not None:
                query['is_public'] = is_public
            if tags:
                query['tags'] = {"$in": tags}
            
            scenarios = list(
                self.custom_scenarios
                .find(query)
                .sort("usage_count", DESCENDING)
            )
            
            for scenario in scenarios:
                scenario['_id'] = str(scenario['_id'])
            
            return scenarios
            
        except Exception as e:
            logger.error(f"Error retrieving custom scenarios: {str(e)}")
            return []
    
    def increment_scenario_usage(self, scenario_key: str) -> bool:
        """Increment usage count for a scenario"""
        if not self.db:
            return False
        
        try:
            self.custom_scenarios.update_one(
                {"scenario_key": scenario_key},
                {"$inc": {"usage_count": 1}}
            )
            return True
        except Exception as e:
            logger.error(f"Error incrementing usage: {str(e)}")
            return False
    
    # ==================== ORIGINAL METHODS (Enhanced) ====================
    
    def compare_multiple_scenarios(
        self,
        base_input: LCAInputSchema,
        scenarios: List[Dict[str, Any]],
        project_name: str = None,
        save_to_db: bool = True
    ) -> List[WhatIfResultSchema]:
        """
        Compare multiple scenarios at once
        
        Args:
            base_input: Base case input
            scenarios: List of scenario configurations
            project_name: Project identifier
            save_to_db: Whether to save comparison
            
        Returns:
            List of scenario results
        """
        results = []
        
        for scenario in scenarios:
            scenario_name = scenario.get("name", "Unnamed Scenario")
            scenario_changes = scenario.get("changes", {})
            
            result = self.analyze_scenario(
                base_input, 
                scenario_changes, 
                scenario_name,
                project_name=project_name,
                save_to_db=save_to_db
            )
            results.append(result)
        
        # Save comparison summary
        if save_to_db and project_name and self.db:
            self._save_comparison(project_name, results)
        
        return results
    
    def _save_comparison(self, project_name: str, results: List[WhatIfResultSchema]) -> str:
        """Save scenario comparison to MongoDB"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            comparison_id = f"comp_{project_name.replace(' ', '_')}_{timestamp}"
            
            scenarios_summary = [
                {
                    "scenario_name": r.scenario_name,
                    "co2_emissions": r.scenario_case.total_co2_emissions,
                    "co2_reduction": r.improvements.get("co2_reduction", 0),
                    "energy_consumption": r.scenario_case.energy_consumption,
                    "energy_savings": r.improvements.get("energy_savings", 0)
                }
                for r in results
            ]
            
            document = {
                "comparison_id": comparison_id,
                "project_name": project_name,
                "scenarios_count": len(results),
                "scenarios": scenarios_summary,
                "created_at": datetime.utcnow()
            }
            
            self.scenario_comparisons.insert_one(document)
            logger.info(f"Comparison saved: {comparison_id}")
            return comparison_id
            
        except Exception as e:
            logger.error(f"Error saving comparison: {str(e)}")
            return None
    
    def get_predefined_scenario(self, scenario_key: str) -> Optional[Dict[str, Any]]:
        """Get a predefined scenario by key"""
        scenario = self.predefined_scenarios.get(scenario_key)
        
        # Check custom scenarios too
        if not scenario and self.db:
            try:
                custom = self.custom_scenarios.find_one({"scenario_key": scenario_key})
                if custom:
                    custom['_id'] = str(custom['_id'])
                    self.increment_scenario_usage(scenario_key)
                    return custom
            except Exception as e:
                logger.error(f"Error retrieving custom scenario: {str(e)}")
        
        return scenario
    
    def list_predefined_scenarios(self) -> List[Dict[str, Any]]:
        """List all available predefined scenarios"""
        scenarios = []
        
        # Add built-in scenarios
        for key, scenario in self.predefined_scenarios.items():
            scenarios.append({
                "key": key,
                "name": scenario["name"],
                "description": scenario["description"],
                "type": "predefined"
            })
        
        # Add public custom scenarios
        if self.db:
            try:
                custom_scenarios = self.get_custom_scenarios(is_public=True)
                for custom in custom_scenarios:
                    scenarios.append({
                        "key": custom['scenario_key'],
                        "name": custom['name'],
                        "description": custom['description'],
                        "type": "custom",
                        "usage_count": custom.get('usage_count', 0)
                    })
            except Exception as e:
                logger.error(f"Error retrieving custom scenarios: {str(e)}")
        
        return scenarios
    
    def sensitivity_analysis(
        self,
        base_input: LCAInputSchema,
        parameter: str,
        values: List[Any],
        project_name: str = None
    ) -> Dict[str, Any]:
        """Perform sensitivity analysis on a single parameter"""
        results = []
        
        for value in values:
            changes = {parameter: value}
            scenario_name = f"{parameter} = {value}"
            
            result = self.analyze_scenario(
                base_input, 
                changes, 
                scenario_name,
                project_name=project_name,
                save_to_db=False  # Don't save individual sensitivity tests
            )
            
            results.append({
                "parameter_value": value,
                "co2_emissions": result.scenario_case.total_co2_emissions,
                "energy_consumption": result.scenario_case.energy_consumption,
                "water_usage": result.scenario_case.water_usage,
                "improvements": result.improvements
            })
        
        return {
            "parameter": parameter,
            "base_value": getattr(base_input, parameter, None),
            "tested_values": values,
            "results": results
        }
    
    def optimize_parameters(
        self,
        base_input: LCAInputSchema,
        optimization_goal: str = "minimize_co2",
        project_name: str = None
    ) -> Dict[str, Any]:
        """Suggest optimal parameter values based on goal"""
        suggestions = {}
        
        if optimization_goal == "minimize_co2":
            suggestions = {
                "recycled_content": 95,
                "production_type": "secondary",
                "energy_source": "renewable",
                "transport_mode": "rail" if base_input.transport_distance > 500 else base_input.transport_mode.value,
                "end_of_life_recycling_rate": 95
            }
        elif optimization_goal == "minimize_energy":
            suggestions = {
                "recycled_content": 90,
                "production_type": "secondary",
                "energy_source": "renewable"
            }
        elif optimization_goal == "maximize_circularity":
            suggestions = {
                "recycled_content": 100,
                "production_type": "secondary",
                "end_of_life_recycling_rate": 98,
                "transport_distance": base_input.transport_distance * 0.5
            }
        
        # Analyze optimized scenario
        optimized_result = self.analyze_scenario(
            base_input,
            suggestions,
            f"Optimized for {optimization_goal}",
            project_name=project_name,
            save_to_db=True
        )
        
        return {
            "optimization_goal": optimization_goal,
            "suggested_changes": suggestions,
            "expected_improvements": optimized_result.improvements,
            "optimized_results": optimized_result
        }
    
    def generate_scenario_summary(
        self,
        results: List[WhatIfResultSchema]
    ) -> Dict[str, Any]:
        """Generate summary comparing all analyzed scenarios"""
        if not results:
            return {"error": "No scenarios to summarize"}
        
        best_co2 = min(results, key=lambda r: r.scenario_case.total_co2_emissions)
        best_energy = min(results, key=lambda r: r.scenario_case.energy_consumption)
        best_water = min(results, key=lambda r: r.scenario_case.water_usage)
        
        avg_co2_reduction = sum(r.improvements.get("co2_reduction", 0) for r in results) / len(results)
        avg_energy_savings = sum(r.improvements.get("energy_savings", 0) for r in results) / len(results)
        
        return {
            "scenarios_analyzed": len(results),
            "best_for_co2": {
                "scenario": best_co2.scenario_name,
                "co2_emissions": best_co2.scenario_case.total_co2_emissions,
                "reduction": best_co2.improvements.get("co2_reduction", 0)
            },
            "best_for_energy": {
                "scenario": best_energy.scenario_name,
                "energy_consumption": best_energy.scenario_case.energy_consumption,
                "savings": best_energy.improvements.get("energy_savings", 0)
            },
            "best_for_water": {
                "scenario": best_water.scenario_name,
                "water_usage": best_water.scenario_case.water_usage,
                "savings": best_water.improvements.get("water_savings", 0)
            },
            "average_improvements": {
                "co2_reduction": round(avg_co2_reduction, 2),
                "energy_savings": round(avg_energy_savings, 2)
            }
        }
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global scenario engine instance
scenario_engine = ScenarioEngine()
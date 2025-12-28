"""
What-If Scenario Analysis Engine
Enables users to test different scenarios and compare environmental impacts
"""

from typing import Dict, Any, List, Optional
import logging
from copy import deepcopy

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
    What-if scenario analysis engine
    Allows testing of different production parameters and their impacts
    """
    
    def __init__(self):
        """Initialize scenario engine"""
        self.predefined_scenarios = self._load_predefined_scenarios()
        logger.info("Scenario Engine initialized successfully")
    
    def _load_predefined_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """
        Load predefined scenario templates
        
        Returns:
            Dictionary of scenario templates
        """
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
        scenario_name: str = "Custom Scenario"
    ) -> WhatIfResultSchema:
        """
        Analyze a what-if scenario
        
        Args:
            base_input: Base case input parameters
            scenario_changes: Parameters to change
            scenario_name: Name of the scenario
            
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
            
            logger.info(f"Scenario analysis completed: {improvements['co2_reduction']}% CO2 reduction")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing scenario: {str(e)}")
            raise
    
    def _apply_changes(
        self,
        base_input: LCAInputSchema,
        changes: Dict[str, Any]
    ) -> LCAInputSchema:
        """
        Apply changes to base input to create scenario
        
        Args:
            base_input: Base case input
            changes: Dictionary of changes
            
        Returns:
            Modified input for scenario
        """
        # Create a copy of base input
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
        
        # Create new input schema
        scenario_input = LCAInputSchema(**scenario_dict)
        
        return scenario_input
    
    def _calculate_improvements(
        self,
        base_result: LCAResultSchema,
        scenario_result: LCAResultSchema
    ) -> Dict[str, float]:
        """
        Calculate improvements between base and scenario
        
        Args:
            base_result: Base case results
            scenario_result: Scenario results
            
        Returns:
            Dictionary of improvement percentages
        """
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
    
    def compare_multiple_scenarios(
        self,
        base_input: LCAInputSchema,
        scenarios: List[Dict[str, Any]]
    ) -> List[WhatIfResultSchema]:
        """
        Compare multiple scenarios at once
        
        Args:
            base_input: Base case input
            scenarios: List of scenario configurations
            
        Returns:
            List of scenario results
        """
        results = []
        
        for scenario in scenarios:
            scenario_name = scenario.get("name", "Unnamed Scenario")
            scenario_changes = scenario.get("changes", {})
            
            result = self.analyze_scenario(base_input, scenario_changes, scenario_name)
            results.append(result)
        
        return results
    
    def get_predefined_scenario(self, scenario_key: str) -> Optional[Dict[str, Any]]:
        """
        Get a predefined scenario by key
        
        Args:
            scenario_key: Scenario identifier
            
        Returns:
            Scenario configuration or None
        """
        return self.predefined_scenarios.get(scenario_key)
    
    def list_predefined_scenarios(self) -> List[Dict[str, Any]]:
        """
        List all available predefined scenarios
        
        Returns:
            List of scenario information
        """
        scenarios = []
        for key, scenario in self.predefined_scenarios.items():
            scenarios.append({
                "key": key,
                "name": scenario["name"],
                "description": scenario["description"]
            })
        return scenarios
    
    def sensitivity_analysis(
        self,
        base_input: LCAInputSchema,
        parameter: str,
        values: List[Any]
    ) -> Dict[str, Any]:
        """
        Perform sensitivity analysis on a single parameter
        
        Args:
            base_input: Base case input
            parameter: Parameter to vary
            values: List of values to test
            
        Returns:
            Sensitivity analysis results
        """
        results = []
        
        for value in values:
            changes = {parameter: value}
            scenario_name = f"{parameter} = {value}"
            
            result = self.analyze_scenario(base_input, changes, scenario_name)
            
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
        optimization_goal: str = "minimize_co2"
    ) -> Dict[str, Any]:
        """
        Suggest optimal parameter values based on goal
        
        Args:
            base_input: Base case input
            optimization_goal: Optimization objective
            
        Returns:
            Optimal parameter suggestions
        """
        suggestions = {}
        
        if optimization_goal == "minimize_co2":
            # Suggest changes that minimize CO2
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
                "energy_source": "renewable",
                "process_efficiency": 95  # Assuming this field exists
            }
        
        elif optimization_goal == "maximize_circularity":
            suggestions = {
                "recycled_content": 100,
                "production_type": "secondary",
                "end_of_life_recycling_rate": 98,
                "transport_distance": base_input.transport_distance * 0.5  # Reduce by half
            }
        
        # Analyze optimized scenario
        optimized_result = self.analyze_scenario(
            base_input,
            suggestions,
            f"Optimized for {optimization_goal}"
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
        """
        Generate summary comparing all analyzed scenarios
        
        Args:
            results: List of scenario results
            
        Returns:
            Summary with best performing scenarios
        """
        if not results:
            return {"error": "No scenarios to summarize"}
        
        # Find best scenarios for each metric
        best_co2 = min(results, key=lambda r: r.scenario_case.total_co2_emissions)
        best_energy = min(results, key=lambda r: r.scenario_case.energy_consumption)
        best_water = min(results, key=lambda r: r.scenario_case.water_usage)
        
        # Calculate average improvements
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


# Global scenario engine instance
scenario_engine = ScenarioEngine()
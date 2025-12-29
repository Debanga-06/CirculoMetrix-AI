"""
Life Cycle Assessment (LCA) Calculation Engine
Implements LCA methodology based on ISO 14040/14044 standards
MongoDB compatible version with calculation tracking
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime, timedelta
from bson import ObjectId

from core.config import settings
from models.schemas import LCAInputSchema, LCAResultSchema, LCABreakdownSchema

# Configure logging
logger = logging.getLogger(__name__)


class LCAEngine:
    """
    Life Cycle Assessment calculation engine
    Calculates environmental impacts across product lifecycle
    """
    
    def __init__(self, db=None):
        """
        Initialize LCA engine and load emission factors
        
        Args:
            db: MongoDB database instance (optional, for storing calculations)
        """
        self.db = db
        self.emission_factors = self._load_emission_factors()
        self.transport_factors = self._load_transport_factors()
        self.recycling_efficiency = self._load_recycling_efficiency()
        logger.info("LCA Engine initialized successfully")
    
    def _load_emission_factors(self) -> pd.DataFrame:
        """
        Load LCA emission factors from CSV
        
        Returns:
            DataFrame with emission factors
        """
        try:
            file_path = Path(settings.LCA_EMISSION_FACTORS_PATH)
            if file_path.exists():
                df = pd.read_csv(file_path)
                logger.info(f"Loaded {len(df)} emission factors")
                return df
            else:
                # Return default factors if file doesn't exist
                logger.warning("Emission factors file not found, using defaults")
                return self._get_default_emission_factors()
        except Exception as e:
            logger.error(f"Error loading emission factors: {str(e)}")
            return self._get_default_emission_factors()
    
    def _enum_value(self, value):
        """Helper to extract value from enum or return as-is"""
        if value is None:
            return None
        return value.value if hasattr(value, "value") else value
    
    def _load_transport_factors(self) -> pd.DataFrame:
        """
        Load transport emission factors
        
        Returns:
            DataFrame with transport factors
        """
        try:
            file_path = Path(settings.TRANSPORT_FACTORS_PATH)
            if file_path.exists():
                df = pd.read_csv(file_path)
                logger.info(f"Loaded transport factors for {len(df)} modes")
                return df
            else:
                return self._get_default_transport_factors()
        except Exception as e:
            logger.error(f"Error loading transport factors: {str(e)}")
            return self._get_default_transport_factors()
    
    def _load_recycling_efficiency(self) -> pd.DataFrame:
        """
        Load recycling efficiency data
        
        Returns:
            DataFrame with recycling efficiency rates
        """
        try:
            file_path = Path(settings.RECYCLING_EFFICIENCY_PATH)
            if file_path.exists():
                df = pd.read_csv(file_path)
                logger.info(f"Loaded recycling efficiency data")
                return df
            else:
                return self._get_default_recycling_efficiency()
        except Exception as e:
            logger.error(f"Error loading recycling efficiency: {str(e)}")
            return self._get_default_recycling_efficiency()
    
    def _get_default_emission_factors(self) -> pd.DataFrame:
        """
        Get default emission factors
        Based on Ecoinvent 3.9 database averages
        """
        data = {
            'material': ['aluminium', 'copper', 'steel'],
            'production_type': ['primary', 'secondary', 'primary'],
            'co2_per_kg': [11.5, 3.2, 2.8],  # kg CO2 per kg material
            'energy_per_kg': [155.0, 28.0, 21.0],  # MJ per kg
            'water_per_kg': [22.0, 15.0, 8.5],  # liters per kg
        }
        
        # Add secondary production for all materials
        data['material'].extend(['aluminium', 'copper', 'steel'])
        data['production_type'].extend(['secondary', 'secondary', 'secondary'])
        data['co2_per_kg'].extend([0.5, 1.2, 0.4])
        data['energy_per_kg'].extend([8.0, 12.0, 4.5])
        data['water_per_kg'].extend([2.0, 5.0, 1.5])
        
        return pd.DataFrame(data)
    
    def _get_default_transport_factors(self) -> pd.DataFrame:
        """
        Get default transport emission factors
        kg CO2 per ton-km
        """
        data = {
            'mode': ['truck', 'rail', 'ship', 'air'],
            'co2_per_ton_km': [0.062, 0.022, 0.008, 0.602],
            'energy_per_ton_km': [0.85, 0.30, 0.11, 8.20]
        }
        return pd.DataFrame(data)
    
    def _get_default_recycling_efficiency(self) -> pd.DataFrame:
        """
        Get default recycling efficiency rates
        """
        data = {
            'material': ['aluminium', 'copper', 'steel'],
            'efficiency': [0.95, 0.98, 0.90],  # Material recovery rate
            'quality_factor': [0.98, 0.99, 0.95]  # Quality retention
        }
        return pd.DataFrame(data)
    
    def calculate_lca(
        self,
        input_data: LCAInputSchema,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        save_calculation: bool = False
    ) -> LCAResultSchema:
        """
        Calculate complete LCA for given input
        
        Args:
            input_data: LCA input parameters
            user_id: User ID for tracking (optional)
            project_id: Project ID for linking (optional)
            save_calculation: Whether to save calculation to database
            
        Returns:
            LCA results with breakdown
        """
        try:
            logger.info(f"Calculating LCA for {input_data.quantity}kg of {input_data.material}")
            
            # Calculate each lifecycle stage
            extraction_emissions = self._calculate_extraction_emissions(input_data)
            production_emissions = self._calculate_production_emissions(input_data)
            transport_emissions = self._calculate_transport_emissions(input_data)
            end_of_life_emissions = self._calculate_end_of_life_emissions(input_data)
            
            # Calculate energy consumption
            total_energy = self._calculate_total_energy(input_data)
            
            # Calculate water usage
            total_water = self._calculate_water_usage(input_data)
            
            # Calculate carbon savings from recycling
            carbon_savings = self._calculate_carbon_savings(input_data)
            
            # Total emissions
            total_co2 = (
                extraction_emissions +
                production_emissions +
                transport_emissions +
                end_of_life_emissions
            )
            
            # Create breakdown
            breakdown = LCABreakdownSchema(
                raw_material_extraction=round(extraction_emissions, 2),
                production=round(production_emissions, 2),
                transport=round(transport_emissions, 2),
                end_of_life=round(end_of_life_emissions, 2)
            )
            
            # Create result
            result = LCAResultSchema(
                total_co2_emissions=round(total_co2, 2),
                co2_per_unit=round(total_co2 / input_data.quantity, 4),
                energy_consumption=round(total_energy, 2),
                energy_per_unit=round(total_energy / input_data.quantity, 2),
                water_usage=round(total_water, 2),
                water_per_unit=round(total_water / input_data.quantity, 2),
                breakdown=breakdown,
                carbon_savings=round(carbon_savings, 2) if carbon_savings > 0 else None
            )
            
            # Save calculation to database if requested
            if save_calculation and self.db is not None:
                self._save_calculation_to_db(input_data, result, user_id, project_id)
            
            logger.info(f"LCA calculation completed: {result.total_co2_emissions} kg CO2")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating LCA: {str(e)}")
            raise
    
    def _calculate_extraction_emissions(self, input_data: LCAInputSchema) -> float:
        """Calculate emissions from raw material extraction"""
        # Virgin material portion
        virgin_portion = (100 - input_data.recycled_content) / 100
        
        # Get extraction factor for primary production
        material = self._enum_value(input_data.material)
        primary_factor = self.emission_factors[
            (self.emission_factors['material'] == material) &
            (self.emission_factors['production_type'] == 'primary')
        ]['co2_per_kg'].values
        
        if len(primary_factor) > 0:
            extraction_factor = primary_factor[0] * 0.3  # 30% of primary production is extraction
        else:
            extraction_factor = 2.0  # Default
        
        emissions = input_data.quantity * virgin_portion * extraction_factor
        return emissions
    
    def _calculate_production_emissions(self, input_data: LCAInputSchema) -> float:
        """Calculate emissions from production/manufacturing"""
        material = self._enum_value(input_data.material)
        production_type = self._enum_value(input_data.production_type)
        
        # Get base production factor
        factor_data = self.emission_factors[
            (self.emission_factors['material'] == material) &
            (self.emission_factors['production_type'] == production_type)
        ]
        
        if len(factor_data) > 0:
            base_factor = factor_data['co2_per_kg'].values[0]
        else:
            base_factor = 5.0
        
        # Apply energy source multiplier
        energy_multipliers = {
            'renewable': 0.1,
            'fossil': 1.2,
            'grid_average': 1.0,
            'nuclear': 0.2,
            'hydro': 0.1,
            'solar': 0.05,
            'wind': 0.05
        }
        
        energy_multiplier = energy_multipliers.get(self._enum_value(input_data.energy_source), 1.0)
        
        # Calculate with recycled content benefit
        recycled_benefit = 1 - (input_data.recycled_content / 100 * 0.8)
        
        emissions = input_data.quantity * base_factor * energy_multiplier * recycled_benefit
        return emissions
    
    def _calculate_transport_emissions(self, input_data: LCAInputSchema) -> float:
        """Calculate emissions from transportation"""
        if input_data.transport_distance == 0:
            return 0.0
        
        # Get transport factor
        transport_mode = self._enum_value(input_data.transport_mode)
        factor_data = self.transport_factors[
            self.transport_factors['mode'] == transport_mode
        ]
        
        if len(factor_data) > 0:
            co2_per_ton_km = factor_data['co2_per_ton_km'].values[0]
        else:
            co2_per_ton_km = 0.062  # Default to truck
        
        # Calculate: (quantity in tons) * distance * factor
        emissions = (input_data.quantity / 1000) * input_data.transport_distance * co2_per_ton_km
        return emissions
    
    def _calculate_end_of_life_emissions(self, input_data: LCAInputSchema) -> float:
        """Calculate emissions from end-of-life treatment"""
        # Recycling rate at end of life
        recycling_rate = input_data.end_of_life_recycling_rate / 100
        
        # Waste to landfill
        landfill_rate = 1 - recycling_rate
        
        # Landfill emissions (methane from organic content, transport)
        landfill_factor = 0.05  # kg CO2 per kg material
        
        # Recycling process emissions (collection, sorting, processing)
        recycling_factor = 0.1  # kg CO2 per kg material
        
        emissions = (
            input_data.quantity * landfill_rate * landfill_factor +
            input_data.quantity * recycling_rate * recycling_factor
        )
        
        return emissions
    
    def _calculate_total_energy(self, input_data: LCAInputSchema) -> float:
        """Calculate total energy consumption"""
        material = self._enum_value(input_data.material)
        production_type = self._enum_value(input_data.production_type)
        
        # Get energy factor
        factor_data = self.emission_factors[
            (self.emission_factors['material'] == material) &
            (self.emission_factors['production_type'] == production_type)
        ]
        
        if len(factor_data) > 0:
            energy_per_kg = factor_data['energy_per_kg'].values[0]
        else:
            energy_per_kg = 50.0  # Default
        
        # Apply recycled content benefit
        recycled_benefit = 1 - (input_data.recycled_content / 100 * 0.75)
        
        total_energy = input_data.quantity * energy_per_kg * recycled_benefit
        
        # Add transport energy
        if input_data.transport_distance > 0:
            transport_mode = self._enum_value(input_data.transport_mode)
            transport_data = self.transport_factors[
                self.transport_factors['mode'] == transport_mode
            ]
            if len(transport_data) > 0:
                energy_per_ton_km = transport_data['energy_per_ton_km'].values[0]
                transport_energy = (input_data.quantity / 1000) * input_data.transport_distance * energy_per_ton_km
                total_energy += transport_energy
        
        return total_energy
    
    def _calculate_water_usage(self, input_data: LCAInputSchema) -> float:
        """Calculate total water usage"""
        material = self._enum_value(input_data.material)
        production_type = self._enum_value(input_data.production_type)
        
        # Get water factor
        factor_data = self.emission_factors[
            (self.emission_factors['material'] == material) &
            (self.emission_factors['production_type'] == production_type)
        ]
        
        if len(factor_data) > 0:
            water_per_kg = factor_data['water_per_kg'].values[0]
        else:
            water_per_kg = 10.0  # Default
        
        # Recycled content reduces water usage significantly
        recycled_benefit = 1 - (input_data.recycled_content / 100 * 0.85)
        
        total_water = input_data.quantity * water_per_kg * recycled_benefit
        return total_water
    
    def _calculate_carbon_savings(self, input_data: LCAInputSchema) -> float:
        """Calculate carbon savings compared to 100% virgin material"""
        if input_data.recycled_content == 0:
            return 0.0
        
        # Calculate emissions with 100% virgin material
        virgin_input = input_data.model_copy(update={
            "recycled_content": 0,
            "production_type": "primary"
        })
        
        virgin_emissions = (
            self._calculate_extraction_emissions(virgin_input) +
            self._calculate_production_emissions(virgin_input)
        )
        
        # Calculate current emissions (extraction + production only)
        current_emissions = (
            self._calculate_extraction_emissions(input_data) +
            self._calculate_production_emissions(input_data)
        )
        
        savings = virgin_emissions - current_emissions
        return max(0, savings)
    
    def _save_calculation_to_db(
        self,
        input_data: LCAInputSchema,
        result: LCAResultSchema,
        user_id: Optional[str],
        project_id: Optional[str]
    ):
        """
        Save LCA calculation to MongoDB
        
        Args:
            input_data: Input parameters
            result: Calculation results
            user_id: User ID
            project_id: Project ID
        """
        try:
            if self.db is None:
                return
            
            calculation_doc = {
                "user_id": user_id,
                "project_id": project_id,
                "input_data": input_data.dict(),
                "results": {
                    "total_co2_emissions": result.total_co2_emissions,
                    "co2_per_unit": result.co2_per_unit,
                    "energy_consumption": result.energy_consumption,
                    "energy_per_unit": result.energy_per_unit,
                    "water_usage": result.water_usage,
                    "water_per_unit": result.water_per_unit,
                    "breakdown": result.breakdown.dict(),
                    "carbon_savings": result.carbon_savings
                },
                "material": self._enum_value(input_data.material),
                "production_type": self._enum_value(input_data.production_type),
                "created_at": datetime.utcnow()
            }
            
            self.db.lca_calculations.insert_one(calculation_doc)
            logger.debug("LCA calculation saved to database")
            
        except Exception as e:
            logger.error(f"Error saving calculation to database: {str(e)}")
    
    def compare_scenarios(
        self,
        base_scenario: LCAInputSchema,
        alternative_scenario: LCAInputSchema
    ) -> Dict[str, Any]:
        """
        Compare two LCA scenarios
        
        Args:
            base_scenario: Base case input
            alternative_scenario: Alternative scenario input
            
        Returns:
            Comparison results with improvements
        """
        base_result = self.calculate_lca(base_scenario)
        alt_result = self.calculate_lca(alternative_scenario)
        
        # Calculate improvements
        co2_improvement = ((base_result.total_co2_emissions - alt_result.total_co2_emissions) 
                          / base_result.total_co2_emissions * 100)
        
        energy_improvement = ((base_result.energy_consumption - alt_result.energy_consumption) 
                             / base_result.energy_consumption * 100)
        
        water_improvement = ((base_result.water_usage - alt_result.water_usage) 
                            / base_result.water_usage * 100)
        
        return {
            "base_case": base_result,
            "alternative_case": alt_result,
            "improvements": {
                "co2_reduction_percent": round(co2_improvement, 2),
                "energy_savings_percent": round(energy_improvement, 2),
                "water_savings_percent": round(water_improvement, 2),
                "absolute_co2_reduction": round(
                    base_result.total_co2_emissions - alt_result.total_co2_emissions, 2
                )
            }
        }
    
    def get_calculation_history(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        material: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get LCA calculation history from database
        
        Args:
            user_id: Filter by user ID (optional)
            project_id: Filter by project ID (optional)
            material: Filter by material type (optional)
            limit: Maximum number of records to return
            
        Returns:
            List of calculation documents
        """
        if self.db is None:
            return []
        
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            if project_id:
                query["project_id"] = project_id
            if material:
                query["material"] = material
            
            calculations = list(
                self.db.lca_calculations
                .find(query)
                .sort("created_at", -1)
                .limit(limit)
            )
            
            # Convert ObjectId to string
            for calc in calculations:
                calc["id"] = str(calc.pop("_id"))
                if "created_at" in calc:
                    calc["created_at"] = calc["created_at"].isoformat()
            
            return calculations
            
        except Exception as e:
            logger.error(f"Error retrieving calculation history: {str(e)}")
            return []
    
    def get_emission_trends(
        self,
        user_id: Optional[str] = None,
        material: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get CO2 emission trends over time
        
        Args:
            user_id: Filter by user ID (optional)
            material: Filter by material type (optional)
            days: Number of days to look back
            
        Returns:
            Trend analysis data
        """
        if self.db is None:
            return {"error": "Database not available"}
        
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            query = {"created_at": {"$gte": start_date}}
            if user_id:
                query["user_id"] = user_id
            if material:
                query["material"] = material
            
            calculations = list(
                self.db.lca_calculations
                .find(query)
                .sort("created_at", 1)
            )
            
            if not calculations:
                return {
                    "trend": "No data",
                    "average_co2": 0,
                    "data_points": []
                }
            
            # Extract emission data and dates
            data_points = [
                {
                    "date": calc["created_at"].isoformat(),
                    "co2_emissions": calc["results"]["total_co2_emissions"],
                    "material": calc.get("material")
                }
                for calc in calculations
            ]
            
            # Calculate statistics
            co2_values = [dp["co2_emissions"] for dp in data_points]
            average_co2 = sum(co2_values) / len(co2_values)
            
            # Simple trend calculation
            mid_point = len(co2_values) // 2
            if mid_point > 0:
                first_half_avg = sum(co2_values[:mid_point]) / mid_point
                second_half_avg = sum(co2_values[mid_point:]) / (len(co2_values) - mid_point)
                
                if second_half_avg < first_half_avg * 0.95:
                    trend = "Improving (Decreasing Emissions)"
                elif second_half_avg > first_half_avg * 1.05:
                    trend = "Worsening (Increasing Emissions)"
                else:
                    trend = "Stable"
            else:
                trend = "Insufficient data"
            
            return {
                "trend": trend,
                "average_co2": round(average_co2, 2),
                "min_co2": round(min(co2_values), 2),
                "max_co2": round(max(co2_values), 2),
                "total_calculations": len(calculations),
                "data_points": data_points
            }
            
        except Exception as e:
            logger.error(f"Error calculating emission trends: {str(e)}")
            return {"error": str(e)}
    
    def get_material_statistics(self, material: Optional[str] = None) -> Dict[str, Any]:
        """
        Get aggregate statistics for LCA calculations
        
        Args:
            material: Filter by material type (optional)
            
        Returns:
            Aggregate statistics
        """
        if self.db is None:
            return {"error": "Database not available"}
        
        try:
            match_stage = {}
            if material:
                match_stage = {"$match": {"material": material}}
            
            pipeline = [
                match_stage if material else {"$match": {}},
                {
                    "$group": {
                        "_id": "$material",
                        "count": {"$sum": 1},
                        "avg_co2": {"$avg": "$results.total_co2_emissions"},
                        "avg_energy": {"$avg": "$results.energy_consumption"},
                        "avg_water": {"$avg": "$results.water_usage"},
                        "total_co2": {"$sum": "$results.total_co2_emissions"},
                        "total_energy": {"$sum": "$results.energy_consumption"},
                        "total_water": {"$sum": "$results.water_usage"}
                    }
                },
                {
                    "$sort": {"count": -1}
                }
            ]
            
            results = list(self.db.lca_calculations.aggregate(pipeline))
            
            # Format results
            statistics = []
            for result in results:
                statistics.append({
                    "material": result["_id"],
                    "total_calculations": result["count"],
                    "average_co2_emissions": round(result.get("avg_co2", 0), 2),
                    "average_energy_consumption": round(result.get("avg_energy", 0), 2),
                    "average_water_usage": round(result.get("avg_water", 0), 2),
                    "total_co2_emissions": round(result.get("total_co2", 0), 2),
                    "total_energy_consumption": round(result.get("total_energy", 0), 2),
                    "total_water_usage": round(result.get("total_water", 0), 2)
                })
            
            return {
                "statistics": statistics,
                "total_materials": len(statistics)
            }
            
        except Exception as e:
            logger.error(f"Error getting material statistics: {str(e)}")
            return {"error": str(e)}


# Factory function to create LCA engine instance
def create_lca_engine(db=None) -> LCAEngine:
    """
    Create and return LCA engine instance
    
    Args:
        db: MongoDB database instance (optional)
        
    Returns:
        LCAEngine instance
    """
    return LCAEngine(db=db)


# Global LCA engine instance
lca_engine = None

def get_lca_engine(db=None) -> LCAEngine:
    """
    Get or create global LCA engine instance
    
    Args:
        db: MongoDB database instance (optional)
        
    Returns:
        LCAEngine instance
    """
    global lca_engine
    if lca_engine is None:
        lca_engine = LCAEngine(db=db)
    elif db is not None and lca_engine.db is None:
        lca_engine.db = db
    return lca_engine
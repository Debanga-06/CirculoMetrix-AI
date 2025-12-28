"""
Life Cycle Assessment (LCA) Calculation Engine
Implements LCA methodology based on ISO 14040/14044 standards
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import logging
from pathlib import Path

from core.config import settings
from models.schemas import LCAInputSchema, LCAResultSchema, LCABreakdownSchema

# Configure logging
logger = logging.getLogger(__name__)


class LCAEngine:
    """
    Life Cycle Assessment calculation engine
    Calculates environmental impacts across product lifecycle
    """
    
    def __init__(self):
        """Initialize LCA engine and load emission factors"""
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
    
    def calculate_lca(self, input_data: LCAInputSchema) -> LCAResultSchema:
        """
        Calculate complete LCA for given input
        
        Args:
            input_data: LCA input parameters
            
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
            
            logger.info(f"LCA calculation completed: {result.total_co2_emissions} kg CO2")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating LCA: {str(e)}")
            raise
    
    def _calculate_extraction_emissions(self, input_data: LCAInputSchema) -> float:
        """
        Calculate emissions from raw material extraction
        
        Args:
            input_data: LCA input parameters
            
        Returns:
            CO2 emissions in kg
        """
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
        """
        Calculate emissions from production/manufacturing
        
        Args:
            input_data: LCA input parameters
            
        Returns:
            CO2 emissions in kg
        """
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
            # Use average if specific combination not found
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
        
        energy_multiplier = energy_multipliers.get(self._enum_value(input_data.energy_source),1.0)
        
        # Calculate with recycled content benefit
        recycled_benefit = 1 - (input_data.recycled_content / 100 * 0.8)
        
        emissions = input_data.quantity * base_factor * energy_multiplier * recycled_benefit
        
        return emissions
    
    def _calculate_transport_emissions(self, input_data: LCAInputSchema) -> float:
        """
        Calculate emissions from transportation
        
        Args:
            input_data: LCA input parameters
            
        Returns:
            CO2 emissions in kg
        """
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
        """
        Calculate emissions from end-of-life treatment
        
        Args:
            input_data: LCA input parameters
            
        Returns:
            CO2 emissions in kg
        """
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
        """
        Calculate total energy consumption
        
        Args:
            input_data: LCA input parameters
            
        Returns:
            Energy consumption in MJ
        """
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
        """
        Calculate total water usage
        
        Args:
            input_data: LCA input parameters
            
        Returns:
            Water usage in liters
        """
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
        """
        Calculate carbon savings compared to 100% virgin material
        
        Args:
            input_data: LCA input parameters
            
        Returns:
            Carbon savings in kg CO2
        """
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


# Global LCA engine instance
lca_engine = LCAEngine()
"""
Circular Economy Metrics Calculation Engine
Implements Material Circularity Indicator (MCI) based on Ellen MacArthur Foundation methodology
"""

from typing import Dict, Any, Optional
import numpy as np
import logging

from models.schemas import CircularityInputSchema, CircularityResultSchema

# Configure logging
logger = logging.getLogger(__name__)


class CircularityEngine:
    """
    Circular economy metrics calculation engine
    Calculates MCI, recycling rates, and circularity levels
    """
    
    def __init__(self):
        """Initialize circularity engine"""
        logger.info("Circularity Engine initialized successfully")
    
    def calculate_circularity_metrics(
        self,
        input_data: CircularityInputSchema
    ) -> CircularityResultSchema:
        """
        Calculate comprehensive circularity metrics
        
        Args:
            input_data: Circularity input parameters
            
        Returns:
            Circularity results including MCI score
        """
        try:
            logger.info(f"Calculating circularity metrics for {input_data.material}")
            
            # Calculate individual metrics
            mci_score = self._calculate_mci(input_data)
            recycled_content_rate = self._calculate_recycled_content_rate(input_data)
            eol_recycling_rate = self._calculate_eol_recycling_rate(input_data)
            waste_reduction = self._calculate_waste_reduction(input_data)
            circularity_level = self._determine_circularity_level(mci_score)
            
            result = CircularityResultSchema(
                mci_score=round(mci_score, 3),
                recycled_content_rate=round(recycled_content_rate, 2),
                end_of_life_recycling_rate=round(eol_recycling_rate, 2),
                waste_reduction=round(waste_reduction, 2),
                circularity_level=circularity_level
            )
            
            logger.info(f"Circularity calculation completed: MCI = {result.mci_score}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating circularity metrics: {str(e)}")
            raise
    
    def _calculate_mci(self, input_data: CircularityInputSchema) -> float:
        """
        Calculate Material Circularity Indicator (MCI)
        Based on Ellen MacArthur Foundation methodology
        
        MCI = 1 - (LFI) × (F(X,W))
        Where:
        - LFI: Linear Flow Index
        - F(X,W): Utility factor
        
        Args:
            input_data: Circularity input parameters
            
        Returns:
            MCI score (0 to 1, where 1 is fully circular)
        """
        # Total material input
        total_input = input_data.virgin_material_input + input_data.recycled_material_input
        
        if total_input == 0:
            return 0.0
        
        # Calculate Virgin Material Fraction (V)
        V = input_data.virgin_material_input / total_input
        
        # Calculate Waste Fraction (W)
        if input_data.waste_generated > 0:
            W = (input_data.waste_generated - input_data.waste_recycled) / input_data.waste_generated
        else:
            W = 0.0
        
        # Calculate Linear Flow Index (LFI)
        # LFI represents the proportion of material that flows linearly
        LFI = (V + W) / 2
        
        # Calculate Utility Factor F(X, W)
        # X is the average number of functional uses
        # Longer lifespan = higher utility
        
        # Industry average lifespan (years)
        material_lifespans = {
            'aluminium': 15,
            'aluminum': 15,
            'copper': 25,
            'steel': 20
        }
        
        average_lifespan = material_lifespans.get(input_data.material.value, 15)
        
        # Utility factor calculation
        if input_data.product_lifespan >= average_lifespan:
            utility_factor = 1.0
        else:
            utility_factor = 0.9 * (input_data.product_lifespan / average_lifespan)
        
        # Calculate MCI
        mci = (1 - LFI) * utility_factor
        
        # Ensure MCI is between 0 and 1
        mci = max(0.0, min(1.0, mci))
        
        return mci
    
    def _calculate_recycled_content_rate(self, input_data: CircularityInputSchema) -> float:
        """
        Calculate recycled content rate
        
        Args:
            input_data: Circularity input parameters
            
        Returns:
            Recycled content rate as percentage
        """
        total_input = input_data.virgin_material_input + input_data.recycled_material_input
        
        if total_input == 0:
            return 0.0
        
        rate = (input_data.recycled_material_input / total_input) * 100
        
        return min(100.0, rate)
    
    def _calculate_eol_recycling_rate(self, input_data: CircularityInputSchema) -> float:
        """
        Calculate end-of-life recycling rate
        
        Args:
            input_data: Circularity input parameters
            
        Returns:
            End-of-life recycling rate as percentage
        """
        if input_data.waste_generated == 0:
            return 0.0
        
        rate = (input_data.waste_recycled / input_data.waste_generated) * 100
        
        return min(100.0, rate)
    
    def _calculate_waste_reduction(self, input_data: CircularityInputSchema) -> float:
        """
        Calculate waste reduction compared to linear model
        
        Args:
            input_data: Circularity input parameters
            
        Returns:
            Waste reduction as percentage
        """
        total_input = input_data.virgin_material_input + input_data.recycled_material_input
        
        if total_input == 0:
            return 0.0
        
        # In a linear model, waste would equal total input
        # Waste reduction = (Expected Waste - Actual Waste) / Expected Waste
        expected_waste = total_input
        actual_waste = input_data.waste_generated - input_data.waste_recycled
        
        if expected_waste == 0:
            return 0.0
        
        reduction = ((expected_waste - actual_waste) / expected_waste) * 100
        
        return max(0.0, min(100.0, reduction))
    
    def _determine_circularity_level(self, mci_score: float) -> str:
        """
        Determine circularity level based on MCI score
        
        Args:
            mci_score: MCI score (0-1)
            
        Returns:
            Circularity level description
        """
        if mci_score >= 0.9:
            return "Excellent"
        elif mci_score >= 0.7:
            return "High"
        elif mci_score >= 0.5:
            return "Medium"
        elif mci_score >= 0.3:
            return "Low"
        else:
            return "Very Low"
    
    def calculate_material_flow_analysis(
        self,
        input_data: CircularityInputSchema
    ) -> Dict[str, Any]:
        """
        Perform material flow analysis
        
        Args:
            input_data: Circularity input parameters
            
        Returns:
            Material flow analysis results
        """
        total_input = input_data.virgin_material_input + input_data.recycled_material_input
        total_output = input_data.waste_generated
        
        # Calculate flows
        flows = {
            "inputs": {
                "virgin_material": input_data.virgin_material_input,
                "recycled_material": input_data.recycled_material_input,
                "total_input": total_input
            },
            "outputs": {
                "product": total_input - total_output,
                "waste_recycled": input_data.waste_recycled,
                "waste_landfill": input_data.waste_generated - input_data.waste_recycled,
                "total_output": total_output
            },
            "efficiency": {
                "material_efficiency": round((total_input - total_output) / total_input * 100, 2) if total_input > 0 else 0,
                "recycling_efficiency": round(input_data.waste_recycled / input_data.waste_generated * 100, 2) if input_data.waste_generated > 0 else 0
            }
        }
        
        return flows
    
    def generate_sankey_data(
        self,
        input_data: CircularityInputSchema
    ) -> Dict[str, Any]:
        """
        Generate data for Sankey diagram visualization
        
        Args:
            input_data: Circularity input parameters
            
        Returns:
            Sankey diagram data structure
        """
        total_input = input_data.virgin_material_input + input_data.recycled_material_input
        product_output = total_input - input_data.waste_generated
        
        # Define nodes
        nodes = [
            {"id": 0, "name": "Virgin Material"},
            {"id": 1, "name": "Recycled Material"},
            {"id": 2, "name": "Production"},
            {"id": 3, "name": "Product"},
            {"id": 4, "name": "Waste"},
            {"id": 5, "name": "Recycling"},
            {"id": 6, "name": "Landfill"}
        ]
        
        # Define links (flows)
        links = [
            {
                "source": 0,
                "target": 2,
                "value": input_data.virgin_material_input,
                "label": "Virgin Input"
            },
            {
                "source": 1,
                "target": 2,
                "value": input_data.recycled_material_input,
                "label": "Recycled Input"
            },
            {
                "source": 2,
                "target": 3,
                "value": product_output,
                "label": "Product Output"
            },
            {
                "source": 2,
                "target": 4,
                "value": input_data.waste_generated,
                "label": "Waste Generated"
            },
            {
                "source": 4,
                "target": 5,
                "value": input_data.waste_recycled,
                "label": "Waste Recycled"
            },
            {
                "source": 4,
                "target": 6,
                "value": input_data.waste_generated - input_data.waste_recycled,
                "label": "Waste to Landfill"
            },
            {
                "source": 5,
                "target": 1,
                "value": input_data.waste_recycled * 0.95,  # Assume 95% recovery
                "label": "Back to Recycled Material"
            }
        ]
        
        return {
            "nodes": nodes,
            "links": links
        }
    
    def benchmark_against_industry(
        self,
        mci_score: float,
        material: str
    ) -> Dict[str, Any]:
        """
        Benchmark MCI score against industry averages
        
        Args:
            mci_score: Calculated MCI score
            material: Material type
            
        Returns:
            Benchmarking results
        """
        # Industry average MCI scores (based on research data)
        industry_averages = {
            'aluminium': 0.65,
            'aluminum': 0.65,
            'copper': 0.70,
            'steel': 0.60
        }
        
        # Best-in-class scores
        best_in_class = {
            'aluminium': 0.90,
            'aluminum': 0.90,
            'copper': 0.92,
            'steel': 0.85
        }
        
        industry_avg = industry_averages.get(material, 0.60)
        best_score = best_in_class.get(material, 0.90)
        
        # Calculate percentile
        if mci_score >= best_score:
            percentile = 100
        elif mci_score <= 0.3:
            percentile = 10
        else:
            percentile = int(((mci_score - 0.3) / (best_score - 0.3)) * 90 + 10)
        
        return {
            "your_score": round(mci_score, 3),
            "industry_average": round(industry_avg, 3),
            "best_in_class": round(best_score, 3),
            "percentile": percentile,
            "gap_to_average": round((mci_score - industry_avg) * 100, 2),
            "gap_to_best": round((best_score - mci_score) * 100, 2),
            "performance": "Above Average" if mci_score > industry_avg else "Below Average"
        }
    
    def calculate_circularity_gap(
        self,
        current: CircularityInputSchema,
        target_mci: float = 0.9
    ) -> Dict[str, Any]:
        """
        Calculate the gap between current and target circularity
        
        Args:
            current: Current circularity parameters
            target_mci: Target MCI score
            
        Returns:
            Gap analysis with recommendations
        """
        current_metrics = self.calculate_circularity_metrics(current)
        current_mci = current_metrics.mci_score
        
        gap = target_mci - current_mci
        
        # Calculate required improvements
        total_input = current.virgin_material_input + current.recycled_material_input
        
        # Estimate required changes
        required_recycled_content = min(100, current_metrics.recycled_content_rate + (gap * 50))
        required_recycling_rate = min(100, current_metrics.end_of_life_recycling_rate + (gap * 40))
        
        return {
            "current_mci": round(current_mci, 3),
            "target_mci": target_mci,
            "gap": round(gap, 3),
            "gap_percentage": round(gap * 100, 2),
            "required_improvements": {
                "increase_recycled_content_to": round(required_recycled_content, 1),
                "increase_recycling_rate_to": round(required_recycling_rate, 1),
                "reduce_virgin_material_by": round((gap * 100) / 2, 1)
            },
            "feasibility": "Achievable" if gap < 0.2 else "Challenging" if gap < 0.4 else "Requires Major Changes"
        }


# Global circularity engine instance
circularity_engine = CircularityEngine()
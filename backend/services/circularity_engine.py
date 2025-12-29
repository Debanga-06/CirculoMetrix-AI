"""
Circular Economy Metrics Calculation Engine
Implements Material Circularity Indicator (MCI) based on Ellen MacArthur Foundation methodology
MongoDB compatible version with metrics tracking
"""

from typing import Dict, Any, Optional, List
import numpy as np
import logging
from datetime import datetime
from bson import ObjectId

from models.schemas import CircularityInputSchema, CircularityResultSchema

# Configure logging
logger = logging.getLogger(__name__)


class CircularityEngine:
    """
    Circular economy metrics calculation engine
    Calculates MCI, recycling rates, and circularity levels
    """
    
    def __init__(self, db=None):
        """
        Initialize circularity engine
        
        Args:
            db: MongoDB database instance (optional, for storing calculations)
        """
        self.db = db
        logger.info("Circularity Engine initialized successfully")
    
    def calculate_circularity_metrics(
        self,
        input_data: CircularityInputSchema,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        save_calculation: bool = False
    ) -> CircularityResultSchema:
        """
        Calculate comprehensive circularity metrics
        
        Args:
            input_data: Circularity input parameters
            user_id: User ID for tracking (optional)
            project_id: Project ID for linking (optional)
            save_calculation: Whether to save calculation to database
            
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
            
            # Save calculation to database if requested
            if save_calculation and self.db is not None:
                self._save_calculation_to_db(input_data, result, user_id, project_id)
            
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
        
        average_lifespan = material_lifespans.get(input_data.material, 15)
        
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
    
    def _save_calculation_to_db(
        self,
        input_data: CircularityInputSchema,
        result: CircularityResultSchema,
        user_id: Optional[str],
        project_id: Optional[str]
    ):
        """
        Save circularity calculation to MongoDB
        
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
                    "mci_score": result.mci_score,
                    "recycled_content_rate": result.recycled_content_rate,
                    "end_of_life_recycling_rate": result.end_of_life_recycling_rate,
                    "waste_reduction": result.waste_reduction,
                    "circularity_level": result.circularity_level
                },
                "material": input_data.material,
                "created_at": datetime.utcnow()
            }
            
            self.db.circularity_calculations.insert_one(calculation_doc)
            logger.debug("Circularity calculation saved to database")
            
        except Exception as e:
            logger.error(f"Error saving calculation to database: {str(e)}")
    
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
    
    def get_calculation_history(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        material: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get circularity calculation history from database
        
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
                self.db.circularity_calculations
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
    
    def get_mci_trends(
        self,
        user_id: Optional[str] = None,
        material: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get MCI score trends over time
        
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
            from datetime import timedelta
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            query = {"created_at": {"$gte": start_date}}
            if user_id:
                query["user_id"] = user_id
            if material:
                query["material"] = material
            
            calculations = list(
                self.db.circularity_calculations
                .find(query)
                .sort("created_at", 1)
            )
            
            if not calculations:
                return {
                    "trend": "No data",
                    "average_mci": 0,
                    "data_points": []
                }
            
            # Extract MCI scores and dates
            data_points = [
                {
                    "date": calc["created_at"].isoformat(),
                    "mci_score": calc["results"]["mci_score"],
                    "material": calc.get("material")
                }
                for calc in calculations
            ]
            
            # Calculate average and trend
            mci_scores = [dp["mci_score"] for dp in data_points]
            average_mci = sum(mci_scores) / len(mci_scores)
            
            # Simple trend calculation (comparing first half to second half)
            mid_point = len(mci_scores) // 2
            if mid_point > 0:
                first_half_avg = sum(mci_scores[:mid_point]) / mid_point
                second_half_avg = sum(mci_scores[mid_point:]) / (len(mci_scores) - mid_point)
                
                if second_half_avg > first_half_avg * 1.05:
                    trend = "Improving"
                elif second_half_avg < first_half_avg * 0.95:
                    trend = "Declining"
                else:
                    trend = "Stable"
            else:
                trend = "Insufficient data"
            
            return {
                "trend": trend,
                "average_mci": round(average_mci, 3),
                "min_mci": round(min(mci_scores), 3),
                "max_mci": round(max(mci_scores), 3),
                "total_calculations": len(calculations),
                "data_points": data_points
            }
            
        except Exception as e:
            logger.error(f"Error calculating MCI trends: {str(e)}")
            return {"error": str(e)}
    
    def get_material_statistics(self, material: Optional[str] = None) -> Dict[str, Any]:
        """
        Get aggregate statistics for circularity calculations
        
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
                        "avg_mci": {"$avg": "$results.mci_score"},
                        "max_mci": {"$max": "$results.mci_score"},
                        "min_mci": {"$min": "$results.mci_score"},
                        "avg_recycled_content": {"$avg": "$results.recycled_content_rate"},
                        "avg_recycling_rate": {"$avg": "$results.end_of_life_recycling_rate"}
                    }
                },
                {
                    "$sort": {"count": -1}
                }
            ]
            
            results = list(self.db.circularity_calculations.aggregate(pipeline))
            
            # Format results
            statistics = []
            for result in results:
                statistics.append({
                    "material": result["_id"],
                    "total_calculations": result["count"],
                    "average_mci_score": round(result.get("avg_mci", 0), 3),
                    "max_mci_score": round(result.get("max_mci", 0), 3),
                    "min_mci_score": round(result.get("min_mci", 0), 3),
                    "average_recycled_content": round(result.get("avg_recycled_content", 0), 2),
                    "average_recycling_rate": round(result.get("avg_recycling_rate", 0), 2)
                })
            
            return {
                "statistics": statistics,
                "total_materials": len(statistics)
            }
            
        except Exception as e:
            logger.error(f"Error getting material statistics: {str(e)}")
            return {"error": str(e)}


# Factory function to create circularity engine instance
def create_circularity_engine(db=None) -> CircularityEngine:
    """
    Create and return circularity engine instance
    
    Args:
        db: MongoDB database instance (optional)
        
    Returns:
        CircularityEngine instance
    """
    return CircularityEngine(db=db)


# Global circularity engine instance
circularity_engine = CircularityEngine()

def get_circularity_engine(db=None) -> CircularityEngine:
    """
    Get or create global circularity engine instance
    
    Args:
        db: MongoDB database instance (optional)
        
    Returns:
        CircularityEngine instance
    """
    global circularity_engine
    if circularity_engine is None:
        circularity_engine = CircularityEngine(db=db)
    elif db is not None and circularity_engine.db is None:
        circularity_engine.db = db
    return circularity_engine
"""
AI/ML Prediction Engine
Machine learning models for environmental impact prediction
MongoDB compatible version with prediction history tracking
"""

from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd
import joblib
import json
import logging
from pathlib import Path
from datetime import datetime
from bson import ObjectId
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from core.config import settings
from models.schemas import AIPredictionInputSchema, AIPredictionResultSchema

# Configure logging
logger = logging.getLogger(__name__)


class AIEngine:
    """
    AI/ML prediction engine for environmental impact forecasting
    Uses ensemble methods for accurate predictions
    """
    
    def __init__(self, db=None):
        """
        Initialize AI engine and load models
        
        Args:
            db: MongoDB database instance (optional, for storing predictions)
        """
        self.db = db
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.is_trained = False
        
        # Try to load existing models
        self._load_models()
        
        # If models don't exist, initialize new ones
        if not self.is_trained:
            self._initialize_models()
        
        logger.info("AI Engine initialized successfully")
    
    def _load_models(self) -> bool:
        """
        Load pre-trained models from disk
        
        Returns:
            True if models loaded successfully
        """
        try:
            model_path = Path(settings.MODEL_PATH)
            scaler_path = Path(settings.SCALER_PATH)
            features_path = Path(settings.FEATURE_COLUMNS_PATH)
            
            if model_path.exists() and scaler_path.exists() and features_path.exists():
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                
                with open(features_path, 'r') as f:
                    self.feature_columns = json.load(f)
                
                self.is_trained = True
                logger.info("Pre-trained models loaded successfully")
                return True
            else:
                logger.warning("Pre-trained models not found")
                return False
                
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            return False
    
    def _initialize_models(self):
        """Initialize new ML models"""
        # Random Forest for CO2 prediction
        self.model = RandomForestRegressor(
            n_estimators=settings.ML_N_ESTIMATORS,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=settings.ML_RANDOM_STATE,
            n_jobs=-1
        )
        
        # Standard scaler for feature normalization
        self.scaler = StandardScaler()
        
        # Define feature columns
        self.feature_columns = [
            'material_aluminium',
            'material_copper',
            'material_steel',
            'production_volume',
            'energy_renewable',
            'energy_fossil',
            'energy_grid',
            'recycled_content',
            'process_efficiency'
        ]
        
        logger.info("New models initialized")
    
    def predict(
        self,
        input_data: AIPredictionInputSchema,
        user_id: Optional[str] = None,
        save_prediction: bool = False
    ) -> AIPredictionResultSchema:
        """
        Make predictions for environmental impact
        
        Args:
            input_data: Prediction input parameters
            user_id: User ID for tracking predictions (optional)
            save_prediction: Whether to save prediction to database
            
        Returns:
            Prediction results with confidence scores
        """
        try:
            logger.info(f"Making prediction for {input_data.material}")
            
            # If model is not trained, use heuristic prediction
            if not self.is_trained:
                result = self._heuristic_prediction(input_data)
            else:
                # Prepare features
                features = self._prepare_features(input_data)
                
                # Scale features
                features_scaled = self.scaler.transform([features])
                
                # Make prediction
                co2_prediction = self.model.predict(features_scaled)[0]
                
                # Estimate energy consumption (correlated with CO2)
                energy_prediction = self._estimate_energy(input_data, co2_prediction)
                
                # Calculate confidence score
                confidence = self._calculate_confidence(input_data)
                
                # Calculate prediction range (confidence interval)
                prediction_range = self._calculate_prediction_range(
                    co2_prediction,
                    energy_prediction,
                    confidence
                )
                
                result = AIPredictionResultSchema(
                    predicted_co2_emissions=round(co2_prediction, 2),
                    predicted_energy_consumption=round(energy_prediction, 2),
                    confidence_score=round(confidence, 3),
                    prediction_range=prediction_range
                )
            
            # Save prediction to database if requested
            if save_prediction and self.db is not None and user_id:
                self._save_prediction_to_db(input_data, result, user_id)
            
            logger.info(f"Prediction completed: {result.predicted_co2_emissions} kg CO2")
            return result
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            # Fallback to heuristic prediction
            return self._heuristic_prediction(input_data)
    
    def _prepare_features(self, input_data: AIPredictionInputSchema) -> list:
        """
        Prepare feature vector from input data
        
        Args:
            input_data: Prediction input
            
        Returns:
            Feature vector as list
        """
        # One-hot encode material type
        material_aluminium = 1 if input_data.material.value in ['aluminium', 'aluminum'] else 0
        material_copper = 1 if input_data.material.value == 'copper' else 0
        material_steel = 1 if input_data.material.value == 'steel' else 0
        
        # One-hot encode energy source
        energy_renewable = 1 if input_data.energy_source.value in ['renewable', 'solar', 'wind', 'hydro'] else 0
        energy_fossil = 1 if input_data.energy_source.value == 'fossil' else 0
        energy_grid = 1 if input_data.energy_source.value == 'grid_average' else 0
        
        features = [
            material_aluminium,
            material_copper,
            material_steel,
            input_data.production_volume,
            energy_renewable,
            energy_fossil,
            energy_grid,
            input_data.recycled_content,
            input_data.process_efficiency
        ]
        
        return features
    
    def _heuristic_prediction(self, input_data: AIPredictionInputSchema) -> AIPredictionResultSchema:
        """
        Make prediction using heuristic rules when ML model not available
        
        Args:
            input_data: Prediction input
            
        Returns:
            Prediction results
        """
        # Base emission factors (kg CO2 per kg)
        base_factors = {
            'aluminium': 8.0,
            'aluminum': 8.0,
            'copper': 2.5,
            'steel': 1.8
        }
        
        base_co2 = base_factors.get(input_data.material.value, 5.0)
        
        # Adjust for energy source
        energy_multipliers = {
            'renewable': 0.2,
            'fossil': 1.3,
            'grid_average': 1.0,
            'solar': 0.15,
            'wind': 0.15,
            'hydro': 0.2,
            'nuclear': 0.3
        }
        
        energy_mult = energy_multipliers.get(input_data.energy_source.value, 1.0)
        
        # Adjust for recycled content (more recycled = less emissions)
        recycling_benefit = 1 - (input_data.recycled_content / 100 * 0.7)
        
        # Adjust for process efficiency
        efficiency_factor = input_data.process_efficiency / 100
        
        # Calculate CO2 prediction
        co2_prediction = (
            input_data.production_volume *
            base_co2 *
            energy_mult *
            recycling_benefit /
            efficiency_factor
        )
        
        # Estimate energy (MJ per kg)
        energy_factors = {
            'aluminium': 85.0,
            'aluminum': 85.0,
            'copper': 35.0,
            'steel': 25.0
        }
        
        base_energy = energy_factors.get(input_data.material.value, 50.0)
        energy_prediction = (
            input_data.production_volume *
            base_energy *
            recycling_benefit /
            efficiency_factor
        )
        
        # Confidence is lower for heuristic predictions
        confidence = 0.75
        
        # Calculate range
        prediction_range = self._calculate_prediction_range(
            co2_prediction,
            energy_prediction,
            confidence
        )
        
        return AIPredictionResultSchema(
            predicted_co2_emissions=round(co2_prediction, 2),
            predicted_energy_consumption=round(energy_prediction, 2),
            confidence_score=round(confidence, 3),
            prediction_range=prediction_range
        )
    
    def _estimate_energy(self, input_data: AIPredictionInputSchema, co2_emissions: float) -> float:
        """
        Estimate energy consumption based on CO2 emissions
        
        Args:
            input_data: Prediction input
            co2_emissions: Predicted CO2 emissions
            
        Returns:
            Estimated energy consumption in MJ
        """
        # Energy intensity varies by energy source
        energy_intensity_factors = {
            'renewable': 12.0,  # MJ per kg CO2
            'fossil': 8.0,
            'grid_average': 10.0,
            'solar': 15.0,
            'wind': 14.0,
            'hydro': 13.0,
            'nuclear': 11.0
        }
        
        intensity = energy_intensity_factors.get(input_data.energy_source.value, 10.0)
        
        energy = co2_emissions * intensity
        
        return energy
    
    def _calculate_confidence(self, input_data: AIPredictionInputSchema) -> float:
        """
        Calculate confidence score for prediction
        
        Args:
            input_data: Prediction input
            
        Returns:
            Confidence score (0-1)
        """
        confidence = 0.85  # Base confidence
        
        # Higher confidence for common materials
        if input_data.material.value in ['aluminium', 'aluminum', 'steel']:
            confidence += 0.05
        
        # Higher confidence for typical recycled content ranges
        if 0 <= input_data.recycled_content <= 80:
            confidence += 0.05
        
        # Higher confidence for typical process efficiency
        if 70 <= input_data.process_efficiency <= 95:
            confidence += 0.05
        
        return min(1.0, confidence)
    
    def _calculate_prediction_range(
        self,
        co2_prediction: float,
        energy_prediction: float,
        confidence: float
    ) -> Dict[str, float]:
        """
        Calculate prediction range (confidence interval)
        
        Args:
            co2_prediction: CO2 prediction
            energy_prediction: Energy prediction
            confidence: Confidence score
            
        Returns:
            Dictionary with min/max ranges
        """
        # Range increases with lower confidence
        uncertainty = (1 - confidence) * 0.3
        
        co2_range = co2_prediction * uncertainty
        energy_range = energy_prediction * uncertainty
        
        return {
            "co2_min": round(co2_prediction - co2_range, 2),
            "co2_max": round(co2_prediction + co2_range, 2),
            "energy_min": round(energy_prediction - energy_range, 2),
            "energy_max": round(energy_prediction + energy_range, 2)
        }
    
    def _save_prediction_to_db(
        self,
        input_data: AIPredictionInputSchema,
        result: AIPredictionResultSchema,
        user_id: str
    ):
        """
        Save prediction to MongoDB for tracking and analytics
        
        Args:
            input_data: Input parameters
            result: Prediction results
            user_id: User ID
        """
        try:
            if self.db is None:
                return
            
            prediction_doc = {
                "user_id": user_id,
                "input_data": input_data.dict(),
                "predictions": {
                    "co2_emissions": result.predicted_co2_emissions,
                    "energy_consumption": result.predicted_energy_consumption,
                    "confidence_score": result.confidence_score,
                    "prediction_range": result.prediction_range
                },
                "model_version": "1.0",
                "is_trained_model": self.is_trained,
                "created_at": datetime.utcnow()
            }
            
            self.db.predictions.insert_one(prediction_doc)
            logger.debug("Prediction saved to database")
            
        except Exception as e:
            logger.error(f"Error saving prediction to database: {str(e)}")
    
    def train_model(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Train the ML model with new data
        
        Args:
            training_data: DataFrame with training samples
            
        Returns:
            Training metrics
        """
        try:
            logger.info("Starting model training...")
            
            # Prepare features and target
            X = training_data[self.feature_columns]
            y = training_data['co2_emissions']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=settings.ML_TEST_SIZE,
                random_state=settings.ML_RANDOM_STATE
            )
            
            # Fit scaler
            self.scaler.fit(X_train)
            X_train_scaled = self.scaler.transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            # Save models
            self._save_models()
            
            self.is_trained = True
            
            metrics = {
                "train_r2_score": round(train_score, 4),
                "test_r2_score": round(test_score, 4),
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "trained_at": datetime.utcnow().isoformat()
            }
            
            # Save training metrics to database
            if self.db is not None:
                self._save_training_metrics(metrics)
            
            logger.info(f"Model training completed: Test R² = {test_score:.4f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            # Ensure directories exist
            Path(settings.MODEL_PATH).parent.mkdir(parents=True, exist_ok=True)
            
            joblib.dump(self.model, settings.MODEL_PATH)
            joblib.dump(self.scaler, settings.SCALER_PATH)
            
            with open(settings.FEATURE_COLUMNS_PATH, 'w') as f:
                json.dump(self.feature_columns, f)
            
            logger.info("Models saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            raise
    
    def _save_training_metrics(self, metrics: Dict[str, Any]):
        """
        Save training metrics to MongoDB
        
        Args:
            metrics: Training metrics dictionary
        """
        try:
            metrics_doc = {
                "model_version": "1.0",
                "metrics": metrics,
                "feature_columns": self.feature_columns,
                "created_at": datetime.utcnow()
            }
            
            self.db.model_training_history.insert_one(metrics_doc)
            logger.debug("Training metrics saved to database")
            
        except Exception as e:
            logger.error(f"Error saving training metrics: {str(e)}")
    
    def batch_predict(
        self,
        input_list: List[AIPredictionInputSchema],
        user_id: Optional[str] = None,
        save_predictions: bool = False
    ) -> List[AIPredictionResultSchema]:
        """
        Make batch predictions
        
        Args:
            input_list: List of AIPredictionInputSchema objects
            user_id: User ID for tracking (optional)
            save_predictions: Whether to save predictions to database
            
        Returns:
            List of prediction results
        """
        results = []
        for input_data in input_list:
            result = self.predict(input_data, user_id, save_predictions)
            results.append(result)
        
        logger.info(f"Batch prediction completed: {len(results)} predictions")
        return results
    
    def get_prediction_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get prediction history from database
        
        Args:
            user_id: Filter by user ID (optional)
            limit: Maximum number of records to return
            
        Returns:
            List of prediction documents
        """
        if self.db is None:
            return []
        
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            
            predictions = list(
                self.db.predictions
                .find(query)
                .sort("created_at", -1)
                .limit(limit)
            )
            
            # Convert ObjectId to string
            for pred in predictions:
                pred["id"] = str(pred.pop("_id"))
                if "created_at" in pred:
                    pred["created_at"] = pred["created_at"].isoformat()
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error retrieving prediction history: {str(e)}")
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model
        
        Returns:
            Model information dictionary
        """
        info = {
            "is_trained": self.is_trained,
            "model_type": type(self.model).__name__ if self.model else None,
            "feature_columns": self.feature_columns,
            "model_path": str(settings.MODEL_PATH),
            "scaler_path": str(settings.SCALER_PATH)
        }
        
        if self.is_trained and self.model:
            info["n_estimators"] = getattr(self.model, 'n_estimators', None)
            info["max_depth"] = getattr(self.model, 'max_depth', None)
        
        return info


# Factory function to create AI engine instance
def create_ai_engine(db=None) -> AIEngine:
    """
    Create and return AI engine instance
    
    Args:
        db: MongoDB database instance (optional)
        
    Returns:
        AIEngine instance
    """
    return AIEngine(db=db)


# Global AI engine instance (can be initialized with db later)
ai_engine = None

def get_ai_engine(db=None) -> AIEngine:
    """
    Get or create global AI engine instance
    
    Args:
        db: MongoDB database instance (optional)
        
    Returns:
        AIEngine instance
    """
    global ai_engine
    if ai_engine is None:
        ai_engine = AIEngine(db=db)
    elif db is not None and ai_engine.db is None:
        ai_engine.db = db
    return ai_engine
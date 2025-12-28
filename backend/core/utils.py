"""
Utility functions for common operations
Data formatting, validation, file handling, and helper functions
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal
import json
import csv
import pandas as pd
import numpy as np
from pathlib import Path
import hashlib
import re
import logging

from core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


# ==========================================
# Response Formatting
# ==========================================

def success_response(
    data: Any = None,
    message: str = "Success",
    meta: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Format successful API response
    
    Args:
        data: Response data
        message: Success message
        meta: Additional metadata
        
    Returns:
        Formatted response dictionary
    """
    response = {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if meta:
        response["meta"] = meta
    
    return response


def error_response(
    error: str,
    details: Optional[Any] = None,
    status_code: int = 400
) -> Dict[str, Any]:
    """
    Format error API response
    
    Args:
        error: Error message
        details: Error details
        status_code: HTTP status code
        
    Returns:
        Formatted error response dictionary
    """
    response = {
        "success": False,
        "error": error,
        "timestamp": datetime.utcnow().isoformat(),
        "status_code": status_code
    }
    
    if details:
        response["details"] = details
    
    return response


# ==========================================
# Data Validation
# ==========================================

def validate_material_type(material: str) -> bool:
    """
    Validate if material type is supported
    
    Args:
        material: Material name
        
    Returns:
        True if valid
    """
    valid_materials = ["aluminium", "aluminum", "copper", "steel"]
    return material.lower() in valid_materials


def validate_production_type(production_type: str) -> bool:
    """
    Validate if production type is supported
    
    Args:
        production_type: Production type
        
    Returns:
        True if valid
    """
    valid_types = ["primary", "secondary", "recycled", "virgin"]
    return production_type.lower() in valid_types


def validate_energy_source(energy_source: str) -> bool:
    """
    Validate if energy source is supported
    
    Args:
        energy_source: Energy source type
        
    Returns:
        True if valid
    """
    valid_sources = ["renewable", "fossil", "grid_average", "nuclear", "hydro", "solar", "wind"]
    return energy_source.lower() in valid_sources


def validate_numeric_range(
    value: Union[int, float],
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None
) -> bool:
    """
    Validate if numeric value is within range
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        True if valid
    """
    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False
    return True


# ==========================================
# Data Transformation
# ==========================================

def normalize_material_name(material: str) -> str:
    """
    Normalize material name to standard format
    
    Args:
        material: Material name
        
    Returns:
        Normalized material name
    """
    material = material.lower().strip()
    
    # Handle common variations
    if material in ["aluminium", "aluminum", "al"]:
        return "aluminium"
    elif material in ["copper", "cu"]:
        return "copper"
    elif material in ["steel", "iron", "fe"]:
        return "steel"
    
    return material


def convert_units(
    value: float,
    from_unit: str,
    to_unit: str
) -> float:
    """
    Convert between common units
    
    Args:
        value: Value to convert
        from_unit: Source unit
        to_unit: Target unit
        
    Returns:
        Converted value
    """
    # Weight conversions
    weight_conversions = {
        ("kg", "g"): 1000,
        ("g", "kg"): 0.001,
        ("kg", "ton"): 0.001,
        ("ton", "kg"): 1000,
        ("lb", "kg"): 0.453592,
        ("kg", "lb"): 2.20462,
    }
    
    # Energy conversions (to MJ)
    energy_conversions = {
        ("kwh", "mj"): 3.6,
        ("mj", "kwh"): 0.277778,
        ("gj", "mj"): 1000,
        ("mj", "gj"): 0.001,
    }
    
    # Distance conversions
    distance_conversions = {
        ("km", "m"): 1000,
        ("m", "km"): 0.001,
        ("km", "mi"): 0.621371,
        ("mi", "km"): 1.60934,
    }
    
    conversion_key = (from_unit.lower(), to_unit.lower())
    
    # Check all conversion dictionaries
    for conversions in [weight_conversions, energy_conversions, distance_conversions]:
        if conversion_key in conversions:
            return value * conversions[conversion_key]
    
    # If no conversion found, return original value
    logger.warning(f"No conversion found for {from_unit} to {to_unit}")
    return value


# ==========================================
# File Handling
# ==========================================

def read_csv_file(file_path: str) -> pd.DataFrame:
    """
    Read CSV file into pandas DataFrame
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        Pandas DataFrame
    """
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Successfully read CSV file: {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error reading CSV file {file_path}: {str(e)}")
        raise


def save_csv_file(df: pd.DataFrame, file_path: str) -> bool:
    """
    Save pandas DataFrame to CSV file
    
    Args:
        df: DataFrame to save
        file_path: Output file path
        
    Returns:
        True if successful
    """
    try:
        df.to_csv(file_path, index=False)
        logger.info(f"Successfully saved CSV file: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving CSV file {file_path}: {str(e)}")
        return False


def get_file_hash(file_path: str) -> str:
    """
    Calculate SHA256 hash of file
    
    Args:
        file_path: Path to file
        
    Returns:
        File hash string
    """
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


# ==========================================
# Data Formatting
# ==========================================

def format_number(
    value: Union[int, float],
    decimals: int = 2,
    include_commas: bool = True
) -> str:
    """
    Format number with specified decimals and commas
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        include_commas: Whether to include thousand separators
        
    Returns:
        Formatted number string
    """
    if include_commas:
        return f"{value:,.{decimals}f}"
    else:
        return f"{value:.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format number as percentage
    
    Args:
        value: Value between 0 and 1
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def format_date(dt: Union[datetime, date], format_str: str = "%Y-%m-%d") -> str:
    """
    Format date/datetime object
    
    Args:
        dt: Date or datetime object
        format_str: Format string
        
    Returns:
        Formatted date string
    """
    return dt.strftime(format_str)


# ==========================================
# Calculation Utilities
# ==========================================

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values
    
    Args:
        old_value: Original value
        new_value: New value
        
    Returns:
        Percentage change
    """
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100


def round_to_significant_figures(value: float, sig_figs: int = 3) -> float:
    """
    Round to specified significant figures
    
    Args:
        value: Value to round
        sig_figs: Number of significant figures
        
    Returns:
        Rounded value
    """
    if value == 0:
        return 0
    return round(value, -int(np.floor(np.log10(abs(value)))) + (sig_figs - 1))


def weighted_average(values: List[float], weights: List[float]) -> float:
    """
    Calculate weighted average
    
    Args:
        values: List of values
        weights: List of weights
        
    Returns:
        Weighted average
    """
    if len(values) != len(weights):
        raise ValueError("Values and weights must have same length")
    
    if sum(weights) == 0:
        return 0
    
    return sum(v * w for v, w in zip(values, weights)) / sum(weights)


# ==========================================
# String Utilities
# ==========================================

def snake_to_camel(snake_str: str) -> str:
    """
    Convert snake_case to camelCase
    
    Args:
        snake_str: String in snake_case
        
    Returns:
        String in camelCase
    """
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def camel_to_snake(camel_str: str) -> str:
    """
    Convert camelCase to snake_case
    
    Args:
        camel_str: String in camelCase
        
    Returns:
        String in snake_case
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


# ==========================================
# JSON Utilities
# ==========================================

class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for special types
    """
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient='records')
        return super().default(obj)


def safe_json_dumps(data: Any, **kwargs) -> str:
    """
    Safely serialize data to JSON string
    
    Args:
        data: Data to serialize
        **kwargs: Additional arguments for json.dumps
        
    Returns:
        JSON string
    """
    return json.dumps(data, cls=CustomJSONEncoder, **kwargs)


# ==========================================
# Logging Utilities
# ==========================================

def log_execution_time(func):
    """
    Decorator to log function execution time
    
    Usage:
        @log_execution_time
        def my_function():
            pass
    """
    from functools import wraps
    import time
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
        return result
    
    return wrapper
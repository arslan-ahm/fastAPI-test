"""Utility functions and helpers."""

from typing import List, Dict, Any
import re
import json
from pathlib import Path


def clean_ingredient_name(ingredient: str) -> str:
    """
    Clean and standardize ingredient names.
    
    Args:
        ingredient: Raw ingredient name
        
    Returns:
        Cleaned ingredient name
    """
    # Remove extra whitespace and convert to lowercase
    ingredient = ingredient.strip().lower()
    
    # Remove common prefixes and suffixes
    prefixes_to_remove = ['fresh', 'organic', 'chopped', 'diced', 'sliced']
    for prefix in prefixes_to_remove:
        if ingredient.startswith(f"{prefix} "):
            ingredient = ingredient[len(prefix):].strip()
    
    # Remove quantities and measurements
    measurement_pattern = r'\b\d+(?:\.\d+)?\s*(?:cups?|tbsp|tsp|oz|lbs?|grams?|kg|ml|liters?)\b'
    ingredient = re.sub(measurement_pattern, '', ingredient).strip()
    
    # Remove extra spaces
    ingredient = re.sub(r'\s+', ' ', ingredient)
    
    return ingredient


def validate_ingredients(ingredients: List[str]) -> List[str]:
    """
    Validate and filter ingredients list.
    
    Args:
        ingredients: List of ingredient names
        
    Returns:
        Validated list of ingredients
    """
    valid_ingredients = []
    
    for ingredient in ingredients:
        cleaned = clean_ingredient_name(ingredient)
        
        # Skip empty or very short ingredients
        if len(cleaned) < 2:
            continue
            
        # Skip common non-food items
        non_food_items = [
            'plate', 'bowl', 'knife', 'spoon', 'fork', 'cutting board',
            'table', 'counter', 'kitchen', 'pan', 'pot', 'container'
        ]
        
        if any(item in cleaned for item in non_food_items):
            continue
            
        valid_ingredients.append(cleaned)
    
    return valid_ingredients


def format_recipe_response(recipe_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format recipe data for consistent response structure.
    
    Args:
        recipe_data: Raw recipe data dictionary
        
    Returns:
        Formatted recipe data
    """
    formatted = recipe_data.copy()
    
    # Ensure instructions are properly formatted
    if isinstance(formatted.get('instructions'), str):
        # Split string instructions into list
        instructions = formatted['instructions'].split('\n')
        formatted['instructions'] = [inst.strip() for inst in instructions if inst.strip()]
    
    # Ensure ingredients are properly formatted
    if isinstance(formatted.get('ingredients'), str):
        # Split string ingredients into list
        ingredients = formatted['ingredients'].split('\n')
        formatted['ingredients'] = [ing.strip() for ing in ingredients if ing.strip()]
    
    # Calculate total time if not provided
    if 'total_time' not in formatted:
        prep_time = formatted.get('prep_time', 0)
        cook_time = formatted.get('cook_time', 0)
        formatted['total_time'] = prep_time + cook_time
    
    return formatted


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load JSON data from file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Loaded JSON data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_json_file(data: Dict[str, Any], file_path: str) -> bool:
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        file_path: Path to save file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove extra spaces and dots
    filename = re.sub(r'\.+', '.', filename)
    filename = re.sub(r'\s+', '_', filename)
    
    # Ensure filename is not too long
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_length = 255 - len(ext) - 1 if ext else 255
        filename = name[:max_name_length] + ('.' + ext if ext else '')
    
    return filename.strip('.')

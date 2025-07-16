from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class CountryStyle(str, Enum):
    """Available country-based food styles with Pakistani as primary focus."""
    PAKISTANI = "Pakistani"  # Primary/Default
    INDIAN = "Indian"
    BANGLADESHI = "Bangladeshi"
    CHINESE = "Chinese"
    TURKISH = "Turkish"
    ARABIC = "Arabic"
    PERSIAN = "Persian"
    AFGHAN = "Afghan"
    ITALIAN = "Italian"
    MEXICAN = "Mexican"
    THAI = "Thai"
    JAPANESE = "Japanese"
    FRENCH = "French"
    AMERICAN = "American"
    MEDITERRANEAN = "Mediterranean"
    ANY = "Any"


class DietType(str, Enum):
    """Available diet types (simplified)."""
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    NON_VEG = "non_veg"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"


class RecipeRequest(BaseModel):
    """Request model for recipe generation from ingredients."""
    
    ingredients: List[str] = Field(
        ...,
        min_items=1,
        max_items=20,
        description="List of ingredients to use in the recipe",
        example=["chicken", "onions", "tomatoes", "ginger-garlic paste"]
    )
    style: Optional[CountryStyle] = Field(
        CountryStyle.PAKISTANI,  # Default to Pakistani cuisine
        description="What style of food do you want?",
        example="Pakistani"
    )
    diet: Optional[List[DietType]] = Field(
        default_factory=list,
        description="Any dietary preferences?",
        example=["vegetarian"]
    )
    people: Optional[int] = Field(
        4,
        ge=1,
        le=12,
        description="How many people will eat this?",
        example=4
    )


class Recipe(BaseModel):
    """Recipe response model."""
    
    name: str = Field(..., description="Name of the recipe")
    description: str = Field(..., description="Brief description of the recipe")
    ingredients: List[str] = Field(..., description="List of ingredients with quantities")
    steps: List[str] = Field(..., description="Step-by-step cooking instructions")
    prep_time: int = Field(..., description="Preparation time in minutes")
    cook_time: int = Field(..., description="Cooking time in minutes")
    total_time: int = Field(..., description="Total time in minutes")
    people: int = Field(..., description="Number of people this serves")
    difficulty: str = Field(..., description="How hard is it? (Easy, Medium, Hard)")
    style: str = Field(..., description="What style of food is this?")
    diet_info: List[str] = Field(default_factory=list, description="Diet information")
    nutrition: Optional[str] = Field(None, description="Nutritional information")
    tips: Optional[List[str]] = Field(default_factory=list, description="Helpful cooking tips")


class RecipeResponse(BaseModel):
    """Response model for recipe generation."""
    
    success: bool = Field(..., description="Whether the request was successful")
    recipe: Optional[Recipe] = Field(None, description="Generated recipe")
    message: Optional[str] = Field(None, description="Response message")


class ImageRecipeRequest(BaseModel):
    """Request model for recipe generation from image."""
    
    style: Optional[CountryStyle] = Field(
        CountryStyle.PAKISTANI,  # Default to Pakistani cuisine
        description="What style of food do you want?",
        example="Pakistani"
    )
    diet: Optional[List[DietType]] = Field(
        default_factory=list,
        description="Any dietary preferences?",
        example=["vegetarian"]
    )
    people: Optional[int] = Field(
        4,
        ge=1,
        le=12,
        description="How many people will eat this?",
        example=4
    )


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="API status")
    message: str = Field(..., description="Health check message")
    version: str = Field(..., description="API version")

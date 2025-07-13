"""Recipe generation service using LLM7."""

from typing import List, Optional
import json

from ..core.config import settings
from ..core.exceptions import RecipeGenerationError
from ..models.schemas import Recipe, RecipeRequest, DietType, CountryStyle
from .llm7_service import LLM7Service


class RecipeService:
    """Service for generating recipes using LLM7."""
    
    def __init__(self):
        """Initialize the recipe service with LLM7."""
        # Initialize LLM7 service as primary
        try:
            self.llm7_service = LLM7Service()
            self.primary_service = "llm7"
        except Exception as e:
            raise Exception(f"Failed to initialize LLM7 service: {e}")
            
        if not self.primary_service:
            raise Exception("No AI service available. Please configure LLM7_TOKEN environment variable.")

    async def generate_recipe_from_ingredients(
        self, 
        request: RecipeRequest
    ) -> Recipe:
        """Generate a recipe from a list of ingredients using LLM7 service."""
        try:
            # Use LLM7 service
            if self.llm7_service and self.primary_service == "llm7":
                return await self.llm7_service.generate_recipe_from_ingredients(request)
                
            raise RecipeGenerationError("LLM7 service not available")
            
        except RecipeGenerationError:
            raise
        except Exception as e:
            raise RecipeGenerationError(f"Failed to generate recipe: {str(e)}")
    
    async def generate_recipe_from_image_ingredients(
        self,
        ingredients: List[str],
        style: Optional[str] = None,
        diet: Optional[List[DietType]] = None,
        people: int = 4
    ) -> Recipe:
        """Generate a recipe from ingredients extracted from an image."""
        try:
            # Create a request object with the extracted ingredients
            request = RecipeRequest(
                ingredients=ingredients,
                style=style,
                diet=diet or [],
                people=people
            )
            
            return await self.generate_recipe_from_ingredients(request)
            
        except Exception as e:
            raise RecipeGenerationError(f"Failed to generate recipe from image ingredients: {str(e)}")
    
    async def extract_ingredients_and_generate_recipe(
        self, 
        image_data: bytes,
        style: Optional[CountryStyle] = None,
        diet: Optional[List[DietType]] = None,
        people: int = 4
    ) -> Recipe:
        """Extract ingredients from image and generate recipe using LLM7 service."""
        try:
            # Use LLM7 service for image processing
            if self.llm7_service and self.primary_service == "llm7":
                return await self.llm7_service.extract_ingredients_and_generate_recipe(
                    image_data, style, diet, people
                )
                
            raise RecipeGenerationError("LLM7 service not available for image processing")
            
        except RecipeGenerationError:
            raise
        except Exception as e:
            raise RecipeGenerationError(f"Failed to process image and generate recipe: {str(e)}")

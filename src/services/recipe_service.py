"""Recipe generation service using LLM7."""

from typing import List, Optional
import json

from ..core.config import settings
from ..core.exceptions import RecipeGenerationError, OpenAIKeyMissingError
from ..models.schemas import Recipe, RecipeRequest, DietType, CountryStyle
from .llm7_service import LLM7Service

# Optional import for Gemini service (fallback)
try:
    from .gemini_service import GeminiService
    GEMINI_AVAILABLE = True
except ImportError:
    GeminiService = None
    GEMINI_AVAILABLE = False


class RecipeService:
    """Service for generating recipes using LLM7 with fallback options."""
    
    def __init__(self):
        """Initialize the recipe service with LLM7 as primary."""
        # Initialize LLM7 service as primary
        try:
            self.llm7_service = LLM7Service()
            self.primary_service = "llm7"
        except Exception as e:
            print(f"Warning: Failed to initialize LLM7 service: {e}")
            self.llm7_service = None
            self.primary_service = None
        
        # Initialize Gemini as fallback (if available)
        if GEMINI_AVAILABLE:
            try:
                self.gemini_service = GeminiService()
                if not self.primary_service:
                    self.primary_service = "gemini"
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini service: {e}")
                self.gemini_service = None
        else:
            print("Warning: Gemini service not available (google.generativeai not installed)")
            self.gemini_service = None
            
        if not self.primary_service:
            raise OpenAIKeyMissingError("No AI service available. Please configure LLM7_TOKEN or GEMINI_API_KEY.")

    async def generate_recipe_from_ingredients(
        self, 
        request: RecipeRequest
    ) -> Recipe:
        """Generate a recipe from a list of ingredients using available AI service."""
        try:
            # Try LLM7 service first
            if self.llm7_service and self.primary_service == "llm7":
                try:
                    return await self.llm7_service.generate_recipe_from_ingredients(request)
                except Exception as e:
                    print(f"LLM7 service failed, trying fallback: {e}")
                    
            # Fallback to Gemini service
            if self.gemini_service:
                return await self.gemini_service.generate_recipe_from_ingredients(request)
                
            raise RecipeGenerationError("No AI service available")
            
        except RecipeGenerationError:
            raise
        except Exception as e:
            raise RecipeGenerationError(f"Failed to generate recipe: {str(e)}")
            
            # Generate the recipe
            response = await self.llm.ainvoke(messages)
            
            # Parse the response
            recipe_data = self._parse_recipe_response(response.content)
            
            return Recipe(**recipe_data)
            
        except Exception as e:
            error_message = str(e)
            if "429" in error_message or "quota" in error_message.lower():
                raise RecipeGenerationError("OpenAI API quota exceeded. Please check your billing and usage limits.")
            elif "401" in error_message or "unauthorized" in error_message.lower():
                raise RecipeGenerationError("Invalid OpenAI API key. Please check your API key configuration.")
            else:
                raise RecipeGenerationError(f"Failed to generate recipe: {error_message}")
    
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
        """Extract ingredients from image and generate recipe using available AI service."""
        try:
            # Try LLM7 service first (it has better image processing)
            if self.llm7_service and self.primary_service == "llm7":
                try:
                    return await self.llm7_service.extract_ingredients_and_generate_recipe(
                        image_data, style, diet, people
                    )
                except Exception as e:
                    print(f"LLM7 service failed, trying fallback: {e}")
                    
            # Fallback to Gemini service
            if self.gemini_service:
                return await self.gemini_service.extract_ingredients_and_generate_recipe(
                    image_data, style, diet, people
                )
                
            raise RecipeGenerationError("No AI service available for image processing")
            
        except RecipeGenerationError:
            raise
        except Exception as e:
            raise RecipeGenerationError(f"Failed to process image and generate recipe: {str(e)}")

"""Gemini AI service for image analysis and recipe generation."""

import base64
import json
from typing import List, Optional
from PIL import Image
import io

# Optional import for Google Generative AI
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

from ..core.config import settings
from ..core.exceptions import ImageProcessingError, RecipeGenerationError, OpenAIKeyMissingError
from ..models.schemas import Recipe, RecipeRequest, DietType


class GeminiService:
    """Service for image analysis and recipe generation using Google Gemini."""
    
    def __init__(self):
        """Initialize the Gemini service."""
        if not GENAI_AVAILABLE:
            raise ImportError("google.generativeai is not installed")
            
        if not settings.gemini_api_key:
            raise OpenAIKeyMissingError("Gemini API key is not configured. Please set GEMINI_API_KEY environment variable.")
            
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
    
    async def extract_ingredients_and_generate_recipe(
        self, 
        image_data: bytes,
        style: Optional[str] = None,
        diet: Optional[List[DietType]] = None,
        people: int = 4
    ) -> Recipe:
        """
        Extract ingredients from image and generate recipe in one step using Gemini.
        
        Args:
            image_data: Raw image data bytes
            style: Food style preference
            diet: Diet preferences
            people: Number of people to serve
            
        Returns:
            Generated Recipe object
        """
        try:
            # Process and validate the image
            processed_image = self._process_image(image_data)
            
            # Create the comprehensive prompt
            prompt = self._create_comprehensive_prompt(style, diet, people)
            
            # Generate recipe using Gemini vision
            response = self.model.generate_content([prompt, processed_image])
            
            # Parse the response
            recipe_data = self._parse_recipe_response(response.text)
            
            return Recipe(**recipe_data)
            
        except Exception as e:
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                raise RecipeGenerationError("Gemini API quota exceeded. Please check your billing and usage limits.")
            elif "unauthorized" in str(e).lower() or "401" in str(e):
                raise RecipeGenerationError("Invalid Gemini API key. Please check your API key configuration.")
            else:
                raise RecipeGenerationError(f"Failed to process image and generate recipe: {str(e)}")
    
    async def generate_recipe_from_ingredients(
        self, 
        request: RecipeRequest
    ) -> Recipe:
        """Generate a recipe from a list of ingredients using Gemini."""
        try:
            # Create prompt for text-based recipe generation
            prompt = self._create_text_recipe_prompt(request)
            
            # Generate the recipe
            response = self.model.generate_content(prompt)
            
            # Parse the response
            recipe_data = self._parse_recipe_response(response.text)
            
            return Recipe(**recipe_data)
            
        except Exception as e:
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                raise RecipeGenerationError("Gemini API quota exceeded. Please check your billing and usage limits.")
            elif "unauthorized" in str(e).lower() or "401" in str(e):
                raise RecipeGenerationError("Invalid Gemini API key. Please check your API key configuration.")
            else:
                raise RecipeGenerationError(f"Failed to generate recipe: {str(e)}")
    
    def _process_image(self, image_data: bytes) -> Image.Image:
        """
        Process and validate the uploaded image.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Processed PIL Image
        """
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image if it's too large (max 1024x1024 for API efficiency)
            max_size = (1024, 1024)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            raise ImageProcessingError(f"Invalid image format: {str(e)}")
    
    def _create_comprehensive_prompt(
        self, 
        style: Optional[str], 
        diet: Optional[List[DietType]], 
        people: int
    ) -> str:
        """Create a comprehensive prompt for image analysis and recipe generation."""
        
        # Build diet preferences string
        diet_preferences = ""
        if diet:
            diet_list = [d.value.replace("_", " ") for d in diet]
            diet_preferences = f"Diet preferences: {', '.join(diet_list)}"
        
        # Build style preference string
        style_preference = f"Food style: {style}" if style and style != "Any" else "Food style: Any (be creative)"
        
        prompt = f"""
You are a professional chef and food expert. Analyze this image and:

1. IDENTIFY all visible ingredients in the image
2. CREATE a complete, unique recipe using those ingredients

Requirements:
- {style_preference}
- {diet_preferences}
- Serves {people} people
- Be creative and practical
- Include exact measurements
- Provide step-by-step instructions

Please respond with a valid JSON object in this EXACT format:
{{
    "name": "Creative Recipe Name",
    "description": "Brief description of the dish",
    "ingredients": ["ingredient 1 with exact quantity", "ingredient 2 with exact quantity"],
    "steps": ["step 1", "step 2", "step 3"],
    "prep_time": 15,
    "cook_time": 30,
    "total_time": 45,
    "people": {people},
    "difficulty": "Easy|Medium|Hard",
    "style": "{style if style else 'Fusion'}",
    "diet_info": ["vegetarian", "dairy_free"],
    "nutrition": "Brief nutritional information",
    "tips": ["helpful tip 1", "helpful tip 2"]
}}

Important: Only use ingredients that you can clearly see in the image. Be specific about quantities and cooking methods.
"""
        return prompt
    
    def _create_text_recipe_prompt(self, request: RecipeRequest) -> str:
        """Create prompt for text-based recipe generation."""
        
        # Build diet preferences string
        diet_preferences = ""
        if request.diet:
            diet_list = [d.value.replace("_", " ") for d in request.diet]
            diet_preferences = f"Diet preferences: {', '.join(diet_list)}"
        
        # Build style preference string
        style_preference = f"Food style: {request.style.value}" if request.style and request.style.value != "Any" else "Food style: Any (be creative)"
        
        prompt = f"""
You are a professional chef. Create a unique, delicious recipe using these ingredients: {', '.join(request.ingredients)}

Requirements:
- {style_preference}
- {diet_preferences}
- Serves {request.people} people
- Be creative but practical for home cooking
- Include exact measurements
- Provide clear step-by-step instructions

Please respond with a valid JSON object in this EXACT format:
{{
    "name": "Creative Recipe Name",
    "description": "Brief description of the dish",
    "ingredients": ["ingredient 1 with exact quantity", "ingredient 2 with exact quantity"],
    "steps": ["step 1", "step 2", "step 3"],
    "prep_time": 15,
    "cook_time": 30,
    "total_time": 45,
    "people": {request.people},
    "difficulty": "Easy|Medium|Hard",
    "style": "{request.style.value if request.style else 'Fusion'}",
    "diet_info": ["vegetarian", "dairy_free"],
    "nutrition": "Brief nutritional information",
    "tips": ["helpful tip 1", "helpful tip 2"]
}}

Make the recipe unique and creative while being practical to cook at home.
"""
        return prompt
    
    def _parse_recipe_response(self, response_content: str) -> dict:
        """Parse the Gemini response into a recipe dictionary."""
        try:
            # Clean up the response
            response_content = response_content.strip()
            
            # Remove markdown code block markers if present
            if response_content.startswith("```json"):
                response_content = response_content[7:]
            elif response_content.startswith("```"):
                response_content = response_content[3:]
            
            if response_content.endswith("```"):
                response_content = response_content[:-3]
            
            # Try to find JSON in the response
            start_idx = response_content.find('{')
            end_idx = response_content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_content[start_idx:end_idx]
                recipe_data = json.loads(json_str)
            else:
                recipe_data = json.loads(response_content.strip())
            
            # Validate and set defaults for required fields
            required_fields = {
                "name": "Delicious Recipe",
                "description": "A tasty dish made with fresh ingredients",
                "ingredients": [],
                "steps": [],
                "prep_time": 15,
                "cook_time": 30,
                "total_time": 45,
                "people": 4,
                "difficulty": "Medium",
                "style": "Fusion",
                "diet_info": [],
                "nutrition": "Nutritional information not available",
                "tips": []
            }
            
            for field, default_value in required_fields.items():
                if field not in recipe_data:
                    recipe_data[field] = default_value
            
            # Ensure ingredients and steps are lists
            if isinstance(recipe_data.get('ingredients'), str):
                recipe_data['ingredients'] = [ing.strip() for ing in recipe_data['ingredients'].split('\n') if ing.strip()]
            
            if isinstance(recipe_data.get('steps'), str):
                recipe_data['steps'] = [step.strip() for step in recipe_data['steps'].split('\n') if step.strip()]
            
            return recipe_data
            
        except json.JSONDecodeError as e:
            raise RecipeGenerationError(f"Failed to parse recipe response: {str(e)}")
        except Exception as e:
            raise RecipeGenerationError(f"Error processing recipe response: {str(e)}")

"""LLM7 service for recipe generation using OpenAI-compatible API."""

import base64
import json
from typing import List, Optional
from PIL import Image
import io
import openai

from ..core.config import settings
from ..core.exceptions import ImageProcessingError, RecipeGenerationError, OpenAIKeyMissingError
from ..models.schemas import Recipe, RecipeRequest, DietType, CountryStyle


class LLM7Service:
    """Service for recipe generation using LLM7's OpenAI-compatible API."""
    
    def __init__(self):
        """Initialize the LLM7 service."""
        if not settings.llm7_token:
            raise OpenAIKeyMissingError("LLM7 token is not configured. Please set LLM7_TOKEN environment variable.")
            
        # Initialize OpenAI client with LLM7 configuration
        self.client = openai.OpenAI(
            base_url=settings.llm7_base_url,
            api_key=settings.llm7_token
        )
    
    async def extract_ingredients_and_generate_recipe(
        self, 
        image_data: bytes,
        style: CountryStyle = CountryStyle.PAKISTANI,
        diet: Optional[List[DietType]] = None,
        people: int = 4
    ) -> Recipe:
        """
        Extract ingredients from image and generate recipe using LLM7's vision model.
        
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
            image_base64 = self._process_image_to_base64(image_data)
            
            # Create the comprehensive prompt for image analysis
            prompt = self._create_image_analysis_prompt(style, diet, people)
            
            # Generate recipe using LLM7 vision model
            response = self.client.chat.completions.create(
                model=settings.llm7_image_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            # Parse the response
            recipe_data = self._parse_recipe_response(response.choices[0].message.content)
            
            return Recipe(**recipe_data)
            
        except Exception as e:
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                raise RecipeGenerationError("LLM7 API quota exceeded. Please check your usage limits.")
            elif "unauthorized" in str(e).lower() or "401" in str(e):
                raise RecipeGenerationError("Invalid LLM7 token. Please check your token configuration.")
            else:
                raise RecipeGenerationError(f"Failed to process image and generate recipe: {str(e)}")
    
    async def generate_recipe_from_ingredients(
        self, 
        request: RecipeRequest
    ) -> Recipe:
        """Generate a recipe from a list of ingredients using LLM7's text model."""
        try:
            # Create prompt for text-based recipe generation
            prompt = self._create_text_recipe_prompt(request)
            
            # Generate the recipe using LLM7's text model
            response = self.client.chat.completions.create(
                model=settings.llm7_text_model,
                messages=[
                    {"role": "system", "content": "You are a professional chef and recipe expert. Always respond with valid JSON in the exact format requested."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            # Parse the response
            recipe_data = self._parse_recipe_response(response.choices[0].message.content)
            
            return Recipe(**recipe_data)
            
        except Exception as e:
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                raise RecipeGenerationError("LLM7 API quota exceeded. Please check your usage limits.")
            elif "unauthorized" in str(e).lower() or "401" in str(e):
                raise RecipeGenerationError("Invalid LLM7 token. Please check your token configuration.")
            else:
                raise RecipeGenerationError(f"Failed to generate recipe from ingredients: {str(e)}")
    
    def _process_image_to_base64(self, image_data: bytes) -> str:
        """Process and validate image, then convert to base64."""
        try:
            # Open and validate the image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if image is too large (max 1024x1024 for efficiency)
            max_size = (1024, 1024)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            return img_base64
            
        except Exception as e:
            raise ImageProcessingError(f"Failed to process image: {str(e)}")
    
    def _create_image_analysis_prompt(
        self, 
        style: CountryStyle, 
        diet: Optional[List[DietType]], 
        people: int
    ) -> str:
        """Create a comprehensive prompt for image analysis and recipe generation."""
        
        # Ensure style is a CountryStyle enum
        if isinstance(style, str):
            try:
                style = CountryStyle(style)
            except ValueError:
                style = CountryStyle.PAKISTANI  # Default fallback
        
        # Build diet preferences string
        diet_preferences = ""
        if diet:
            diet_list = [d.value.replace("_", " ") for d in diet]
            diet_preferences = f"Diet preferences: {', '.join(diet_list)}"
        
        # Build style preference string with Pakistani focus
        if style == CountryStyle.PAKISTANI:
            style_guidance = """
Pakistani cuisine focus: Create authentic Pakistani dishes using traditional spices and cooking methods. 
Include common Pakistani ingredients like:
- Spices: red chili powder, turmeric, coriander powder, cumin powder, garam masala, bay leaves
- Fresh ingredients: ginger-garlic paste, green chilies, fresh coriander, mint
- Cooking methods: bhuna (sautéing), dum cooking, tandoori style
- Popular dishes: biryani, karahi, qorma, haleem, nihari, pulao, kebabs
"""
        else:
            style_guidance = f"Food style: {style.value} cuisine with authentic flavors and traditional cooking methods"
        
        prompt = f"""
You are a professional Pakistani chef with expertise in South Asian and international cuisines. Analyze this image and:

1. IDENTIFY all visible ingredients in the image (be thorough - look for spices, vegetables, meat, grains)
2. CREATE an authentic, delicious recipe using those ingredients

{style_guidance}

Requirements:
- {diet_preferences}
- Serves {people} people
- Use traditional cooking techniques and authentic spice combinations
- Include precise measurements in both metric and local units where applicable
- Provide detailed, step-by-step instructions
- Include cooking tips for best results

Please respond with a valid JSON object in this EXACT format:
{{
    "name": "Recipe Name (in English with Urdu/local name if applicable)",
    "description": "Detailed description highlighting the dish's origin, flavors, and appeal",
    "ingredients": [
        "ingredient 1 with precise measurement",
        "ingredient 2 with precise measurement"
    ],
    "instructions": [
        "Detailed step 1 with cooking techniques",
        "Detailed step 2 with timing and visual cues"
    ],
    "prep_time": 15,
    "cook_time": 30,
    "total_time": 45,
    "servings": {people},
    "difficulty": "Easy",
    "cuisine": "{style.value}",
    "diet_tags": {json.dumps([d.value for d in diet] if diet else [])},
    "nutrition": "Detailed nutritional benefits and calorie information",
    "tips": [
        "Professional cooking tip 1",
        "Storage and serving suggestion",
        "Variation or substitution tip"
    ]
}}

Make sure the response is valid JSON only, no additional text.
"""
        return prompt
    
    def _create_text_recipe_prompt(self, request: RecipeRequest) -> str:
        """Create a prompt for text-based recipe generation from ingredients."""
        
        # Format ingredients
        ingredients_list = ", ".join(request.ingredients)
        
        # Ensure style is a CountryStyle enum
        style = request.style
        if isinstance(style, str):
            try:
                style = CountryStyle(style)
            except ValueError:
                style = CountryStyle.PAKISTANI  # Default fallback
        
        # Build diet preferences string
        diet_preferences = ""
        if request.diet:
            diet_list = [d.value.replace("_", " ") for d in request.diet]
            diet_preferences = f"Diet preferences: {', '.join(diet_list)}"
        
        # Build style preference string with Pakistani focus
        if style == CountryStyle.PAKISTANI:
            style_guidance = """
Pakistani cuisine focus: Create authentic Pakistani dishes with traditional flavors. Use these guidelines:
- Traditional spices: red chili powder, turmeric (haldi), coriander powder (dhania), cumin (zeera), garam masala
- Common ingredients: ginger-garlic paste, green chilies, fresh coriander (hara dhania), yogurt, onions
- Cooking techniques: bhuna (sautéing until oil separates), dum cooking, slow cooking for rich flavors
- Authentic dishes: biryani, karahi, qorma, pulao, kebabs, curry, haleem, nihari
- Use traditional measurements where applicable (e.g., "1 cup" for rice, "1 tsp" for spices)
"""
        elif style in [CountryStyle.INDIAN, CountryStyle.BANGLADESHI]:
            style_guidance = f"{style.value} cuisine with authentic spices and traditional cooking methods"
        else:
            style_guidance = f"{style.value} cuisine with authentic flavors and traditional cooking methods"
        
        prompt = f"""
You are a professional Pakistani chef with expertise in South Asian and international cuisines. Create an authentic, delicious recipe using these ingredients: {ingredients_list}

{style_guidance}

Requirements:
- {diet_preferences}
- Serves {request.people} people
- Use traditional cooking techniques and authentic spice combinations
- Include precise measurements and detailed instructions
- Make it practical for home cooking
- Include helpful cooking tips and techniques

Please respond with a valid JSON object in this EXACT format:
{{
    "name": "Recipe Name (include local name if applicable)",
    "description": "Rich description highlighting flavors, origin, and what makes this dish special",
    "ingredients": [
        "ingredient 1 with precise measurement (e.g., '500g chicken, cut into pieces')",
        "ingredient 2 with precise measurement (e.g., '2 tsp red chili powder')"
    ],
    "instructions": [
        "Detailed step 1 with cooking techniques and timing",
        "Detailed step 2 with visual cues and tips"
    ],
    "prep_time": 15,
    "cook_time": 30,
    "total_time": 45,
    "servings": {request.people},
    "difficulty": "Easy",
    "cuisine": "{style.value}",
    "diet_tags": {json.dumps([d.value for d in request.diet] if request.diet else [])},
    "nutrition": "Comprehensive nutritional information including calories and key nutrients",
    "tips": [
        "Professional cooking tip for best results",
        "Storage and reheating instructions", 
        "Serving suggestions and variations"
    ]
}}

Make sure the response is valid JSON only, no additional text.
"""
        return prompt
    
    def _parse_recipe_response(self, response_text: str) -> dict:
        """Parse the AI response and extract recipe data."""
        try:
            # Clean the response text
            response_text = response_text.strip()
            
            # Find JSON content
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "{" in response_text:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                response_text = response_text[start:end]
            
            # Parse JSON
            recipe_data = json.loads(response_text)
            
            # Map fields to match Recipe model expectations
            mapped_data = {}
            
            # Direct mappings
            mapped_data["name"] = recipe_data.get("name", "Unnamed Recipe")
            mapped_data["description"] = recipe_data.get("description", "A delicious recipe")
            mapped_data["ingredients"] = recipe_data.get("ingredients", [])
            mapped_data["difficulty"] = recipe_data.get("difficulty", "Medium")
            
            # Map instructions to steps
            mapped_data["steps"] = recipe_data.get("instructions", recipe_data.get("steps", []))
            
            # Parse time fields (remove "minutes" and convert to int)
            def parse_time(time_str):
                if isinstance(time_str, int):
                    return time_str
                if isinstance(time_str, str):
                    # Extract number from strings like "15 minutes"
                    import re
                    match = re.search(r'\d+', time_str)
                    return int(match.group()) if match else 15
                return 15
            
            mapped_data["prep_time"] = parse_time(recipe_data.get("prep_time", "15"))
            mapped_data["cook_time"] = parse_time(recipe_data.get("cook_time", "30"))
            mapped_data["total_time"] = parse_time(recipe_data.get("total_time", "45"))
            
            # Map servings to people
            mapped_data["people"] = recipe_data.get("servings", recipe_data.get("people", 4))
            
            # Map cuisine to style
            mapped_data["style"] = recipe_data.get("cuisine", recipe_data.get("style", "International"))
            
            # Map diet_tags to diet_info
            diet_tags = recipe_data.get("diet_tags", recipe_data.get("diet_info", []))
            if isinstance(diet_tags, str):
                try:
                    diet_tags = json.loads(diet_tags)
                except:
                    diet_tags = [diet_tags] if diet_tags else []
            mapped_data["diet_info"] = diet_tags
            
            # Optional fields
            mapped_data["nutrition"] = recipe_data.get("nutrition", "Nutritional information not available")
            mapped_data["tips"] = recipe_data.get("tips", [])
            
            return mapped_data
            
        except json.JSONDecodeError as e:
            raise RecipeGenerationError(f"Failed to parse recipe response as JSON: {str(e)}")
        except Exception as e:
            raise RecipeGenerationError(f"Failed to parse recipe response: {str(e)}")

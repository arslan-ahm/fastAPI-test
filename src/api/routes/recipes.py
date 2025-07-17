"""Recipe API routes."""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from typing import Optional, List
import logging

from ...models.schemas import (
    RecipeRequest, 
    RecipeResponse, 
    ImageRecipeRequest,
    CountryStyle,
    DietType
)
from ...api.dependencies import RecipeServiceDep, LLM7ServiceDep, APIKeyValidation

# Check if Gemini is available
try:
    from ...api.dependencies import GeminiServiceDep
    GEMINI_AVAILABLE = GeminiServiceDep is not None
except ImportError:
    GeminiServiceDep = None
    GEMINI_AVAILABLE = False

from ...core.exceptions import (
    RecipeGenerationError, 
    ImageProcessingError, 
    InvalidIngredientsError
)
from ...utils.helpers import validate_ingredients

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["recipes"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Recipe API is running"}


@router.post("/from-ingredients", response_model=RecipeResponse)
async def generate_recipe_from_ingredients(
    request: RecipeRequest,
    recipe_service: RecipeServiceDep,
    _: APIKeyValidation = None
):
    """
    Generate a recipe from a list of ingredients.
    
    This endpoint takes a list of ingredients and optional preferences
    to generate a unique recipe using AI. Uses LLM7 as primary service
    with Gemini as fallback if available.
    """
    try:
        logger.info(f"Generating recipe from ingredients: {request.ingredients}")
        
        # Validate ingredients
        if not request.ingredients:
            raise InvalidIngredientsError("No ingredients provided")
        
        validated_ingredients = validate_ingredients(request.ingredients)
        if not validated_ingredients:
            raise InvalidIngredientsError("No valid ingredients found")
        
        # Update request with validated ingredients
        request.ingredients = validated_ingredients
        
        # Use the recipe service which handles LLM7 and Gemini fallback internally
        recipe = await recipe_service.generate_recipe_from_ingredients(request)
        
        logger.info(f"Successfully generated recipe: {recipe.name}")
        
        return RecipeResponse(
            success=True,
            recipe=recipe,
            message="Recipe generated successfully using LLM7"
        )
        
    except InvalidIngredientsError as e:
        logger.error(f"Invalid ingredients error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RecipeGenerationError as e:
        logger.error(f"Recipe generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in recipe generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating the recipe"
        )


@router.post("/from-image", response_model=RecipeResponse)
async def generate_recipe_from_image(
    recipe_service: RecipeServiceDep,
    file: UploadFile = File(..., description="Image file containing ingredients"),
    style: Optional[CountryStyle] = Form(CountryStyle.PAKISTANI),
    diet: Optional[str] = Form(None, description="Comma-separated diet preferences (vegetarian, vegan, non_veg, etc.)"),
    people: Optional[int] = Form(4),
    _: APIKeyValidation = None
):
    """
    Generate a recipe from an image of ingredients using LLM7 or Gemini AI.
    
    This endpoint uses AI vision to analyze the image, extract ingredients,
    and generate a complete recipe in one step. Prefers LLM7 but falls back to Gemini.
    """
    try:
        logger.info(f"Processing image upload: {file.filename}")
        
        # Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image file too large. Maximum size is 10MB"
            )
        
        # Parse diet preferences
        parsed_diet = []
        if diet:
            diet_names = [d.strip().lower().replace(" ", "_") for d in diet.split(',')]
            for diet_type in DietType:
                if diet_type.value.lower() in diet_names:
                    parsed_diet.append(diet_type)
        
        # Generate recipe directly from image using available AI service
        logger.info("Generating recipe from image using AI...")
        recipe = await recipe_service.extract_ingredients_and_generate_recipe(
            image_data=file_content,
            style=style,  # Pass the enum directly, not style.value
            diet=parsed_diet,
            people=people
        )
        
        logger.info(f"Successfully generated recipe from image: {recipe.name}")
        
        return RecipeResponse(
            success=True,
            recipe=recipe,
            message=f"Recipe generated successfully from image using AI"
        )
        
    except ImageProcessingError as e:
        logger.error(f"Image processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RecipeGenerationError as e:
        logger.error(f"Recipe generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in image recipe generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the image"
        )


@router.get("/styles")
async def get_available_styles():
    """Get list of available food styles."""
    styles = [style.value for style in CountryStyle]
    return {"styles": styles}


@router.get("/diets")
async def get_diet_types():
    """Get list of available diet types."""
    diets = [diet.value for diet in DietType]
    return {"diets": diets}

"""API dependencies and dependency injection."""

from fastapi import Depends, HTTPException, status
from typing import Annotated

from ..core.config import settings
from ..services.recipe_service import RecipeService
from ..services.llm7_service import LLM7Service

# Optional import for Gemini service
try:
    from ..services.gemini_service import GeminiService
    GEMINI_AVAILABLE = True
except ImportError:
    GeminiService = None
    GEMINI_AVAILABLE = False


def get_recipe_service() -> RecipeService:
    """Dependency to get recipe service instance."""
    try:
        return RecipeService()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize recipe service: {str(e)}"
        )


def get_llm7_service() -> LLM7Service:
    """Dependency to get LLM7 service instance."""
    try:
        return LLM7Service()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize LLM7 service: {str(e)}"
        )


def get_gemini_service() -> GeminiService:
    """Dependency to get Gemini service instance."""
    if not GEMINI_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gemini service is not available. Please install google-generativeai package."
        )
    try:
        return GeminiService()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize Gemini service: {str(e)}"
        )


def validate_api_key() -> bool:
    """Dependency to validate API keys are configured."""
    if not settings.llm7_token and not settings.gemini_api_key and not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No AI API key is configured. Please set LLM7_TOKEN, GEMINI_API_KEY, or OPENAI_API_KEY environment variable."
        )
    return True


# Type aliases for dependency injection
RecipeServiceDep = Annotated[RecipeService, Depends(get_recipe_service)]
LLM7ServiceDep = Annotated[LLM7Service, Depends(get_llm7_service)]
APIKeyValidation = Annotated[bool, Depends(validate_api_key)]

# Optional Gemini service dependency
if GEMINI_AVAILABLE:
    GeminiServiceDep = Annotated[GeminiService, Depends(get_gemini_service)]
else:
    GeminiServiceDep = None

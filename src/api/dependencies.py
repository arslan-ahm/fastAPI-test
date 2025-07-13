"""API dependencies and dependency injection."""

from fastapi import Depends, HTTPException, status
from typing import Annotated

from ..core.config import settings
from ..services.recipe_service import RecipeService
from ..services.llm7_service import LLM7Service


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


def validate_api_key() -> bool:
    """Dependency to validate LLM7 API key is configured."""
    if not settings.llm7_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM7 token is not configured. Please set LLM7_TOKEN environment variable."
        )
    return True


# Type aliases for dependency injection
RecipeServiceDep = Annotated[RecipeService, Depends(get_recipe_service)]
LLM7ServiceDep = Annotated[LLM7Service, Depends(get_llm7_service)]
APIKeyValidation = Annotated[bool, Depends(validate_api_key)]

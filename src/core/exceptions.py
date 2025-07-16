"""Custom exceptions for the Recipe API."""

from fastapi import HTTPException
from typing import Any, Optional


class RecipeAPIException(HTTPException):
    """Base exception for Recipe API."""
    
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[dict] = None,
    ) -> None:
        super().__init__(status_code, detail, headers)


class OpenAIKeyMissingError(RecipeAPIException):
    """Raised when OpenAI API key is missing."""
    
    def __init__(self) -> None:
        super().__init__(
            status_code=500,
            detail="OpenAI API key is not configured. Please set OPENAI_API_KEY environment variable."
        )


class RecipeGenerationError(RecipeAPIException):
    """Raised when recipe generation fails."""
    
    def __init__(self, detail: str = "Failed to generate recipe") -> None:
        super().__init__(
            status_code=500,
            detail=detail
        )


class ImageProcessingError(RecipeAPIException):
    """Raised when image processing fails."""
    
    def __init__(self, detail: str = "Failed to process image") -> None:
        super().__init__(
            status_code=400,
            detail=detail
        )


class InvalidIngredientsError(RecipeAPIException):
    """Raised when ingredients list is invalid."""
    
    def __init__(self, detail: str = "Invalid ingredients provided") -> None:
        super().__init__(
            status_code=400,
            detail=detail
        )

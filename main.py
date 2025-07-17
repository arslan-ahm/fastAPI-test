"""
Recipe API - FastAPI application for generating recipes using LLM7.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from src.core.config import settings
from src.api.routes.recipes import router as recipes_router
from src.models.schemas import HealthResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# Include routers
app.include_router(recipes_router, prefix="/api/recipes")

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with API information."""
    return HealthResponse(
        status="healthy",
        message=f"Welcome to {settings.app_name}",
        version=settings.app_version
    )

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="API is running successfully",
        version=settings.app_version
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An internal server error occurred",
            "detail": str(exc) if settings.debug else "Internal server error"
        }
    )

# Export for Vercel
handler = app

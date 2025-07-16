"""
Recipe API - FastAPI application for generating recipes using LangChain and OpenAI.

This application provides two main endpoints:
1. Generate recipes from ingredient lists
2. Generate recipes from images of ingredients

Author: Recipe API Team
Version: 1.0.0
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from src.core.config import settings
from src.api.routes.recipes import router as recipes_router
from src.models.schemas import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Recipe API...")
    logger.info(f"OpenAI API Key configured: {'Yes' if settings.openai_api_key else 'No'}")
    yield
    # Shutdown
    logger.info("Shutting down Recipe API...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
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
app.include_router(recipes_router)


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
    logger.error(f"Global exception handler caught: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An internal server error occurred",
            "detail": str(exc) if settings.debug else "Internal server error"
        }
    )


if __name__ == "__main__":
    logger.info("Starting Recipe API server...")
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info"
    )

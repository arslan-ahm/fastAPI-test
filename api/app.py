"""
Vercel-compatible FastAPI application for Recipe API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import configuration and routes
from src.core.config import settings
from src.api.routes.recipes import router as recipes_router
from src.models.schemas import HealthResponse

# Create FastAPI application with minimal configuration for Vercel
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
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An internal server error occurred",
            "detail": str(exc) if settings.debug else "Internal server error"
        }
    )

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info"
    )

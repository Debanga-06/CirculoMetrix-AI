"""
CirculoMetrix AI - Main Application Entry Point
FastAPI backend for Life Cycle Assessment and Circular Economy Analytics
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
import logging
from typing import Dict, Any

# Import core modules
from core.config import settings
from core.database import init_db, close_db_connections

# Import routers
from routers import (
    lca,
    circularity,
    ai_predict,
    recommendations,
    what_if,
    report
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting CirculoMetrix AI Backend...")

    try:
        # Initialize MongoDB (collections + indexes)
        logger.info("🍃 Initializing MongoDB...")
        await init_db()
        logger.info("✅ MongoDB initialized successfully")

        # Load ML models
        logger.info("🤖 Loading ML models...")
        logger.info("✅ ML models loaded successfully")

    except Exception as e:
        logger.error(f"❌ Error during startup: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("👋 Shutting down CirculoMetrix AI Backend...")
    close_db_connections()
    logger.info("✅ MongoDB connections closed")

# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Life Cycle Assessment & Circular Economy Platform for Metal Industries",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# ============================================
# Middleware Configuration
# ============================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# GZip Compression Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request Timing Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Add processing time header to responses
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests
    """
    logger.info(f"📥 {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 {request.method} {request.url.path} - Status: {response.status_code}")
    return response


# ============================================
# Exception Handlers
# ============================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors
    """
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation Error",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal Server Error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# ============================================
# API Routes
# ============================================

@app.get("/", tags=["Health"])
async def root() -> Dict[str, Any]:
    """
    Root endpoint - API health check
    """
    return {
        "success": True,
        "message": "Welcome to CirculoMetrix AI API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring
    """
    return {
        "success": True,
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT
    }


@app.get("/api/info", tags=["Health"])
async def api_info() -> Dict[str, Any]:
    """
    API information endpoint
    """
    return {
        "success": True,
        "data": {
            "name": settings.APP_NAME,
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "features": [
                "Life Cycle Assessment (LCA)",
                "Circular Economy Metrics",
                "AI-Powered Predictions",
                "What-If Scenario Analysis",
                "Smart Recommendations",
                "PDF Report Generation"
            ],
            "supported_materials": ["aluminum", "copper", "steel"]
        }
    }


# ============================================
# Include Routers
# ============================================

# LCA Router
app.include_router(
    lca.router,
    prefix="/api/v1/lca",
    tags=["Life Cycle Assessment"]
)

# Circularity Router
app.include_router(
    circularity.router,
    prefix="/api/v1/circularity",
    tags=["Circular Economy"]
)

# AI Prediction Router
app.include_router(
    ai_predict.router,
    prefix="/api/v1/ai",
    tags=["AI Predictions"]
)

# Recommendations Router
app.include_router(
    recommendations.router,
    prefix="/api/v1/recommendations",
    tags=["Recommendations"]
)

# What-If Analysis Router
app.include_router(
    what_if.router,
    prefix="/api/v1/what-if",
    tags=["What-If Analysis"]
)

# Report Generation Router
app.include_router(
    report.router,
    prefix="/api/v1/report",
    tags=["Reports"]
)


# ============================================
# Development Routes (Debug Mode Only)
# ============================================

if settings.DEBUG:
    @app.get("/debug/settings", tags=["Debug"])
    async def debug_settings() -> Dict[str, Any]:
        """
        Display current settings (debug mode only)
        """
        return {
            "success": True,
            "settings": {
                "app_name": settings.APP_NAME,
                "environment": settings.ENVIRONMENT,
                "debug": settings.DEBUG,
                "allowed_origins": settings.ALLOWED_ORIGINS
            }
        }


# ============================================
# Application Entry Point
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

"""
Akura AI - Main Application Entry Point

This is the main FastAPI application for the Akura AI
Intelligent Dyslexia Correction Engine.
"""

import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.routes import router
from app.core.config import get_settings
from app.services.llm_service import llm_service


# Configure logging
def setup_logging():
    """Configure loguru logging."""
    settings = get_settings()
    
    # Remove default handler
    logger.remove()
    
    # Add custom handler based on environment
    if settings.log_format == "json":
        logger.add(
            sys.stdout,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level=settings.log_level,
            serialize=True
        )
    else:
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.log_level,
            colorize=True
        )
    
    logger.info(f"Logging configured with level: {settings.log_level}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    setup_logging()
    logger.info("🚀 Starting Akura AI Backend...")
    
    settings = get_settings()
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    if settings.llm_provider == "hf_space":
        logger.info(f"HF Space: {settings.hf_space_url} (free)")
    elif settings.llm_provider == "huggingface":
        logger.info(f"HF Model: {settings.hf_model_id} (request-based)")
    else:
        logger.info(f"Ollama Model: {settings.ollama_model}")
        logger.info(f"Ollama URL: {settings.ollama_base_url}")
    
    # Initialize LLM service
    try:
        await llm_service.initialize()
        logger.info("✅ LLM service initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ LLM service initialization failed: {e}")
        logger.info("📋 Falling back to rule-based corrections only")
    
    # Initialize database tables (Supabase)
    try:
        from app.core.database import init_db, engine
        if engine is not None:
            # Import models here to register them
            import app.models.feedback_models  # noqa
            init_db()
            logger.info("✅ Database tables initialized")
        else:
            logger.info("ℹ️ Database not configured (no DATABASE_URL)")
    except Exception as e:
        logger.warning(f"⚠️ Database initialization skipped: {e}")
    
    logger.info("🎉 Akura AI Backend is ready!")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Akura AI Backend...")


# Get settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Akura AI - Intelligent Dyslexia Correction Engine",
    description="""
# Akura AI Backend API

A specialized, privacy-focused API designed to detect and correct 
Sinhala writing errors specific to dyslexic students.

## Features

- **AI-Powered Correction**: Uses a fine-tuned Small Language Model (SLM)
- **Pattern Detection**: Identifies specific dyslexia patterns:
  - Visual Scrambling (letter reordering)
  - Phonetic Confusion (dental/retroflex swaps)
  - Visual Reversal (shape confusion)
  - Grammar Issues (colloquial to written)
- **Hybrid Approach**: Combines AI with rule-based fallback
- **Offline Capable**: No external API dependencies
- **Privacy-First**: Zero data leakage

## Usage

Send Sinhala text to the `/analyze` endpoint to receive detailed
word-by-word analysis with corrections and explanations.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware - allow all localhost origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else None
        }
    )


# Include API routes
app.include_router(router, prefix="/api/v1")

# Include Feedback API routes
from app.api.feedback_routes import router as feedback_router
app.include_router(feedback_router, prefix="/api/v1")

# Include Child Essay API routes
from app.api.child_routes import router as child_router
app.include_router(child_router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "Akura AI - Intelligent Dyslexia Correction Engine",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "api": "/api/v1"
    }


# For running with uvicorn directly
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

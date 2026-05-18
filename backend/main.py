"""
Meeting Action Items Dashboard - FastAPI Backend
Production-ready API for managing action items with Azure Data Lake integration
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import List, Optional

# Import routes and models
from routes import actions
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Meeting Action Items Dashboard Backend Starting")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Azure Storage Account: {settings.azure_storage_account_name}")
    yield
    # Shutdown
    logger.info("🛑 Backend Shutting Down")

# Initialize FastAPI app
app = FastAPI(
    title="Meeting Action Items Dashboard API",
    description="Production-ready API for managing action items with Azure Data Lake integration",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"CORS enabled for origins: {settings.cors_origins}")

# Include routers
app.include_router(actions.router, prefix="/api/actions", tags=["Actions"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "✅ Running",
        "service": "Meeting Action Items Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "get_all_actions": "GET /api/actions",
            "create_action": "POST /api/actions",
            "update_action": "PUT /api/actions/{id}",
            "delete_action": "DELETE /api/actions/{id}",
            "health_check": "GET /health"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy", "service": "action-items-api"}

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP Exception: {exc.detail}")
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Generic exception handler"""
    logger.error(f"Unexpected error: {str(exc)}")
    return {
        "error": "Internal server error",
        "status_code": 500
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from fastapi import APIRouter

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routers import sources, auth, notifications, categories
from .database.migrations import init_db_with_migrations
from .services.scheduler.job_scheduler import JobScheduler
from .config.settings import settings
from .middleware import SwaggerAuthMiddleware, RateLimitMiddleware

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: JobScheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    global scheduler
    
    # Startup
    logger.info("Initializing database...")
    init_db_with_migrations()
    logger.info("Database initialized")
    
    # Start scheduler
    logger.info("Starting scheduler...")
    scheduler = JobScheduler()
    await scheduler.start()
    logger.info("Scheduler started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down scheduler...")
    if scheduler:
        await scheduler.shutdown()
    logger.info("Application shutdown complete")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Social Knowledge API",
    description="API for managing news sources and automated news crawling",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "https://dailybriefai-cyan.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Swagger authentication middleware
app.add_middleware(SwaggerAuthMiddleware)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

api_router = APIRouter(prefix="/api/v1")

# Include API routes
api_router.include_router(sources.router)
api_router.include_router(auth.router)
api_router.include_router(notifications.router)
api_router.include_router(categories.router)

app.include_router(api_router)

@app.get("/")
def root():
    return {
        "message": "Social Knowledge API",
        "version": "0.1.0",
        "docs": "/docs"
    }

# def signal_handler(sig, frame):
#     """Handle shutdown signals"""
#     logger.info("Received shutdown signal")
#     if scheduler:
#         asyncio.run(scheduler.shutdown())
#     sys.exit(0)


# signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level=settings.log_level.lower()
    )


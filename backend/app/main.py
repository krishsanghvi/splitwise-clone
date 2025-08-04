from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import supabase_conn
from app.api import users
from app.api import groups
from app.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up SplitFlow API...")

    # Connect to Supabase
    if supabase_conn.connect():
        logger.info("Database connection established")
    else:
        logger.error("Failed to connect to database")
        raise Exception("Database connection failed")

    yield

    # Shutdown
    logger.info("Shutting down SplitFlow API...")

# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    description="A FastAPI backend for expense splitting",
    version="1.0.0",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    lifespan=lifespan
)

# Include routers
app.include_router(
    users.router,
    prefix=f"{settings.api_prefix}/users",
    tags=["users"]
)

app.include_router(
    groups.router,
    prefix=f"{settings.api_prefix}/groups",
    tags=["groups"]
)


@app.get("/")
async def root():
    return {"message": "Welcome to SplitFlow API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "splitflow-api"}

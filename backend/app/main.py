from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import supabase_conn
from app.api import users
from app.api import groups
from app.api import group_members
from app.api import categories
from app.api import balances
from app.api import expenses
from app.api import expense_shares
from app.api import settlements
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

app.include_router(
    group_members.router,
    prefix=f"{settings.api_prefix}/group_members",
    tags=["group_members"]
)

app.include_router(
    categories.router,
    prefix=f"{settings.api_prefix}/categories",
    tags=["categories"]
)

app.include_router(
    balances.router,
    prefix=f"{settings.api_prefix}/balances",
    tags=["balances"]
)

app.include_router(
    expenses.router,
    prefix=f"{settings.api_prefix}/expenses",
    tags=["expenses"]
)

app.include_router(
    expense_shares.router,
    prefix=f"{settings.api_prefix}/expense_shares",
    tags=["expense_shares"]
)

app.include_router(
    settlements.router,
    prefix=f"{settings.api_prefix}/settlements",
    tags=["settlements"]
)


@app.get("/")
async def root():
    return {"message": "Welcome to SplitFlow API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "splitflow-api"}

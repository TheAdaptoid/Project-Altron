"""
Application entrypoint.

This module provides the FastAPI application instance and the lifespan
async context manager for creating and tearing down the database and
logging configuration.

"""

# Standard Libraries
from contextlib import asynccontextmanager

# External Libraries
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Internal Libraries
from app.routers import conversations, messages
from app.database import create_db_and_tables
from app.logger.logger import logger, LoggerMiddleware


@asynccontextmanager
async def lifespan(app_: FastAPI):
    """
    Startup and shutdown functionality handler.

    Args:
        app (FastAPI): FastAPI application instance.
    """
    # On Startup
    logger.info("Starting up...")
    create_db_and_tables()

    yield

    # On Shutdown
    logger.info("Shutting down...")


app = FastAPI(lifespan=lifespan)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggerMiddleware)

# Routers
app.include_router(conversations.router)
app.include_router(messages.router)

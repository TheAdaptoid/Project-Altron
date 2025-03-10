# Standard Libraries
from contextlib import asynccontextmanager

# External Libraries
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Internal Libraries
from app.routers import conversations
from app.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown functionality handler.

    Args:
        app (FastAPI): FastAPI application instance.
    """
    # On Startup
    print("Starting up...")
    create_db_and_tables()

    yield

    # On Shutdown
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversations.router)

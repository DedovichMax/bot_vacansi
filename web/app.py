# web/app.py
from fastapi import FastAPI
from utils.database import Database


def create_app(db: Database, config: dict) -> FastAPI:
    """Create FastAPI application.

    Args:
        db: Database instance.
        config: Application configuration.

    Returns:
        Configured FastAPI application.
    """
    app = FastAPI(title="Telegram Vacancy Bot", version="1.0.0")

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}

    return app

# web/app.py
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from utils.database import Database
from web.auth import verify_credentials
from web.routes import router


def create_app(db: Database, config: dict) -> FastAPI:
    """Create FastAPI application with routes and templates.

    Args:
        db: Database instance.
        config: Application configuration dict.

    Returns:
        Configured FastAPI application.
    """
    app = FastAPI(title="Telegram Vacancy Bot", version="1.0.0")

    # Store references in app state for dependency injection
    app.state.db = db
    app.state.web_config = config.get("web", {})

    # Include API routes
    app.include_router(router)

    # Templates
    templates = Jinja2Templates(directory="web/templates")

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request, _user: str = Depends(verify_credentials)):
        """Main dashboard page."""
        stats = db.get_stats()
        channels = db.get_channels()
        filters = db.get_filters()
        vacancies = db.get_vacancies(limit=50)

        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "stats": stats,
                "channels": channels,
                "filters": filters,
                "vacancies": vacancies,
            },
        )

    return app

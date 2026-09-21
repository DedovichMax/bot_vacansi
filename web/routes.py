# web/routes.py
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from utils.database import Database
from web.auth import verify_credentials

router = APIRouter()


def _get_db(request: Request) -> Database:
    """Get database instance from app state."""
    return request.app.state.db


# --- Health (no auth) ---


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# --- Channels ---


@router.get("/api/channels")
async def get_channels(
    request: Request,
    _user: str = Depends(verify_credentials),
) -> list:
    """Get all monitored channels."""
    db: Database = _get_db(request)
    return db.get_channels()


@router.post("/api/channels")
async def add_channel(
    channel: dict[str, str],
    request: Request,
    _user: str = Depends(verify_credentials),
) -> dict:
    """Add a new channel to monitor."""
    channel_name = channel.get("channel_name")
    if not channel_name:
        raise HTTPException(status_code=400, detail="channel_name required")

    db: Database = _get_db(request)
    channel_id = db.add_channel(channel_name)
    return {"id": channel_id, "channel_name": channel_name}


@router.delete("/api/channels/{channel_id}")
async def delete_channel(
    channel_id: int,
    request: Request,
    _user: str = Depends(verify_credentials),
) -> dict:
    """Delete a channel."""
    db: Database = _get_db(request)
    deleted = db.delete_channel(channel_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Channel not found")
    return {"deleted": True}


# --- Filters ---


@router.get("/api/filters")
async def get_filters(
    request: Request,
    _user: str = Depends(verify_credentials),
) -> list:
    """Get all vacancy filters."""
    db: Database = _get_db(request)
    return db.get_filters()


@router.post("/api/filters")
async def add_filter(
    filter_data: dict[str, Any],
    request: Request,
    _user: str = Depends(verify_credentials),
) -> dict:
    """Add a new vacancy filter."""
    name = filter_data.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="name required")

    phrases = filter_data.get("phrases", [])
    exclude = filter_data.get("exclude", [])
    weight = filter_data.get("weight", 5)

    db: Database = _get_db(request)
    filter_id = db.add_filter(name, phrases, exclude, weight)
    return {"id": filter_id, "name": name}


@router.delete("/api/filters/{filter_id}")
async def delete_filter(
    filter_id: int,
    request: Request,
    _user: str = Depends(verify_credentials),
) -> dict:
    """Delete a filter."""
    db: Database = _get_db(request)
    deleted = db.delete_filter(filter_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Filter not found")
    return {"deleted": True}


# --- Vacancies ---


@router.get("/api/vacancies")
async def get_vacancies(
    request: Request,
    limit: int = 100,
    _user: str = Depends(verify_credentials),
) -> list:
    """Get found vacancies."""
    db: Database = _get_db(request)
    return db.get_vacancies(limit)


# --- Stats ---


@router.get("/api/stats")
async def get_stats(
    request: Request,
    _user: str = Depends(verify_credentials),
) -> dict:
    """Get dashboard statistics."""
    db: Database = _get_db(request)
    return db.get_stats()

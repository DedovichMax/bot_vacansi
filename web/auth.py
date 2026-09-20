# web/auth.py
import secrets
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


def _get_web_config(request: Request) -> dict:
    """Extract web config from app state."""
    return getattr(request.app.state, "web_config", {})


def verify_credentials(
    credentials: HTTPBasicCredentials = Depends(security),
    request: Request = None,
) -> str:
    """Verify HTTP Basic Auth credentials.

    Args:
        credentials: Injected Basic Auth credentials.
        request: FastAPI request for accessing app config.

    Returns:
        Authenticated username.

    Raises:
        HTTPException: 401 if credentials are invalid.
    """
    web_config = _get_web_config(request) if request else {}
    correct_username = web_config.get("username", "admin")
    correct_password = web_config.get("password", "password")

    username_correct = secrets.compare_digest(credentials.username, correct_username)
    password_correct = secrets.compare_digest(credentials.password, correct_password)

    if not (username_correct and password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

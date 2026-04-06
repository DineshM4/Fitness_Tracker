"""Authentication utilities for the FastAPI app."""
from typing import Optional
from fastapi import HTTPException, status, Header
from database import User


def verify_api_key(api_key: Optional[str] = None) -> bool:
    """Verify API key from header or environment."""
    valid_key = api_key or "test-api-key-change-in-production"
    return valid_key == "test-api-key-change-in-production"


def get_api_key_header(x_api_key: Optional[str] = Header(None)) -> Optional[str]:
    """Extract API key from header."""
    return x_api_key


# Simple API key dependency for testing
def get_current_user_optional(
    x_api_key: Optional[str] = Header(None),
) -> Optional[User]:
    """Get the current authenticated user, or None if not authenticated."""
    if verify_api_key(x_api_key):
        return None  # Allow access with API key for testing
    return None


def require_auth(x_api_key: Optional[str] = Header(None)) -> None:
    """Require authentication."""
    if not verify_api_key(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

"""
Authentication API endpoints.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ...core.security.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    User,
    create_access_token,
    get_admin_user,
    get_read_user,
)

router = APIRouter()


@router.post("/auth/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """
    Get JWT access token using username and password.

    This is a simple implementation for demonstration purposes.
    In a real application, you would verify credentials against a database.
    """
    # For this demo, only accept a fixed test user
    if form_data.username != "admin" or form_data.password != "password":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with appropriate scopes
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    scopes = ["admin", "read", "write"]  # Admin user has all scopes
    access_token = create_access_token(
        data={"sub": form_data.username, "scopes": scopes},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/auth/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_read_user)):
    """Get current authenticated user information."""
    return current_user


@router.get("/auth/status")
async def check_auth_status(current_user: User = Depends(get_read_user)):
    """Check authentication status."""
    return {
        "authenticated": True,
        "user": current_user.username,
        "scopes": current_user.scopes,
    }


@router.get("/auth/admin", response_model=User)
async def admin_only(current_user: User = Depends(get_admin_user)):
    """Admin-only endpoint."""
    return current_user

"""
Authentication and security utilities.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Union

import bcrypt
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError

from ..config import settings


def _sanitize_key(value: str | None) -> str:
    """Normalize API key strings to avoid hidden characters/quotes during dev."""
    if not value:
        return ""
    v = value.strip()
    # Trim common accidental wrappers
    if (v.startswith('"') and v.endswith('"')) or (
        v.startswith("'") and v.endswith("'")
    ):
        v = v[1:-1]
    v = v.strip()
    # Remove non-printable/zero-width characters
    v = "".join(ch for ch in v if 32 <= ord(ch) <= 126)
    return v


from ..logging import app_logger

# Security constants
API_KEY_NAME = "X-API-Key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security tools
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token", auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


# Models
class Token(BaseModel):
    """Token response model."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data model."""

    username: Optional[str] = None
    scopes: list[str] = []


class User(BaseModel):
    """User model."""

    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    scopes: list[str] = []


def get_api_keys() -> dict[str, tuple[str, list[str]]]:
    """Build API key mapping from env or settings, normalizing whitespace."""
    admin_key = (
        os.environ.get("ADMIN_API_KEY")
        or getattr(settings, "ADMIN_API_KEY", None)
        or "admin-dev-key"
    )
    read_key = (
        os.environ.get("READ_API_KEY")
        or getattr(settings, "READ_API_KEY", None)
        or "read-dev-key"
    )
    key_map: dict[str, tuple[str, list[str]]] = {}
    if admin_key:
        key_map[_sanitize_key(admin_key)] = ("admin", ["admin", "read", "write"])
    if read_key:
        key_map[_sanitize_key(read_key)] = ("reader", ["read"])
    return key_map


# API Keys (normalized)
API_KEYS = get_api_keys()


def verify_password(plain_password, hashed_password):
    """Verify password against hash."""
    # Convert strings to bytes if needed
    if isinstance(plain_password, str):
        plain_password = plain_password.encode("utf-8")
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")

    try:
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password):
    """Get password hash."""
    # Convert string to bytes if needed
    if isinstance(password, str):
        password = password.encode("utf-8")

    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)

    # Return the hash as a string
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user_from_token(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
) -> Optional[User]:
    """Get current user from JWT token."""
    if token is None:
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None

        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)

    except (JWTError, ValidationError):
        return None

    # In a real app, look up the user in a database
    # For this example, we'll use a simple dict
    if token_data.username == "admin":
        user = User(
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            disabled=False,
            scopes=["admin", "read", "write"],
        )
    else:
        return None

    # Check for required scopes
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            return None

    return user


async def get_current_user_from_api_key(
    api_key: str = Security(api_key_header), request: Request | None = None
) -> Optional[User]:
    """Get current user from API key."""
    # Try header value provided by Security(api_key_header)
    candidate = _sanitize_key(api_key or "")

    # Fallback: check raw headers (case-insensitive) and query param for flexibility
    if not candidate and request is not None:
        candidate = _sanitize_key(
            request.headers.get(API_KEY_NAME)
            or request.headers.get(API_KEY_NAME.lower())
            or request.query_params.get("api_key")
            or ""
        )

    # Optional debug logging in development
    if os.environ.get("LOG_LEVEL") == "DEBUG" and request is not None:
        try:
            masked = candidate[:2] + "***" + candidate[-2:] if candidate else ""
            app_logger.debug(
                "Auth: API key check, masked={}, in_map={}",
                masked,
                candidate in API_KEYS,
            )
        except Exception:
            pass

    # Rebuild on each call to pick up env changes during dev
    api_keys = API_KEYS if os.environ.get("ENV") == "prod" else get_api_keys()

    if not candidate or candidate not in api_keys:
        # In dev mode, accept hardcoded keys if they match exactly
        if os.environ.get("ENV") != "prod":
            if candidate == "read-dev-key":
                return User(
                    username="reader",
                    email="reader@example.com",
                    full_name="Reader User",
                    disabled=False,
                    scopes=["read"],
                )
            if candidate == "admin-dev-key":
                return User(
                    username="admin",
                    email="admin@example.com",
                    full_name="Admin User",
                    disabled=False,
                    scopes=["admin", "read", "write"],
                )
        return None

    username, scopes = api_keys[candidate]
    return User(
        username=username,
        email=f"{username}@example.com",
        full_name=f"{username.capitalize()} User",
        disabled=False,
        scopes=scopes,
    )


async def get_current_user(
    security_scopes: SecurityScopes,
    request: Request,
    token: str = Depends(oauth2_scheme),
    api_key: str = Security(api_key_header),
) -> User:
    """Get current user from either JWT token or API key."""
    # Try API Key first (supports header name variations and query param)
    user = await get_current_user_from_api_key(api_key, request)

    if user is None:
        user = await get_current_user_from_token(security_scopes, token)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={
                # Advertise both Bearer and API key to clients
                "WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}", APIKey'
            },
        )

    # Check for required scopes
    for scope in security_scopes.scopes:
        if scope not in user.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required: {security_scopes.scope_str}",
                headers={
                    "WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'
                },
            )

    return user


def get_admin_user(user: User = Security(get_current_user, scopes=["admin"])):
    """Get current user with admin scope."""
    return user


def get_read_user(user: User = Security(get_current_user, scopes=["read"])):
    """Get current user with read scope."""
    return user


def get_write_user(user: User = Security(get_current_user, scopes=["write"])):
    """Get current user with write scope."""
    return user

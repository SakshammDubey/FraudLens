
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from supabase import create_client
from supabase_auth.errors import AuthApiError

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

logger = logging.getLogger("fraudlens.auth")

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_KEY must be set in the project .env file."
    )

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter(prefix="/auth", tags=["authentication"])
bearer = HTTPBearer(auto_error=False)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


def _auth_error(exc: AuthApiError) -> HTTPException:
    message = str(exc).lower()

    logger.warning("Supabase Auth API error: %s", str(exc))

    if "already registered" in message or "already been registered" in message:
        return HTTPException(409, "An account with this email may already exist.")

    if "invalid login credentials" in message:
        return HTTPException(401, "Incorrect email or password.")

    if "email not confirmed" in message:
        return HTTPException(401, "Confirm your email address before signing in.")

    if "password should be" in message or "weak password" in message:
        return HTTPException(400, "Choose a stronger password.")

    if "rate limit" in message or "too many requests" in message:
        return HTTPException(429, "Too many attempts. Please try again later.")

    # The detailed reason is written to the backend terminal.
    return HTTPException(
        status_code=400,
        detail="Supabase rejected the authentication request. Check the backend terminal for the diagnostic error.",
    )


@router.post("/register")
def register(body: RegisterRequest) -> dict[str, Any]:
    email = str(body.email).lower().strip()

    try:
        response = supabase.auth.sign_up(
            {"email": email, "password": body.password}
        )
    except AuthApiError as exc:
        raise _auth_error(exc) from None
    except Exception as exc:
        logger.exception("Unexpected error during Supabase registration")
        raise HTTPException(
            status_code=502,
            detail="Could not contact Supabase. Check the backend terminal.",
        ) from None

    user = response.user
    session = response.session

    if user is None:
        raise HTTPException(502, "Supabase did not return a user record.")

    user_data = {
        "id": str(user.id),
        "email": user.email or email,
    }

    if session is None:
        return {
            "confirmation_required": True,
            "message": (
                "Registration received. Check your email to confirm "
                "your account before signing in."
            ),
            "user": user_data,
        }

    return {
        "confirmation_required": False,
        "access_token": session.access_token,
        "token_type": "bearer",
        "user": user_data,
    }


@router.post("/login")
def login(body: LoginRequest) -> dict[str, Any]:
    email = str(body.email).lower().strip()

    try:
        response = supabase.auth.sign_in_with_password(
            {"email": email, "password": body.password}
        )
    except AuthApiError as exc:
        raise _auth_error(exc) from None
    except Exception:
        logger.exception("Unexpected error during Supabase login")
        raise HTTPException(
            status_code=502,
            detail="Could not contact Supabase. Check the backend terminal.",
        ) from None

    user = response.user
    session = response.session

    if user is None or session is None:
        raise HTTPException(
            status_code=401,
            detail="No active session returned. Confirm your email and try again.",
        )

    return {
        "access_token": session.access_token,
        "token_type": "bearer",
        "user": {"id": str(user.id), "email": user.email or email},
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sign in to access this resource.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        response = supabase.auth.get_user(credentials.credentials)
        user = response.user
    except Exception:
        logger.warning("Supabase rejected or could not verify the access token.")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    if user is None or not user.email:
        raise HTTPException(
            status_code=401,
            detail="Unable to verify the signed-in user.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"id": str(user.id), "email": user.email}


@router.get("/me")
def me(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    return {"user": user}

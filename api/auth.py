
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "fraudlens_users.sqlite3"
SECRET_KEY = os.getenv("FRAUDLENS_SECRET_KEY", "")
TOKEN_TTL_SECONDS = 60 * 60 * 12

router = APIRouter(prefix="/auth", tags=["authentication"])
bearer = HTTPBearer(auto_error=False)


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _init_db() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at INTEGER NOT NULL
            )
            """
        )


_init_db()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


def _password_hash(
    password: str,
    salt: bytes | None = None,
) -> str:
    salt = salt or secrets.token_bytes(16)

    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        310_000,
    )

    return f"{salt.hex()}${derived.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, _ = stored.split("$", 1)
        salt = bytes.fromhex(salt_hex)

        candidate = _password_hash(password, salt)

        return hmac.compare_digest(candidate, stored)

    except (ValueError, TypeError):
        return False


def _sign(payload: str) -> str:
    if not SECRET_KEY:
        raise HTTPException(
            status_code=503,
            detail=(
                "Authentication is not configured. "
                "Set FRAUDLENS_SECRET_KEY and restart the API."
            ),
        )

    body = (
        base64.urlsafe_b64encode(payload.encode())
        .decode()
        .rstrip("=")
    )

    signature = hmac.new(
        SECRET_KEY.encode(),
        body.encode(),
        hashlib.sha256,
    ).hexdigest()

    return f"{body}.{signature}"


def _make_token(user_id: int, email: str) -> str:
    expires = int(time.time()) + TOKEN_TTL_SECONDS
    return _sign(f"{user_id}|{expires}|{email}")


def _decode_token(token: str) -> dict[str, Any]:
    try:
        body, signature = token.rsplit(".", 1)

        expected = hmac.new(
            SECRET_KEY.encode(),
            body.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not SECRET_KEY or not hmac.compare_digest(
            signature,
            expected,
        ):
            raise ValueError("Invalid signature")

        padded = body + "=" * (-len(body) % 4)

        decoded = base64.urlsafe_b64decode(
            padded.encode()
        ).decode()

        user_id, expires, email = decoded.split("|", 2)

        if int(expires) < int(time.time()):
            raise ValueError("Expired token")

        return {
            "id": int(user_id),
            "email": email,
        }

    except (ValueError, TypeError, UnicodeDecodeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        ) from None


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer
    ),
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Sign in to access this resource",
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="A bearer token is required",
        )

    return _decode_token(credentials.credentials)


@router.post("/register")
def register(body: RegisterRequest):
    email = str(body.email).lower().strip()

    with _connect() as connection:
        existing = connection.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,),
        ).fetchone()

        if existing:
            raise HTTPException(
                status_code=409,
                detail="An account with this email already exists",
            )

        cursor = connection.execute(
            """
            INSERT INTO users(email, password_hash, created_at)
            VALUES (?, ?, ?)
            """,
            (
                email,
                _password_hash(body.password),
                int(time.time()),
            ),
        )

        user_id = int(cursor.lastrowid)

    return {
        "access_token": _make_token(user_id, email),
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": email,
        },
    }


@router.post("/login")
def login(body: LoginRequest):
    email = str(body.email).lower().strip()

    with _connect() as connection:
        user = connection.execute(
            """
            SELECT id, email, password_hash
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

    if user is None or not _verify_password(
        body.password,
        user["password_hash"],
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )

    user_id = int(user["id"])

    return {
        "access_token": _make_token(
            user_id,
            user["email"],
        ),
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": user["email"],
        },
    }


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return {"user": user}

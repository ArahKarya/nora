"""NORA — auth dependency: Bearer token OR httpOnly cookie 'nora_token'."""
from __future__ import annotations

from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import User
from .security import decode_token

COOKIE_NAME = "nora_token"


def _extract_token(authorization: str | None, cookie: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    if cookie:
        return cookie
    return None


def get_current_user(
    authorization: str | None = Header(default=None),
    nora_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    token = _extract_token(authorization, nora_token)
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise cred_exc
    payload = decode_token(token)
    if not payload or not payload.get("sub"):
        raise cred_exc
    user = db.get(User, payload["sub"])
    if not user:
        raise cred_exc
    return user

"""NORA — password hashing + JWT."""
from __future__ import annotations
import os
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

_SECRET = os.getenv("SECRET_KEY")
if not _SECRET:
    raise RuntimeError(
        "SECRET_KEY env wajib di-set (tidak ada default). "
        "Generate: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
    )
SECRET_KEY: str = _SECRET
ALGORITHM = "HS256"
EXPIRE_DAYS = int(os.getenv("NORA_TOKEN_EXPIRE_DAYS", "1"))

# bcrypt batas 72 byte — truncate manual (hindari ValueError di bcrypt 4.x).
_MAX = 72


def hash_password(password: str) -> str:
    pw = password.encode("utf-8")[:_MAX]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        pw = password.encode("utf-8")[:_MAX]
        return bcrypt.checkpw(pw, password_hash.encode("utf-8"))
    except Exception:
        return False


def create_access_token(subject: str, extra: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": subject, "iat": now, "exp": now + timedelta(days=EXPIRE_DAYS)}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

import secrets
import hashlib
from datetime import datetime, timedelta


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def token_expiry(minutes: int = 30) -> datetime:
    return datetime.utcnow() + timedelta(minutes=minutes)

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError

_password_hasher = PasswordHasher()
SESSION_HOURS = 8

def hash_password(password: str) -> str:
    return _password_hasher.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _password_hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError, ValueError):
        return False

def create_session_token() -> tuple[str, str, datetime]:
    token = secrets.token_urlsafe(40)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=SESSION_HOURS)
    return token, token_hash, expires_at

def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

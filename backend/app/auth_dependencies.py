from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserSession
from app.security import hash_session_token
from app.role_policy import role_has_permission

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    token_hash = hash_session_token(credentials.credentials)
    session = db.query(UserSession).filter(
        UserSession.token_hash == token_hash,
        UserSession.revoked_at.is_(None),
        UserSession.expires_at > datetime.now(timezone.utc),
    ).first()
    if (
        session is None
        or not session.user.is_active
        or (session.user.institution is not None and not session.user.institution.is_active)
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is invalid or expired")
    return session.user

def require_roles(*roles: str):
    allowed = frozenset(roles)
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this resource")
        return user
    return dependency

def require_permission(permission: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if not role_has_permission(user.role, permission):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this resource")
        return user
    return dependency

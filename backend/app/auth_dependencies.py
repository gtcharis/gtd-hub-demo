from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserSession
from app.security import hash_session_token
from app.role_policy import role_has_permission


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User:
    """
    Resolve the authenticated user from a valid, non-revoked session.

    Access is denied when:
    - Credentials are missing or invalid.
    - The session does not exist, has expired or was revoked.
    - The user account is inactive.
    - A non-Programme Administrator has no institution.
    - The user's institution is inactive.
    """

    if (
        credentials is None
        or credentials.scheme.lower() != "bearer"
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    token_hash = hash_session_token(
        credentials.credentials
    )

    session = (
        db.query(UserSession)
        .filter(
            UserSession.token_hash == token_hash,
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > datetime.now(timezone.utc),
        )
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is invalid or expired",
        )

    user = session.user

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or unavailable",
        )

    # Programme Administrators are programme-wide and do not
    # require an institution assignment.
    if user.role == "Programme Administrator":
        return user

    # All other roles must belong to an active institution.
    institution = user.institution

    if institution is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User institution is unavailable",
        )

    if not institution.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User institution is inactive",
        )

    return user


def require_roles(*roles: str):
    """
    Restrict an endpoint to explicitly permitted roles.
    """
    allowed = frozenset(roles)

    def dependency(
        user: User = Depends(get_current_user),
    ) -> User:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )

        return user

    return dependency


def require_permission(permission: str):
    """
    Restrict an endpoint using the central role-permission policy.
    """
    def dependency(
        user: User = Depends(get_current_user),
    ) -> User:
        if not role_has_permission(user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )

        return user

    return dependency
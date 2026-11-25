
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserSession
from app.security import (
    create_session_token,
    hash_session_token,
    verify_password,
)
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse
from app.auth_dependencies import get_current_user
from app.role_policy import permissions_for_role


router = APIRouter(prefix="/auth", tags=["authentication"])


def user_payload(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "institution_id": user.institution_id,
        "institution_name": (
            user.institution.name if user.institution else None
        ),
        "is_active": user.is_active,
        "permissions": sorted(permissions_for_role(user.role)),
    }


def _account_has_valid_scope(user: User) -> bool:
    """
    Programme Administrators are programme-wide.
    All other roles must belong to an active institution.
    """
    if user.role == "Programme Administrator":
        return user.institution_id is None

    institution = user.institution

    return (
        institution is not None
        and institution.is_active
    )


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    email = payload.email.strip().lower()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if (
        user is None
        or not user.is_active
        or not verify_password(
            payload.password,
            user.password_hash,
        )
        or not _account_has_valid_scope(user)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect",
        )

    token, token_hash, expires_at = create_session_token()

    db.add(
        UserSession(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
    )

    db.commit()

    return {
        "access_token": token,
        "expires_at": expires_at,
        "user": user_payload(user),
    }


@router.get("/me", response_model=UserResponse)
def me(
    user: User = Depends(get_current_user),
):
    return user_payload(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    token = (
        authorization.split(" ", 1)[1]
        if authorization and " " in authorization
        else ""
    )

    session = (
        db.query(UserSession)
        .filter(
            UserSession.user_id == user.id,
            UserSession.token_hash == hash_session_token(token),
            UserSession.revoked_at.is_(None),
        )
        .first()
    )

    if session:
        session.revoked_at = datetime.now(timezone.utc)
        db.commit()

    return None

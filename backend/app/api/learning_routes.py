
from datetime import datetime, timezone
import hashlib
import json
from ipaddress import ip_address
from urllib.parse import urlparse
from uuid import uuid4
from zipfile import ZipFile, BadZipFile
from io import BytesIO
import os
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text

from app.database import get_db
from app.models import (
    User,
    Institution,
    LearningCategory,
    LearningResource,
    LearningAuditEvent,
)
from app.auth_dependencies import require_permission
from app.learning_storage import SupabaseStorage, StorageConfigurationError


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/learning", tags=["learning library"])

MAX_FILE_BYTES = 10 * 1024 * 1024

ALLOWED = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


def _visible(query, user):
    if user.role != "Programme Administrator":
        if user.institution_id is None:
            return query.filter(LearningResource.institution_id.is_(None))

        return query.filter(
            (LearningResource.institution_id.is_(None))
            | (LearningResource.institution_id == user.institution_id)
        )

    return query


def _resource_out(row):
    return {
        "id": row.id,
        "title": row.title,
        "description": row.description,
        "category_id": row.category_id,
        "category": row.category.name,
        "resource_type": row.resource_type,
        "source_type": row.source_type,
        "original_filename": row.original_filename,
        "mime_type": row.mime_type,
        "file_size": row.file_size,
        "external_url": row.external_url,
        "publisher": row.publisher,
        "keywords": row.keywords,
        "institution_id": row.institution_id,
        "institution_name": (
            row.institution.name if row.institution else "Programme-wide"
        ),
        "status": row.status,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def _audit(db, resource, user, action):
    db.execute(text("SELECT pg_advisory_xact_lock(731904222)"))

    last = (
        db.query(LearningAuditEvent)
        .order_by(LearningAuditEvent.sequence.desc())
        .with_for_update()
        .first()
    )

    sequence = last.sequence + 1 if last else 1
    previous = last.event_hash if last else "0" * 64
    created = datetime.now(timezone.utc)

    event = {
        "sequence": sequence,
        "resource_id": resource.id if resource else None,
        "actor_user_id": user.id,
        "action": action,
        "created_at": created.isoformat(),
    }

    event_json = json.dumps(
        event,
        sort_keys=True,
        separators=(",", ":"),
    )

    digest = hashlib.sha256(
        f"{sequence}:{previous}:{event_json}".encode("utf-8")
    ).hexdigest()

    db.add(
        LearningAuditEvent(
            sequence=sequence,
            resource_id=resource.id if resource else None,
            actor_user_id=user.id,
            action=action,
            event_json=event_json,
            previous_hash=previous,
            event_hash=digest,
            created_at=created,
        )
    )


def _check_scope(user, institution_id):
    if user.role == "Programme Administrator":
        return

    elif user.role == "Organisation Administrator":
        if institution_id != user.institution_id or institution_id is None:
            raise HTTPException(
                403,
                "Organisation Administrators may manage resources for their own institution only",
            )

    else:
        raise HTTPException(
            403,
            "Learning resource management is restricted",
        )


def _validate_external_url(value: str):
    parsed = urlparse(value.strip())

    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise HTTPException(
            422,
            "External resources must use a valid HTTPS URL",
        )

    host = parsed.hostname.lower().rstrip(".")

    if (
        host in {"localhost", "localhost.localdomain"}
        or host.endswith(".localhost")
        or host.endswith(".local")
    ):
        raise HTTPException(
            422,
            "Local and private network URLs are not permitted",
        )

    try:
        address = ip_address(host)

        if not address.is_global:
            raise HTTPException(
                422,
                "Local and private network URLs are not permitted",
            )

    except ValueError:
        pass

    return value.strip()


def _validate_file(filename: str, content_type: str, content: bytes):
    ext = os.path.splitext(filename.lower())[1]
    expected = ALLOWED.get(ext)

    if not expected or content_type.lower() != expected:
        raise HTTPException(
            415,
            "Only PDF, DOCX and PPTX documents are supported",
        )

    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(
            413,
            "The maximum document size is 10 MB",
        )

    if ext == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise HTTPException(
                415,
                "The uploaded file is not a valid PDF document",
            )

    else:
        try:
            with ZipFile(BytesIO(content)) as archive:
                names = set(archive.namelist())

                expected_entry = (
                    "word/document.xml"
                    if ext == ".docx"
                    else "ppt/presentation.xml"
                )

                if (
                    "[Content_Types].xml" not in names
                    or expected_entry not in names
                ):
                    raise HTTPException(
                        415,
                        "The uploaded Office document is invalid",
                    )

        except BadZipFile:
            raise HTTPException(
                415,
                "The uploaded Office document is invalid",
            )

    return ext, expected


@router.get("/categories")
def categories(
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("learning:read")),
):
    return [
        {
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "description": c.description,
        }
        for c in (
            db.query(LearningCategory)
            .filter(LearningCategory.is_active.is_(True))
            .order_by(
                LearningCategory.sort_order,
                LearningCategory.name,
            )
            .all()
        )
    ]


@router.get("/resources")
def resources(
    q: str = "",
    category_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("learning:read")),
):
    query = (
        _visible(
            db.query(LearningResource).options(
                joinedload(LearningResource.category),
                joinedload(LearningResource.institution),
            ),
            user,
        )
        .filter(LearningResource.status == "published")
    )

    if category_id:
        query = query.filter(
            LearningResource.category_id == category_id
        )

    rows = query.order_by(
        LearningResource.updated_at.desc()
    ).all()

    term = q.strip().casefold()

    return [
        _resource_out(r)
        for r in rows
        if not term
        or term in (
            r.title
            + " "
            + r.description
            + " "
            + r.keywords
            + " "
            + (r.publisher or "")
        ).casefold()
    ]


@router.get("/manage/resources")
def manage_resources(
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("learning:manage")),
):
    query = db.query(LearningResource).options(
        joinedload(LearningResource.category),
        joinedload(LearningResource.institution),
    )

    if user.role == "Organisation Administrator":
        query = query.filter(
            LearningResource.institution_id == user.institution_id
        )

    return [
        _resource_out(r)
        for r in query.order_by(
            LearningResource.updated_at.desc()
        ).all()
    ]


@router.post("/resources", status_code=201)
def create_resource(
    title: str = Form(...),
    description: str = Form(""),
    category_id: int = Form(...),
    resource_type: str = Form("Guide"),
    source_type: str = Form(...),
    publisher: str = Form(""),
    keywords: str = Form(""),
    institution_id: int | None = Form(None),
    external_url: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("learning:manage")),
):
    title = title.strip()

    if not title or len(title) > 180:
        raise HTTPException(
            422,
            "A title of up to 180 characters is required",
        )

    if user.role == "Organisation Administrator" and institution_id is None:
        institution_id = user.institution_id

    _check_scope(user, institution_id)

    if institution_id is not None:
        institution = db.get(Institution, institution_id)

        if not institution or not institution.is_active:
            raise HTTPException(404, "Institution not found")

    category = db.get(LearningCategory, category_id)

    if not category or not category.is_active:
        raise HTTPException(
            422,
            "Select a valid learning category",
        )

    if source_type not in {"upload", "external_link"}:
        raise HTTPException(
            422,
            "Invalid resource source type",
        )

    if source_type == "external_link":
        if file is not None or not external_url:
            raise HTTPException(
                422,
                "Provide an external URL only",
            )

        external_url = _validate_external_url(external_url)
        path = filename = mime = None
        size = None

    else:
        if file is None or not file.filename:
            raise HTTPException(
                422,
                "Choose a document to upload",
            )

        content = file.file.read(MAX_FILE_BYTES + 1)

        ext, mime = _validate_file(
            file.filename,
            file.content_type or "",
            content,
        )

        path = f"resources/{uuid4().hex}{ext}"
        filename = os.path.basename(file.filename)[:255]
        size = len(content)

        try:
            storage = SupabaseStorage()
            storage.upload(path, content, mime)

        except StorageConfigurationError as exc:
            raise HTTPException(503, str(exc))

        except Exception:
            raise HTTPException(
                502,
                "The document could not be saved to private storage",
            )

        external_url = None

    now = datetime.now(timezone.utc)

    row = LearningResource(
        title=title,
        description=description.strip()[:1600],
        category_id=category_id,
        resource_type=resource_type.strip()[:40],
        source_type=source_type,
        storage_path=path,
        original_filename=filename,
        mime_type=mime,
        file_size=size,
        external_url=external_url,
        publisher=publisher.strip()[:180] or None,
        keywords=keywords.strip()[:500],
        institution_id=institution_id,
        status="draft",
        created_by_user_id=user.id,
        updated_by_user_id=user.id,
        created_at=now,
        updated_at=now,
    )

    db.add(row)

    try:
        db.flush()
        _audit(db, row, user, "resource_created")
        db.commit()

    except Exception:
        db.rollback()

        if path:
            try:
                SupabaseStorage().delete(path)
            except Exception:
                pass

        raise

    db.refresh(row)

    row = (
        db.query(LearningResource)
        .options(
            joinedload(LearningResource.category),
            joinedload(LearningResource.institution),
        )
        .get(row.id)
    )

    return _resource_out(row)


@router.patch("/resources/{resource_id}")
def update_resource(
    resource_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("learning:manage")),
):
    row = (
        db.query(LearningResource)
        .options(
            joinedload(LearningResource.category),
            joinedload(LearningResource.institution),
        )
        .filter(LearningResource.id == resource_id)
        .first()
    )

    if not row:
        raise HTTPException(404, "Resource not found")

    if (
        user.role == "Organisation Administrator"
        and row.institution_id != user.institution_id
    ):
        raise HTTPException(404, "Resource not found")

    allowed = {
        "title",
        "description",
        "category_id",
        "resource_type",
        "publisher",
        "keywords",
    }

    for key, value in payload.items():
        if key not in allowed:
            raise HTTPException(
                422,
                f"Field cannot be changed: {key}",
            )

        if key == "category_id":
            category = db.get(LearningCategory, value)

            if not category or not category.is_active:
                raise HTTPException(422, "Invalid category")

            row.category = category

        if isinstance(value, str):
            value = value.strip()

        setattr(row, key, value)

    row.updated_by_user_id = user.id
    row.updated_at = datetime.now(timezone.utc)

    _audit(db, row, user, "resource_updated")
    db.commit()
    db.refresh(row)

    return _resource_out(row)


@router.post("/resources/{resource_id}/status/{action}")
def resource_action(
    resource_id: int,
    action: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("learning:manage")),
):
    row = (
        db.query(LearningResource)
        .options(
            joinedload(LearningResource.category),
            joinedload(LearningResource.institution),
        )
        .filter(LearningResource.id == resource_id)
        .first()
    )

    if not row:
        raise HTTPException(404, "Resource not found")

    if (
        user.role == "Organisation Administrator"
        and row.institution_id != user.institution_id
    ):
        raise HTTPException(404, "Resource not found")

    if action == "publish":
        row.status = "published"

    elif action == "unpublish":
        row.status = "draft"

    elif action == "archive":
        row.status = "archived"

    else:
        raise HTTPException(404, "Unknown resource action")

    row.updated_by_user_id = user.id
    row.updated_at = datetime.now(timezone.utc)

    _audit(db, row, user, f"resource_{action}")
    db.commit()
    db.refresh(row)

    return _resource_out(row)


@router.post("/resources/{resource_id}/access")
def access_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("learning:read")),
):
    row = (
        _visible(db.query(LearningResource), user)
        .filter(
            LearningResource.id == resource_id,
            LearningResource.status == "published",
        )
        .first()
    )

    if not row:
        raise HTTPException(404, "Resource not found")

    _audit(db, row, user, "resource_accessed")
    db.commit()

    if row.source_type == "external_link":
        return {
            "url": row.external_url,
            "source_type": "external_link",
        }

    try:
        url = SupabaseStorage().signed_url(
            row.storage_path,
            300,
        )

    except StorageConfigurationError as exc:
        raise HTTPException(503, str(exc))

    except Exception:
        raise HTTPException(
            502,
            "A secure document link could not be created",
        )

    return {
        "url": url,
        "source_type": "upload",
        "expires_in": 300,
    }


@router.delete("/resources/{resource_id}")
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("learning:manage")),
):
    # Lock only the learning_resources row.
    # This avoids PostgreSQL's FOR UPDATE error on nullable
    # sides of the joined category and institution relationships.
    row = (
        db.query(LearningResource)
        .options(
            joinedload(LearningResource.category),
            joinedload(LearningResource.institution),
        )
        .filter(LearningResource.id == resource_id)
        .with_for_update(of=LearningResource)
        .first()
    )

    if not row:
        raise HTTPException(404, "Resource not found")

    # Enforce institution-level deletion boundaries.
    if user.role == "Organisation Administrator":
        if row.institution_id != user.institution_id:
            raise HTTPException(404, "Resource not found")

    elif user.role != "Programme Administrator":
        raise HTTPException(
            403,
            "Resource deletion is restricted",
        )

    # Preserve a snapshot before the resource is removed.
    snapshot = {
        "resource_id": row.id,
        "title": row.title,
        "source_type": row.source_type,
        "storage_path": row.storage_path,
        "original_filename": row.original_filename,
        "institution_id": row.institution_id,
        "institution_name": (
            row.institution.name
            if row.institution
            else "Programme-wide"
        ),
        "category": (
            row.category.name
            if row.category
            else None
        ),
        "status": row.status,
    }

    # Remove uploaded content first.
    # If storage fails, retain the database record so that
    # the deletion can be retried.
    if row.source_type == "upload" and row.storage_path:
        try:
            SupabaseStorage().delete(row.storage_path)

        except StorageConfigurationError as exc:
            logger.exception(
                "Storage configuration error during resource deletion: resource_id=%s",
                resource_id,
            )
            raise HTTPException(503, str(exc))

        except Exception:
            # Log the underlying exception and traceback.
            # This is the diagnostic change in this version.
            logger.exception(
                "Supabase storage deletion failed: resource_id=%s, storage_path=%s",
                resource_id,
                row.storage_path,
            )

            raise HTTPException(
                502,
                "The document could not be removed from private storage. "
                "The resource record has been retained.",
            )

    try:
        db.execute(
            text("SELECT pg_advisory_xact_lock(731904222)")
        )

        last = (
            db.query(LearningAuditEvent)
            .order_by(LearningAuditEvent.sequence.desc())
            .with_for_update()
            .first()
        )

        sequence = last.sequence + 1 if last else 1
        previous = last.event_hash if last else "0" * 64
        created = datetime.now(timezone.utc)

        event = {
            "sequence": sequence,
            "resource_id": row.id,
            "actor_user_id": user.id,
            "action": "resource_deleted",
            "created_at": created.isoformat(),
            "resource_snapshot": snapshot,
        }

        event_json = json.dumps(
            event,
            sort_keys=True,
            separators=(",", ":"),
        )

        digest = hashlib.sha256(
            f"{sequence}:{previous}:{event_json}".encode("utf-8")
        ).hexdigest()

        db.add(
            LearningAuditEvent(
                sequence=sequence,
                resource_id=row.id,
                actor_user_id=user.id,
                action="resource_deleted",
                event_json=event_json,
                previous_hash=previous,
                event_hash=digest,
                created_at=created,
            )
        )

        db.delete(row)
        db.commit()

    except Exception:
        db.rollback()

        raise HTTPException(
            500,
            "The resource could not be deleted from the database. "
            "If it contained an uploaded file, storage cleanup may need "
            "to be retried.",
        )

    return {
        "message": "Learning resource permanently deleted",
        "resource_id": resource_id,
    }

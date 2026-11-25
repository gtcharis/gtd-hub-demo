
"""Private Supabase Storage adapter for the GTD Hub Learning Library."""

import os
import logging
from urllib.parse import quote

import httpx


logger = logging.getLogger(__name__)


class StorageConfigurationError(RuntimeError):
    pass


class SupabaseStorage:
    def __init__(self):
        self.base_url = os.getenv("SUPABASE_URL", "").rstrip("/")
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        self.bucket = os.getenv(
            "SUPABASE_STORAGE_BUCKET",
            "gtdhub-learning-resources",
        )

        if not self.base_url or not self.key:
            raise StorageConfigurationError(
                "Learning document storage is not configured"
            )

    def _headers(self, content_type="application/json"):
        return {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": content_type,
        }

    def _raise_storage_error(self, operation, response):
        # Do not log API keys or Authorization headers.
        # Supabase response bodies contain useful error details.
        try:
            detail = response.text[:1500]
        except Exception:
            detail = "No response body available"

        logger.error(
            "Supabase storage %s failed: status=%s, response=%s",
            operation,
            response.status_code,
            detail,
        )

        raise RuntimeError(
            f"Storage {operation} failed "
            f"({response.status_code}): {detail}"
        )

    def upload(self, path: str, content: bytes, content_type: str):
        url = (
            f"{self.base_url}/storage/v1/object/"
            f"{quote(self.bucket, safe='')}/"
            f"{quote(path, safe='/')}"
        )

        response = httpx.post(
            url,
            content=content,
            headers={
                **self._headers(content_type),
                "x-upsert": "false",
            },
            timeout=30,
        )

        if response.status_code not in (200, 201):
            self._raise_storage_error("upload", response)

    def signed_url(self, path: str, expires_in: int = 300) -> str:
        url = (
            f"{self.base_url}/storage/v1/object/sign/"
            f"{quote(self.bucket, safe='')}/"
            f"{quote(path, safe='/')}"
        )

        response = httpx.post(
            url,
            json={"expiresIn": expires_in},
            headers=self._headers(),
            timeout=15,
        )

        if response.status_code != 200:
            self._raise_storage_error("signed URL creation", response)

        payload = response.json()

        signed = payload.get("signedURL") or payload.get("signedUrl")

        if not signed:
            raise RuntimeError(
                "Storage returned no signed URL"
            )

        return (
            signed
            if signed.startswith("http")
            else f"{self.base_url}/storage/v1{signed}"
        )

    
def delete(self, path: str):
    """
    Delete one object using Supabase's bucket-level remove operation.
    """

    clean_path = path.lstrip("/")

    if not clean_path:
        raise ValueError("Storage object path cannot be empty")

    url = (
        f"{self.base_url}/storage/v1/object/"
        f"{quote(self.bucket, safe='')}"
    )

    response = httpx.request(
        "DELETE",
        url,
        json={"prefixes": [clean_path]},
        headers=self._headers(),
        timeout=30,
    )

    if response.status_code in (200, 204):
        logger.info(
            "Supabase storage object deleted: bucket=%s, path=%s",
            self.bucket,
            clean_path,
        )
        return

    self._raise_storage_error("delete", response)

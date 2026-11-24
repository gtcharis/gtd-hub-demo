"""Authenticated encryption and tamper-evident audit helpers for restricted case data."""
import base64, hashlib, hmac, json, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import HTTPException

KEY_VERSION = os.getenv("CASE_ENCRYPTION_KEY_VERSION", "v1")

def _key(name: str) -> bytes:
    raw = os.getenv(name, "").strip()
    if not raw:
        raise HTTPException(status_code=503, detail=f"Secure case service unavailable: {name} is not configured")
    try:
        value = base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Secure case service unavailable: {name} is invalid") from exc
    if len(value) != 32:
        raise HTTPException(status_code=503, detail=f"Secure case service unavailable: {name} must decode to 32 bytes")
    return value

def encrypt_case(data: dict, case_id: str, institution_id: int) -> tuple[bytes, bytes, str]:
    nonce = os.urandom(12)
    aad = f"gtdhub:case:{case_id}:institution:{institution_id}:schema:1".encode()
    ciphertext = AESGCM(_key("CASE_ENCRYPTION_KEY")).encrypt(nonce, json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode(), aad)
    return ciphertext, nonce, KEY_VERSION

def decrypt_case(ciphertext: bytes, nonce: bytes, key_version: str, case_id: str, institution_id: int) -> dict:
    if key_version != KEY_VERSION:
        raise HTTPException(status_code=503, detail="Case encryption key version is unavailable; contact the system owner")
    aad = f"gtdhub:case:{case_id}:institution:{institution_id}:schema:1".encode()
    try:
        plain = AESGCM(_key("CASE_ENCRYPTION_KEY")).decrypt(nonce, ciphertext, aad)
        return json.loads(plain)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Case data could not be authenticated or decrypted") from exc

def audit_digest(sequence: int, previous_hash: str, event_json: str) -> str:
    message = f"{sequence}|{previous_hash}|{event_json}".encode()
    return hmac.new(_key("CASE_AUDIT_HMAC_KEY"), message, hashlib.sha256).hexdigest()

import base64, os
import pytest
from app.case_security import encrypt_case, decrypt_case

@pytest.fixture(autouse=True)
def test_crypto_keys(monkeypatch):
    monkeypatch.setenv("CASE_ENCRYPTION_KEY", base64.urlsafe_b64encode(b"e" * 32).decode())
    monkeypatch.setenv("CASE_AUDIT_HMAC_KEY", base64.urlsafe_b64encode(b"a" * 32).decode())

def test_case_payload_is_authenticated_encrypted():
    payload = {"narrative": "synthetic confidential example"}
    ciphertext, nonce, version = encrypt_case(payload, "case-123", 42)
    assert b"synthetic confidential example" not in ciphertext
    assert len(nonce) == 12
    assert decrypt_case(ciphertext, nonce, version, "case-123", 42) == payload
    with pytest.raises(Exception):
        decrypt_case(ciphertext, nonce, version, "case-123", 43)

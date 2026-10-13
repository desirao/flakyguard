"""HMAC-SHA256 Webhook Authentication & Signature Verification."""

import hashlib
import hmac
from typing import Optional
from app.config import settings


DEFAULT_SECRET = settings.GITHUB_WEBHOOK_SECRET


def compute_hmac_signature(payload_bytes: bytes, secret: Optional[str] = None) -> str:
    """Compute HMAC SHA-256 signature for given payload."""
    sec = (secret or settings.GITHUB_WEBHOOK_SECRET).encode("utf-8")
    sig = hmac.new(sec, payload_bytes, hashlib.sha256).hexdigest()
    return f"sha256={sig}"


generate_hmac_signature = compute_hmac_signature


def verify_hmac_signature(
    payload_bytes: bytes,
    signature_header: Optional[str],
    secret: Optional[str] = None,
) -> bool:
    """Verify incoming X-Hub-Signature-256 using constant-time comparison."""
    if not signature_header:
        return False

    expected_sig = compute_hmac_signature(payload_bytes, secret)

    # Constant-time comparison protects against timing attacks
    return hmac.compare_digest(expected_sig, signature_header)

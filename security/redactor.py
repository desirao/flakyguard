"""Secret & PII Redaction Engine and Prompt Injection Sanitizer.

Filters API keys, passwords, bearer tokens, private keys, IP addresses,
and prompt injection attempts from untrusted CI logs and incoming payloads.
"""

import re
from typing import Dict, List, Tuple

# Compiled regex patterns for credential detection
REDACTION_PATTERNS = [
    # AWS Access Key ID
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED_SECRET:AWS_KEY]"),
    # GitHub Tokens
    (re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{16,}\b"), "[REDACTED_SECRET:GITHUB_PAT]"),
    (re.compile(r"\bgithub_pat_[a-zA-Z0-9_]{20,}\b"), "[REDACTED_SECRET:GITHUB_PAT]"),
    # Generic API Keys & Hex Secrets
    (re.compile(r"(?i)(api[_-]?key|secret[_-]?key|token)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{16,})['\"]?"), r"\1=[REDACTED_SECRET:API_KEY]"),
    # JWT Tokens
    (re.compile(r"\beyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b"), "[REDACTED_SECRET:JWT_TOKEN]"),
    # Authorization Bearer Headers
    (re.compile(r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}"), "Bearer [REDACTED_SECRET:BEARER_TOKEN]"),
    # Private Key Headers
    (re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----[\s\S]*?-----END [A-Z ]+PRIVATE KEY-----"), "[REDACTED_SECRET:PRIVATE_KEY]"),
    # Database Connection Passwords
    (re.compile(r"(postgresql|mysql|mongodb|redis)://([^:]+):([^@]+)@"), r"\1://\2:[REDACTED_PASSWORD]@"),
    # Non-local IPv4 Addresses
    (re.compile(r"\b(?!127\.0\.0\.1|0\.0\.0\.0)(?:[1-9]\d{0,2}\.){3}[1-9]\d{0,2}\b"), "[REDACTED_IP]"),
    # Passwords in URLs, configs, or queries
    (re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?([^\s'\"]+)['\"]?"), r"\1=[REDACTED_PASSWORD]"),
    # Stripe Secret Keys
    (re.compile(r"\bsk_(live|test)_[a-zA-Z0-9]{14,}\b"), "[REDACTED_STRIPE_KEY]"),
]

# Adversarial prompt injection keywords
INJECTION_KEYWORDS = [
    re.compile(r"(?i)ignore\s+(all\s+)?(previous\s+|prior\s+)?instructions"),
    re.compile(r"(?i)system\s+prompt\s*(override|:)"),
    re.compile(r"(?i)you\s+are\s+now\s+in\s+dan\s+mode"),
    re.compile(r"(?i)<<<ci_log_(start|end)>>>"),
]


def redact_secrets(raw_text: str) -> Tuple[str, int]:
    """Redact sensitive credentials from text. Returns (sanitized_text, count_of_redactions)."""
    if not raw_text:
        return "", 0

    sanitized = raw_text
    total_redacted = 0

    for pattern, replacement in REDACTION_PATTERNS:
        matches = len(pattern.findall(sanitized))
        if matches > 0:
            total_redacted += matches
            sanitized = pattern.sub(replacement, sanitized)

    return sanitized, total_redacted


def sanitize_prompt_injection(raw_text: str) -> Tuple[str, bool]:
    """Detect and defuse prompt injection attempts inside untrusted logs."""
    is_adversarial = False
    sanitized = raw_text

    for kw in INJECTION_KEYWORDS:
        if kw.search(sanitized):
            is_adversarial = True
            sanitized = kw.sub("[INJECTION_BLOCKED]", sanitized)

    return sanitized, is_adversarial


def is_safe_log(raw_text: str) -> bool:
    """Return True if no prompt injection patterns are detected."""
    _, is_adversarial = sanitize_prompt_injection(raw_text)
    return not is_adversarial

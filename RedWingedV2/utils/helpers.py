"""
RedWinged V2 — Utility Helpers
=================================
Data formatting, sanitization, and common utilities.
"""
from __future__ import annotations
import re
from datetime import datetime, timezone
from typing import Any


def sanitize_input(value: str, *, max_length: int = 200) -> str:
    """
    Sanitize user input by stripping whitespace and dangerous characters.

    Args:
        value: Raw user input.
        max_length: Maximum allowed length.

    Returns:
        Cleaned string safe for use in URLs and display.
    """
    cleaned = value.strip()
    # Remove control characters
    cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", cleaned)
    # Truncate
    return cleaned[:max_length]


def sanitize_username(username: str) -> str:
    """
    Sanitize a username for use in URL templates.

    Removes special characters that are not typically valid in usernames.

    Args:
        username: Raw username input.

    Returns:
        Cleaned username string.
    """
    cleaned = sanitize_input(username, max_length=64)
    # Allow alphanumeric, underscores, hyphens, and dots
    cleaned = re.sub(r"[^a-zA-Z0-9_.\-]", "", cleaned)
    return cleaned


def format_table_row(data: dict[str, Any], keys: list[str]) -> list[str]:
    """
    Extract and format values from a dict for table display.

    Args:
        data: Source dictionary.
        keys: Keys to extract in order.

    Returns:
        List of string values.
    """
    return [str(data.get(k, "—")) for k in keys]


def timestamp() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def truncate(text: str, length: int = 80, suffix: str = "…") -> str:
    """Truncate text to a maximum length with suffix."""
    if len(text) <= length:
        return text
    return text[: length - len(suffix)] + suffix


def format_bytes(size: int) -> str:
    """Format byte count into human-readable string."""
    for unit in ("B", "KB", "MB", "GB"):
        if abs(size) < 1024:
            return f"{size:.1f} {unit}"
        size //= 1024
    return f"{size:.1f} TB"


def is_valid_email(email: str) -> bool:
    """Basic email format validation."""
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def extract_domain(url: str) -> str:
    """Extract domain from a URL string."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.hostname or ""
    except Exception:
        return ""

"""
Admin security middleware and utilities.

Provides:
- Audit logging for admin actions
- Admin action rate limiting
- Login attempt tracking and account lockout
"""

import logging
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Account lockout
# ---------------------------------------------------------------------------

MAX_FAILED_LOGIN_ATTEMPTS = 10
ACCOUNT_LOCKOUT_MINUTES = 15


def check_account_locked(user: models.User) -> None:
    """Raise 423 if account is temporarily locked due to failed attempts."""
    if user.locked_until and user.locked_until > datetime.utcnow():
        remaining = int((user.locked_until - datetime.utcnow()).total_seconds() / 60)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account temporarily locked. Try again in {remaining} minutes.",
        )


def record_failed_login(db: Session, user: models.User, ip_address: str | None = None) -> None:
    """Increment failed login counter; lock account if threshold exceeded."""
    user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
    if user.failed_login_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
        user.locked_until = datetime.utcnow() + timedelta(minutes=ACCOUNT_LOCKOUT_MINUTES)
        logger.warning(
            "Account locked user=%s attempts=%d ip=%s",
            user.email, user.failed_login_attempts, ip_address,
        )
    db.commit()


def reset_failed_login_count(db: Session, user: models.User) -> None:
    """Reset failed login counter on successful login."""
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()


# ---------------------------------------------------------------------------
# Audit logging
# ---------------------------------------------------------------------------

def log_admin_action(
    db: Session,
    user_id: str,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> models.AuditLog:
    """Create an audit log entry for an admin action."""
    entry = models.AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(entry)
    db.commit()
    return entry


# ---------------------------------------------------------------------------
# Rate limiting helpers
# ---------------------------------------------------------------------------

class AdminRateLimiter:
    """
    Simple in-memory rate limiter for admin actions.
    Falls back gracefully if storage fails.
    """

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: dict[str, list[datetime]] = {}

    def check(self, key: str) -> bool:
        """Return True if request is allowed, False if rate limited."""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window_seconds)

        if key not in self._buckets:
            self._buckets[key] = []

        self._buckets[key] = [t for t in self._buckets[key] if t > cutoff]

        if len(self._buckets[key]) >= self.max_requests:
            return False

        self._buckets[key].append(now)
        return True


admin_rate_limiter = AdminRateLimiter(max_requests=120, window_seconds=60)

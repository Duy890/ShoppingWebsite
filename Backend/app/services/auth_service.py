from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from .. import models, repositories
from ..core.config import get_settings
from ..core.email import build_reset_password_email, build_verify_email_change_email, send_email
from ..core.security import (
    create_access_token as _create_access_token,
    create_mfa_challenge_token,
    create_refresh_token as _create_refresh_token_core,
    decode_mfa_challenge_token,
    hash_password,
    verify_password,
)
from ._common import generate_unique_token


def register_user(db: Session, email: str, password: str, full_name: Optional[str] = None) -> models.User:
    if repositories.get_user_by_email(db, email):
        raise ValueError("Email already registered")

    hashed_password = hash_password(password)
    return repositories.create_user(db, email=email, hashed_password=hashed_password, full_name=full_name)


def authenticate_user(db: Session, email: str, password: str) -> models.User:
    user = repositories.get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid email or password")
    return user


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    return _create_access_token(subject, expires_delta)


def get_user(db: Session, user_id: str) -> models.User:
    user = repositories.get_user(db, user_id)
    if not user:
        raise ValueError("User not found")
    return user


async def create_reset_token_and_send_email(db: Session, email: str) -> None:
    user = repositories.get_user_by_email(db, email)
    if not user:
        raise ValueError("No account found with this email")

    token = generate_unique_token(db, models.PasswordResetToken)
    reset_token = models.PasswordResetToken(
        token=token,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(hours=1),
        used=False,
    )
    db.add(reset_token)
    db.commit()

    reset_url = f"{get_settings().FRONTEND_URL}/reset-password?token={token}"
    html = build_reset_password_email(reset_url, user.full_name or "")
    await send_email(
        to=email,
        subject="Reset your password — Electronics Store",
        html_body=html,
    )


async def create_email_change_token_and_send(db: Session, user: models.User, new_email: str) -> None:
    existing = repositories.get_user_by_email(db, new_email)
    if existing and existing.id != user.id:
        raise ValueError("This email is already registered to another account")

    token = generate_unique_token(db, models.EmailChangeToken)
    email_token = models.EmailChangeToken(
        token=token,
        user_id=user.id,
        new_email=new_email,
        expires_at=datetime.utcnow() + timedelta(hours=1),
        used=False,
    )
    db.add(email_token)
    db.commit()

    verify_url = f"{get_settings().FRONTEND_URL}/verify-email-change?token={token}"
    html = build_verify_email_change_email(verify_url, new_email, user.full_name or "")
    await send_email(
        to=new_email,
        subject="Confirm your new email — Electronics Store",
        html_body=html,
    )


def confirm_email_change(db: Session, token: str) -> models.User:
    email_token = (
        db.query(models.EmailChangeToken)
        .filter(models.EmailChangeToken.token == token, models.EmailChangeToken.used.is_(False))
        .first()
    )
    if not email_token:
        raise ValueError("Invalid or expired verification token")

    if datetime.utcnow() > email_token.expires_at:
        email_token.used = True
        db.commit()
        raise ValueError("Verification link has expired")

    user = repositories.get_user(db, email_token.user_id)
    if not user:
        raise ValueError("User not found")

    user.email = email_token.new_email
    email_token.used = True
    db.commit()
    db.refresh(user)
    return user


def create_reset_token(db: Session, email: str) -> str:
    user = repositories.get_user_by_email(db, email)
    if not user:
        raise ValueError("No account found with this email")
    token = generate_unique_token(db, models.PasswordResetToken)
    reset_token = models.PasswordResetToken(
        token=token,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(hours=1),
        used=False,
    )
    db.add(reset_token)
    db.commit()
    return token


def reset_password(db: Session, token: str, new_password: str) -> models.User:
    reset_token = (
        db.query(models.PasswordResetToken)
        .filter(models.PasswordResetToken.token == token, models.PasswordResetToken.used.is_(False))
        .first()
    )
    if not reset_token:
        raise ValueError("Invalid or expired reset token")

    if datetime.utcnow() > reset_token.expires_at:
        reset_token.used = True
        db.commit()
        raise ValueError("Reset token has expired")

    user = repositories.get_user(db, reset_token.user_id)
    if not user:
        raise ValueError("User not found")
    user.hashed_password = hash_password(new_password)
    reset_token.used = True
    db.commit()
    db.refresh(user)
    return user


def get_login_history_for_user(db: Session, user_id: str, limit: int = 20):
    return repositories.get_login_history(db, user_id, limit)


def record_login_attempt(
    db: Session, user_id: str, success: bool,
    ip_address: str | None = None, user_agent: str | None = None,
    fail_reason: str | None = None,
) -> models.LoginHistory:
    return repositories.create_login_history(db, user_id, success, ip_address, user_agent, fail_reason)


def create_mfa_challenge(db: Session, user: models.User) -> str:
    token, jti, expires = create_mfa_challenge_token(user.id)
    repositories.create_mfa_challenge(db, user.id, jti, expires)
    return token


def verify_mfa_challenge_and_login(
    db: Session, challenge_token: str, totp_code: str,
    device_info: str | None = None, ip_address: str | None = None,
) -> tuple[models.User, str, str]:
    payload = decode_mfa_challenge_token(challenge_token)
    if not payload:
        raise ValueError("Invalid or expired MFA challenge token")

    user_id = payload.get("sub")
    jti = payload.get("jti")
    if not user_id or not jti:
        raise ValueError("Invalid MFA challenge token")

    stored = repositories.get_mfa_challenge_by_jti(db, jti)
    if not stored:
        raise ValueError("MFA challenge already used or expired")
    if stored.user_id != user_id:
        raise ValueError("MFA challenge token user mismatch")

    try:
        import pyotp
    except ImportError:
        raise ValueError("MFA not available (pyotp not installed)")

    user = repositories.get_user(db, user_id)
    if not user or not user.mfa_secret:
        raise ValueError("MFA not configured for this account")

    totp = pyotp.TOTP(user.mfa_secret)
    if not totp.verify(totp_code):
        raise ValueError("Invalid MFA code")

    repositories.mark_mfa_challenge_used(db, jti)

    raw_token, token_hash, expires = _create_refresh_token_core(user_id)
    repositories.create_refresh_token(db, user_id, token_hash, expires, device_info, ip_address)
    access = _create_access_token(user_id)
    return user, access, raw_token

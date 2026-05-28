from sqlalchemy.orm import Session

from .. import repositories
from ..core.security import create_refresh_token as _create_refresh_token


def create_refresh_token_for_user(
    db: Session, user_id: str, device_info: str | None = None, ip_address: str | None = None
) -> tuple[str, str]:
    raw_token, token_hash, expires = _create_refresh_token(user_id)
    repositories.create_refresh_token(db, user_id, token_hash, expires, device_info, ip_address)
    return raw_token, token_hash


def revoke_all_sessions(db: Session, user_id: str) -> None:
    repositories.revoke_all_user_refresh_tokens(db, user_id)


def rotate_refresh_token(
    db: Session,
    old_token_id: str,
    user_id: str,
    device_info: str | None = None,
    ip_address: str | None = None,
) -> tuple[str, str]:
    """Revoke token cũ và phát hành token mới (refresh token rotation)."""
    repositories.revoke_refresh_token(db, old_token_id)
    return create_refresh_token_for_user(db, user_id, device_info, ip_address)

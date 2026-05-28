from sqlalchemy.orm import Session

from .. import models, repositories


def update_profile(
    db: Session,
    user: models.User,
    full_name: str | None = None,
    avatar_url: str | None = None,
) -> models.User:
    """Cập nhật thông tin profile của user."""
    return repositories.update_user_profile(db, user, full_name, avatar_url)

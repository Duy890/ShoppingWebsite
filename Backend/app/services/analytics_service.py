from sqlalchemy.orm import Session

from .. import repositories


def get_admin_stats(db: Session):
    return {
        "total_products": repositories.get_product_count(db),
        "total_orders": repositories.get_order_count(db),
        "total_revenue": repositories.get_total_revenue(db),
        "total_users": repositories.get_user_count(db),
    }


def get_revenue_by_month(db: Session) -> list[dict]:
    return repositories.get_revenue_by_month(db)


def get_revenue_by_year(db: Session) -> list[dict]:
    return repositories.get_revenue_by_year(db)


def get_audit_logs(db: Session, limit: int = 100, offset: int = 0):
    return repositories.get_audit_logs(db, limit, offset)


def get_audit_logs_for_user(db: Session, user_id: str, limit: int = 50, offset: int = 0):
    """Lấy audit logs của một user cụ thể theo user_id."""
    return repositories.get_audit_logs_for_user(db, user_id, limit, offset)


def get_login_history_for_user(db: Session, user_id: str, limit: int = 20):
    """Lấy lịch sử đăng nhập của một user cụ thể."""
    return repositories.get_login_history(db, user_id, limit)


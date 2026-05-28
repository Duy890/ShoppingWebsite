from typing import Optional

from sqlalchemy.orm import Session

from .. import repositories


def get_categories(db: Session):
    return repositories.get_categories(db)


def get_categories_tree(db: Session):
    return repositories.get_categories_tree(db)


def get_brands_by_category(db: Session, category_id: str | None = None):
    return repositories.get_brands_by_category(db, category_id)


def get_search_suggestions(db: Session, query: str, limit: int = 8):
    return repositories.get_search_suggestions(db, query, limit)


def create_category(
    db: Session,
    name: str,
    description: Optional[str] = None,
    parent_id: Optional[str] = None,
):
    return repositories.create_category(db, name, description, parent_id)


def get_category(db: Session, category_id: str):
    category = repositories.get_category(db, category_id)
    if not category:
        raise ValueError("Category not found")
    return category


def delete_category(db: Session, category_id: str):
    category = repositories.get_category(db, category_id)
    if not category:
        raise ValueError("Category not found")
    if category.children:
        raise ValueError("Category has child categories and cannot be deleted")
    if category.products:
        raise ValueError("Category has products and cannot be deleted")
    repositories.delete_category(db, category)

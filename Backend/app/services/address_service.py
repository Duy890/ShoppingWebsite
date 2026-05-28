from sqlalchemy.orm import Session

from .. import repositories


def get_user_addresses(db: Session, user_id: str):
    return repositories.get_addresses_by_user(db, user_id)


def create_address(db: Session, user_id: str, address_data: dict):
    return repositories.create_address(db, user_id, address_data)


def update_address(db: Session, user_id: str, address_id: str, updates: dict):
    address = repositories.get_address_by_id(db, address_id)
    if not address or address.user_id != user_id:
        raise ValueError("Address not found")
    return repositories.update_address(db, address, updates)


def delete_address(db: Session, user_id: str, address_id: str):
    address = repositories.get_address_by_id(db, address_id)
    if not address or address.user_id != user_id:
        raise ValueError("Address not found")
    repositories.delete_address(db, address)


def set_default_address(db: Session, user_id: str, address_id: str):
    address = repositories.get_address_by_id(db, address_id)
    if not address or address.user_id != user_id:
        raise ValueError("Address not found")
    return repositories.set_default_address(db, address)

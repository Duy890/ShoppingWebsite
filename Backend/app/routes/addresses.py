"""Address routes: CRUD + set default."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..services import address_service
from ..core.database import get_db
from ..deps import get_current_user

router = APIRouter(tags=["addresses"])


@router.get("/addresses", response_model=list[schemas.AddressRead])
def read_addresses(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return address_service.get_user_addresses(db, current_user.id)


@router.post("/addresses", response_model=schemas.AddressRead)
def create_address(payload: schemas.AddressCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return address_service.create_address(db, current_user.id, payload.dict())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/addresses/{address_id}", response_model=schemas.AddressRead)
def edit_address(address_id: str, payload: schemas.AddressUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return address_service.update_address(db, current_user.id, address_id, payload.dict(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_address(address_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        address_service.delete_address(db, current_user.id, address_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/addresses/{address_id}/set-default", response_model=schemas.AddressRead)
def set_default_address(address_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return address_service.set_default_address(db, current_user.id, address_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

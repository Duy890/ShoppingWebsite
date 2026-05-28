"""Order routes: CRUD, tracking, timeline, admin order management."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..services import order_service
from ..core.admin_security import log_admin_action
from ..core.database import get_db
from ..deps import get_current_user, require_admin

router = APIRouter(tags=["orders"])
logger = logging.getLogger(__name__)


@router.post("/orders", response_model=schemas.OrderRead)
def create_order(payload: schemas.OrderCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"ORDER PAYLOAD RECEIVED: {payload.dict()}")
    try:
        return order_service.create_order(
            db,
            current_user.id,
            [item.dict() for item in payload.items],
            payload.shipping_address,
            payload.payment_method,
            payload.address_id,
            payload.shipping_method,
            payload.shipping_fee,
            payload.order_note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/orders", response_model=list[schemas.OrderRead])
def read_orders(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return order_service.get_user_orders(db, current_user.id)


@router.get("/orders/{order_id}", response_model=schemas.OrderRead)
def read_order(order_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        order = order_service.get_order(db, order_id)
        if order.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        return order
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/admin/orders", response_model=list[schemas.OrderRead])
def read_all_orders(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    return order_service.get_all_orders(db)


@router.put("/orders/{order_id}/status", response_model=schemas.OrderRead)
def set_order_status(order_id: str, payload: schemas.OrderStatusUpdate, request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        result = order_service.update_order_status_with_history(db, order_id, payload.status, payload.note, current_user.id)
        log_admin_action(
            db, current_user.id, "order.status.update", "order", order_id,
            details={"status": result.status, "note": payload.note},
            ip_address=request.client.host if request.client else None,
        )
        return result
    except ValueError as exc:
        log_admin_action(
            db, current_user.id, "order.status.update.failed", "order", order_id,
            details={"error": str(exc)},
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/orders/{order_id}/tracking", response_model=schemas.OrderTracking)
def get_order_tracking(order_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        order = order_service.get_order(db, order_id)
        if order.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        return schemas.OrderTracking(
            order_id=order.id,
            status=order.status,
            tracking_code=order.tracking_code,
            shipping_provider=order.shipping_provider,
            estimated_delivery=order.estimated_delivery,
            delivered_at=order.delivered_at,
            cancelled_at=order.cancelled_at,
            cancel_reason=order.cancel_reason,
            shipping_method=order.shipping_method,
            shipping_fee=order.shipping_fee,
            estimated_delivery_days=order.estimated_delivery_days,
            order_note=order.order_note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/orders/{order_id}/timeline", response_model=schemas.OrderTimeline)
def get_order_timeline(order_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        order = order_service.get_order(db, order_id)
        if order.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        history = order_service.get_order_tracking_timeline(db, order_id)
        return schemas.OrderTimeline(history=history)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/admin/orders/{order_id}/simulate-next", response_model=schemas.OrderRead)
def simulate_next_order_status(order_id: str, request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        result = order_service.simulate_next_order_status(db, order_id, current_user.id)
        log_admin_action(
            db, current_user.id, "order.status.simulate", "order", order_id,
            details={"status": result.status},
            ip_address=request.client.host if request.client else None,
        )
        return result
    except ValueError as exc:
        log_admin_action(
            db, current_user.id, "order.status.simulate.failed", "order", order_id,
            details={"error": str(exc)},
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(status_code=400, detail=str(exc))

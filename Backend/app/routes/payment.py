"""Payment routes: MoMo payment creation and IPN callback."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..services import payment_service, order_service
from ..core.database import get_db
from ..deps import get_current_user

router = APIRouter(tags=["payment"])


@router.post("/payment/momo/create", response_model=schemas.MoMoPaymentResponse)
def create_momo_payment(
    payload: schemas.MoMoPaymentRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = payment_service.create_momo_payment(
            amount=payload.amount,
            order_id=payload.order_id,
            order_info=payload.order_info,
        )
        return schemas.MoMoPaymentResponse(
            pay_url=result.get("payUrl", ""),
            result_code=result.get("resultCode", 0),
            message=result.get("message", ""),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/payment/momo/ipn")
def momo_ipn(payload: schemas.MoMoIPNPayload, db: Session = Depends(get_db)):
    payload_dict = payload.dict()

    if not payment_service.verify_momo_ipn_signature(payload_dict):
        raise HTTPException(status_code=400, detail="Invalid signature")

    order_id = payload.orderId

    try:
        if payload.resultCode == 0:
            order_service.update_order_status_with_history(
                db, order_id, "confirmed", "MoMo payment successful", None
            )
        else:
            order_service.update_order_status_with_history(
                db, order_id, "payment_failed", f"MoMo: {payload.message}", None
            )
    except Exception as e:
        print(f"IPN processing error: {e}")

    return {"status": "ok"}

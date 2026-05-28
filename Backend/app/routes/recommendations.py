"""Recommendation routes: personalized, similar products, cart co-purchase."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..services import recommendation_service
from ..core.database import get_db
from ..deps import get_current_user, get_optional_user

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations", response_model=schemas.RecommendationResponse)
def get_recommendations(
    limit: int = 8,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_optional_user),
):
    user_id = current_user.id if current_user else None
    items = recommendation_service.get_recommendations(db, user_id=user_id, limit=limit)
    strategy = "personalized" if user_id else "popular"
    return {"items": items, "strategy": strategy}


@router.get("/products/{product_id}/similar", response_model=schemas.RecommendationResponse)
def get_similar_products(
    product_id: str,
    limit: int = 6,
    db: Session = Depends(get_db),
):
    items = recommendation_service.get_similar_products(db, product_id=product_id, limit=limit)
    return {"items": items, "strategy": "similar"}


@router.get("/cart/recommendations", response_model=schemas.RecommendationResponse)
def get_cart_recommendations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    items = recommendation_service.get_cart_recommendations(db, user_id=current_user.id, limit=4)
    return {"items": items, "strategy": "co_purchase"}

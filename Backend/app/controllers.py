from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import chat_service, models, schemas, services
from .core.database import get_db
from .core.security import create_access_token, decode_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    try:
        user = services.get_user(db, user_id)
        return user
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")


def require_admin(user: models.User) -> None:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

UPLOAD_DIR = Path(__file__).resolve().parent / "static" / "images"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def build_image_url(filename: str, request: Request) -> str:
    base_url = str(request.base_url).rstrip('/')
    return f"{base_url}/uploads/images/{filename}"


@router.post("/upload-image")
def upload_image(request: Request, file: UploadFile = File(...), current_user: models.User = Depends(get_current_user)):
    require_admin(current_user)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file")

    extension = Path(file.filename).suffix or ".jpg"
    filename = f"{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / filename

    try:
        with file_path.open("wb") as buffer:
            buffer.write(file.file.read())
    except OSError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to save uploaded image") from exc

    return {"image_url": build_image_url(filename, request)}


@router.post("/upload-avatar")
def upload_avatar(request: Request, file: UploadFile = File(...), current_user: models.User = Depends(get_current_user)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file")

    extension = Path(file.filename).suffix or ".jpg"
    filename = f"avatar_{current_user.id}_{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / filename

    try:
        with file_path.open("wb") as buffer:
            buffer.write(file.file.read())
    except OSError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to save uploaded avatar") from exc

    return {"avatar_url": build_image_url(filename, request)}


@router.post("/auth/register", response_model=schemas.TokenWithUser)
def register_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        user = services.register_user(db, payload.email, payload.password, payload.full_name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    access_token = services.create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.post("/auth/login", response_model=schemas.TokenWithUser)
def login(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        user = services.authenticate_user(db, payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    access_token = services.create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.get("/auth/me", response_model=schemas.UserResponse)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.put("/users/me", response_model=schemas.UserResponse)
def update_profile(payload: schemas.UserUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = services.update_profile(db, current_user, payload.full_name, payload.avatar_url)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return user


@router.post("/api/chat", response_model=schemas.ChatResponse)
def chat(payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    return chat_service.process_chat_request(payload, db)


@router.get("/addresses", response_model=list[schemas.AddressRead])
def read_addresses(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.get_user_addresses(db, current_user.id)


@router.post("/addresses", response_model=schemas.AddressRead)
def create_address(payload: schemas.AddressCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return services.create_address(db, current_user.id, payload.dict())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.put("/addresses/{address_id}", response_model=schemas.AddressRead)
def edit_address(address_id: str, payload: schemas.AddressUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return services.update_address(db, current_user.id, address_id, payload.dict(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_address(address_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        services.delete_address(db, current_user.id, address_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch("/addresses/{address_id}/set-default", response_model=schemas.AddressRead)
def set_default_address(address_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return services.set_default_address(db, current_user.id, address_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/categories", response_model=list[schemas.CategoryRead])
def read_categories(db: Session = Depends(get_db)):
    return services.get_categories(db)


@router.get("/categories/tree", response_model=list[schemas.CategoryTreeRead])
def read_category_tree(db: Session = Depends(get_db)):
    return services.get_categories_tree(db)


@router.get("/search/suggestions", response_model=list[schemas.SearchSuggestionRead])
def read_search_suggestions(q: str | None = None, db: Session = Depends(get_db)):
    return services.get_search_suggestions(db, q or "")


@router.post("/categories", response_model=schemas.CategoryRead)
def create_category(payload: schemas.CategoryCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    return services.create_category(db, payload.name, payload.description)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        services.delete_category(db, category_id)
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/products", response_model=list[schemas.ProductRead])
def read_products(category: str | None = None, search: str | None = None, featured: bool | None = None, sortBy: str | None = None, db: Session = Depends(get_db)):
    return services.get_products(db, category, search, featured, sortBy)


@router.get("/products/{product_id}", response_model=schemas.ProductRead)
def read_product(product_id: str, db: Session = Depends(get_db)):
    try:
        return services.get_product(db, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/products/{product_id}/specifications")
def read_product_specifications(product_id: str, db: Session = Depends(get_db)):
    try:
        return services.get_grouped_product_specifications(db, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/products/{product_id}/specifications", response_model=schemas.ProductSpecificationRead)
def create_product_specification(product_id: str, payload: schemas.ProductSpecificationCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        return services.create_product_specification(db, product_id, payload.dict())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.put("/products/{product_id}/specifications")
def replace_product_specifications(product_id: str, payload: schemas.ProductSpecificationBulkSave, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        specs = services.replace_product_specifications(db, product_id, [item.dict() for item in payload.specifications])
        return services.group_specifications(specs)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.put("/specifications/{specification_id}", response_model=schemas.ProductSpecificationRead)
def edit_product_specification(specification_id: str, payload: schemas.ProductSpecificationUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        return services.update_product_specification(db, specification_id, payload.dict(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/specifications/{specification_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_product_specification(specification_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        services.delete_product_specification(db, specification_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/spec-templates/{product_type}", response_model=list[schemas.SpecTemplateRead])
def read_spec_templates(product_type: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    return services.get_spec_templates(db, product_type)


@router.get("/products/{product_id}/reviews", response_model=list[schemas.ReviewRead])
def read_product_reviews(product_id: str, db: Session = Depends(get_db)):
    return services.get_product_reviews(db, product_id)


@router.post("/products/{product_id}/reviews", response_model=schemas.ReviewRead)
def create_product_review(product_id: str, payload: schemas.ReviewCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return services.create_review(db, current_user.id, product_id, payload.rating, payload.comment)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/products", response_model=schemas.ProductRead)
def create_product(payload: schemas.ProductCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    return services.create_product(db, payload.dict())


@router.put("/products/{product_id}", response_model=schemas.ProductRead)
def edit_product(product_id: str, payload: schemas.ProductUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        return services.update_product(db, product_id, payload.dict(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_product(product_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        services.delete_product(db, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/cart", response_model=schemas.CartRead)
def read_cart(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = services.get_or_create_cart(db, current_user.id)
    items = services.get_cart_items(db, current_user.id)
    cart.items = items
    return cart


@router.post("/cart/items", response_model=schemas.CartItemRead)
def add_cart_item(payload: schemas.CartItemCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return services.add_to_cart(db, current_user.id, payload.product_id, payload.quantity)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.patch("/cart/items/{item_id}", response_model=schemas.CartItemRead)
def modify_cart_item(item_id: str, payload: schemas.CartItemUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return services.update_cart_item(db, item_id, payload.quantity)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/cart/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(item_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        services.remove_cart_item(db, item_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/cart/clear", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    services.clear_cart(db, current_user.id)


@router.post("/orders", response_model=schemas.OrderRead)
def create_order(payload: schemas.OrderCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return services.create_order(
            db,
            current_user.id,
            [item.dict() for item in payload.items],
            payload.shipping_address,
            payload.payment_method,
            payload.address_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/orders", response_model=list[schemas.OrderRead])
def read_orders(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.get_user_orders(db, current_user.id)


@router.get("/orders/{order_id}", response_model=schemas.OrderRead)
def read_order(order_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return services.get_order(db, order_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/admin/orders", response_model=list[schemas.OrderRead])
def read_all_orders(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    return services.get_all_orders(db)


@router.put("/orders/{order_id}/status", response_model=schemas.OrderRead)
def set_order_status(order_id: str, payload: schemas.OrderStatusUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        return services.update_order_status_with_history(db, order_id, payload.status, payload.note, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/orders/{order_id}/tracking", response_model=schemas.OrderTracking)
def get_order_tracking(order_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        order = services.get_order(db, order_id)
        if order.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return schemas.OrderTracking(
            order_id=order.id,
            status=order.status,
            tracking_code=order.tracking_code,
            shipping_provider=order.shipping_provider,
            estimated_delivery=order.estimated_delivery,
            delivered_at=order.delivered_at,
            cancelled_at=order.cancelled_at,
            cancel_reason=order.cancel_reason
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/orders/{order_id}/timeline", response_model=schemas.OrderTimeline)
def get_order_timeline(order_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        order = services.get_order(db, order_id)
        if order.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        history = services.get_order_tracking_timeline(db, order_id)
        return schemas.OrderTimeline(history=history)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/admin/orders/{order_id}/simulate-next", response_model=schemas.OrderRead)
def simulate_next_order_status(order_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        return services.simulate_next_order_status(db, order_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/admin/stats", response_model=schemas.AdminStats)
def admin_stats(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    return services.get_admin_stats(db)


@router.get("/admin/stats", response_model=schemas.AdminStats)
def admin_stats(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    return services.get_admin_stats(db)

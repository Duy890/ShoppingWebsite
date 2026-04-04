from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import models, schemas, services
from .core.database import get_db
from .core.security import create_access_token, decode_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    user = services.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


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
        user = services.update_profile(db, current_user, payload.full_name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return user


@router.get("/categories", response_model=list[schemas.CategoryRead])
def read_categories(db: Session = Depends(get_db)):
    return services.get_categories(db)


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
        return services.create_order(db, current_user.id, [item.dict() for item in payload.items], payload.shipping_address, payload.payment_method)
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
        return services.update_order_status(db, order_id, payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/admin/stats", response_model=schemas.AdminStats)
def admin_stats(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    return services.get_admin_stats(db)

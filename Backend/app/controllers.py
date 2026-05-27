from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import chat_service, models, repositories, schemas, services
from .core.config import get_settings
from .core.database import get_db
from .core.rate_limit import limiter
from .core.security import create_access_token, decode_access_token, verify_password, hash_password

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_optional_user(
    token: str = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db),
) -> models.User | None:
    try:
        return get_current_user(token, db)
    except Exception:
        return None

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
MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

def build_image_url(filename: str, request: Request) -> str:
    base_url = str(request.base_url).rstrip('/')
    return f"{base_url}/uploads/images/{filename}"


def get_safe_image_extension(file: UploadFile) -> str:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File type not allowed")
    return extension


@router.post("/upload-image")
def upload_image(request: Request, file: UploadFile = File(...), current_user: models.User = Depends(get_current_user)):
    require_admin(current_user)
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file")

    extension = get_safe_image_extension(file)
    filename = f"{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / filename
    file_bytes = file.file.read()
    if len(file_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum size is 5MB.",
        )

    try:
        with file_path.open("wb") as buffer:
            buffer.write(file_bytes)
    except OSError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to save uploaded image") from exc

    return {"image_url": build_image_url(filename, request)}


@router.post("/upload-avatar")
def upload_avatar(request: Request, file: UploadFile = File(...), current_user: models.User = Depends(get_current_user)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file")

    extension = get_safe_image_extension(file)
    filename = f"avatar_{current_user.id}_{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / filename
    file_bytes = file.file.read()
    if len(file_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum size is 5MB.",
        )

    try:
        with file_path.open("wb") as buffer:
            buffer.write(file_bytes)
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
@limiter.limit("5/minute")
def login(payload: schemas.UserCreate, request: Request, db: Session = Depends(get_db)):
    try:
        user = services.authenticate_user(db, payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    access_token = services.create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.get("/auth/me", response_model=schemas.UserResponse)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.post("/auth/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(payload: schemas.ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)):
    """
    Send a real password reset email to the user.
    Always returns 200 to avoid user enumeration.
    """
    try:
        await services.create_reset_token_and_send_email(db, payload.email)
    except ValueError:
        pass  # Don't reveal whether the email exists
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")
    return {"message": "If this email is registered, a reset link has been sent."}


@router.post("/auth/reset-password")
def reset_password(payload: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        services.reset_password(db, payload.token, payload.new_password)
        return {"message": "Password reset successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/auth/request-email-change")
async def request_email_change(
    payload: schemas.EmailChangeRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a verification link to the new email address."""
    try:
        await services.create_email_change_token_and_send(db, current_user, payload.new_email)
        return {"message": "Verification email sent to the new address."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")


@router.get("/auth/verify-email-change")
def verify_email_change(token: str, db: Session = Depends(get_db)):
    """
    Called when user clicks the link in their email.
    Applies the email change and redirects to the profile page.
    """
    try:
        services.confirm_email_change(db, token)
        return RedirectResponse(url=f"{get_settings().FRONTEND_URL}/profile?email_changed=1")
    except ValueError:
        return RedirectResponse(url=f"{get_settings().FRONTEND_URL}/profile?email_error=1")


@router.post("/auth/change-password")
def change_password(
    payload: schemas.ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


@router.post("/payment/momo/create", response_model=schemas.MoMoPaymentResponse)
def create_momo_payment(
    payload: schemas.MoMoPaymentRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        result = services.create_momo_payment(
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

    if not services.verify_momo_ipn_signature(payload_dict):
        raise HTTPException(status_code=400, detail="Invalid signature")

    order_id = payload.orderId

    try:
        if payload.resultCode == 0:
            services.update_order_status_with_history(
                db, order_id, "confirmed", "MoMo payment successful", None
            )
        else:
            services.update_order_status_with_history(
                db, order_id, "payment_failed", f"MoMo: {payload.message}", None
            )
    except Exception as e:
        print(f"IPN processing error: {e}")

    return {"status": "ok"}


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
    try:
        return services.create_category(db, payload.name, payload.description, payload.parent_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        services.delete_category(db, category_id)
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/products")
def read_products(
    category: str | None = None,
    search: str | None = None,
    featured: bool | None = None,
    sortBy: str | None = None,
    product_type: str | None = None,
    brand: str | None = None,
    page: int = 1,
    limit: int = 12,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_optional_user),
):
    page = max(1, page)
    limit = min(max(1, limit), 100)
    result = services.get_products(db, category, search, featured, sortBy, product_type, brand, page, limit)
    if search and search.strip():
        user_id = current_user.id if current_user else None
        products_list = result.get("items", [])
        repositories.log_search(db, search, user_id, len(products_list))
    return result


@router.get("/products/{product_id}", response_model=schemas.ProductRead)
def read_product(product_id: str, db: Session = Depends(get_db)):
    try:
        product = services.get_product(db, product_id)
        repositories.increment_view_count(db, product_id)
        return product
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


@router.get("/products/{product_id}/images", response_model=list[schemas.ProductImageRead])
def get_product_images(product_id: str, db: Session = Depends(get_db)):
    return repositories.get_product_images(db, product_id)


@router.put("/admin/products/{product_id}/images", response_model=list[schemas.ProductImageRead])
def update_product_images(
    product_id: str,
    images: list[schemas.ProductImageCreate],
    db: Session = Depends(get_db),
):
    product = repositories.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    repositories.replace_product_images(db, product_id, [img.model_dump() for img in images])

    primary = next((img for img in images if img.is_primary), images[0] if images else None)
    if primary:
        product.image_url = primary.url
    db.commit()

    return repositories.get_product_images(db, product_id)


@router.get("/products/{product_id}/reviews", response_model=list[schemas.ReviewRead])
def read_product_reviews(product_id: str, db: Session = Depends(get_db)):
    return services.get_product_reviews(db, product_id)


@router.post("/products/{product_id}/reviews", response_model=schemas.ReviewRead)
def create_product_review(product_id: str, payload: schemas.ReviewCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return services.create_review(db, current_user.id, product_id, payload.rating, payload.comment)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/wishlist", response_model=schemas.WishlistRead)
def read_wishlist(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = services.get_wishlist(db, current_user.id)
    return {"items": items}


@router.get("/wishlist/ids", response_model=list[str])
def read_wishlist_ids(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.get_wishlist_product_ids(db, current_user.id)


@router.post("/wishlist/{product_id}", status_code=status.HTTP_201_CREATED)
def add_wishlist(product_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return services.add_to_wishlist(db, current_user.id, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/wishlist/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_wishlist(product_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        services.remove_from_wishlist(db, current_user.id, product_id)
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


@router.get("/products/{product_id}/variants", response_model=list[schemas.ProductVariantRead])
def get_product_variants(product_id: str, db: Session = Depends(get_db)):
    try:
        return services.get_product_variants(db, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/admin/products/{product_id}/variants", response_model=schemas.ProductVariantRead)
def create_product_variant(product_id: str, payload: schemas.ProductVariantCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        return services.create_product_variant(db, product_id, payload.dict())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.put("/admin/variants/{variant_id}", response_model=schemas.ProductVariantRead)
def update_product_variant(variant_id: str, payload: schemas.ProductVariantUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        return services.update_product_variant(db, variant_id, payload.dict(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/admin/variants/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_variant(variant_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    try:
        services.delete_product_variant(db, variant_id)
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
        return services.add_to_cart(db, current_user.id, payload.product_id, payload.quantity, payload.variant_id)
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
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"ORDER PAYLOAD RECEIVED: {payload.dict()}")
    try:
        return services.create_order(
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/orders", response_model=list[schemas.OrderRead])
def read_orders(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.get_user_orders(db, current_user.id)


@router.get("/orders/{order_id}", response_model=schemas.OrderRead)
def read_order(order_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        order = services.get_order(db, order_id)
        if order.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return order
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
            cancel_reason=order.cancel_reason,
            shipping_method=order.shipping_method,
            shipping_fee=order.shipping_fee,
            estimated_delivery_days=order.estimated_delivery_days,
            order_note=order.order_note,
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


@router.get("/admin/revenue/monthly")
def revenue_monthly(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    return services.get_revenue_by_month(db)


@router.get("/admin/revenue/yearly")
def revenue_yearly(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin(current_user)
    return services.get_revenue_by_year(db)


@router.post("/admin/generate-description", response_model=schemas.GenerateDescriptionResponse)
async def generate_product_description(
    request: schemas.GenerateDescriptionRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dùng OpenRouter để tạo mô tả sản phẩm tự động từ dữ liệu form."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    from .chatbot.openrouter_formatter import openrouter_formatter
    import json

    if not openrouter_formatter.enabled:
        raise HTTPException(
            status_code=503,
            detail="AI service not configured. Set OPENROUTER_API_KEY in .env"
        )

    product_data = request.product_data

    system_prompt = """You are a professional Vietnamese e-commerce copywriter specializing in electronics, gaming laptops, PCs, smartphones, and technology products.

STRICT RULES:
- ONLY use the provided product information.
- NEVER invent specifications, benchmarks, features, ports, materials, technologies, or performance claims.
- NEVER generate fake FPS, benchmark scores, battery life, or unsupported capabilities.
- If information is missing, omit it naturally instead of guessing.
- Keep technical accuracy and consistency.
- Use natural, fluent, professional Vietnamese.
- Optimize writing for SEO and customer readability.
- Focus on real customer benefits instead of exaggerated marketing language.

TASK:
Generate a complete Vietnamese e-commerce product description based ONLY on the provided structured product data.
The output must include:
1. Short product introduction (1-2 sentences, highlight the most important feature)
2. Key highlights in bullet points (4-6 bullets, each 10-20 words, factual only)
3. Detailed product description (3-5 paragraphs, professional, no repetition)
4. Gaming/performance summary if product_type is laptop or phone (empty string if not applicable)
5. SEO meta description under 160 characters

WRITING STYLE:
- Professional, Modern, Premium, Technology-focused
- Clear and persuasive, Human-like writing
- Vietnamese language throughout

OUTPUT FORMAT:
Return ONLY valid JSON, no markdown fences, no explanation:
{
  "short_description": "",
  "key_highlights": [],
  "full_description": "",
  "performance_summary": "",
  "seo_description": ""
}"""

    user_prompt = f"PRODUCT DATA:\n{json.dumps(product_data, ensure_ascii=False, indent=2)}"

    try:
        completion = openrouter_formatter.client.chat.completions.create(
            model=openrouter_formatter.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=2048,
            extra_headers={
                "HTTP-Referer": "https://techzone.vn",
                "X-Title": "TechZone Admin",
            },
            timeout=45,
        )
        raw = completion.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        if raw.endswith("```"):
            raw = raw[:-3].strip()

        result = json.loads(raw)
        return schemas.GenerateDescriptionResponse(**result)

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"AI returned invalid JSON: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


# --- Recommendations ---

@router.get("/recommendations", response_model=schemas.RecommendationResponse)
def get_recommendations(
    limit: int = 8,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_optional_user),
):
    user_id = current_user.id if current_user else None
    items = services.get_recommendations(db, user_id=user_id, limit=limit)
    strategy = "personalized" if user_id else "popular"
    return {"items": items, "strategy": strategy}


@router.get("/products/{product_id}/similar", response_model=schemas.RecommendationResponse)
def get_similar_products(
    product_id: str,
    limit: int = 6,
    db: Session = Depends(get_db),
):
    items = services.get_similar_products(db, product_id=product_id, limit=limit)
    return {"items": items, "strategy": "similar"}


@router.get("/cart/recommendations", response_model=schemas.RecommendationResponse)
def get_cart_recommendations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    items = services.get_cart_recommendations(db, user_id=current_user.id, limit=4)
    return {"items": items, "strategy": "co_purchase"}


# --- Admin Analytics ---

@router.get("/admin/analytics/top-searches")
def top_searches(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(current_user)
    return repositories.get_top_searches(db, limit=20)


@router.get("/admin/analytics/top-viewed")
def top_viewed_products(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(current_user)
    products = (
        db.query(models.Product)
        .filter(models.Product.status == "active")
        .order_by(models.Product.view_count.desc())
        .limit(10)
        .all()
    )
    return [
        {"id": p.id, "name": p.name, "view_count": p.view_count,
         "rating": p.rating, "price": p.price}
        for p in products
    ]


@router.get("/admin/analytics/cart-abandonment")
def cart_abandonment(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(current_user)
    from sqlalchemy import func
    rows = (
        db.query(
            models.CartItem.product_id,
            func.count(models.CartItem.id).label("cart_count"),
        )
        .group_by(models.CartItem.product_id)
        .order_by(func.count(models.CartItem.id).desc())
        .limit(10)
        .all()
    )
    result = []
    for r in rows:
        p = db.query(models.Product).filter(
            models.Product.id == r.product_id
        ).first()
        order_count = (
            db.query(func.count(models.OrderItem.id))
            .filter(models.OrderItem.product_id == r.product_id)
            .scalar() or 0
        )
        if p:
            result.append({
                "id": p.id,
                "name": p.name,
                "cart_count": r.cart_count,
                "order_count": order_count,
                "abandonment_rate": round(
                    (r.cart_count - order_count) / r.cart_count * 100, 1
                ) if r.cart_count > 0 else 0,
            })
    return result

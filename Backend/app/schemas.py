from datetime import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

class EmailChangeRequest(BaseModel):
    new_email: EmailStr

# ── Refresh Token ──

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

# ── MFA ──

class MFAEnableRequest(BaseModel):
    password: str

class MFAVerifyRequest(BaseModel):
    code: str

    @field_validator("code")
    @classmethod
    def strip_and_validate_code(cls, v: str) -> str:
        cleaned = v.strip().replace(" ", "")
        if not cleaned.isdigit():
            raise ValueError("Code must contain digits only")
        if len(cleaned) != 6:
            raise ValueError("Code must be exactly 6 digits")
        return cleaned

class MFADisableRequest(BaseModel):
    password: str
    code: str

    @field_validator("code")
    @classmethod
    def strip_and_validate_code(cls, v: str) -> str:
        cleaned = v.strip().replace(" ", "")
        if not cleaned.isdigit():
            raise ValueError("Code must contain digits only")
        if len(cleaned) != 6:
            raise ValueError("Code must be exactly 6 digits")
        return cleaned

class MFASetupResponse(BaseModel):
    secret: str
    qr_code_url: str

class MFAStatusResponse(BaseModel):
    mfa_enabled: bool


class MFAChallengeVerifyRequest(BaseModel):
    challenge_token: str
    code: str = Field(..., min_length=6, max_length=6)


class LoginResponse(BaseModel):
    access_token: str = ""
    refresh_token: str = ""
    token_type: str = "bearer"
    user: Optional["UserResponse"] = None
    mfa_required: bool = False
    mfa_challenge_token: str = ""

# ── Audit Log ──

class AuditLogRead(BaseModel):
    id: str
    user_id: str
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[Any] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

# ── Login History ──

class LoginHistoryRead(BaseModel):
    id: str
    user_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool
    fail_reason: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

class MoMoPaymentRequest(BaseModel):
    order_id: str
    amount: int
    order_info: str

class MoMoPaymentResponse(BaseModel):
    pay_url: str
    result_code: int
    message: str

class MoMoIPNPayload(BaseModel):
    partnerCode: str
    orderId: str
    requestId: str
    amount: int
    orderInfo: str
    orderType: str
    transId: int
    resultCode: int
    message: str
    payType: str
    responseTime: int
    extraData: str
    signature: str

class Token(BaseModel):
    access_token: str
    refresh_token: str = ""
    token_type: str


class TokenWithUser(Token):
    user: "UserResponse"


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class UserResponse(UserBase):
    id: str
    is_admin: bool
    role: str
    avatar_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    parent_id: Optional[str] = None


class CategoryRead(CategoryBase):
    id: str
    slug: Optional[str] = None
    level: Optional[int] = 0
    parent_id: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CategoryTreeRead(CategoryBase):
    id: str
    slug: Optional[str] = None
    level: Optional[int] = 0
    parent_id: Optional[str] = None
    children: list["CategoryTreeRead"] = []

    model_config = {"from_attributes": True}


class SearchSuggestionRead(BaseModel):
    id: str
    type: Literal["product", "category"]
    label: str
    subtitle: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    message: str
    history: List[dict[str, Any]] = Field(default_factory=list)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    intent: str
    entities: dict[str, Any] = {}
    message: str
    products: List[dict[str, Any]] = []
    comparison: dict[str, Any] = {}
    gaming_result: dict[str, Any] = {}
    recommendations: List[dict[str, Any]] = []
    actions: List[dict[str, Any]] = []


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    category_id: Optional[str] = None
    image_url: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    product_type: Optional[str] = None
    rating: float = 0.0
    review_count: int = 0
    featured: bool = False
    status: str = "active"
    view_count: int = 0
    embedding: Optional[List[float]] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category_id: Optional[str] = None
    image_url: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    product_type: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    featured: Optional[bool] = None
    status: Optional[str] = None
    view_count: Optional[int] = None
    embedding: Optional[List[float]] = None


class ProductImageRead(BaseModel):
    id: str
    product_id: str
    url: str
    alt_text: Optional[str] = ""
    is_primary: bool = False
    sort_order: int = 0
    model_config = {"from_attributes": True}


class ProductImageCreate(BaseModel):
    url: str
    alt_text: Optional[str] = ""
    is_primary: bool = False
    sort_order: int = 0


class ProductRead(ProductBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[CategoryRead] = None
    reviews: List["ReviewRead"] = []
    variants: List["ProductVariantRead"] = []
    specifications: List["ProductSpecificationRead"] = []
    product_images: List[ProductImageRead] = []

    model_config = {"from_attributes": True}


class WishlistItemRead(BaseModel):
    id: str
    product: ProductRead
    created_at: datetime

    model_config = {"from_attributes": True}


class WishlistRead(BaseModel):
    items: list[WishlistItemRead]


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class ReviewRead(ReviewBase):
    id: str
    user_id: str
    product_id: str
    created_at: datetime
    user: UserResponse

    model_config = {"from_attributes": True}


class ProductSpecificationBase(BaseModel):
    group_name: str
    spec_key: str
    spec_value: Optional[str] = None
    unit: Optional[str] = None
    display_order: int = 0


class ProductSpecificationCreate(ProductSpecificationBase):
    pass


class AddressBase(BaseModel):
    full_name: str
    phone: str
    street: str
    province: str
    district: str
    ward: str
    country: str = "Vietnam"
    is_default: bool = False


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    street: Optional[str] = None
    province: Optional[str] = None
    district: Optional[str] = None
    ward: Optional[str] = None
    country: Optional[str] = None
    is_default: Optional[bool] = None


class AddressRead(AddressBase):
    id: str
    user_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductSpecificationUpdate(BaseModel):
    group_name: Optional[str] = None
    spec_key: Optional[str] = None
    spec_value: Optional[str] = None
    display_order: Optional[int] = None


class ProductSpecificationRead(ProductSpecificationBase):
    id: str
    product_id: str
    unit: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductSpecificationBulkSave(BaseModel):
    specifications: List[ProductSpecificationCreate]


class SpecTemplateCreate(BaseModel):
    product_type: str
    group_name: str
    spec_key: str
    default_order: int = 0


class SpecTemplateRead(BaseModel):
    id: str
    product_type: str
    group_name: str
    spec_key: str
    default_order: int

    model_config = {"from_attributes": True}


class ProductVariantBase(BaseModel):
    color_name: Optional[str] = None
    color_code: Optional[str] = None
    # color_code supports: HEX (#1C1C1E), rgba(), transparent, gradients
    version_name: Optional[str] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    sku: Optional[str] = None
    price: float
    compare_price: Optional[float] = None
    stock: int = 0
    image_url: Optional[str] = None
    is_default: bool = False
    status: str = "active"


class ProductVariantCreate(ProductVariantBase):
    pass


class ProductVariantUpdate(BaseModel):
    color_name: Optional[str] = None
    color_code: Optional[str] = None
    version_name: Optional[str] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    compare_price: Optional[float] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    is_default: Optional[bool] = None
    status: Optional[str] = None


class ProductVariantRead(ProductVariantBase):
    id: str
    product_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CartItemCreate(BaseModel):
    product_id: str
    variant_id: Optional[str] = None
    quantity: int = Field(..., gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)


class CartItemRead(BaseModel):
    id: str
    quantity: int
    product: ProductRead
    variant: Optional[ProductVariantRead] = None

    model_config = {"from_attributes": True}


class CartRead(BaseModel):
    id: str
    user_id: str
    items: List[CartItemRead] = []

    model_config = {"from_attributes": True}


class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)
    price: float


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    address_id: Optional[str] = None
    shipping_address: Optional[str] = None
    payment_method: Optional[str] = None
    shipping_method: Optional[str] = None
    shipping_fee: float = 0
    order_note: Optional[str] = None


class OrderItemRead(BaseModel):
    id: str
    quantity: int
    price: float
    product: ProductRead

    model_config = {"from_attributes": True}


class UserBasicInfo(BaseModel):
    id: str
    full_name: Optional[str] = None
    email: str

    model_config = {"from_attributes": True}


class OrderRead(BaseModel):
    id: str
    user_id: str
    user: Optional[UserBasicInfo] = None
    total_amount: float
    status: str
    shipping_address: Optional[str] = None
    payment_method: Optional[str] = None
    address_id: Optional[str] = None
    tracking_code: Optional[str] = None
    shipping_provider: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancel_reason: Optional[str] = None
    order_note: Optional[str] = None
    shipping_method: Optional[str] = None
    shipping_fee: float = 0
    estimated_delivery_days: Optional[int] = None
    items: List[OrderItemRead] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: str
    note: Optional[str] = None


class OrderStatusHistoryRead(BaseModel):
    id: str
    old_status: Optional[str] = None
    new_status: str
    note: Optional[str] = None
    changed_by: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderTracking(BaseModel):
    order_id: str
    status: str
    tracking_code: Optional[str] = None
    shipping_provider: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancel_reason: Optional[str] = None
    shipping_method: Optional[str] = None
    shipping_fee: float = 0
    estimated_delivery_days: Optional[int] = None
    order_note: Optional[str] = None


class OrderTimeline(BaseModel):
    history: List[OrderStatusHistoryRead]


class AdminStats(BaseModel):
    total_products: int
    total_orders: int
    total_revenue: float
    total_users: int


class GenerateDescriptionRequest(BaseModel):
    product_data: dict

class GenerateDescriptionResponse(BaseModel):
    short_description: str
    key_highlights: list[str]
    full_description: str
    performance_summary: str
    seo_description: str

class RecommendationItem(BaseModel):
    id: str
    name: str
    price: float
    image_url: Optional[str] = None
    brand: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    product_type: Optional[str] = None


class RecommendationResponse(BaseModel):
    items: list[RecommendationItem]
    strategy: str


TokenWithUser.update_forward_refs()

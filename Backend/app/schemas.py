from datetime import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenWithUser(Token):
    user: "UserResponse"


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


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
    pass


class CategoryRead(CategoryBase):
    id: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CategoryTreeRead(CategoryBase):
    id: str
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
    history: List[dict[str, Any]] = []


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


class ProductRead(ProductBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[CategoryRead] = None
    reviews: List["ReviewRead"] = []

    model_config = {"from_attributes": True}


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
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductSpecificationBulkSave(BaseModel):
    specifications: List[ProductSpecificationCreate]


class SpecTemplateRead(BaseModel):
    id: str
    product_type: str
    group_name: str
    spec_key: str
    default_order: int

    model_config = {"from_attributes": True}


class CartItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)


class CartItemRead(BaseModel):
    id: str
    quantity: int
    product: ProductRead

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


class OrderItemRead(BaseModel):
    id: str
    quantity: int
    price: float
    product: ProductRead

    model_config = {"from_attributes": True}


class OrderRead(BaseModel):
    id: str
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


class OrderTimeline(BaseModel):
    history: List[OrderStatusHistoryRead]


class AdminStats(BaseModel):
    total_products: int
    total_orders: int
    total_revenue: float
    total_users: int


TokenWithUser.update_forward_refs()

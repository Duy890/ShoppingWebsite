from datetime import datetime
from typing import List, Optional

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
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: Optional[str] = None


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    category_id: Optional[str] = None
    image_url: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
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
    items: List[OrderItemRead] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: str


class AdminStats(BaseModel):
    total_products: int
    total_orders: int
    total_revenue: float
    total_users: int


TokenWithUser.update_forward_refs()

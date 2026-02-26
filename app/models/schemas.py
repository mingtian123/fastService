from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

# 响应模型
class ResponseModel(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# 用户模型
class UserBase(BaseModel):
    name: str
    email: Optional[str] = None
    metadata_json: Optional[Dict] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    metadata_json: Optional[Dict] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 订单模型
class OrderBase(BaseModel):
    order_no: str
    user_id: int
    amount: float = 0.0
    status: str = "pending"
    metadata_json: Optional[Dict] = None

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    amount: Optional[float] = None
    status: Optional[str] = None
    metadata_json: Optional[Dict] = None

class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 产品模型
class ProductBase(BaseModel):
    name: str
    price: float = 0.0
    stock: int = 0
    description: Optional[str] = None
    metadata_json: Optional[Dict] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    description: Optional[str] = None
    metadata_json: Optional[Dict] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 查询参数
class QueryParams(BaseModel):
    skip: int = 0
    limit: int = 100
    search: Optional[str] = None

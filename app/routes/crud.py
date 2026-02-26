from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional, List
from app.database import get_db, User, Order, Product
from app.models.schemas import (
    UserCreate, UserUpdate, UserResponse,
    OrderCreate, OrderUpdate, OrderResponse,
    ProductCreate, ProductUpdate, ProductResponse,
    ResponseModel
)

router = APIRouter()

# ========== 用户管理接口 ==========

@router.get("/users", response_model=ResponseModel)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表"""
    query = select(User)
    if search:
        query = query.where(or_(
            User.name.contains(search),
            User.email.contains(search)
        ))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return ResponseModel(data=[UserResponse.model_validate(u) for u in users])

@router.get("/users/{user_id}", response_model=ResponseModel)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个用户"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return ResponseModel(data=UserResponse.model_validate(user))

@router.post("/users", response_model=ResponseModel)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """创建用户"""
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return ResponseModel(data=UserResponse.model_validate(db_user))

@router.put("/users/{user_id}", response_model=ResponseModel)
async def update_user(
    user_id: int, 
    user_update: UserUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """更新用户"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    return ResponseModel(data=UserResponse.model_validate(user))

@router.delete("/users/{user_id}", response_model=ResponseModel)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """删除用户"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    await db.delete(user)
    await db.commit()
    return ResponseModel(message="删除成功")

# ========== 订单管理接口 ==========

@router.get("/orders", response_model=ResponseModel)
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取订单列表"""
    query = select(Order)
    if user_id:
        query = query.where(Order.user_id == user_id)
    if status:
        query = query.where(Order.status == status)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    orders = result.scalars().all()
    
    return ResponseModel(data=[OrderResponse.model_validate(o) for o in orders])

@router.get("/orders/{order_id}", response_model=ResponseModel)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个订单"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return ResponseModel(data=OrderResponse.model_validate(order))

@router.post("/orders", response_model=ResponseModel)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
    """创建订单"""
    db_order = Order(**order.model_dump())
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return ResponseModel(data=OrderResponse.model_validate(db_order))

@router.put("/orders/{order_id}", response_model=ResponseModel)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新订单"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    for field, value in order_update.model_dump(exclude_unset=True).items():
        setattr(order, field, value)
    
    await db.commit()
    await db.refresh(order)
    return ResponseModel(data=OrderResponse.model_validate(order))

@router.delete("/orders/{order_id}", response_model=ResponseModel)
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db)):
    """删除订单"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    await db.delete(order)
    await db.commit()
    return ResponseModel(message="删除成功")

# ========== 产品管理接口 ==========

@router.get("/products", response_model=ResponseModel)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取产品列表"""
    query = select(Product)
    if search:
        query = query.where(Product.name.contains(search))
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()
    
    return ResponseModel(data=[ProductResponse.model_validate(p) for p in products])

@router.get("/products/{product_id}", response_model=ResponseModel)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个产品"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return ResponseModel(data=ProductResponse.model_validate(product))

@router.post("/products", response_model=ResponseModel)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    """创建产品"""
    db_product = Product(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return ResponseModel(data=ProductResponse.model_validate(db_product))

@router.put("/products/{product_id}", response_model=ResponseModel)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新产品"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    for field, value in product_update.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    
    await db.commit()
    await db.refresh(product)
    return ResponseModel(data=ProductResponse.model_validate(product))

@router.delete("/products/{product_id}", response_model=ResponseModel)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """删除产品"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    await db.delete(product)
    await db.commit()
    return ResponseModel(message="删除成功")

# ========== 统计接口 ==========

@router.get("/stats", response_model=ResponseModel)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """获取统计数据"""
    # 用户数量
    user_count = await db.execute(select(func.count(User.id)))
    # 订单数量
    order_count = await db.execute(select(func.count(Order.id)))
    # 订单总金额
    order_amount = await db.execute(select(func.sum(Order.amount)))
    # 产品数量
    product_count = await db.execute(select(func.count(Product.id)))
    
    return ResponseModel(data={
        "user_count": user_count.scalar(),
        "order_count": order_count.scalar(),
        "total_order_amount": order_amount.scalar() or 0,
        "product_count": product_count.scalar()
    })

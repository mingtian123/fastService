"""
fastService - FastAPI Web Service with SQLite
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db, close_db
from app.routes import health, crud

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    yield
    # 关闭时清理资源
    await close_db()

app = FastAPI(
    title="fastService",
    description="基于FastAPI和SQLite的高性能数据服务",
    version="1.1.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router, prefix="/api/v1", tags=["健康检查"])
app.include_router(crud.router, prefix="/api/v1", tags=["数据管理"])

@app.get("/")
async def root():
    return {
        "service": "fastService",
        "version": "1.1.0",
        "database": "SQLite",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "users": "/api/v1/users",
            "orders": "/api/v1/orders",
            "products": "/api/v1/products",
            "stats": "/api/v1/stats"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

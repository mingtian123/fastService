"""
fastService - FastAPI Web Service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import query, health

app = FastAPI(
    title="fastService",
    description="高性能数据查询Web服务",
    version="1.0.0"
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
app.include_router(query.router, prefix="/api/v1", tags=["数据查询"])

@app.get("/")
async def root():
    return {
        "service": "fastService",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import APIRouter, Query
from typing import Optional, Dict, Any
from app.services.data_service import DataService

router = APIRouter()
data_service = DataService()

@router.get("/query")
async def query_data(
    source: str = Query(..., description="数据源名称"),
    table: Optional[str] = Query(None, description="表名"),
    limit: int = Query(100, ge=1, le=1000, description="返回条数")
):
    """
    通用数据查询接口
    """
    result = await data_service.query(source, table, limit)
    return {
        "code": 200,
        "data": result,
        "source": source
    }

@router.get("/query/{item_id}")
async def query_by_id(item_id: str, source: str = Query(...)):
    """
    根据ID查询单条数据
    """
    result = await data_service.get_by_id(source, item_id)
    return {
        "code": 200,
        "data": result
    }

@router.post("/query/sql")
async def query_by_sql(sql: str, params: Optional[Dict[str, Any]] = None):
    """
    SQL查询接口（需要权限控制）
    """
    result = await data_service.query_sql(sql, params)
    return {
        "code": 200,
        "data": result
    }

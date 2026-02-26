from typing import Optional, Dict, Any, List
import asyncio

class DataService:
    """数据查询服务"""
    
    def __init__(self):
        # 模拟数据源配置
        self._mock_data = {
            "users": [
                {"id": 1, "name": "张三", "email": "zhangsan@example.com"},
                {"id": 2, "name": "李四", "email": "lisi@example.com"},
                {"id": 3, "name": "王五", "email": "wangwu@example.com"},
            ],
            "orders": [
                {"id": "A001", "user_id": 1, "amount": 100.0, "status": "completed"},
                {"id": "A002", "user_id": 2, "amount": 200.0, "status": "pending"},
                {"id": "A003", "user_id": 1, "amount": 150.0, "status": "completed"},
            ],
            "products": [
                {"id": "P001", "name": "产品A", "price": 99.9, "stock": 100},
                {"id": "P002", "name": "产品B", "price": 199.9, "stock": 50},
                {"id": "P003", "name": "产品C", "price": 299.9, "stock": 200},
            ]
        }
    
    async def query(self, source: str, table: Optional[str], limit: int = 100) -> List[Dict]:
        """
        通用查询
        """
        await asyncio.sleep(0.01)  # 模拟异步IO
        
        if source in self._mock_data:
            data = self._mock_data[source]
            return data[:limit]
        
        return []
    
    async def get_by_id(self, source: str, item_id: str) -> Optional[Dict]:
        """
        根据ID查询
        """
        await asyncio.sleep(0.01)
        
        if source not in self._mock_data:
            return None
        
        for item in self._mock_data[source]:
            if str(item.get("id")) == item_id:
                return item
        
        return None
    
    async def query_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        SQL查询（示例实现）
        """
        await asyncio.sleep(0.01)
        
        # 这里应该连接真实数据库执行SQL
        # 目前返回模拟数据
        return [{"note": "SQL查询结果", "sql": sql, "params": params}]

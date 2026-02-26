from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class ResponseModel(BaseModel):
    code: int
    message: str = "success"
    data: Optional[Any] = None
    timestamp: datetime = datetime.now()

class QueryRequest(BaseModel):
    source: str
    table: Optional[str] = None
    filters: Optional[dict] = None
    limit: int = 100
    offset: int = 0

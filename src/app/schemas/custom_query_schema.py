from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class QueryCondition(BaseModel):
    table: str
    column: str
    operator: str
    value: Any

class QueryParameters(BaseModel):
    model: str
    columns: Dict[str, List[str]]  # Dictionary with {table_name: [column_names]}
    filters: Optional[List[QueryCondition]] = None  # List of filter conditions
    order_by: Optional[List[str]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    join_tables: Optional[List[str]] = None

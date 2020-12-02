from typing import Any, Dict, Optional

from pydantic import BaseModel


class JupyterBookError(BaseModel):
    summary: str
    trace: str
    failing_cell_index: int


class JupyterBookResult(BaseModel):
    document: Dict[Any, Any]
    error: Optional[JupyterBookError]

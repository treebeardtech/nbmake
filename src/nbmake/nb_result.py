from typing import Any, Dict, Optional

from pydantic import BaseModel


class NotebookError(BaseModel):
    summary: str
    trace: str
    failing_cell_index: int


class NotebookResult(BaseModel):
    document: Dict[Any, Any]
    error: Optional[NotebookError]

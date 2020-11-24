from typing import Any, Dict, Optional

from pydantic import BaseModel


class JupyterBookResult(BaseModel):
    document: Dict[Any, Any]
    failing_cell_index: Optional[int]

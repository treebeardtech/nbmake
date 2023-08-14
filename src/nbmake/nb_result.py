from dataclasses import dataclass
from typing import Optional

from nbformat import NotebookNode


@dataclass
class NotebookError:
    summary: str
    trace: str
    failing_cell_index: int


@dataclass
class NotebookResult:
    nb: NotebookNode
    error: Optional[NotebookError]

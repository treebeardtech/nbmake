from nbformat import NotebookNode
from typing import Any


def new_notebook() -> NotebookNode:
    ...


def new_code_cell(src: str) -> Any:
    ...

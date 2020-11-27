from typing import List, Any


def write(nb: NotebookNode, path: str):
    ...


class NotebookNode:
    cells: List[Any]
    ...


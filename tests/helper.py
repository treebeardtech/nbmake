from pathlib import Path
from typing import Any, Callable, Dict, List, TypeVar

import yaml
from nbformat import write
from nbformat.v4 import new_markdown_cell  # type: ignore
from nbformat.v4 import new_code_cell, new_notebook

T = TypeVar("T")


class MockValidator(object):
    def __init__(self, validator: Callable[[T], bool]):
        self.validator = validator

    def __eq__(self, other: T):
        return bool(self.validator(other))


passing_nb = [
    # In [1]:
    "a = 5",
    # In [2]:
    "for i in range(10):\n" + "    print(i)",
    # In [3]:
    "print(a)",
    # In [4]:
    "a",
    # In [5]:
    "import os\n" + "os.curdir",
]

failing_nb = [
    # In [1]:
    "raise Exception('something went wrong')"
]


# def build_nb(sources: List[str]) -> NotebookNode:

#     return nb


def write_nb(sources: List[str], path: Path, title: str = "default-title"):
    nb = new_notebook()
    nb.cells.append(new_markdown_cell(f"# {title}"))  # type: ignore
    for src in sources:
        nb.cells.append(new_code_cell(src))
    write(nb, str(path))


def write_config(conf: Dict[Any, Any], filename: Path = Path("_config.yml")) -> Path:
    with open(filename, "w") as c:
        yaml.dump(conf, c)
    return filename

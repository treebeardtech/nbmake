import os
from pathlib import Path
from typing import Any, Dict, List

from nbformat import write
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook
from pytest import Pytester, fixture

HOME: str = os.environ["HOME"]

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


def write_nb(
    sources: List[str],
    path: Path,
    title: str = "default-title",
    metadata: Dict[str, Any] = {},
):
    nb = new_notebook()
    nb.metadata = metadata
    nb.cells.append(new_markdown_cell(f"# {title}"))
    for src in sources:
        nb.cells.append(new_code_cell(src))
    write(nb, str(path))


@fixture
def testdir2(pytester: Pytester):
    os.environ[
        "HOME"
    ] = HOME  # ensures jupyter client can start the ipykernel subprocess without module location issues # noqa

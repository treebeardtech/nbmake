import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml
from nbformat import write
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook
from pytest import Pytester, fixture

HOME: str = os.environ["HOME"]

passing_nb = [
    # In [1]:
    ("co", "a = 5"),
    # In [2]:
    ("co", "for i in range(10):\n" + "    print(i)"),
    # In [3]:
    ("co", "print(a)"),
    # In [4]:
    ("co", "a"),
    # In [5]:
    ("co", "import os\n" + "os.curdir"),
]

failing_nb = [
    # In [1]:
    ("co", "raise Exception('something went wrong')")
]


bycell_nb = [
    # In [1]:
    ("md", "# The initialization cell above that will be run for all tests below."),
    # In [2]:
    ("co", "import hashlib"),
    # In [3]:
    ("md", "# first test"),
    # In [4]:
    ("co", "hashlib.blake2b(digest_size=32, person=b'Joe'"),
    # In [5]:
    ("md", "# a heading, not a test"),
    # In [6]:
    ("md", "## second test"),
    # In [7]:
    ("md", ("This is the second test being run. The second initialization block is "
            "run before it and so hashlib is found.")),
    # In [8]:
    ("co", "hashlib.blake2b(digest_size=32, person=b'Smith'"),
]



def write_nb(
    sources: List[Tuple[str, str]],
    path: Path,
    title: str = "default-title",
    metadata: Dict[str, Any] = {},
):
    nb = new_notebook()
    nb.metadata = metadata
    nb.cells.append(new_markdown_cell(f"# {title}"))
    for celltype, src in sources:
        new_cell = new_code_cell if celltype == "md" else new_markdown_cell
        nb.cells.append(new_cell(src))
    write(nb, str(path))


def write_config(conf: Dict[Any, Any], filename: Path = Path("_config.yml")) -> Path:
    Path(filename).write_text(yaml.dump(conf))
    return filename


@fixture
def testdir2(pytester: Pytester):
    os.environ[
        "HOME"
    ] = HOME  # ensures jupyter client can start the ipykernel subprocess without module location issues

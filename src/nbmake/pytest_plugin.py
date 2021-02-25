from pathlib import Path
from typing import Any, Optional

from .pytest_items import NotebookFile


def pytest_addoption(parser: Any):
    group = parser.getgroup("nbmake", "notebook testing")
    group.addoption(
        "--nbmake", action="store_true", help="Test notebooks", default=False
    )
    group.addoption(
        "--overwrite",
        action="store_true",
        help="Overwrite the source ipynbs",
        default=False,
    )


def pytest_collect_file(path: str, parent: Any) -> Optional[Any]:
    opt = parent.config.option
    p = Path(path)
    if opt.nbmake and p.match("*ipynb") and "_build" not in p.parts:
        return NotebookFile.from_parent(parent, fspath=path)

    return None

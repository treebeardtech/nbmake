import asyncio
import sys
from pathlib import Path
from typing import Any, Optional

from .pytest_items import NotebookFile


def pytest_addoption(parser: Any):
    # See https://bugs.python.org/issue37373 and
    # https://github.com/nteract/papermill/issues/515
    if (
        sys.version_info[0] == 3
        and sys.version_info[1] >= 8
        and sys.platform.startswith("win")
    ):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

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
    group.addoption(
        "--nbmake-timeout",
        action="store",
        help="Sets the default timeout for a notebook (seconds)",
        default=300,
        type=int,
    )


def pytest_collect_file(path: str, parent: Any) -> Optional[Any]:
    opt = parent.config.option
    p = Path(path)
    if opt.nbmake and p.match("*ipynb") and "_build" not in p.parts:
        return NotebookFile.from_parent(parent, fspath=path)

    return None

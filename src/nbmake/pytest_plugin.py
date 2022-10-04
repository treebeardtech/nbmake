import asyncio
import sys
from pathlib import Path
from typing import Any, Optional

import pkg_resources

from .pytest_items import NotebookFile
from .pytest_items import NotebookFileByCell


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
        help="Sets the default cell timeout (seconds)",
        default=300,
        type=int,
    )
    group.addoption(
        "--nbmake-kernel",
        action="store",
        help="Overrides the kernel used for all notebooks",
        type=str,
    )
    group.addoption(
        "--nbmake-by-cell",
        action="store_true",
        help="Break out each notebook section into its own individual unit tests",
    )


def pytest_collect_file(path: str, parent: Any) -> Optional[Any]:
    opt = parent.config.option
    p = Path(path)
    if (
        opt.nbmake
        and (p.match("*ipynb") or p.match("*.py"))
        and "_build" not in p.parts
    ):
        cls = NotebookFileByCell if opt.nbmake_by_cell else NotebookFile
        ver: int = int(pkg_resources.get_distribution("pytest").version[0])
        return (
            cls.from_parent(parent, fspath=path)
            if ver < 7
            else cls.from_parent(parent, path=p)
        )

    return None

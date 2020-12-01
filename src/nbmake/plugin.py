import os
import traceback
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Generator, Optional

import pytest  # type: ignore
from _pytest.config import Config  # type: ignore
from _pytest.config.argparsing import Parser  # type: ignore
from jupyter_cache import get_cache  # type: ignore
from pygments import highlight  # type: ignore
from pygments.formatters import TerminalTrueColorFormatter  # type: ignore
from pygments.lexers import Python3TracebackLexer  # type: ignore

from .jupyter_book_result import JupyterBookResult
from .jupyter_book_run import JupyterBookRun


def pytest_addoption(parser: Any):
    group = parser.getgroup("nbmake", "notebook testing")
    group.addoption("--nbmake", action="store_true", help="Test notebooks")
    group.addoption(
        "--jbconfig",
        action="store",
        help="Your jupyter-book config file",
    )
    # "--warningiserror",
    # "--nitpick",


def pytest_configure(config: Config):  # type: ignore
    # hack to prevent race condition initialising cache
    # TODO infer cache loc, move this to a more appropriate hook
    if config.jbconfig:
        get_cache("_build/.jupyter_cache").list_cache_records()
        get_cache("docs/_build/.jupyter_cache").list_cache_records()


def pytest_collect_file(path: str, parent: Any) -> Optional[Any]:  # type: ignore
    """
    Collect IPython notebooks using the specified pytest hook
    """
    opt = parent.config.option
    if opt.nbmake and fnmatch(path, "*.ipynb"):
        return NotebookFile.from_parent(parent, fspath=path)  # type: ignore

    return None


class NotebookFile(pytest.File):  # type: ignore
    def collect(self) -> Generator[Any, Any, Any]:
        yield NotebookItem.from_parent(self, filename=self.name)


class NotebookFailedException(Exception):
    pass


class NotebookItem(pytest.Item):  # type: ignore
    def __init__(self, parent: Any, filename: str):
        super().__init__("", parent)
        self.filename = filename
        # self.config = parent.config.option.jbconfig

    def runtest(self):
        config: Optional[str] = self.parent.config.option.jbconfig

        run = JupyterBookRun(Path(self.filename), Path(config) if config else None)
        res: JupyterBookResult = run.execute()

        if res.failing_cell_index != None:
            raise NotebookFailedException(res)

    def repr_failure(self, excinfo: Any) -> str:
        if type(excinfo.value) != NotebookFailedException:
            tb = "".join(traceback.format_tb(excinfo.tb))
            err_str = f"NBMAKE INTERNAL ERROR:\n{excinfo.value}\n{tb}"
            if os.name == "nt":
                return err_str

            return highlight(  # type: ignore
                err_str, Python3TracebackLexer(), TerminalTrueColorFormatter()
            )

        res: JupyterBookResult = excinfo.value.args[0]
        return f"🍋 repr_failure\n {res.document['cells'][res.failing_cell_index]}"

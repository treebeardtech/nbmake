import os
import traceback
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Generator, Optional

import pytest  # type: ignore
from _pytest._code.code import TerminalRepr  # type: ignore
from _pytest.config import Config  # type: ignore
from _pytest.config.argparsing import Parser  # type: ignore
from jupyter_cache import get_cache  # type: ignore
from pygments import highlight  # type: ignore
from pygments.formatters import TerminalTrueColorFormatter  # type: ignore
from pygments.lexers import Python3TracebackLexer  # type: ignore

from .jupyter_book_result import JupyterBookError, JupyterBookResult
from .jupyter_book_run import JupyterBookRun
from .nbmake_failure_repr import NbMakeFailureRepr


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
    # TODO infer cache loc
    if hasattr(config.option, "jbconfig") and config.option.jbconfig:  # type: ignore
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


# def pytest_terminal_summary(terminalreporter, exitstatus, config):
#     reports = terminalreporter.getreports('')
#     content = os.linesep.join(text for report in reports for secname, text in report.sections)
#     if content:
#         terminalreporter.ensure_newline()
#         terminalreporter.section('My custom section', sep='-', blue=True, bold=True)
#         terminalreporter.line(content)


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
        if res.error != None:
            raise NotebookFailedException(res)

    def repr_failure(self, excinfo: Any) -> TerminalRepr:  # type: ignore
        def create_internal_err() -> str:
            tb = "".join(traceback.format_tb(excinfo.tb))
            err = f"{excinfo.value}\n{tb}"
            err_str: str = (
                err
                if os.name == "nt"
                else highlight(  # type: ignore
                    err, Python3TracebackLexer(), TerminalTrueColorFormatter()
                )
            )

            return NbMakeFailureRepr(
                "NBMAKE INTERNAL ERROR\n" + err_str,
                "NBMAKE INTERNAL ERROR",
            )

        if type(excinfo.value) != NotebookFailedException:
            return create_internal_err()

        res: JupyterBookResult = excinfo.value.args[0]
        if isinstance(res.error, type(None)):
            return create_internal_err()

        error: JupyterBookError = res.error  # type:ignore
        return NbMakeFailureRepr(error.trace, error.summary)

    def reportinfo(self):  # type:ignore
        return self.fspath, 0, self.filename  # type:ignore

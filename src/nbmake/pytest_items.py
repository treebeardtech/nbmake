import os
import traceback
from pathlib import Path
from typing import Any, Generator, Optional

import pytest  # type: ignore
from _pytest._code.code import (  # type: ignore
    ReprFileLocation,
    TerminalRepr,
    TerminalWriter,
)
from jupyter_cache import get_cache  # type: ignore
from pygments import highlight  # type: ignore
from pygments.formatters import TerminalTrueColorFormatter  # type: ignore
from pygments.lexers import Python3TracebackLexer  # type: ignore

from .jupyter_book_result import JupyterBookError, JupyterBookResult
from .jupyter_book_run import JupyterBookRun


class NbMakeFailureRepr(TerminalRepr):  # type: ignore
    def __init__(self, term: str, summary: str):
        self.term = term
        self.reprcrash = ReprFileLocation("", "", summary)  # type: ignore

    def toterminal(self, tw: TerminalWriter) -> None:  # type: ignore
        tw.write(f"{self.term}\n")


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
        path_output: Path = Path(self.parent.config.option.path_output)  # type: ignore

        run = JupyterBookRun(
            Path(self.filename),
            path_output=path_output / Path(os.path.splitext(self.filename)[0]),
            config_filename=Path(config) if config else None,
            cache=get_cache(path_output / "cache"),  # type: ignore
        )
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

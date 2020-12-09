import os
import traceback
from pathlib import Path
from typing import Any, Generator, Optional

import pytest
from _pytest._code.code import ReprFileLocation, TerminalRepr, TerminalWriter
from jupyter_cache import get_cache
from pygments import highlight
from pygments.formatters import TerminalTrueColorFormatter
from pygments.lexers import Python3TracebackLexer

from .nb_result import NotebookError, NotebookResult
from .nb_run import NotebookRun


class NbMakeFailureRepr(TerminalRepr):
    def __init__(self, term: str, summary: str):
        self.term = term
        self.reprcrash = ReprFileLocation("", "", summary)

    def toterminal(self, tw: TerminalWriter) -> None:
        tw.write(f"{self.term}\n")


class NotebookFile(pytest.File):
    def collect(self) -> Generator[Any, Any, Any]:
        yield NotebookItem.from_parent(self, filename=self.name)


class NotebookFailedException(Exception):
    pass


class NotebookItem(pytest.Item):
    nbmake = True

    def __init__(self, parent: Any, filename: str):
        super().__init__("", parent)
        self.filename = filename

    def runtest(self):
        # config: Optional[str] = self.parent.config.option.jbc c onfig
        option = self.parent.config.option
        path_output: Path = Path(option.path_output)
        run = NotebookRun(
            Path(self.filename),
            path_output=path_output / Path(os.path.splitext(self.filename)[0]),
            cache=get_cache(path_output / "_build" / ".jupyter_cache"),
            verbose=bool(option.verbose),
        )
        res: NotebookResult = run.execute()
        if res.error != None:
            raise NotebookFailedException(res)

    def repr_failure(self, excinfo: Any, style: Optional[Any] = None) -> TerminalRepr:
        def create_internal_err() -> str:
            tb = "".join(traceback.format_tb(excinfo.tb))
            err = f"{excinfo.value}\n{tb}"
            err_str: str = (
                err
                if os.name == "nt"
                else highlight(
                    err, Python3TracebackLexer(), TerminalTrueColorFormatter()
                )
            )

            return NbMakeFailureRepr(
                "NBMAKE INTERNAL ERROR\n" + err_str,
                "NBMAKE INTERNAL ERROR",
            )

        if type(excinfo.value) != NotebookFailedException:
            return create_internal_err()

        res: NotebookResult = excinfo.value.args[0]
        if isinstance(res.error, type(None)):
            return create_internal_err()

        error: NotebookError = res.error  # type:ignore
        return NbMakeFailureRepr(error.trace, error.summary)

    def reportinfo(self):  # type:ignore
        return self.fspath, 0, self.filename  # type:ignore

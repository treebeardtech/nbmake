import os
import traceback
from pathlib import Path
from typing import Any, Generator, Optional

import nbformat
import pytest
from _pytest._code.code import ReprFileLocation, TerminalRepr, TerminalWriter
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
        yield NotebookItem.from_parent(self, filename=str(Path(self.fspath)))


class NotebookFailedException(Exception):
    pass


class NotebookItem(pytest.Item):
    nbmake = True

    def __init__(self, parent: Any, filename: str):
        super().__init__("", parent)
        self.filename = filename

    def runtest(self):
        option = self.parent.config.option
        source = Path(self.config.rootdir) / self.filename
        run = NotebookRun(
            source,
            option.nbmake_timeout,
            verbose=bool(option.verbose),
            kernel=option.nbmake_kernel,
            find_import_errors=option.nbmake_find_import_errors,
        )

        res: NotebookResult = run.execute()

        if option.overwrite:
            nbformat.write(res.nb, str(source))

        if res.error != None:
            raise NotebookFailedException(res)

    def repr_failure(self, excinfo: Any, style: Optional[Any] = None) -> TerminalRepr:
        def create_internal_err() -> Any:
            tb = "".join(traceback.format_tb(excinfo.tb))
            err = f"{excinfo.value}\n{tb}"
            err_str: Any = (
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

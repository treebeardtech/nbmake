import os
from os import path
import re
import traceback
from pathlib import Path
from typing import Any, Generator, List, Optional, Tuple

import nbformat
import pytest
from _pytest._code.code import ReprFileLocation, TerminalRepr, TerminalWriter
from pygments import highlight
from pygments.formatters import TerminalTrueColorFormatter
from pygments.lexers import Python3TracebackLexer

from .nb_result import NotebookError, NotebookResult
from .nb_run import NotebookRun, convert_and_read_notebook

import jupytext.formats
import jupytext.jupytext


class NbMakeFailureRepr(TerminalRepr):
    def __init__(self, term: str, summary: str):
        self.term = term
        self.reprcrash = ReprFileLocation("", "", summary)

    def toterminal(self, tw: TerminalWriter) -> None:
        tw.write(f"{self.term}\n")


# A list of lists of (index, cell).
Sections = List[List[Tuple[int, Any]]]


def find_sections(nb: nbformat.NotebookNode) -> Sections:
    """Return a list of cells sectioned off by markdown cells.

    Each of the (index, cell) output groups starts with a new markdown cell.
    """
    sections = []
    section = []
    for index, cell in enumerate(nb.cells):
        cell_type = cell["cell_type"]
        if cell_type == "markdown" and re.match("^#+ ", cell["source"]):
            if section:
                sections.append(section)
            section = []
        section.append((index, cell))

    if section:
        sections.append(section)
    return sections


class NotebookFile(pytest.File):
    """Collection entire files as tests."""

    def collect(self) -> Generator[Any, Any, Any]:
        yield NotebookItem.from_parent(self, filename=str(Path(self.fspath)))


class NotebookFileByCell(pytest.File):
    """Break up notebook files into sections each of which a test."""

    def collect(self) -> Generator[Any, Any, Any]:
        """
        Initialization cell groups start with an '# init' markdown cell and
        those seen prior to a test cell are prepended to be run before it.

        Test cell groups start with an '# test' markdown cell and we run the
        initialization cells seen up to this point before running these cells
        as an independent group.

        Other cell groups are simply ignored.
        """
        nb = convert_and_read_notebook(self.fspath)

        sections = find_sections(nb)
        yield from self.tests_from_sections_simple(sections)

    def tests_from_sections_simple(self, sections: Sections):
        init_cells = []
        for section in sections:
            index, cell = next(iter(section))
            assert cell["cell_type"] == "markdown"

            match = re.match(r"#+ (.*)", cell["source"])
            if not match:
                # Cumulate the init cells based on the position.
                init_cells.extend(index for index, _ in section)
            else:
                code_cells = [index for index, _ in section]
                yield NotebookItem.from_parent(
                    self,
                    name=match.group(1).strip(),
                    filename=str(Path(self.fspath)),
                    cell_indices=(init_cells + code_cells),
                )

    def tests_from_sections_explicit(self, sections: Sections):
        init_cells = []
        for section in sections:
            index, cell = next(iter(section))
            assert cell["cell_type"] == "markdown"

            if re.match(r"#+ init\b", cell["source"]):
                # Cumulate the init cells based on the position.
                init_cells.extend(index for index, _ in section)

            elif re.match(r"#+ test\b", cell["source"]):
                match = re.match(r"#+ test:(.*)", cell["source"])
                code_cells = [index for index, _ in section]
                yield NotebookItem.from_parent(
                    self,
                    name=match.group(1).strip(),
                    filename=str(Path(self.fspath)),
                    cell_indices=(init_cells + code_cells),
                )


class NotebookFailedException(Exception):
    pass


class NotebookItem(pytest.Item):
    """A notebook item, either a complete file, or a subset of cells."""

    nbmake = True

    def __init__(
        self,
        parent: Any,
        name: str,
        filename: str,
        cell_indices: Optional[List[int]] = None,
    ):
        super().__init__(name, parent)
        self.filename = filename

        # Note: if 'cell_indices' is None, the entire notebook is executed as
        # one. Otherwise the subset of given cell inidces is executed.
        self.cell_indices = cell_indices

    def runtest(self):
        option = self.parent.config.option
        source = Path(self.config.rootdir) / self.filename

        run = NotebookRun(
            source,
            option.nbmake_timeout,
            verbose=bool(option.verbose),
            kernel=option.nbmake_kernel,
            cell_indices=self.cell_indices
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

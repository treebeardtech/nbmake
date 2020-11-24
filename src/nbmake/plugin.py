from fnmatch import fnmatch
from typing import Any, Generator, Optional

import pytest  # type: ignore
from _pytest.config.argparsing import Parser  # type: ignore

from .jupyter_book_result import JupyterBookResult
from .jupyter_book_run import JupyterBookRun


def pytest_addoption(parser: Any):
    group = parser.getgroup("nbmake", "notebook testing")
    group.addoption("--nbmake", action="store_true", help="Test Jupyter notebooks")


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

    def runtest(self):
        run = JupyterBookRun(self.filename)
        res: JupyterBookResult = run.execute()

        if res.failing_cell_index != None:
            raise NotebookFailedException(res)

    def repr_failure(self, excinfo: Any):
        if type(excinfo.value) != NotebookFailedException:
            raise excinfo.value

        res: JupyterBookResult = excinfo.value.args[0]
        return f"🍋 repr_failure\n {res.document['cells'][res.failing_cell_index]}"

    def reportinfo(self):
        return f"reportinfo {self.filename} 🍋 info", 0, f"reportinfo {self.filename} 🍋 info"  # type: ignore

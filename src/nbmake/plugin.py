import os
from fnmatch import fnmatch
from typing import Any, Generator, Optional

import pytest  # type: ignore
from _pytest.config.argparsing import Parser  # type: ignore
from jupyter_book.commands import build


def pytest_addoption(parser: Any):
    group = parser.getgroup("nbmake", "notebook testing")
    group.addoption("--nbmake", action="store_true", help="Test Jupyter notebooks")
    group.addoption(
        "--nbmake-cell-timeout",
        action="store",
        default=2000,
        type=float,
        help="Timeout for cell execution, in seconds.",
    )


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


class NotebookItem(pytest.Item):  # type: ignore
    def __init__(self, parent, filename):
        super().__init__("", parent)
        self.filename = filename

    def runtest(self):
        print(f"cwd: {os.getcwd()}")

        build(self.filename)

    def repr_failure(self, excinfo: Any):
        # print_tb(excinfo.tb)
        return f"🍋 repr_failure {excinfo.value}"

    def reportinfo(self):
        return f"reportinfo {self.filename} 🍋 info", 0, f"reportinfo {self.filename} 🍋 info"  # type: ignore


# def pytest_runtest_makereport(item, call):
#     if call.when == "setup":
#         print("Called after setup for test case is executed.")
#     if call.when == "call":
#         print("Called after test case is executed.")
#         print("-->{}<--".format(call.excinfo))
#     if call.when == "teardown":
#         print("Called after teardown for test case is executed.")

import os
import sys
from fnmatch import fnmatch
from traceback import print_tb
from typing import Any, Generator, Optional

import pytest  # type: ignore
from _pytest.config.argparsing import Parser  # type: ignore

from .conf import NbMakeContext
from .helper import create_github_details
from .runtime.run import NotebookRun


def pytest_addoption(parser: Any):
    group = parser.getgroup("general")
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
        yield NotebookItem.from_parent(self, name=self.name, spec={})


class NotebookItem(pytest.Item):  # type: ignore
    def __init__(self, name, parent, spec):
        super().__init__(name, parent)
        self.spec = spec

    def runtest(self):
        print(f"cwd: {os.getcwd()}")
        ctx = NbMakeContext(
            **{
                "api_url": "",
                "api_key": "",
                "filename": self.name,
                "github_details": create_github_details(),
            }
        )
        nb_run = NotebookRun(ctx)
        status = nb_run.start()
        if status != 0:
            raise Exception("tb failed")

    def repr_failure(self, excinfo: Any):
        print_tb(excinfo.tb)
        sys.stderr.write(str(excinfo.value))
        return

    def reportinfo(self):
        return "info"

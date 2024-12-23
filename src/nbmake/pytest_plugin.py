import asyncio
import os
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Any, Optional

from pytest import ExitCode

from .pytest_items import NotebookFile


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
        "--nbmake-find-import-errors",
        action="store_true",
        help="Runs all cells, only reports import errors",
        default=False,
    )


def _should_collect(p: Path, nbmake_enabled: bool):
    return nbmake_enabled and p.match("*ipynb") and "_build" not in p.parts


ver: int = int(version("pytest")[0])
if ver < 7:

    def pytest_collect_file(path: str, parent: Any) -> Optional[Any]:
        if _should_collect(Path(path), parent.config.option.nbmake):
            return NotebookFile.from_parent(parent, fspath=path)

else:

    def pytest_collect_file(file_path: Path, parent: Any) -> Optional[Any]:
        if _should_collect(file_path, parent.config.option.nbmake):
            return NotebookFile.from_parent(parent, path=file_path)


def pytest_terminal_summary(terminalreporter: Any, exitstatus: int, config: Any):
    if config.option.nbmake:
        # this message can be disabled with pytest --no-summary
        # but let us know if it is annoying you
        # ...we can also print diagnostics/stats here -- requests welcome
        try:
            if os.environ.get("GITHUB_ACTIONS", False):
                if exitstatus == ExitCode.TESTS_FAILED:
                    print(
                        "\n* nbmake: Automate reading GitHub Actions logs with our bot: https://github.com/marketplace/treebeard-build\n"
                    )
            else:
                print(
                    "\nLearn more about nbmake at https://github.com/treebeardtech/nbmake\n"
                )
        except:  # noqa
            pass

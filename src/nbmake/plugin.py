import os
import traceback
import uuid
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Generator, List, Optional

import pytest  # type: ignore
import yaml
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
from .util import data_dir


def pytest_addoption(parser: Any):
    group = parser.getgroup("nbmake", "notebook testing")
    group.addoption("--nbmake", action="store_true", help="Test notebooks")
    group.addoption(
        "--jbconfig",
        action="store",
        help="Your jupyter-book config file",
    )
    group.addoption(
        "--path-output", action="store", default=str(data_dir / str(uuid.uuid4()))
    )
    # "--warningiserror",
    # "--nitpick",


def pytest_configure(config: Config):  # type: ignore
    # hack to prevent race condition initialising cache
    config_path = Path("_config.yml")
    path_out: str = config.option.path_output
    config_path.write_text(
        yaml.dump(
            {
                "exclude_patterns": [".*/**/*", "Library/**/*", ".pytest_cache/**/*"],
                "execute": {
                    "execute_notebooks": "cache",
                    "cache": str(Path(path_out) / "cache"),
                    # "only_build_toc_files": True
                },
            }
        )
    )


def pytest_collect_file(path: str, parent: Any) -> Optional[Any]:  # type: ignore
    """
    Collect IPython notebooks using the specified pytest hook
    """
    opt = parent.config.option
    if opt.nbmake and fnmatch(path, "*.ipynb"):
        return NotebookFile.from_parent(parent, fspath=path)  # type: ignore

    return None


def pytest_collectreport(report: Any) -> None:
    """Collector finished collecting."""
    build_toc([Path(i.name) for i in report.result if isinstance(i, NotebookFile)])


def build_toc(files: List[Path]):
    toc = [{"file": str(f).replace(".ipynb", "")} for f in files]
    if len(toc) == 0:
        return
    toc[0]["title"] = "test results"
    toc_path = Path("_toc.yml")
    toc_path.write_text(yaml.dump(toc))


def pytest_sessionfinish(session: Any, exitstatus: Any):
    """ whole test run finishes. """

    toc_path = "_toc.yml"
    if not (getattr(session.config.option, "nbmake") and Path(toc_path).exists()):
        return

    import subprocess
    from subprocess import CalledProcessError

    from .jupyter_book_run import JB_BINARY

    config_path = "_config.yml"

    args = [
        str(JB_BINARY),
        "build",
        f"--toc={toc_path}",
        f"--config={config_path}",
        f"--path-output={session.config.option.path_output}",
        str(session.config.rootdir),
    ]
    try:
        print("\n\nBUILDING FINAL")
        out = subprocess.check_output(args, stderr=subprocess.STDOUT)
        print(out.decode())
    except CalledProcessError as err:
        print(err.output.decode())
    # run with only_build_toc_files: true


# def pytest_terminal_summary(terminalreporter, exitstatus, config):

#     toc_path = Path(config.option.toc)
#     if not toc_path.exists():
#         pass
#     terminalreporter.line(f"BUILDING BOOK: jb build --toc {config.option.toc} --path-output {config.option.path_output} {config.rootdir}")
#     # run with only_build_toc_files: true


# reports = terminalreporter.getreports('')
# content = os.linesep.join(text for report in reports for secname, text in report.sections)
# if content:
#     terminalreporter.ensure_newline()
#     terminalreporter.section('My custom section', sep='-', blue=True, bold=True)
#     terminalreporter.line(content)


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
